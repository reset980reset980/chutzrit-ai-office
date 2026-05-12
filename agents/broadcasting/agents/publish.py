"""Publish Agent for broadcasting packages."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from agents.broadcasting.pipeline.config import PROJECT_ROOT, RuntimeConfig
from agents.broadcasting.publishers import LinkedInPublisher, PublishResult, TistoryPublisher


PublisherFactory = Callable[[], Any]


class PublishAgent:
    """Plan and execute sequential publishing after the final quality gate."""

    name = "PublishAgent"

    def __init__(
        self,
        config: RuntimeConfig,
        *,
        tistory_publisher_factory: PublisherFactory | None = None,
        linkedin_publisher_factory: PublisherFactory | None = None,
    ) -> None:
        self.config = config
        self.tistory_publisher_factory = tistory_publisher_factory
        self.linkedin_publisher_factory = linkedin_publisher_factory

    def run(self, package: dict[str, Any]) -> dict[str, Any]:
        """Build a publish plan without executing external side effects."""
        return self.build_plan(package)

    def build_plan(self, package: dict[str, Any]) -> dict[str, Any]:
        """Build a publish plan without pretending absent adapters succeeded."""
        reflection = package.get("reflection", {})
        score = int(reflection.get("score", 0))
        quality_passed = score >= 90
        quality_ready = self._quality_ready(package)
        public_requires_approval = self.config.public_content_require_approval

        blog_status = self._blog_status(public_requires_approval, quality_ready)
        linkedin_status = self._linkedin_status(blog_status, public_requires_approval, quality_ready)
        discord_status = "auto_dispatch_pending" if self.config.discord_channel_auto_publish else "disabled"
        external_api_status = self._external_api_status(blog_status, linkedin_status)

        return {
            "agent": self.name,
            "quality_score": score,
            "quality_passed": quality_passed,
            "quality_ready_for_publish": quality_ready,
            "external_api_status": external_api_status,
            "processing_mode": "sequential_tistory_first_with_discord_dispatch",
            "executed_at": "",
            "publish_strategy": {
                "mode": "sequential",
                "order": ["blog", "linkedin", "discord"],
                "dependencies": {
                    "blog": [],
                    "linkedin": ["blog.url"],
                    "discord": [],
                },
                "reason": "LinkedIn 원고는 티스토리 실제 발행 URL이 필요하므로 블로그를 먼저 발행한다.",
            },
            "channels": {
                "blog": {
                    "status": blog_status,
                    "provider": self._blog_provider(),
                    "url": "",
                    "reason": self._reason_for_status(blog_status),
                    "details": {},
                },
                "linkedin": {
                    "status": linkedin_status,
                    "provider": "linkedin_posts_api",
                    "url": "",
                    "reason": self._reason_for_status(linkedin_status),
                    "details": {},
                },
                "discord": {
                    "status": discord_status,
                    "provider": "discord_channel",
                    "url": "",
                    "reason": "Discord 봇이 final 파일을 채널에 자동 발송한다.",
                    "details": {},
                },
            },
        }

    def execute(
        self,
        package: dict[str, Any],
        output_path: Path,
        *,
        progress_callback: Callable[[str], None] | None = None,
    ) -> dict[str, Any]:
        """Execute enabled external publishers in Tistory-first order."""
        plan = self.build_plan(package)
        package["publish_plan"] = plan
        channels = plan["channels"]

        if channels["blog"]["status"] == "ready":
            blog_result = self._publish_blog(package, output_path)
            channels["blog"] = blog_result.to_dict()
        else:
            blog_result = PublishResult(channel="blog", **channels["blog"])

        if blog_result.status == "published" and blog_result.url:
            package.setdefault("drafts", {})["linkedin"] = replace_blog_link(
                str(package.get("drafts", {}).get("linkedin", "")),
                blog_result.url,
            )
            if self._linkedin_status("published", self.config.public_content_require_approval, True) == "ready":
                channels["linkedin"] = self._publish_linkedin(package).to_dict()
            else:
                linkedin_status = self._linkedin_status("published", self.config.public_content_require_approval, True)
                channels["linkedin"] = {
                    "status": linkedin_status,
                    "provider": "linkedin_posts_api",
                    "url": "",
                    "reason": self._reason_for_status(linkedin_status),
                    "details": {},
                }
        else:
            channels["linkedin"] = PublishResult(
                channel="linkedin",
                status="blocked_until_blog_url",
                provider="linkedin_posts_api",
                reason=self._reason_for_status("blocked_until_blog_url"),
            ).to_dict()

        plan["external_api_status"] = self._external_api_status(
            channels["blog"]["status"],
            channels["linkedin"]["status"],
        )
        plan["executed_at"] = datetime.now().isoformat()
        package["publish_plan"] = plan
        return plan

    def _publish_blog(self, package: dict[str, Any], output_path: Path) -> PublishResult:
        publisher = self._tistory_publisher()
        blog_markdown = str(package.get("drafts", {}).get("blog", ""))
        return publisher.publish(blog_markdown, output_dir=output_path)

    def _publish_linkedin(self, package: dict[str, Any]) -> PublishResult:
        publisher = self._linkedin_publisher()
        linkedin_text = str(package.get("drafts", {}).get("linkedin", ""))
        if "[블로그 링크]" in linkedin_text:
            return PublishResult(
                channel="linkedin",
                status="blocked_until_blog_url",
                provider="linkedin_posts_api",
                reason="LinkedIn 원고에 [블로그 링크] 자리표시자가 남아 있어 공개 게시를 중단한다.",
            )
        return publisher.publish(linkedin_text)

    def _tistory_publisher(self) -> Any:
        if self.tistory_publisher_factory:
            return self.tistory_publisher_factory()
        return TistoryPublisher(
            manage_url=self.config.tistory_manage_url,
            blog_url=self.config.tistory_blog_url,
            write_url=self.config.tistory_write_url,
            storage_state=self.config.playwright_storage_state,
            headless=self.config.playwright_headless,
            publish_mode=self.config.tistory_publish_mode,
        )

    def _linkedin_publisher(self) -> Any:
        if self.linkedin_publisher_factory:
            return self.linkedin_publisher_factory()
        return LinkedInPublisher(
            access_token=self.config.linkedin_access_token,
            author_urn=self.config.linkedin_author_urn,
            version=self.config.linkedin_version,
        )

    def _quality_ready(self, package: dict[str, Any]) -> bool:
        reflection = package.get("reflection", {})
        if int(reflection.get("score", 0)) >= 90:
            return True
        revision_count = int(package.get("revision_count", 0))
        max_revision_loops = int(package.get("max_revision_loops", 3))
        return revision_count >= max_revision_loops

    def _blog_status(self, public_requires_approval: bool, quality_ready: bool) -> str:
        if not quality_ready:
            return "quality_gate_blocked"
        if public_requires_approval:
            return "approval_required"
        if not self.config.tistory_auto_publish:
            return "external_publish_disabled"
        if self.config.blog_publisher != "tistory":
            return "unsupported_provider"
        if not self.config.tistory_manage_url:
            return "not_connected"
        if not self._storage_state_ready():
            return "not_connected"
        if self.config.tistory_publish_mode.lower() != "public":
            return "external_publish_disabled"
        return "ready"

    def _linkedin_status(self, blog_status: str, public_requires_approval: bool, quality_ready: bool) -> str:
        if not quality_ready:
            return "quality_gate_blocked"
        if public_requires_approval:
            return "approval_required"
        if blog_status not in {"published"}:
            return "blocked_until_blog_url"
        if not self.config.linkedin_auto_publish:
            return "external_publish_disabled"
        if not self.config.linkedin_access_token or not self.config.linkedin_author_urn:
            return "not_connected"
        return "ready"

    def _storage_state_ready(self) -> bool:
        if not self.config.playwright_storage_state:
            return False
        path = Path(self.config.playwright_storage_state).expanduser()
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path.exists()

    def _blog_provider(self) -> str:
        if self.config.blog_publisher == "tistory":
            return "tistory_playwright"
        return self.config.blog_publisher

    @staticmethod
    def _reason_for_status(status: str) -> str:
        reasons = {
            "approval_required": "공개 게시 전 사용자 승인이 필요하다.",
            "blocked_until_blog_url": "티스토리 실제 발행 URL이 없어 LinkedIn 공개 게시를 중단한다.",
            "dependency_missing": "필수 실행 패키지가 설치되지 않았다.",
            "external_publish_disabled": "자동 공개 게시 설정이 꺼져 있다.",
            "failed": "플랫폼 게시 중 오류가 발생했다.",
            "not_connected": "필수 세션, 토큰, 또는 연결 정보가 준비되지 않았다.",
            "published": "공개 게시가 완료됐다.",
            "quality_gate_blocked": "품질 게이트가 아직 배포 조건을 충족하지 못했다.",
            "ready": "자동 공개 게시 조건이 준비됐다.",
            "unsupported_provider": "지원하지 않는 블로그 배포 제공자다.",
        }
        return reasons.get(status, "")

    @staticmethod
    def _external_api_status(blog_status: str, linkedin_status: str) -> str:
        statuses = {blog_status, linkedin_status}
        if "approval_required" in statuses:
            return "approval_required"
        if "ready" in statuses:
            return "ready"
        if statuses == {"published"}:
            return "published"
        if "published" in statuses and statuses <= {"published", "external_publish_disabled"}:
            return "partial_published"
        if "failed" in statuses or "dependency_missing" in statuses:
            return "failed"
        if "not_connected" in statuses or "blocked_until_blog_url" in statuses:
            return "not_connected"
        if statuses == {"external_publish_disabled"}:
            return "disabled"
        if "quality_gate_blocked" in statuses:
            return "quality_gate_blocked"
        return "not_connected"


def replace_blog_link(linkedin_text: str, blog_url: str) -> str:
    """Replace LinkedIn blog-link placeholders with the actual Tistory URL."""
    updated = (
        linkedin_text.replace("[블로그 링크]", blog_url)
        .replace("{BLOG_URL}", blog_url)
        .replace("BLOG_URL", blog_url)
    )
    if blog_url not in updated:
        updated = updated.rstrip() + f"\n\n자세한 글은 블로그에서 볼 수 있습니다.\n{blog_url}"
    return updated

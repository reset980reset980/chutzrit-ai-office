"""Tests for the broadcasting multi-agent pipeline."""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from agents.broadcasting.pipeline.config import RuntimeConfig, load_runtime_config
from agents.broadcasting.pipeline.progress import format_multi_platform_publish_report
from agents.broadcasting.pipeline.generator import generate_content_package
from agents.broadcasting.pipeline import storage
from agents.broadcasting.pipeline.visuals import generate_visual_assets_for_saved_package
from agents.broadcasting.agents import InputParserAgent, PublishAgent
from agents.broadcasting.publishers import PublishResult
from agents.broadcasting.publishers.tistory import markdown_to_tistory_html
from scripts.save_tistory_session import assert_isolated_browser_profile_dir, known_real_browser_profile_dirs


class FakeJSONClient:
    """Prompt-aware fake client for multi-agent orchestration tests."""

    def __init__(self) -> None:
        self.calls: list[str] = []
        self.lock = threading.Lock()

    def create_json(self, prompt: str, *, max_output_tokens: int = 12000) -> dict:
        with self.lock:
            self.calls.append(prompt)

        if "Content Strategy Agent" in prompt:
            return {
                "title": "AI 자동화는 답변보다 운영 구조다",
                "source_summary": "AI 자동화에서 프롬프트보다 실행 구조가 중요하다는 메모",
                "strategy": {
                    "core_message": "핵심은 답변이 아니라 운영 구조다.",
                    "target_reader": "AI 자동화 실무자와 1인 창업자",
                    "claim": "AI 자동화 품질은 프롬프트보다 입력, 도구, 검증 설계에서 갈린다.",
                    "platform_directions": {
                        "blog": "운영 구조 중심으로 길게 설명한다.",
                        "linkedin": "전문가용 인사이트로 압축한다.",
                        "telegram": "짧은 실행 기준으로 전달한다.",
                    },
                },
            }
        if "Insight Agent" in prompt:
            return {
                "chutzrit_insight": "프롬프트는 시작점이고, 운영 구조는 실패를 복구하는 설계다.",
                "practical_points": ["입력 계약을 정한다.", "검증 기준을 둔다."],
                "examples": ["콘텐츠 자동 배포 전에 품질 게이트를 둔다."],
                "cautions": ["검증 없는 자동 발행은 브랜드 리스크가 된다."],
            }
        if "Blog Writer Agent" in prompt:
            return {
                "draft": (
                    "# AI 자동화는 답변보다 운영 구조다\n\n"
                    "## 문제는 프롬프트가 아니다\n"
                    "AI 자동화의 핵심은 더 좋은 문장을 쓰는 일이 아니라 반복 실행되는 운영 구조를 설계하는 일이다.\n\n"
                    "## 필요한 설계\n"
                    "입력, 도구, 권한, 검증 기준이 분리되어 있어야 한다.\n\n"
                    "## 실무 기준\n"
                    "문제는 모델이 아니라 실패해도 복구되는 구조가 있는지에서 갈린다."
                )
            }
        if "LinkedIn Writer Agent" in prompt:
            return {
                "draft": (
                    "AI 자동화의 차이는 답변이 아니라 구조에서 납니다\n\n"
                    "같은 프롬프트를 써도 결과가 갈리는 이유는 모델보다 운영 구조에 있습니다.\n\n"
                    "입력, 도구, 권한, 검증 기준을 먼저 설계해야 합니다.\n\n"
                    "블로그 전문 [블로그 링크]"
                )
            }
        if "Telegram Newsletter Writer Agent" in prompt:
            return {
                "draft": (
                    "## AI 자동화는 구조부터 봐야 합니다\n"
                    "프롬프트만 고치면 자동화가 좋아진다고 보기 쉽습니다. 실제 차이는 입력과 검증 기준을 어떻게 운영하느냐에서 납니다.\n\n"
                    "- 입력 형식을 먼저 정하세요.\n"
                    "- 실패했을 때 멈추는 기준을 두세요."
                )
            }
        if "Self Reflection Agent" in prompt:
            return {
                "score": 92,
                "passed": True,
                "channel_scores": {"blog": 92, "linkedin": 91, "telegram": 91},
                "strengths": ["채널별 기준을 충족한다."],
                "problems": [],
                "revision_instructions": [],
                "publish_status": "자동 발송 가능",
            }
        if "Image Prompt Agent" in prompt:
            base_prompt = (
                "A practical AI automation workspace with a laptop, connected workflow nodes, "
                "clean editorial lighting, no text, no logo, no watermark"
            )
            return {
                "prompts": {
                    "blog": {
                        "purpose": "blog_hero",
                        "size": "1536x1024",
                        "quality": "medium",
                        "prompt": base_prompt,
                    },
                    "linkedin": {
                        "purpose": "linkedin_feed",
                        "size": "1024x1024",
                        "quality": "medium",
                        "prompt": base_prompt,
                    },
                    "telegram": {
                        "purpose": "telegram_newsletter",
                        "size": "1024x1024",
                        "quality": "medium",
                        "prompt": base_prompt,
                    },
                }
            }
        if "Visual Quality Agent" in prompt:
            return {
                "score": 91,
                "passed": True,
                "problems": [],
                "recommendations": ["현재 이미지 방향을 유지한다."],
            }
        if "Visual Strategy Agent" in prompt:
            return {
                "visual_concept": "AI 자동화 운영실의 작업 흐름",
                "mood": "실용적이고 선명한 기술 교육 분위기",
                "subject": "노트북과 자동화 플로우가 보이는 책상",
                "metaphor": "AI를 도구가 아니라 운영 구조 안에 배치하는 장면",
                "avoid": ["text", "logo", "watermark", "stock photo look"],
                "channels": {
                    "blog": "넓은 대표 이미지로 운영 구조를 보여준다.",
                    "linkedin": "피드에서 메시지가 즉시 보이는 정사각형 장면.",
                    "telegram": "작고 선명한 뉴스레터용 장면.",
                },
            }
        raise AssertionError(f"Unexpected prompt: {prompt[:200]}")


class RevisionFakeJSONClient(FakeJSONClient):
    """Fake client that forces one blog-only revision loop."""

    def __init__(self) -> None:
        super().__init__()
        self.reflection_count = 0

    def create_json(self, prompt: str, *, max_output_tokens: int = 12000) -> dict:
        if prompt.startswith("너는 후츠릿 콘텐츠의 Self Reflection Agent"):
            with self.lock:
                self.calls.append(prompt)
                self.reflection_count += 1
                count = self.reflection_count
            if count == 1:
                return {
                    "score": 85,
                    "passed": False,
                    "channel_scores": {"blog": 80, "linkedin": 92, "telegram": 92},
                    "strengths": ["LinkedIn과 Telegram은 기준을 충족한다."],
                    "problems": ["블로그 훅이 약하다."],
                    "revision_instructions": ["블로그만 더 선명하게 수정하라."],
                    "publish_status": "수정 필요",
                }
            return {
                "score": 93,
                "passed": True,
                "channel_scores": {"blog": 93, "linkedin": 92, "telegram": 92},
                "strengths": ["수정 기준을 충족한다."],
                "problems": [],
                "revision_instructions": [],
                "publish_status": "자동 발송 가능",
            }
        if "블로그 원고 하나만 수정" in prompt:
            with self.lock:
                self.calls.append(prompt)
            return {
                "draft": (
                    "# AI 자동화는 운영 구조에서 갈린다\n\n"
                    "## 문제는 답변 품질이 아니다\n"
                    "핵심은 자동화가 실패했을 때 멈추고 복구되는 운영 설계를 갖추는 일이다.\n\n"
                    "## 필요한 설계\n"
                    "입력 계약, 도구 권한, 검증 기준을 분리해야 한다.\n\n"
                    "## 실무 기준\n"
                    "차이는 프롬프트가 아니라 반복 가능한 구조에서 갈린다."
                )
            }
        return super().create_json(prompt, max_output_tokens=max_output_tokens)


class SlowWriterFakeJSONClient(FakeJSONClient):
    """Fake client that makes writer prompts slow enough to prove parallelism."""

    def create_json(self, prompt: str, *, max_output_tokens: int = 12000) -> dict:
        writer_markers = (
            "Blog Writer Agent",
            "LinkedIn Writer Agent",
            "Telegram Newsletter Writer Agent",
        )
        if any(marker in prompt for marker in writer_markers):
            time.sleep(0.25)
        return super().create_json(prompt, max_output_tokens=max_output_tokens)


class MaxRevisionFakeJSONClient(FakeJSONClient):
    """Fake client that never passes reflection so loop limit can be verified."""

    def __init__(self) -> None:
        super().__init__()
        self.reflection_count = 0

    def create_json(self, prompt: str, *, max_output_tokens: int = 12000) -> dict:
        if prompt.startswith("너는 후츠릿 콘텐츠의 Self Reflection Agent"):
            with self.lock:
                self.calls.append(prompt)
                self.reflection_count += 1
            return {
                "score": 82,
                "passed": False,
                "channel_scores": {"blog": 82, "linkedin": 82, "telegram": 82},
                "strengths": [],
                "problems": ["전체 메시지가 약하다."],
                "revision_instructions": ["각 채널의 주장을 더 선명하게 수정하라."],
                "publish_status": "수정 필요",
            }
        if "원고 하나만 수정" in prompt:
            with self.lock:
                self.calls.append(prompt)
            if "블로그 원고 하나만 수정" in prompt:
                return {"draft": "# 수정된 블로그\n\n## 문제\n본문\n\n## 구조\n본문\n\n## 기준\n본문"}
            if "LinkedIn 원고 하나만 수정" in prompt:
                return {"draft": "수정된 LinkedIn\n\n본문입니다.\n\n블로그 전문 [블로그 링크]"}
            return {"draft": "## 수정된 Telegram 뉴스레터\n본문입니다."}
        return super().create_json(prompt, max_output_tokens=max_output_tokens)


class FakeImageClient:
    """Fake image client that writes deterministic image bytes."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, Path, str, str]] = []

    def generate_image(
        self,
        prompt: str,
        output_path: Path,
        *,
        size: str,
        quality: str,
    ) -> dict[str, str]:
        """Write a tiny placeholder image file without external APIs."""
        self.calls.append((prompt, output_path, size, quality))
        output_path.write_bytes(b"fake-png-bytes")
        return {"provider": "fake_image_client", "model": "fake-image-model"}


def build_config(*, image_generation_enabled: bool = False) -> RuntimeConfig:
    """Build a minimal runtime config for tests."""
    return RuntimeConfig(
        discord_webhook_url="https://discord.example/webhook",
        discord_bot_token="token",
        discord_guild_id="guild",
        discord_broadcasting_channel_id="channel",
        discord_newsletter_channel_id="newsletter",
        discord_allowed_user_ids={"user"},
        openai_api_key="key",
        image_generation_enabled=image_generation_enabled,
    )


def build_publish_config(storage_state: str) -> RuntimeConfig:
    """Build a config with external publishers enabled."""
    return RuntimeConfig(
        discord_webhook_url="https://discord.example/webhook",
        discord_bot_token="token",
        discord_guild_id="guild",
        discord_broadcasting_channel_id="channel",
        discord_newsletter_channel_id="newsletter",
        discord_allowed_user_ids={"user"},
        openai_api_key="key",
        tistory_manage_url="https://chutzrit.tistory.com/manage",
        tistory_auto_publish=True,
        playwright_storage_state=storage_state,
        linkedin_access_token="linkedin-token",
        linkedin_author_urn="urn:li:person:123",
        linkedin_auto_publish=True,
    )


class FakeTistoryPublisher:
    """Fake Tistory publisher for publish-agent tests."""

    def __init__(self, result: PublishResult) -> None:
        self.result = result
        self.calls = 0

    def publish(self, markdown: str, *, output_dir: Path) -> PublishResult:
        self.calls += 1
        return self.result


class FakeLinkedInPublisher:
    """Fake LinkedIn publisher for publish-agent tests."""

    def __init__(self) -> None:
        self.calls = 0
        self.last_text = ""

    def publish(self, text: str) -> PublishResult:
        self.calls += 1
        self.last_text = text
        return PublishResult(
            channel="linkedin",
            status="published",
            provider="linkedin_posts_api",
            url="https://www.linkedin.com/feed/update/urn:li:share:123/",
            reason="LinkedIn 게시 완료",
        )


class BroadcastingMultiAgentTests(unittest.TestCase):
    def test_input_parser_detects_memo_link_and_link_with_memo(self) -> None:
        parser = InputParserAgent(fetch_links=False)

        memo = parser.run("Codex를 써보니까 에이전트 시대가 왔다는 게 실감난다.")
        link = parser.run("https://example.com/article")
        link_with_memo = parser.run("이 관점이 중요하다 https://example.com/article")

        self.assertEqual(memo["input_type"], "memo")
        self.assertEqual(link["input_type"], "link")
        self.assertEqual(link_with_memo["input_type"], "link_with_memo")
        self.assertEqual(link["urls"], ["https://example.com/article"])

    def test_telegram_runtime_config_does_not_require_discord_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "TELEGRAM_BOT_TOKEN=123456:test-token",
                        "TELEGRAM_BROADCASTING_CHAT_ID=1001",
                        "TELEGRAM_NEWSLETTER_CHAT_ID=1002",
                        "TELEGRAM_ALLOWED_USER_IDS=42,43",
                        "OPENAI_API_KEY=test-openai-key",
                    ]
                ),
                encoding="utf-8",
            )

            with patch.dict(os.environ, {}, clear=True):
                config = load_runtime_config(
                    env_path,
                    require_discord=False,
                    require_telegram=True,
                )

        self.assertEqual(config.telegram_bot_token, "123456:test-token")
        self.assertEqual(config.telegram_broadcasting_chat_id, "1001")
        self.assertEqual(config.telegram_newsletter_chat_id, "1002")
        self.assertEqual(config.telegram_allowed_user_ids, {"42", "43"})
        self.assertEqual(config.discord_bot_token, "")

    def test_telegram_runtime_config_can_bootstrap_without_chat_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "TELEGRAM_BOT_TOKEN=123456:test-token",
                    ]
                ),
                encoding="utf-8",
            )

            with patch.dict(os.environ, {}, clear=True):
                config = load_runtime_config(
                    env_path,
                    require_discord=False,
                    require_telegram=True,
                    require_openai=False,
                )

        self.assertEqual(config.telegram_bot_token, "123456:test-token")
        self.assertEqual(config.telegram_broadcasting_chat_id, "")
        self.assertEqual(config.telegram_newsletter_chat_id, "")
        self.assertEqual(config.openai_api_key, "")

    def test_generate_content_package_uses_independent_subagents(self) -> None:
        client = FakeJSONClient()

        package = generate_content_package(
            "AI 자동화는 프롬프트보다 운영 구조가 중요하다.",
            build_config(),
            client=client,
        )

        self.assertEqual(package["agent_architecture"]["mode"], "multi_agent")
        self.assertEqual(package["drafts"]["blog"].splitlines()[0], "# AI 자동화는 답변보다 운영 구조다")
        self.assertEqual(package["reflection"]["score"], 92)
        self.assertEqual(package["revision_count"], 0)
        self.assertEqual(package["publish_plan"]["channels"]["blog"]["status"], "external_publish_disabled")
        self.assertEqual(package["publish_plan"]["publish_strategy"]["order"], ["blog", "linkedin", "telegram"])
        self.assertEqual(package["publish_plan"]["publish_strategy"]["dependencies"]["linkedin"], ["blog.url"])

        joined_calls = "\n".join(client.calls)
        for marker in (
            "Content Strategy Agent",
            "Insight Agent",
            "Blog Writer Agent",
            "LinkedIn Writer Agent",
            "Telegram Newsletter Writer Agent",
            "Self Reflection Agent",
        ):
            self.assertIn(marker, joined_calls)

    def test_visual_agents_prepare_and_generate_saved_images(self) -> None:
        client = FakeJSONClient()
        package = generate_content_package(
            "Codex를 써보니까 에이전트 시대가 왔다는 게 실감난다.",
            build_config(image_generation_enabled=True),
            client=client,
        )

        self.assertEqual(package["visual_assets"]["status"], "pending_generation")
        self.assertIn("VisualStrategyAgent", package["agent_architecture"]["agents"])
        self.assertIn("ImagePromptAgent", package["agent_architecture"]["agents"])

        with tempfile.TemporaryDirectory() as temp_dir:
            original_output_root = storage.OUTPUT_ROOT
            storage.OUTPUT_ROOT = Path(temp_dir)
            try:
                draft_path = storage.save_content_package(
                    package,
                    now=datetime(2026, 5, 12, 9, 0, 0),
                )
                image_client = FakeImageClient()
                visual_assets = generate_visual_assets_for_saved_package(
                    package,
                    build_config(image_generation_enabled=True),
                    draft_path,
                    client=client,
                    image_client=image_client,
                )
            finally:
                storage.OUTPUT_ROOT = original_output_root

            final_path = Path(temp_dir) / "final" / draft_path.name
            metadata = json.loads((draft_path / "metadata.json").read_text(encoding="utf-8"))
            visual_quality = json.loads((draft_path / "visual-quality.json").read_text(encoding="utf-8"))

            self.assertEqual(visual_assets["status"], "generated")
            self.assertEqual(len(image_client.calls), 3)
            self.assertTrue((draft_path / "visuals" / "blog.png").exists())
            self.assertTrue((final_path / "visuals" / "blog.png").exists())
            self.assertEqual(metadata["visual_assets_status"], "generated")
            self.assertEqual(visual_quality["score"], 91)

    def test_platform_writers_run_in_parallel(self) -> None:
        client = SlowWriterFakeJSONClient()

        started_at = time.perf_counter()
        generate_content_package(
            "AI 자동화는 프롬프트보다 운영 구조가 중요하다.",
            build_config(),
            client=client,
        )
        elapsed = time.perf_counter() - started_at

        self.assertLess(elapsed, 0.65)

    def test_revision_agent_revises_failed_channel_only(self) -> None:
        client = RevisionFakeJSONClient()

        package = generate_content_package(
            "AI 자동화는 프롬프트보다 운영 구조가 중요하다.",
            build_config(),
            client=client,
        )

        self.assertEqual(package["revision_count"], 1)
        self.assertEqual(package["reflection"]["score"], 93)
        self.assertIn("운영 구조에서 갈린다", package["drafts"]["blog"])
        self.assertIn("블로그 전문 [블로그 링크]", package["drafts"]["linkedin"])

        revision_calls = [call for call in client.calls if "원고 하나만 수정" in call]
        self.assertEqual(len(revision_calls), 1)
        self.assertIn("블로그 원고 하나만 수정", revision_calls[0])

    def test_revision_loop_is_limited_to_three_attempts(self) -> None:
        client = MaxRevisionFakeJSONClient()

        package = generate_content_package(
            "AI 자동화는 프롬프트보다 운영 구조가 중요하다.",
            build_config(),
            client=client,
        )

        self.assertEqual(package["revision_count"], 3)
        self.assertEqual(package["max_revision_loops"], 3)
        self.assertEqual(client.reflection_count, 4)

    def test_storage_writes_draft_and_final_package_files(self) -> None:
        client = FakeJSONClient()
        package = generate_content_package(
            "AI 자동화는 프롬프트보다 운영 구조가 중요하다.",
            build_config(),
            client=client,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            original_output_root = storage.OUTPUT_ROOT
            storage.OUTPUT_ROOT = Path(temp_dir)
            try:
                draft_path = storage.save_content_package(
                    package,
                    now=datetime(2026, 5, 12, 9, 0, 0),
                )
            finally:
                storage.OUTPUT_ROOT = original_output_root

            final_path = Path(temp_dir) / "final" / draft_path.name
            self.assertTrue((draft_path / "reflection.md").exists())
            self.assertTrue((draft_path / "publish-plan.json").exists())
            self.assertTrue((final_path / "blog.md").exists())

            metadata = json.loads((draft_path / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["output_type"], "draft")
            self.assertEqual(metadata["input_type"], "memo")
            self.assertEqual(metadata["agent_architecture"]["mode"], "multi_agent")
            self.assertEqual(metadata["channel_publish_status"]["telegram"], "auto_dispatch_pending")

    def test_telegram_dispatch_updates_newsletter_publish_status(self) -> None:
        client = FakeJSONClient()
        package = generate_content_package(
            "AI 자동화는 프롬프트보다 운영 구조가 중요하다.",
            build_config(),
            client=client,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            original_output_root = storage.OUTPUT_ROOT
            storage.OUTPUT_ROOT = Path(temp_dir)
            try:
                draft_path = storage.save_content_package(package)
                storage.record_telegram_dispatch(draft_path, "https://t.me/c/1001/33")
            finally:
                storage.OUTPUT_ROOT = original_output_root

            plan = json.loads((draft_path / "publish-plan.json").read_text(encoding="utf-8"))
            metadata = json.loads((draft_path / "metadata.json").read_text(encoding="utf-8"))

        self.assertEqual(plan["channels"]["telegram"]["status"], "published")
        self.assertEqual(plan["channels"]["telegram"]["provider"], "telegram_chat")
        self.assertEqual(plan["channels"]["telegram"]["url"], "https://t.me/c/1001/33")
        self.assertEqual(metadata["channel_publish_status"]["telegram"], "published")

    def test_publish_agent_executes_tistory_then_linkedin(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "tistory-state.json"
            state_path.write_text("{}", encoding="utf-8")
            package = {
                "drafts": {
                    "blog": "# 제목\n\n본문",
                    "linkedin": "블로그 전문 [블로그 링크]",
                    "telegram": "뉴스레터",
                },
                "reflection": {"score": 92, "passed": True},
                "revision_count": 0,
                "max_revision_loops": 3,
            }
            tistory = FakeTistoryPublisher(
                PublishResult(
                    channel="blog",
                    status="published",
                    provider="tistory_playwright",
                    url="https://chutzrit.tistory.com/123",
                    reason="Tistory 게시 완료",
                )
            )
            linkedin = FakeLinkedInPublisher()

            plan = PublishAgent(
                build_publish_config(str(state_path)),
                tistory_publisher_factory=lambda: tistory,
                linkedin_publisher_factory=lambda: linkedin,
            ).execute(package, Path(temp_dir))

            self.assertEqual(tistory.calls, 1)
            self.assertEqual(linkedin.calls, 1)
            self.assertIn("https://chutzrit.tistory.com/123", linkedin.last_text)
            self.assertNotIn("[블로그 링크]", package["drafts"]["linkedin"])
            self.assertEqual(plan["channels"]["blog"]["status"], "published")
            self.assertEqual(plan["channels"]["linkedin"]["status"], "published")
            self.assertEqual(plan["external_api_status"], "published")

    def test_publish_agent_blocks_linkedin_when_tistory_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "tistory-state.json"
            state_path.write_text("{}", encoding="utf-8")
            package = {
                "drafts": {
                    "blog": "# 제목\n\n본문",
                    "linkedin": "블로그 전문 [블로그 링크]",
                    "telegram": "뉴스레터",
                },
                "reflection": {"score": 92, "passed": True},
                "revision_count": 0,
                "max_revision_loops": 3,
            }
            tistory = FakeTistoryPublisher(
                PublishResult(
                    channel="blog",
                    status="failed",
                    provider="tistory_playwright",
                    reason="Tistory 실패",
                )
            )
            linkedin = FakeLinkedInPublisher()

            plan = PublishAgent(
                build_publish_config(str(state_path)),
                tistory_publisher_factory=lambda: tistory,
                linkedin_publisher_factory=lambda: linkedin,
            ).execute(package, Path(temp_dir))

            self.assertEqual(tistory.calls, 1)
            self.assertEqual(linkedin.calls, 0)
            self.assertEqual(plan["channels"]["linkedin"]["status"], "blocked_until_blog_url")

    def test_consolidated_publish_report_includes_all_channel_results(self) -> None:
        plan = {
            "channels": {
                "blog": {
                    "status": "failed",
                    "url": "",
                    "reason": "Tistory 본문 입력 실패",
                },
                "linkedin": {
                    "status": "blocked_until_blog_url",
                    "url": "",
                    "reason": "티스토리 실제 발행 URL이 없어 LinkedIn 공개 게시를 중단한다.",
                },
                "telegram": {
                    "status": "published",
                    "url": "https://t.me/c/1001/33",
                    "reason": "Telegram 뉴스레터 채팅방에 발송됐다.",
                },
            }
        }

        report = format_multi_platform_publish_report(
            plan,
            output_path=Path("/tmp/package"),
            title="테스트 콘텐츠",
        )

        self.assertIn("멀티플랫폼 배포 결과", report)
        self.assertIn("부분 배포 완료", report)
        self.assertIn("Telegram 뉴스레터", report)
        self.assertIn("https://t.me/c/1001/33", report)
        self.assertIn("블로그", report)
        self.assertIn("Tistory 본문 입력 실패", report)
        self.assertIn("LinkedIn", report)
        self.assertIn("티스토리 실제 발행 URL", report)

    def test_tistory_session_capture_refuses_real_browser_profile(self) -> None:
        real_brave_profile = known_real_browser_profile_dirs()[0] / "Default"

        with self.assertRaises(SystemExit):
            assert_isolated_browser_profile_dir(real_brave_profile)

        with tempfile.TemporaryDirectory() as temp_dir:
            isolated_profile = Path(temp_dir) / "outputs" / "broadcasting" / "session" / "brave-playwright-profile"
            assert_isolated_browser_profile_dir(isolated_profile)

    def test_tistory_markdown_is_rendered_as_editor_html(self) -> None:
        markdown = (
            "망설임은 감정이 아니라 안전장치다.\n\n"
            "## 망설임은 속도를 늦추는 게 아니라 사고를 줄인다\n\n"
            "- 검증 기준을 둔다.\n"
            "- 멈춤 지점을 정한다.\n\n"
            "자세한 글은 [후츠릿](https://chutzrit.tistory.com)에서 본다."
        )

        rendered = markdown_to_tistory_html(markdown)

        self.assertIn("<p>망설임은 감정이 아니라 안전장치다.</p>", rendered)
        self.assertIn("<h2>망설임은 속도를 늦추는 게 아니라 사고를 줄인다</h2>", rendered)
        self.assertIn("<ul>", rendered)
        self.assertIn("<li>검증 기준을 둔다.</li>", rendered)
        self.assertIn('<a href="https://chutzrit.tistory.com"', rendered)
        self.assertNotIn("## 망설임", rendered)


if __name__ == "__main__":
    unittest.main()

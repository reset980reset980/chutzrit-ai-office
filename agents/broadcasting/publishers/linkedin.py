"""LinkedIn Posts API publisher."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import unquote
from urllib.request import Request, urlopen

from .base import PublishResult


LINKEDIN_POSTS_URL = "https://api.linkedin.com/rest/posts"


class LinkedInPublisher:
    """Publish a text-only LinkedIn post through the Posts API."""

    provider = "linkedin_posts_api"

    def __init__(self, *, access_token: str, author_urn: str, version: str) -> None:
        self.access_token = access_token
        self.author_urn = author_urn
        self.version = version

    def publish(self, text: str) -> PublishResult:
        """Publish text to LinkedIn and return the created post URL when available."""
        if not self.access_token or not self.author_urn:
            return PublishResult(
                channel="linkedin",
                status="not_connected",
                provider=self.provider,
                reason="LINKEDIN_ACCESS_TOKEN 또는 LINKEDIN_AUTHOR_URN이 비어 있다.",
            )

        payload = {
            "author": self.author_urn,
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        request = Request(
            LINKEDIN_POSTS_URL,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
                "Linkedin-Version": self.version,
                "User-Agent": "ChutzritAIOffice/0.1 (broadcasting-pipeline)",
            },
        )

        try:
            with urlopen(request, timeout=60) as response:
                post_id = response.headers.get("x-restli-id", "")
                return PublishResult(
                    channel="linkedin",
                    status="published",
                    provider=self.provider,
                    url=build_linkedin_post_url(post_id),
                    reason="LinkedIn Posts API 공개 게시가 완료됐다.",
                    details={
                        "http_status": response.status,
                        "post_id": post_id,
                    },
                )
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            return PublishResult(
                channel="linkedin",
                status="failed",
                provider=self.provider,
                reason=f"LinkedIn API HTTP {exc.code}: {error_body[:500]}",
                details={"http_status": exc.code},
            )
        except URLError as exc:
            return PublishResult(
                channel="linkedin",
                status="failed",
                provider=self.provider,
                reason=f"LinkedIn API 네트워크 오류: {exc.reason}",
            )


def build_linkedin_post_url(post_id: str) -> str:
    """Build a human-facing LinkedIn feed URL from a REST.li post id."""
    decoded = unquote(post_id or "").strip()
    if not decoded:
        return ""
    return f"https://www.linkedin.com/feed/update/{decoded}/"


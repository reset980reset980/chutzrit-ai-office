"""Discord publishing result helpers."""

from __future__ import annotations

from .base import PublishResult


def build_discord_dispatch_result(message_url: str) -> PublishResult:
    """Build a normalized Discord dispatch result."""
    return PublishResult(
        channel="discord",
        status="published",
        provider="discord_channel",
        url=message_url,
        reason="Discord 뉴스레터가 뉴스레터 채널에 발송됐다.",
    )

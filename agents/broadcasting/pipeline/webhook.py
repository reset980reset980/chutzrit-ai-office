"""Discord webhook reporting for broadcasting outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .http import request_json


def send_broadcasting_report(
    webhook_url: str,
    *,
    package: dict[str, Any],
    output_path: Path,
) -> None:
    """Send a Discord report for a generated content package."""
    reflection = package.get("reflection", {})
    approval = package.get("approval", {})
    score = reflection.get("score", "unknown")
    channel_scores = reflection.get("channel_scores", {})
    problems = reflection.get("problems", [])
    quality_passed = approval.get("quality_passed", False)
    status = "초안 생성 완료" if quality_passed else "검토 필요"
    channel_score_text = ", ".join(
        f"{name} {value}" for name, value in channel_scores.items()
    ) or "없음"
    problem_text = "\n".join(f"- {problem}" for problem in problems[:3]) or "- 없음"
    content = (
        "## 콘텐츠배포팀 평가 결과\n"
        f"**상태** {status}\n"
        f"**제목** {package.get('title', '')}\n"
        f"**총점** {score}\n"
        f"**채널 점수** {channel_score_text}\n"
        f"**수정 루프** {package.get('revision_count', 0)}회\n\n"
        "**주요 피드백**\n"
        f"{problem_text}\n\n"
        "**산출물** 블로그, LinkedIn, Discord 뉴스레터\n"
        f"**파일** {output_path}\n"
        "**처리 방식** 생성 완료 후 Discord 채널에 자동 발송\n"
        "**외부 API 배포** 아직 미연결"
    )
    request_json(webhook_url, method="POST", payload={"content": content})

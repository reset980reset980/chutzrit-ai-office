"""Discord progress message formatting for the broadcasting pipeline."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any


def format_source_progress(source_payload: dict[str, Any]) -> str:
    """Format source parsing results for Discord."""
    raw_text = str(source_payload.get("raw_text", "")).strip()
    urls = source_payload.get("urls", [])
    link_summaries = source_payload.get("link_summaries", [])
    input_type = "링크 + 메모" if urls and raw_text else "링크" if urls else "메모"
    summary_status = f"{len(link_summaries)}개 수집" if urls else "해당 없음"
    return (
        "## 🧾 Input Parser 완료\n"
        f"입력 유형 {input_type}\n"
        f"감지한 링크 {len(urls)}개\n"
        f"링크 메타데이터 {summary_status}\n"
        f"입력 미리보기 {compact_text(raw_text, 180)}"
        f"{format_link_summary_progress(link_summaries)}"
    )


def format_link_summary_progress(link_summaries: Any) -> str:
    """Format fetched link summaries for the Input Parser Discord message."""
    if not isinstance(link_summaries, list) or not link_summaries:
        return ""

    lines = ["\n\n링크 핵심 내용"]
    for index, summary in enumerate(link_summaries[:3], start=1):
        parsed = parse_link_summary(str(summary))
        title = parsed.get("제목") or "제목 없음"
        core = parsed.get("핵심 내용") or parsed.get("설명") or "핵심 내용 추출 실패"
        url = parsed.get("url") or ""
        lines.append(f"{index}. {compact_text(title, 90)}")
        lines.append(f"   - {compact_text(core, 220)}")
        if url:
            lines.append(f"   - {url}")
    return "\n".join(lines)


def parse_link_summary(summary: str) -> dict[str, str]:
    """Parse link summary text into display fields."""
    result: dict[str, str] = {}
    lines = [line.strip() for line in summary.splitlines() if line.strip()]
    if lines:
        result["url"] = lines[0]
    for line in lines[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def format_strategy_progress(package: dict[str, Any]) -> str:
    """Format content strategy results for Discord."""
    strategy = package.get("strategy", {})
    directions = strategy.get("platform_directions", {})
    return (
        "## 🧭 Content Strategy Agent 완료\n"
        f"핵심 메시지 {compact_text(strategy.get('core_message', ''), 180)}\n"
        f"타깃 독자 {compact_text(strategy.get('target_reader', ''), 140)}\n"
        f"글의 주장 {compact_text(strategy.get('claim', ''), 180)}\n\n"
        "플랫폼 방향\n"
        f"- 블로그 {compact_text(directions.get('blog', ''), 120)}\n"
        f"- LinkedIn {compact_text(directions.get('linkedin', ''), 120)}\n"
        f"- Discord {compact_text(directions.get('discord', ''), 120)}"
    )


def format_insight_progress(package: dict[str, Any]) -> str:
    """Format insight results for Discord."""
    insight = package.get("insight", {})
    practical_points = insight.get("practical_points", [])
    examples = insight.get("examples", [])
    cautions = insight.get("cautions", [])
    return (
        "## 💡 Insight Agent 완료\n"
        f"관점 {compact_text(insight.get('chutzrit_insight', ''), 220)}\n\n"
        "적용 포인트\n"
        f"{format_short_bullets(practical_points, '없음')}\n\n"
        "예시와 주의점\n"
        f"- 예시 {compact_text(first_item(examples), 120)}\n"
        f"- 주의 {compact_text(first_item(cautions), 120)}"
    )


def format_writer_progress(package: dict[str, Any]) -> str:
    """Format platform writer results for Discord."""
    drafts = package.get("drafts", {})
    blog = str(drafts.get("blog", "")).strip()
    linkedin = str(drafts.get("linkedin", "")).strip()
    discord = str(drafts.get("discord", "")).strip()
    return (
        "## ✍️ Platform Writer Agents 완료\n"
        f"- 블로그 {len(blog)}자 / 첫 줄 {compact_text(first_line(blog), 90)}\n"
        f"- LinkedIn {len(linkedin)}자 / 첫 줄 {compact_text(first_line(linkedin), 90)}\n"
        f"- Discord 뉴스레터 {len(discord)}자 / 첫 줄 {compact_text(first_line(discord), 90)}"
    )


def format_reflection_progress(
    package: dict[str, Any],
    reflection: dict[str, Any],
    revision_count: int,
    max_revision_loops: int,
) -> str:
    """Format quality reflection for Discord progress updates."""
    score = reflection.get("score", "unknown")
    status = "통과" if reflection.get("passed") else "검토 필요"
    channel_scores = reflection.get("channel_scores", {})
    strengths = reflection.get("strengths", [])
    problems = reflection.get("problems", [])
    revision_instructions = reflection.get("revision_instructions", [])
    channel_score_text = ", ".join(
        f"{name} {value}" for name, value in channel_scores.items()
    ) or "없음"

    return (
        "## 🧪 콘텐츠배포팀 평가 결과\n"
        f"상태 {status}\n"
        f"제목 {package.get('title', '')}\n"
        f"총점 {score}\n"
        f"채널 점수 {channel_score_text}\n"
        f"수정 루프 {revision_count}/{max_revision_loops}회\n\n"
        "주요 피드백\n"
        f"{bullet_list(problems, '없음')}\n\n"
        "수정할 사항\n"
        f"{bullet_list(revision_instructions, '없음')}\n\n"
        "유지할 점\n"
        f"{bullet_list(strengths, '없음')}"
    )


def format_revision_start_progress(
    reflection: dict[str, Any],
    revision_count: int,
    max_revision_loops: int,
    channels: list[str],
) -> str:
    """Format revision start progress with concrete feedback."""
    problems = reflection.get("problems", [])
    revision_instructions = reflection.get("revision_instructions", [])
    channel_text = ", ".join(channels)
    return (
        f"## 🔁 Revision Agent {revision_count}/{max_revision_loops}회차 시작\n"
        f"현재 점수 {reflection.get('score', 'unknown')}\n"
        f"수정 대상 채널 {channel_text}\n\n"
        "이번 수정에서 반영할 피드백\n"
        f"{format_short_bullets(problems, '없음')}\n\n"
        "수정 지시\n"
        f"{format_short_bullets(revision_instructions, '없음')}"
    )


def format_revision_progress(
    package: dict[str, Any],
    revision_count: int,
    max_revision_loops: int,
    channels: list[str],
) -> str:
    """Format revision completion progress."""
    drafts = package.get("drafts", {})
    lines = [
        f"## 🛠️ Revision Agent {revision_count}/{max_revision_loops}회차 완료",
        f"제목 {package.get('title', '')}",
    ]
    for channel in channels:
        label = {"blog": "블로그", "linkedin": "LinkedIn", "discord": "Discord"}.get(channel, channel)
        lines.append(f"- {label} 첫 줄 {compact_text(first_line(str(drafts.get(channel, ''))), 100)}")
    return "\n".join(lines)


def format_final_gate_progress(
    reflection: dict[str, Any],
    revision_count: int,
    max_revision_loops: int,
) -> str:
    """Format final gate decision."""
    if reflection.get("passed"):
        return (
            "## ✅ Final Quality Gate 통과\n"
            f"최종 점수 {reflection.get('score', 'unknown')}\n"
            f"수정 루프 {revision_count}/{max_revision_loops}회\n"
            "Publish Agent가 발송과 외부 배포 상태를 정리합니다."
        )
    return (
        "## ⚠️ Final Quality Gate 기준 미달\n"
        f"최종 점수 {reflection.get('score', 'unknown')}\n"
        f"수정 루프 {revision_count}/{max_revision_loops}회\n"
        "최대 수정 루프를 모두 사용했습니다. 현재 결과를 저장하고 Discord에 발송합니다."
    )


def format_publish_progress(package: dict[str, Any]) -> str:
    """Format Publish Agent decision."""
    publish_plan = package.get("publish_plan", {})
    channels = publish_plan.get("channels", {})
    blog = channels.get("blog", {})
    linkedin = channels.get("linkedin", {})
    discord = channels.get("discord", {})
    return (
        "## 🚀 Publish Agent 배포 계획\n"
        f"블로그 {blog.get('status', 'unknown')} - {blog.get('reason', '')}\n"
        f"LinkedIn {linkedin.get('status', 'unknown')} - {linkedin.get('reason', '')}\n"
        f"Discord {discord.get('status', 'unknown')} - {discord.get('reason', '')}\n"
        f"외부 배포 상태 {publish_plan.get('external_api_status', 'unknown')}"
    )


def format_multi_platform_publish_report(
    publish_plan: dict[str, Any],
    *,
    output_path: Path | str,
    title: str = "",
) -> str:
    """Format one consolidated publish report after every channel attempt finishes."""
    channels = publish_plan.get("channels", {})
    ordered_channels = ("blog", "linkedin", "discord")
    published = [
        channel
        for channel in ordered_channels
        if str(channels.get(channel, {}).get("status") or "") in {"published", "draft_saved"}
    ]
    blocked = [
        channel
        for channel in ordered_channels
        if channel not in published
    ]

    if len(published) == len(ordered_channels):
        status_text = "전체 배포 완료"
        status_icon = "✅"
    elif published:
        status_text = "부분 배포 완료"
        status_icon = "⚠️"
    else:
        status_text = "배포 실패"
        status_icon = "❌"

    lines = [
        f"## {status_icon} 멀티플랫폼 배포 결과",
        f"**상태** {status_text}",
    ]
    if title:
        lines.append(f"**제목** {title}")
    lines.append(f"**시간** {datetime.now().isoformat(timespec='seconds')}")

    if published:
        lines.append("\n### ✅ 배포 완료")
        for channel in published:
            lines.append(format_publish_report_line(channel, channels.get(channel, {})))

    if blocked:
        lines.append("\n### ⚠️ 확인 필요")
        for channel in blocked:
            lines.append(format_publish_report_line(channel, channels.get(channel, {})))

    lines.append(f"\n📁 **파일** `{output_path}`")
    return "\n".join(lines)


def format_publish_report_line(channel_name: str, result: dict[str, Any]) -> str:
    """Format one channel line for the consolidated publish report."""
    labels = {
        "blog": "블로그",
        "linkedin": "LinkedIn",
        "discord": "Discord 뉴스레터",
    }
    status = str(result.get("status") or "unknown")
    url = str(result.get("url") or "").strip()
    reason = compact_text(str(result.get("reason") or ""), 180)
    status_label = channel_publish_status_label(status)
    icon = channel_publish_status_icon(status)
    link = f" - {url}" if url else ""
    reason_text = f" - {reason}" if reason else ""
    return f"- {icon} **{labels.get(channel_name, channel_name)}**: {status_label}{link}{reason_text}"


def channel_publish_status_icon(status: str) -> str:
    """Return an icon for one channel publish status."""
    if status in {"published", "draft_saved"}:
        return "✅"
    if status in {"blocked_until_blog_url", "external_publish_disabled", "not_connected", "approval_required"}:
        return "⚠️"
    if status in {"failed", "dependency_missing"}:
        return "❌"
    return "ℹ️"


def format_channel_publish_progress(
    channel_name: str,
    result: dict[str, Any],
    output_path: Path | str | None = None,
) -> str:
    """Format one channel publish result immediately after that channel finishes."""
    labels = {
        "blog": "블로그",
        "linkedin": "LinkedIn",
        "discord": "Discord",
    }
    status = str(result.get("status") or "unknown")
    status_label = channel_publish_status_label(status)
    url = str(result.get("url") or "")
    reason = str(result.get("reason") or "")
    lines = [
        "[팀] 콘텐츠배포팀",
        f"[상태] {status_label}",
        f"[채널] {labels.get(channel_name, channel_name)}",
        f"[URL] {url or '없음'}",
        f"[시간] {datetime.now().isoformat(timespec='seconds')}",
    ]
    if reason:
        lines.append(f"[메시지] {reason}")
    if output_path:
        lines.append(f"[파일] {output_path}")
    return "\n".join(lines)


def channel_publish_status_label(status: str) -> str:
    """Return a Korean status label for one channel publish result."""
    labels = {
        "published": "배포 완료",
        "draft_saved": "임시저장 완료",
        "external_publish_disabled": "배포 대기",
        "blocked_until_blog_url": "배포 중단",
        "not_connected": "배포 연결 필요",
        "dependency_missing": "배포 실패",
        "failed": "배포 실패",
        "disabled": "배포 비활성화",
        "ready": "배포 대기",
    }
    return labels.get(status, "배포 상태 확인 필요")


def compact_text(value: Any, limit: int = 120) -> str:
    """Compact text for Discord progress messages."""
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if not text:
        return "없음"
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def first_line(value: str) -> str:
    """Return the first non-empty line."""
    for line in value.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def first_item(value: Any) -> str:
    """Return the first list item as text."""
    if isinstance(value, list) and value:
        return str(value[0])
    return ""


def format_short_bullets(value: Any, fallback: str) -> str:
    """Format up to three bullet items."""
    if not isinstance(value, list) or not value:
        return f"- {fallback}"
    return "\n".join(f"- {compact_text(item, 120)}" for item in value[:3])


def bullet_list(items: Any, fallback: str) -> str:
    """Format up to three full bullet items."""
    if not isinstance(items, list) or not items:
        return f"- {fallback}"
    return "\n".join(f"- {str(item)}" for item in items[:3])

"""Output storage for broadcasting content packages."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT


OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "broadcasting"


def save_content_package(package: dict[str, Any], *, now: datetime | None = None) -> Path:
    """Save a content package under drafts and final output folders."""
    current = now or datetime.now()
    slug = slugify(package.get("title") or package.get("source_summary") or "content")
    package_id = f"{current:%Y-%m-%d}-{slug}"
    draft_target = OUTPUT_ROOT / "drafts" / package_id
    final_target = OUTPUT_ROOT / "final" / package_id
    package["output_paths"] = {
        "draft": str(draft_target),
        "final": str(final_target),
    }

    write_package_files(draft_target, package, package_id, current, output_type="draft")
    write_package_files(final_target, package, package_id, current, output_type="final")
    return draft_target


def refresh_publish_files(package: dict[str, Any], draft_path: Path) -> None:
    """Refresh saved draft/final files after PublishAgent mutates publish state."""
    for target in saved_package_targets(package, draft_path):
        drafts = package.get("drafts", {})
        write_text(target / "blog.md", drafts.get("blog", ""))
        write_text(target / "linkedin.md", drafts.get("linkedin", ""))
        write_text(target / "telegram.md", drafts.get("telegram", drafts.get("discord", "")))
        write_text(target / "discord.md", drafts.get("discord", drafts.get("telegram", "")))
        write_json(target / "publish-plan.json", package.get("publish_plan", {}))
        write_visual_package_files(target, package)
        refresh_metadata_publish_fields(target, package)


def refresh_visual_files(package: dict[str, Any], draft_path: Path) -> None:
    """Refresh saved visual metadata files after image generation."""
    for target in saved_package_targets(package, draft_path):
        write_visual_package_files(target, package)
        refresh_metadata_publish_fields(target, package)


def record_discord_dispatch(draft_path: Path, message_url: str) -> None:
    """Record the Discord newsletter dispatch URL in saved package files."""
    record_newsletter_dispatch(
        draft_path,
        message_url,
        channel="discord",
        provider="discord_channel",
        reason="Discord 뉴스레터가 뉴스레터 채널에 발송됐다.",
    )


def record_telegram_dispatch(draft_path: Path, message_url: str) -> None:
    """Record the Telegram newsletter dispatch URL in saved package files."""
    record_newsletter_dispatch(
        draft_path,
        message_url,
        channel="telegram",
        provider="telegram_chat",
        reason="Telegram 뉴스레터 채팅방에 발송됐다.",
    )


def record_newsletter_dispatch(
    draft_path: Path,
    message_url: str,
    *,
    channel: str,
    provider: str,
    reason: str,
) -> None:
    """Record the reader-facing newsletter dispatch result."""
    for target in saved_package_targets({}, draft_path):
        plan_path = target / "publish-plan.json"
        if not plan_path.exists():
            continue
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan.setdefault("channels", {})[channel] = {
            "status": "published",
            "provider": provider,
            "url": message_url,
            "reason": reason,
            "details": {},
        }
        write_json(plan_path, plan)
        refresh_metadata_publish_fields(target, {"publish_plan": plan})


def saved_package_targets(package: dict[str, Any], draft_path: Path) -> list[Path]:
    """Return draft and final output folders for an already-saved package."""
    targets = [draft_path]
    final_value = package.get("output_paths", {}).get("final") if package else ""
    final_path = Path(final_value) if final_value else draft_path.parents[1] / "final" / draft_path.name
    if final_path not in targets and final_path.exists():
        targets.append(final_path)
    return targets


def refresh_metadata_publish_fields(target: Path, package: dict[str, Any]) -> None:
    """Refresh publish-related metadata fields without changing generated_at."""
    metadata_path = target / "metadata.json"
    if not metadata_path.exists():
        return
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    publish_plan = package.get("publish_plan", {})
    publish_channels = publish_plan.get("channels", {})
    metadata["channel_publish_status"] = {
        channel: value.get("status", "")
        for channel, value in publish_channels.items()
        if isinstance(value, dict)
    }
    metadata["published_urls"] = {
        channel: value.get("url", "")
        for channel, value in publish_channels.items()
        if isinstance(value, dict)
    }
    metadata["external_api_status"] = publish_plan.get("external_api_status", "")
    metadata["processing_mode"] = publish_plan.get("processing_mode", "")
    visual_assets = package.get("visual_assets", {})
    if visual_assets:
        metadata["channel_processing_status"] = {
            **metadata.get("channel_processing_status", {}),
            "visuals": visual_assets.get("status", ""),
        }
        metadata["visual_assets_status"] = visual_assets.get("status", "")
        metadata["visual_assets"] = visual_assets.get("assets", {})
    if package.get("visual_quality"):
        metadata["visual_quality"] = package.get("visual_quality", {})
    if package.get("visual_observations"):
        metadata["visual_observations"] = package.get("visual_observations", {})
    write_json(metadata_path, metadata)


def write_package_files(
    target: Path,
    package: dict[str, Any],
    package_id: str,
    generated_at: datetime,
    *,
    output_type: str,
) -> None:
    """Write all package files into a target folder."""
    target.mkdir(parents=True, exist_ok=True)

    write_text(target / "source.md", render_source(package))
    write_text(target / "strategy.md", render_strategy(package))
    write_text(target / "insight.md", render_insight(package))

    drafts = package.get("drafts", {})
    write_text(target / "blog.md", drafts.get("blog", ""))
    write_text(target / "linkedin.md", drafts.get("linkedin", ""))
    write_text(target / "telegram.md", drafts.get("telegram", drafts.get("discord", "")))
    write_text(target / "discord.md", drafts.get("discord", drafts.get("telegram", "")))

    write_text(target / "reflection.md", render_reflection(package))
    write_json(target / "reflection.json", package.get("reflection", {}))
    write_visual_package_files(target, package)
    write_json(target / "metadata.json", build_metadata(package, package_id, generated_at, output_type))
    write_json(target / "approval-status.json", package.get("approval", {}))
    write_json(target / "publish-plan.json", package.get("publish_plan", {}))


def write_visual_package_files(target: Path, package: dict[str, Any]) -> None:
    """Write visual strategy, prompt, quality, and asset metadata files."""
    write_json(target / "visual-strategy.json", package.get("visual_strategy", {}))
    write_json(target / "image-prompts.json", package.get("image_prompts", {}))
    write_json(target / "visual-assets.json", package.get("visual_assets", {}))
    write_json(target / "visual-observations.json", package.get("visual_observations", {}))
    write_json(target / "visual-quality.json", package.get("visual_quality", {}))


def render_source(package: dict[str, Any]) -> str:
    """Render source metadata as Markdown."""
    source = package.get("source", {})
    urls = "\n".join(f"- {url}" for url in source.get("urls", [])) or "- 없음"
    summaries = "\n\n".join(source.get("link_summaries", [])) or "없음"
    return f"# Source\n\n## Raw Input\n\n{source.get('raw_text', '')}\n\n## URLs\n\n{urls}\n\n## Link Summaries\n\n{summaries}\n"


def render_strategy(package: dict[str, Any]) -> str:
    """Render strategy as Markdown."""
    strategy = package.get("strategy", {})
    directions = strategy.get("platform_directions", {})
    return (
        "# Strategy\n\n"
        f"- 핵심 메시지: {strategy.get('core_message', '')}\n"
        f"- 타깃 독자: {strategy.get('target_reader', '')}\n"
        f"- 주장: {strategy.get('claim', '')}\n\n"
        "## Platform Directions\n\n"
        f"- Blog: {directions.get('blog', '')}\n"
        f"- LinkedIn: {directions.get('linkedin', '')}\n"
        f"- Telegram: {directions.get('telegram', directions.get('discord', ''))}\n"
    )


def render_insight(package: dict[str, Any]) -> str:
    """Render insight as Markdown."""
    insight = package.get("insight", {})
    practical = "\n".join(f"- {item}" for item in insight.get("practical_points", []))
    examples = "\n".join(f"- {item}" for item in insight.get("examples", []))
    cautions = "\n".join(f"- {item}" for item in insight.get("cautions", []))
    return (
        "# Insight\n\n"
        f"{insight.get('chutzrit_insight', '')}\n\n"
        "## Practical Points\n\n"
        f"{practical}\n\n"
        "## Examples\n\n"
        f"{examples}\n\n"
        "## Cautions\n\n"
        f"{cautions}\n"
    )


def render_reflection(package: dict[str, Any]) -> str:
    """Render reflection as Markdown."""
    reflection = package.get("reflection", {})
    channel_scores = reflection.get("channel_scores", {})
    strengths = "\n".join(f"- {item}" for item in reflection.get("strengths", [])) or "- 없음"
    problems = "\n".join(f"- {item}" for item in reflection.get("problems", [])) or "- 없음"
    instructions = "\n".join(f"- {item}" for item in reflection.get("revision_instructions", [])) or "- 없음"
    scores = "\n".join(f"- {channel}: {score}" for channel, score in channel_scores.items()) or "- 없음"
    return (
        "# Reflection\n\n"
        f"- 총점: {reflection.get('score', '')}\n"
        f"- 통과 여부: {reflection.get('passed', False)}\n"
        f"- 배포 상태: {reflection.get('publish_status', '')}\n\n"
        "## Channel Scores\n\n"
        f"{scores}\n\n"
        "## Strengths\n\n"
        f"{strengths}\n\n"
        "## Problems\n\n"
        f"{problems}\n\n"
        "## Revision Instructions\n\n"
        f"{instructions}\n"
    )


def build_metadata(
    package: dict[str, Any],
    package_id: str,
    generated_at: datetime,
    output_type: str,
) -> dict[str, Any]:
    """Build metadata for a saved package."""
    source = package.get("source", {})
    reflection = package.get("reflection", {})
    publish_plan = package.get("publish_plan", {})
    publish_channels = publish_plan.get("channels", {})
    visual_assets = package.get("visual_assets", {})
    return {
        "package_id": package_id,
        "output_type": output_type,
        "generated_at": generated_at.isoformat(),
        "title": package.get("title", ""),
        "source_summary": package.get("source_summary", ""),
        "input_type": detect_input_type(source),
        "target_persona": package.get("strategy", {}).get("target_reader", ""),
        "revision_count": package.get("revision_count", 0),
        "target_channels": ["blog", "linkedin", "telegram"],
        "agent_architecture": package.get("agent_architecture", {}),
        "quality_score": reflection.get("score", 0),
        "quality_passed": reflection.get("passed", False),
        "channel_scores": reflection.get("channel_scores", {}),
        "channel_processing_status": {
            "blog": "generated",
            "linkedin": "generated",
            "telegram": "generated",
            "visuals": visual_assets.get("status", ""),
        },
        "visual_assets_status": visual_assets.get("status", ""),
        "visual_assets": visual_assets.get("assets", {}),
        "visual_observations": package.get("visual_observations", {}),
        "visual_quality": package.get("visual_quality", {}),
        "channel_publish_status": {
            channel: value.get("status", "")
            for channel, value in publish_channels.items()
            if isinstance(value, dict)
        },
        "published_urls": {
            channel: value.get("url", "")
            for channel, value in publish_channels.items()
            if isinstance(value, dict)
        },
        "external_api_status": publish_plan.get("external_api_status", ""),
        "processing_mode": publish_plan.get("processing_mode", ""),
        "output_paths": package.get("output_paths", {}),
    }


def detect_input_type(source: dict[str, Any]) -> str:
    """Detect whether the source was a memo, link, or link with memo."""
    explicit_type = source.get("input_type")
    if explicit_type in {"memo", "link", "link_with_memo"}:
        return str(explicit_type)

    urls = source.get("urls", [])
    raw_text = str(source.get("raw_text", ""))
    note_text = raw_text
    for url in urls:
        note_text = note_text.replace(str(url), "")
    has_note = bool(note_text.strip())
    if urls and has_note:
        return "link_with_memo"
    if urls:
        return "link"
    return "memo"


def write_text(path: Path, value: str) -> None:
    """Write UTF-8 text."""
    path.write_text(value.strip() + "\n", encoding="utf-8")


def write_json(path: Path, value: dict[str, Any]) -> None:
    """Write formatted JSON."""
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    """Create a stable short slug for an output directory."""
    normalized = re.sub(r"[^0-9A-Za-z가-힣]+", "-", value).strip("-").lower()
    normalized = normalized[:48].strip("-") or "content"
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    return f"{normalized}-{digest}"

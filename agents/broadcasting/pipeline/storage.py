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
    """Save a content package under outputs/broadcasting/drafts."""
    current = now or datetime.now()
    slug = slugify(package.get("title") or package.get("source_summary") or "content")
    package_id = f"{current:%Y-%m-%d}-{slug}"
    target = OUTPUT_ROOT / "drafts" / package_id
    target.mkdir(parents=True, exist_ok=True)

    write_text(target / "source.md", render_source(package))
    write_text(target / "strategy.md", render_strategy(package))
    write_text(target / "insight.md", render_insight(package))

    drafts = package.get("drafts", {})
    write_text(target / "blog.md", drafts.get("blog", ""))
    write_text(target / "linkedin.md", drafts.get("linkedin", ""))
    write_text(target / "discord.md", drafts.get("discord", ""))

    write_json(target / "reflection.json", package.get("reflection", {}))
    write_json(target / "metadata.json", build_metadata(package, package_id))
    write_json(target / "approval-status.json", package.get("approval", {}))
    return target


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
        f"- Discord: {directions.get('discord', '')}\n"
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


def build_metadata(package: dict[str, Any], package_id: str) -> dict[str, Any]:
    """Build metadata for a saved package."""
    return {
        "package_id": package_id,
        "title": package.get("title", ""),
        "source_summary": package.get("source_summary", ""),
        "revision_count": package.get("revision_count", 0),
        "target_channels": ["blog", "linkedin", "discord"],
    }


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

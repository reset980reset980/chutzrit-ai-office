"""Backward-compatible entrypoint for broadcasting content generation."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from agents.broadcasting.agents.types import JSONClient

from .config import RuntimeConfig
from .orchestrator import generate_content_package as generate_multi_agent_content_package


ProgressCallback = Callable[[str], None]


def generate_content_package(
    source_text: str,
    config: RuntimeConfig,
    *,
    max_revision_loops: int = 3,
    progress_callback: ProgressCallback | None = None,
    client: JSONClient | None = None,
) -> dict[str, Any]:
    """Generate a package through the broadcasting team's multi-agent pipeline."""
    return generate_multi_agent_content_package(
        source_text,
        config,
        max_revision_loops=max_revision_loops,
        progress_callback=progress_callback,
        client=client,
    )

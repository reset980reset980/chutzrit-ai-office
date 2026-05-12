"""Input Parser Agent for broadcasting requests."""

from __future__ import annotations

from typing import Any

from agents.broadcasting.pipeline.source import parse_source_context


class InputParserAgent:
    """Parse a raw Discord message into source context."""

    name = "InputParserAgent"

    def run(self, source_text: str) -> dict[str, Any]:
        """Parse raw source text and fetch lightweight link metadata."""
        source = parse_source_context(source_text)
        return {
            "raw_text": source.raw_text,
            "urls": source.urls,
            "link_summaries": source.link_summaries,
        }

"""Input Parser Agent for broadcasting requests."""

from __future__ import annotations

from typing import Any

from agents.broadcasting.pipeline.source import parse_source_context


class InputParserAgent:
    """Parse a raw Discord message into source context."""

    name = "InputParserAgent"

    def __init__(self, *, fetch_links: bool = True) -> None:
        """Create the parser."""
        self.fetch_links = fetch_links

    def run(self, source_text: str) -> dict[str, Any]:
        """Parse raw source text and fetch lightweight link metadata."""
        source = parse_source_context(source_text, fetch_links=self.fetch_links)
        return {
            "raw_text": source.raw_text,
            "urls": source.urls,
            "link_summaries": source.link_summaries,
            "input_type": source.input_type,
        }

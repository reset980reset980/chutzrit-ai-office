"""Base helpers for platform writer agents."""

from __future__ import annotations

from agents.broadcasting.agents.types import JSONClient, JSONDict
from agents.broadcasting.pipeline.prompts import build_writer_prompt


class PlatformWriterAgent:
    """Generate one platform-specific draft."""

    channel = ""
    name = "PlatformWriterAgent"

    def __init__(self, client: JSONClient) -> None:
        self.client = client

    def run(self, source: JSONDict, strategy: JSONDict, insight: JSONDict) -> str:
        """Generate a single channel draft."""
        result = self.client.create_json(
            build_writer_prompt(self.channel, source, strategy, insight),
            max_output_tokens=12000,
        )
        draft = result.get("draft") or result.get(self.channel) or result.get("content") or ""
        return str(draft).strip()

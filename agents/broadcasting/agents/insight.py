"""Insight Agent."""

from __future__ import annotations

from .types import JSONClient, JSONDict
from agents.broadcasting.pipeline.prompts import build_insight_prompt


class InsightAgent:
    """Turn the strategy into a sharper Chutzrit-style point of view."""

    name = "InsightAgent"

    def __init__(self, client: JSONClient) -> None:
        self.client = client

    def run(self, source: JSONDict, strategy: JSONDict) -> JSONDict:
        """Generate practical insight for platform writers."""
        result = self.client.create_json(
            build_insight_prompt(source, strategy),
            max_output_tokens=5000,
        )
        return result.get("insight") if isinstance(result.get("insight"), dict) else result

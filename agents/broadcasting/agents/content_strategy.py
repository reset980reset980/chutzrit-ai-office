"""Content Strategy Agent."""

from __future__ import annotations

from .types import JSONClient, JSONDict
from agents.broadcasting.pipeline.prompts import build_strategy_prompt


class ContentStrategyAgent:
    """Choose the message, target reader, claim, and channel directions."""

    name = "ContentStrategyAgent"

    def __init__(self, client: JSONClient) -> None:
        self.client = client

    def run(self, source: JSONDict) -> JSONDict:
        """Generate the strategy document for this source."""
        result = self.client.create_json(build_strategy_prompt(source), max_output_tokens=5000)
        strategy = result.get("strategy")
        if isinstance(strategy, dict):
            return result
        return {
            "title": result.get("title", ""),
            "source_summary": result.get("source_summary", ""),
            "strategy": result,
        }

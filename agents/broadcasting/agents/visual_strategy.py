"""Visual Strategy Agent."""

from __future__ import annotations

from .types import JSONClient, JSONDict
from agents.broadcasting.pipeline.prompts import build_visual_strategy_prompt


class VisualStrategyAgent:
    """Choose image concepts that fit the final content package."""

    name = "VisualStrategyAgent"

    def __init__(self, client: JSONClient) -> None:
        self.client = client

    def run(self, package: JSONDict) -> JSONDict:
        """Generate a visual strategy for this content package."""
        result = self.client.create_json(build_visual_strategy_prompt(package), max_output_tokens=4000)
        return result.get("visual_strategy") if isinstance(result.get("visual_strategy"), dict) else result

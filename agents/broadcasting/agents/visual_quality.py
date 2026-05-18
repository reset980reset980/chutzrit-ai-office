"""Visual Quality Agent."""

from __future__ import annotations

from .types import JSONClient, JSONDict
from agents.broadcasting.pipeline.prompts import build_visual_quality_prompt


class VisualQualityAgent:
    """Evaluate whether generated images fit the final content package."""

    name = "VisualQualityAgent"

    def __init__(self, client: JSONClient) -> None:
        self.client = client

    def run(
        self,
        package: JSONDict,
        visual_strategy: JSONDict,
        image_prompts: JSONDict,
        visual_assets: JSONDict,
    ) -> JSONDict:
        """Evaluate generated visual asset metadata."""
        result = self.client.create_json(
            build_visual_quality_prompt(package, visual_strategy, image_prompts, visual_assets),
            max_output_tokens=3000,
        )
        score = int(result.get("score", 0))
        result["score"] = score
        result["passed"] = bool(result.get("passed", score >= 85))
        return result

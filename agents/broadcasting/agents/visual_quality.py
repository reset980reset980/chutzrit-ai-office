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
        visual_observations: JSONDict | None = None,
    ) -> JSONDict:
        """Evaluate generated visual asset metadata."""
        result = self.client.create_json(
            build_visual_quality_prompt(
                package,
                visual_strategy,
                image_prompts,
                visual_assets,
                visual_observations or {},
            ),
            max_output_tokens=3000,
        )
        score = int(result.get("score", 0))
        result["score"] = score
        requires_regeneration = has_regeneration_request(visual_observations or {})
        if requires_regeneration:
            result["passed"] = False
            result["score"] = min(score, 84)
        else:
            result["passed"] = bool(result.get("passed", score >= 85))
        return result


def has_regeneration_request(visual_observations: JSONDict) -> bool:
    """Return whether actual image inspection found a channel that must be regenerated."""
    channels = visual_observations.get("channels", {})
    if not isinstance(channels, dict):
        return False
    return any(
        isinstance(channel, dict) and bool(channel.get("requires_regeneration"))
        for channel in channels.values()
    )

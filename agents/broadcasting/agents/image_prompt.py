"""Image Prompt Agent."""

from __future__ import annotations

from .types import JSONClient, JSONDict
from agents.broadcasting.pipeline.prompts import build_image_prompt_prompt


class ImagePromptAgent:
    """Turn a visual strategy into channel-specific image prompts."""

    name = "ImagePromptAgent"

    def __init__(self, client: JSONClient) -> None:
        self.client = client

    def run(self, package: JSONDict, visual_strategy: JSONDict) -> JSONDict:
        """Generate image prompts for all visual channels."""
        result = self.client.create_json(
            build_image_prompt_prompt(package, visual_strategy),
            max_output_tokens=5000,
        )
        return result

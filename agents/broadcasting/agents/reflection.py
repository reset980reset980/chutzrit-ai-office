"""Self Reflection Agent."""

from __future__ import annotations

from .types import JSONClient, JSONDict
from agents.broadcasting.pipeline.prompts import build_reflection_prompt
from agents.broadcasting.pipeline.quality import enforce_style_gates, normalize_reflection


class SelfReflectionAgent:
    """Evaluate the generated package against Chutzrit quality gates."""

    name = "SelfReflectionAgent"

    def __init__(self, client: JSONClient) -> None:
        self.client = client

    def run(self, package: JSONDict) -> JSONDict:
        """Evaluate a content package."""
        reflection = normalize_reflection(
            self.client.create_json(build_reflection_prompt(package), max_output_tokens=4000)
        )
        return enforce_style_gates(package, reflection)

"""OpenAI SDK client for the broadcasting pipeline."""

from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI, OpenAIError


class OpenAIResponseError(RuntimeError):
    """Raised when an OpenAI response cannot be used."""


class OpenAIClient:
    """Small wrapper around the official OpenAI SDK."""

    def __init__(self, *, api_key: str, model: str) -> None:
        """Create the client."""
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def create_text(
        self,
        prompt: str,
        *,
        max_output_tokens: int = 12000,
        json_mode: bool = False,
    ) -> str:
        """Call the Responses API and return output text."""
        options: dict[str, Any] = {}
        if json_mode:
            options["text"] = {"format": {"type": "json_object"}}
        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                max_output_tokens=max_output_tokens,
                **options,
            )
        except OpenAIError as exc:
            raise OpenAIResponseError(f"OpenAI request failed: {exc}") from exc

        text = response.output_text
        if not text:
            raise OpenAIResponseError("OpenAI response did not contain output text")
        return text

    def create_json(self, prompt: str, *, max_output_tokens: int = 12000) -> dict[str, Any]:
        """Call the Responses API and parse a JSON object from the output."""
        text = self.create_text(prompt, max_output_tokens=max_output_tokens, json_mode=True)
        return parse_json_object(text)


def parse_json_object(text: str) -> dict[str, Any]:
    """Parse a JSON object even if the model wrapped it in a code fence."""
    stripped = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", stripped, re.DOTALL)
    if fenced:
        stripped = fenced.group(1).strip()

    if not stripped.startswith("{"):
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start >= 0 and end > start:
            stripped = stripped[start : end + 1]
    stripped = re.sub(r",(\s*[}\]])", r"\1", stripped)

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise OpenAIResponseError(f"Failed to parse JSON output: {exc}") from exc

    if not isinstance(parsed, dict):
        raise OpenAIResponseError("OpenAI output JSON was not an object")

    return parsed

"""OpenAI SDK client for the broadcasting pipeline."""

from __future__ import annotations

import json
import base64
import re
from pathlib import Path
from typing import Any

from openai import OpenAI, OpenAIError


class OpenAIResponseError(RuntimeError):
    """Raised when an OpenAI response cannot be used."""


class OpenAIClient:
    """Small wrapper around the official OpenAI SDK."""

    def __init__(self, *, api_key: str, model: str) -> None:
        """Create the client."""
        self.client = OpenAI(api_key=api_key, timeout=90.0)
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
        print(
            "OpenAI request start "
            f"model={self.model} "
            f"json_mode={json_mode} "
            f"prompt_chars={len(prompt)} "
            f"max_output_tokens={max_output_tokens}",
            flush=True,
        )
        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                max_output_tokens=max_output_tokens,
                **options,
            )
        except OpenAIError as exc:
            print(f"OpenAI request failed: {type(exc).__name__}", flush=True)
            raise OpenAIResponseError(f"OpenAI request failed: {exc}") from exc

        text = response.output_text
        if not text:
            raise OpenAIResponseError("OpenAI response did not contain output text")
        print(f"OpenAI request complete output_chars={len(text)}", flush=True)
        return text

    def create_json(self, prompt: str, *, max_output_tokens: int = 12000) -> dict[str, Any]:
        """Call the Responses API and parse a JSON object from the output."""
        text = self.create_text(prompt, max_output_tokens=max_output_tokens, json_mode=True)
        return parse_json_object(text)

    def create_json_with_images(
        self,
        prompt: str,
        image_paths: list[tuple[str, Path]],
        *,
        max_output_tokens: int = 12000,
    ) -> dict[str, Any]:
        """Call the Responses API with local images and parse a JSON object."""
        content: list[dict[str, str]] = [{"type": "input_text", "text": prompt}]
        for label, image_path in image_paths:
            content.append({"type": "input_text", "text": f"[Image: {label}]"})
            content.append(
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{base64.b64encode(image_path.read_bytes()).decode('ascii')}",
                }
            )

        print(
            "OpenAI vision request start "
            f"model={self.model} "
            f"images={len(image_paths)} "
            f"prompt_chars={len(prompt)} "
            f"max_output_tokens={max_output_tokens}",
            flush=True,
        )
        try:
            response = self.client.responses.create(
                model=self.model,
                input=[{"role": "user", "content": content}],
                max_output_tokens=max_output_tokens,
                text={"format": {"type": "json_object"}},
            )
        except OpenAIError as exc:
            print(f"OpenAI vision request failed: {type(exc).__name__}", flush=True)
            raise OpenAIResponseError(f"OpenAI vision request failed: {exc}") from exc

        text = response.output_text
        if not text:
            raise OpenAIResponseError("OpenAI vision response did not contain output text")
        print(f"OpenAI vision request complete output_chars={len(text)}", flush=True)
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

"""Shared typing helpers for broadcasting subagents."""

from __future__ import annotations

from typing import Any, Protocol


JSONDict = dict[str, Any]


class JSONClient(Protocol):
    """Minimal client interface needed by LLM-backed subagents."""

    def create_json(self, prompt: str, *, max_output_tokens: int = 12000) -> JSONDict:
        """Return a JSON object for the given prompt."""

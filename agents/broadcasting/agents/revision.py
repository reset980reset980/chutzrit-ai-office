"""Revision Agent."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from .types import JSONClient, JSONDict
from agents.broadcasting.pipeline.prompts import build_channel_revision_prompt


class RevisionAgent:
    """Revise only the channels that failed the quality gate."""

    name = "RevisionAgent"

    def __init__(self, client: JSONClient) -> None:
        self.client = client

    def run(self, package: JSONDict, reflection: JSONDict, channels: list[str]) -> dict[str, str]:
        """Revise selected channel drafts in parallel."""
        revisions: dict[str, str] = {}
        with ThreadPoolExecutor(max_workers=max(1, len(channels))) as executor:
            futures = {
                executor.submit(self._revise_channel, package, reflection, channel): channel
                for channel in channels
            }
            for future in as_completed(futures):
                channel = futures[future]
                revisions[channel] = future.result()
        return revisions

    def _revise_channel(self, package: JSONDict, reflection: JSONDict, channel: str) -> str:
        result = self.client.create_json(
            build_channel_revision_prompt(package, reflection, channel),
            max_output_tokens=12000,
        )
        draft = result.get("draft") or result.get(channel) or result.get("content") or ""
        return str(draft).strip()

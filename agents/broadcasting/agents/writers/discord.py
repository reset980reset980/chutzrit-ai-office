"""Discord Newsletter Writer Agent."""

from __future__ import annotations

from .base import PlatformWriterAgent


class DiscordNewsletterWriterAgent(PlatformWriterAgent):
    """Write the Discord newsletter draft."""

    channel = "discord"
    name = "DiscordNewsletterWriterAgent"

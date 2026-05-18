"""Telegram newsletter writer agent.

The module path is kept for compatibility with older imports.
"""

from __future__ import annotations

from .base import PlatformWriterAgent


class TelegramNewsletterWriterAgent(PlatformWriterAgent):
    """Write the Telegram newsletter draft."""

    channel = "telegram"
    name = "TelegramNewsletterWriterAgent"

"""LinkedIn Writer Agent."""

from __future__ import annotations

from .base import PlatformWriterAgent


class LinkedInWriterAgent(PlatformWriterAgent):
    """Write the LinkedIn draft."""

    channel = "linkedin"
    name = "LinkedInWriterAgent"

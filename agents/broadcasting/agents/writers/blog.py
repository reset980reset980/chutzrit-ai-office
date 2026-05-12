"""Blog Writer Agent."""

from __future__ import annotations

from .base import PlatformWriterAgent


class BlogWriterAgent(PlatformWriterAgent):
    """Write the long-form blog draft."""

    channel = "blog"
    name = "BlogWriterAgent"

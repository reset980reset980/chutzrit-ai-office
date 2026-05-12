"""Content generation pipeline for the broadcasting team."""

from __future__ import annotations

from typing import Any


def generate_content_package(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Generate a content package through the default pipeline."""
    from .generator import generate_content_package as run

    return run(*args, **kwargs)


def save_content_package(*args: Any, **kwargs: Any):
    """Save a content package."""
    from .storage import save_content_package as run

    return run(*args, **kwargs)


__all__ = ["generate_content_package", "save_content_package"]

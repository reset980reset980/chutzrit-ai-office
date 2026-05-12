"""Shared publisher result types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PublishResult:
    """Normalized result returned by a platform publisher."""

    channel: str
    status: str
    provider: str
    url: str = ""
    reason: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable result."""
        return {
            "status": self.status,
            "provider": self.provider,
            "url": self.url,
            "reason": self.reason,
            "details": self.details,
        }


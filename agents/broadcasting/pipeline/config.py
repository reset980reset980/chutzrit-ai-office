"""Configuration helpers for the broadcasting pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ENV_PATH = PROJECT_ROOT / ".env"


@dataclass(frozen=True)
class RuntimeConfig:
    """Runtime configuration loaded from environment variables."""

    discord_webhook_url: str
    discord_bot_token: str
    discord_guild_id: str
    discord_broadcasting_channel_id: str
    discord_allowed_user_ids: set[str]
    openai_api_key: str
    openai_model: str = "gpt-5.4-mini"
    public_content_require_approval: bool = False
    discord_channel_auto_publish: bool = True


def load_dotenv(path: Path = DEFAULT_ENV_PATH) -> dict[str, str]:
    """Load simple KEY=VALUE lines from a local .env file."""
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        values[key] = value
        os.environ.setdefault(key, value)

    return values


def load_runtime_config(env_path: Path = DEFAULT_ENV_PATH) -> RuntimeConfig:
    """Load and validate runtime configuration."""
    values = load_dotenv(env_path)

    def read(key: str, default: str = "") -> str:
        return os.environ.get(key) or values.get(key) or default

    required_keys = (
        "DISCORD_WEBHOOK_URL",
        "DISCORD_BOT_TOKEN",
        "DISCORD_GUILD_ID",
        "DISCORD_BROADCASTING_CHANNEL_ID",
        "DISCORD_ALLOWED_USER_IDS",
        "OPENAI_API_KEY",
    )
    missing = [key for key in required_keys if not read(key)]
    if missing:
        raise ValueError("Missing required env keys: " + ", ".join(missing))

    return RuntimeConfig(
        discord_webhook_url=read("DISCORD_WEBHOOK_URL"),
        discord_bot_token=read("DISCORD_BOT_TOKEN"),
        discord_guild_id=read("DISCORD_GUILD_ID"),
        discord_broadcasting_channel_id=read("DISCORD_BROADCASTING_CHANNEL_ID"),
        discord_allowed_user_ids={
            user_id.strip()
            for user_id in read("DISCORD_ALLOWED_USER_IDS").split(",")
            if user_id.strip()
        },
        openai_api_key=read("OPENAI_API_KEY"),
        openai_model=read("OPENAI_MODEL", "gpt-5.4-mini"),
        public_content_require_approval=read("PUBLIC_CONTENT_REQUIRE_APPROVAL", "false").lower() == "true",
        discord_channel_auto_publish=read("DISCORD_CHANNEL_AUTO_PUBLISH", "true").lower() == "true",
    )

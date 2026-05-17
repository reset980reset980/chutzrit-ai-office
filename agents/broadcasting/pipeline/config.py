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

    discord_webhook_url: str = ""
    discord_bot_token: str = ""
    discord_guild_id: str = ""
    discord_broadcasting_channel_id: str = ""
    discord_newsletter_channel_id: str = ""
    discord_allowed_user_ids: set[str] | None = None
    telegram_bot_token: str = ""
    telegram_broadcasting_chat_id: str = ""
    telegram_newsletter_chat_id: str = ""
    telegram_allowed_user_ids: set[str] | None = None
    openai_api_key: str = ""
    openai_model: str = "gpt-5.4-mini"
    public_content_require_approval: bool = False
    discord_channel_auto_publish: bool = True
    blog_publisher: str = "tistory"
    tistory_manage_url: str = ""
    tistory_blog_url: str = ""
    tistory_write_url: str = ""
    tistory_publish_mode: str = "public"
    tistory_auto_publish: bool = False
    playwright_storage_state: str = ""
    playwright_headless: bool = True
    linkedin_access_token: str = ""
    linkedin_author_urn: str = ""
    linkedin_version: str = "202602"
    linkedin_auto_publish: bool = False


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


def load_runtime_config(
    env_path: Path = DEFAULT_ENV_PATH,
    *,
    require_discord: bool = True,
    require_telegram: bool = False,
    require_openai: bool = True,
) -> RuntimeConfig:
    """Load and validate runtime configuration."""
    values = load_dotenv(env_path)

    def read(key: str, default: str = "") -> str:
        return os.environ.get(key) or values.get(key) or default

    required_keys = ["OPENAI_API_KEY"] if require_openai else []
    if require_discord:
        required_keys.extend(
            [
                "DISCORD_BOT_TOKEN",
                "DISCORD_GUILD_ID",
                "DISCORD_BROADCASTING_CHANNEL_ID",
            ]
        )
    if require_telegram:
        required_keys.extend(
            [
                "TELEGRAM_BOT_TOKEN",
            ]
        )
    missing = [key for key in required_keys if not read(key)]
    if missing:
        raise ValueError("Missing required env keys: " + ", ".join(missing))

    discord_broadcasting_channel_id = read("DISCORD_BROADCASTING_CHANNEL_ID")
    telegram_broadcasting_chat_id = read("TELEGRAM_BROADCASTING_CHAT_ID")

    return RuntimeConfig(
        discord_webhook_url=read("DISCORD_WEBHOOK_URL"),
        discord_bot_token=read("DISCORD_BOT_TOKEN"),
        discord_guild_id=read("DISCORD_GUILD_ID"),
        discord_broadcasting_channel_id=discord_broadcasting_channel_id,
        discord_newsletter_channel_id=read(
            "DISCORD_NEWSLETTER_CHANNEL_ID",
            discord_broadcasting_channel_id,
        ),
        discord_allowed_user_ids={
            user_id.strip()
            for user_id in read("DISCORD_ALLOWED_USER_IDS").split(",")
            if user_id.strip()
        },
        telegram_bot_token=read("TELEGRAM_BOT_TOKEN"),
        telegram_broadcasting_chat_id=telegram_broadcasting_chat_id,
        telegram_newsletter_chat_id=read(
            "TELEGRAM_NEWSLETTER_CHAT_ID",
            telegram_broadcasting_chat_id,
        ),
        telegram_allowed_user_ids={
            user_id.strip()
            for user_id in read("TELEGRAM_ALLOWED_USER_IDS").split(",")
            if user_id.strip()
        },
        openai_api_key=read("OPENAI_API_KEY"),
        openai_model=read("OPENAI_MODEL", "gpt-5.4-mini"),
        public_content_require_approval=read("PUBLIC_CONTENT_REQUIRE_APPROVAL", "false").lower() == "true",
        discord_channel_auto_publish=read("DISCORD_CHANNEL_AUTO_PUBLISH", "true").lower() == "true",
        blog_publisher=read("BLOG_PUBLISHER", "tistory"),
        tistory_manage_url=read("TISTORY_MANAGE_URL"),
        tistory_blog_url=read("TISTORY_BLOG_URL"),
        tistory_write_url=read("TISTORY_WRITE_URL"),
        tistory_publish_mode=read("TISTORY_PUBLISH_MODE", "public"),
        tistory_auto_publish=read("TISTORY_AUTO_PUBLISH", "false").lower() == "true",
        playwright_storage_state=read("PLAYWRIGHT_STORAGE_STATE"),
        playwright_headless=read("PLAYWRIGHT_HEADLESS", "true").lower() == "true",
        linkedin_access_token=read("LINKEDIN_ACCESS_TOKEN"),
        linkedin_author_urn=read("LINKEDIN_AUTHOR_URN"),
        linkedin_version=read("LINKEDIN_VERSION", "202602"),
        linkedin_auto_publish=read("LINKEDIN_AUTO_PUBLISH", "false").lower() == "true",
    )

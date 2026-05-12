#!/usr/bin/env python3
"""Validate local credentials for Chutzrit AI Office integrations."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"

REQUIRED_ENV_KEYS = (
    "DISCORD_WEBHOOK_URL",
    "DISCORD_BOT_TOKEN",
    "DISCORD_GUILD_ID",
    "DISCORD_BROADCASTING_CHANNEL_ID",
    "DISCORD_ALLOWED_USER_IDS",
    "OPENAI_API_KEY",
)

OPENAI_DEFAULT_MODEL = "gpt-5.4-mini"


class IntegrationError(RuntimeError):
    """Raised when an integration check fails."""


def load_env(path: Path) -> dict[str, str]:
    """Load simple KEY=VALUE lines from a dotenv file."""
    values: dict[str, str] = {}
    if not path.exists():
        raise IntegrationError(f"Missing env file: {path}")

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


def require_env(values: dict[str, str], keys: tuple[str, ...]) -> None:
    """Fail if required environment variables are missing."""
    missing = [key for key in keys if not values.get(key)]
    if missing:
        raise IntegrationError("Missing required env keys: " + ", ".join(missing))


def request_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
    timeout: int = 20,
) -> dict[str, Any]:
    """Send an HTTP request and return JSON without exposing secrets."""
    body = None
    request_headers = {
        "Accept": "application/json",
        "User-Agent": "ChutzritAIOffice/0.1 (integration-check; Python urllib)",
    }
    if headers:
        request_headers.update(headers)

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    req = Request(url=url, data=body, headers=request_headers, method=method)

    try:
        with urlopen(req, timeout=timeout) as response:
            response_body = response.read().decode("utf-8")
            if not response_body:
                return {"ok": True, "status": response.status}
            return json.loads(response_body)
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise IntegrationError(f"HTTP {exc.code} from {url}: {error_body[:500]}") from exc
    except URLError as exc:
        raise IntegrationError(f"Network error for {url}: {exc.reason}") from exc


def check_env(values: dict[str, str]) -> None:
    """Print required env key status without printing secret values."""
    require_env(values, REQUIRED_ENV_KEYS)
    print("[ok] required .env keys are set")


def check_discord_bot(values: dict[str, str]) -> None:
    """Validate Discord bot token and broadcasting channel access."""
    token = values["DISCORD_BOT_TOKEN"]
    channel_id = values["DISCORD_BROADCASTING_CHANNEL_ID"]
    headers = {"Authorization": f"Bot {token}"}

    bot_user = request_json("https://discord.com/api/v10/users/@me", headers=headers)
    channel = request_json(
        f"https://discord.com/api/v10/channels/{channel_id}",
        headers=headers,
    )

    bot_name = bot_user.get("username", "unknown")
    channel_name = channel.get("name", "unknown")
    print(f"[ok] discord bot token works: bot={bot_name}")
    print(f"[ok] discord channel is accessible: channel={channel_name}")


def check_discord_webhook(values: dict[str, str]) -> None:
    """Send a Discord webhook test report."""
    payload = {
        "content": (
            "[Chutzrit AI Office]\n"
            "team: broadcasting\n"
            "status: Discord webhook integration test succeeded"
        )
    }
    request_json(values["DISCORD_WEBHOOK_URL"], method="POST", payload=payload)
    print("[ok] discord webhook sent a test message")


def check_openai(values: dict[str, str]) -> None:
    """Validate OpenAI API access using the Responses API."""
    model = values.get("OPENAI_MODEL") or OPENAI_DEFAULT_MODEL
    payload = {
        "model": model,
        "input": "Reply with exactly: ok",
        "max_output_tokens": 20,
    }
    response = request_json(
        "https://api.openai.com/v1/responses",
        method="POST",
        headers={"Authorization": f"Bearer {values['OPENAI_API_KEY']}"},
        payload=payload,
    )

    response_id = response.get("id", "unknown")
    print(f"[ok] openai responses api works: model={model}, response_id={response_id}")


def check_tistory_session(values: dict[str, str]) -> None:
    """Validate that the stored Tistory session reaches the manage page."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from agents.broadcasting.publishers.tistory import TistoryPublisher  # noqa: PLC0415

    publisher = TistoryPublisher(
        manage_url=values.get("TISTORY_MANAGE_URL", ""),
        blog_url=values.get("TISTORY_BLOG_URL", ""),
        write_url=values.get("TISTORY_WRITE_URL", ""),
        storage_state=values.get("PLAYWRIGHT_STORAGE_STATE", ""),
        headless=True,
        publish_mode=values.get("TISTORY_PUBLISH_MODE", "public"),
    )
    result = publisher.validate_session()
    if result.status != "connected":
        raise IntegrationError(f"tistory session check failed: {result.status} - {result.reason}")
    print("[ok] tistory playwright session works")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", default=str(ENV_PATH), help="Path to .env file")
    parser.add_argument("--discord-bot", action="store_true", help="Check Discord bot token and channel")
    parser.add_argument("--discord-webhook", action="store_true", help="Send Discord webhook test message")
    parser.add_argument("--openai", action="store_true", help="Check OpenAI Responses API")
    parser.add_argument("--tistory", action="store_true", help="Check Tistory Playwright login session")
    parser.add_argument("--all", action="store_true", help="Run every integration check")
    return parser.parse_args()


def main() -> int:
    """Run selected integration checks."""
    args = parse_args()

    try:
        values = load_env(Path(args.env))
        check_env(values)
        if args.all or args.discord_bot:
            check_discord_bot(values)
        if args.all or args.discord_webhook:
            check_discord_webhook(values)
        if args.all or args.openai:
            check_openai(values)
        if args.all or args.tistory:
            check_tistory_session(values)
    except IntegrationError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

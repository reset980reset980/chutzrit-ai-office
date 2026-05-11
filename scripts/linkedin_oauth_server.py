#!/usr/bin/env python3
"""Run a local LinkedIn OAuth callback server and save the token to .env."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlencode, urlparse
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"
DEFAULT_REDIRECT_URI = "http://127.0.0.1:3000/callback"
DEFAULT_SCOPES = "openid profile email w_member_social"


def load_dotenv(path: Path = ENV_PATH) -> dict[str, str]:
    """Load simple KEY=VALUE pairs into the process environment."""
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


def require_env(keys: tuple[str, ...]) -> None:
    """Exit with a clear message when required environment values are missing."""
    missing = [key for key in keys if not os.environ.get(key)]
    if missing:
        raise SystemExit("Missing required env keys: " + ", ".join(missing))


def build_authorization_url(client_id: str, redirect_uri: str, scopes: str, state: str) -> str:
    """Build the LinkedIn authorization URL."""
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scopes,
        "state": state,
    }
    return "https://www.linkedin.com/oauth/v2/authorization?" + urlencode(params, quote_via=quote)


def exchange_code_for_token(code: str, redirect_uri: str) -> dict[str, Any]:
    """Exchange an OAuth code for a LinkedIn access token."""
    payload = urlencode(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": os.environ["LINKEDIN_CLIENT_ID"],
            "client_secret": os.environ["LINKEDIN_CLIENT_SECRET"],
        }
    ).encode("utf-8")
    request = Request(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    return request_json(request)


def fetch_userinfo(access_token: str) -> dict[str, Any]:
    """Fetch OpenID Connect user info to derive a person author URN."""
    request = Request(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )
    return request_json(request)


def request_json(request: Request) -> dict[str, Any]:
    """Send a request and parse a JSON response."""
    try:
        with urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LinkedIn API error {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"LinkedIn API request failed: {exc}") from exc
    return json.loads(body)


def update_env_file(path: Path, updates: dict[str, str]) -> None:
    """Update or append keys in a local .env file without printing secrets."""
    existing_lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    seen: set[str] = set()
    next_lines: list[str] = []

    for line in existing_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            next_lines.append(line)
            continue
        key = line.split("=", 1)[0].strip()
        if key in updates:
            next_lines.append(f"{key}={updates[key]}")
            seen.add(key)
        else:
            next_lines.append(line)

    for key, value in updates.items():
        if key not in seen:
            next_lines.append(f"{key}={value}")

    path.write_text("\n".join(next_lines).rstrip() + "\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass


class OAuthHandler(BaseHTTPRequestHandler):
    """Handle the LinkedIn OAuth callback."""

    expected_state = ""
    redirect_uri = ""
    env_path = ENV_PATH
    result: dict[str, Any] | None = None

    def do_GET(self) -> None:  # noqa: N802
        """Handle GET /callback from LinkedIn."""
        parsed = urlparse(self.path)
        if parsed.path != "/callback":
            self.respond(404, "Not found")
            return

        params = parse_qs(parsed.query)
        if params.get("error"):
            error = params.get("error_description", params["error"])[0]
            type(self).result = {"ok": False, "error": error}
            self.respond(400, f"LinkedIn authorization failed: {error}")
            self.shutdown_server()
            return

        state = params.get("state", [""])[0]
        if state != self.expected_state:
            type(self).result = {"ok": False, "error": "state mismatch"}
            self.respond(400, "State mismatch. Retry OAuth from the generated URL.")
            self.shutdown_server()
            return

        code = params.get("code", [""])[0]
        if not code:
            type(self).result = {"ok": False, "error": "missing code"}
            self.respond(400, "Missing authorization code.")
            self.shutdown_server()
            return

        try:
            token_payload = exchange_code_for_token(code, self.redirect_uri)
            access_token = str(token_payload["access_token"])
            userinfo = fetch_userinfo(access_token)
            expires_in = int(token_payload.get("expires_in", 0))
            expires_at = str(int(time.time()) + expires_in) if expires_in else ""
            author_urn = ""
            if userinfo.get("sub"):
                author_urn = f"urn:li:person:{userinfo['sub']}"

            updates = {
                "LINKEDIN_ACCESS_TOKEN": access_token,
                "LINKEDIN_TOKEN_EXPIRES_AT": expires_at,
            }
            if author_urn:
                updates["LINKEDIN_AUTHOR_URN"] = author_urn

            update_env_file(self.env_path, updates)
            type(self).result = {
                "ok": True,
                "author_urn_saved": bool(author_urn),
                "expires_in": expires_in,
            }
            self.respond(
                200,
                "LinkedIn access token saved to .env. You can close this tab and return to Codex.",
            )
        except Exception as exc:  # noqa: BLE001
            type(self).result = {"ok": False, "error": str(exc)}
            self.respond(500, f"Token exchange failed: {exc}")
        finally:
            self.shutdown_server()

    def log_message(self, format: str, *args: object) -> None:
        """Suppress default HTTP logs so tokens never leak through query logs."""
        return

    def respond(self, status: int, message: str) -> None:
        """Send a small HTML response to the browser."""
        body = (
            "<!doctype html><meta charset='utf-8'>"
            "<title>LinkedIn OAuth</title>"
            "<body style='font-family:system-ui;margin:40px'>"
            f"<h1>{'완료' if status < 400 else '실패'}</h1>"
            f"<p>{message}</p>"
            "</body>"
        ).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def shutdown_server(self) -> None:
        """Shutdown the local callback server after the current response."""
        threading.Thread(target=self.server.shutdown, daemon=True).start()


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--redirect-uri", default=os.environ.get("LINKEDIN_REDIRECT_URI", DEFAULT_REDIRECT_URI))
    parser.add_argument("--scopes", default=os.environ.get("LINKEDIN_SCOPES", DEFAULT_SCOPES))
    parser.add_argument("--env-path", default=str(ENV_PATH))
    return parser.parse_args()


def main() -> int:
    """Run the OAuth callback server."""
    load_dotenv()
    args = parse_args()
    require_env(("LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET"))

    redirect_uri = args.redirect_uri
    parsed_redirect = urlparse(redirect_uri)
    if parsed_redirect.hostname not in {"127.0.0.1", "localhost"}:
        raise SystemExit("Only localhost redirect URIs are supported by this helper.")
    if parsed_redirect.path != "/callback":
        raise SystemExit("Redirect URI path must be /callback.")

    host = parsed_redirect.hostname or "127.0.0.1"
    port = parsed_redirect.port or 80
    state = secrets.token_urlsafe(24)
    auth_url = build_authorization_url(
        client_id=os.environ["LINKEDIN_CLIENT_ID"],
        redirect_uri=redirect_uri,
        scopes=args.scopes,
        state=state,
    )

    OAuthHandler.expected_state = state
    OAuthHandler.redirect_uri = redirect_uri
    OAuthHandler.env_path = Path(args.env_path)
    OAuthHandler.result = None

    print("LinkedIn OAuth callback server is running.")
    print(f"Redirect URI: {redirect_uri}")
    print("Open this authorization URL in your browser:")
    print(auth_url)
    print("Waiting for LinkedIn callback...")

    with HTTPServer((host, port), OAuthHandler) as server:
        server.serve_forever()

    result = OAuthHandler.result or {"ok": False, "error": "no callback result"}
    if result.get("ok"):
        print("LinkedIn token saved to .env.")
        print(f"Author URN saved: {'yes' if result.get('author_urn_saved') else 'no'}")
        print(f"Expires in seconds: {result.get('expires_in')}")
        return 0

    print(f"LinkedIn OAuth failed: {result.get('error')}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

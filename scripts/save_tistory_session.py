#!/usr/bin/env python3
"""Save a Tistory Playwright login session for the broadcasting publisher."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.broadcasting.pipeline.config import load_runtime_config  # noqa: E402
from agents.broadcasting.publishers.tistory import resolve_project_path  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", choices=("chromium", "brave"), default="chromium")
    parser.add_argument(
        "--brave-profile",
        default="Default",
        help="Deprecated; Brave session capture now uses a dedicated Playwright profile.",
    )
    parser.add_argument(
        "--save-after",
        type=int,
        default=0,
        help="Save storage state after this many seconds without URL detection",
    )
    parser.add_argument("--timeout", type=int, default=900, help="Seconds to wait for login")
    parser.add_argument("--url", help="Tistory URL to open first")
    return parser.parse_args()


def main() -> int:
    """Open Tistory, wait for login, and save Playwright storage state."""
    args = parse_args()
    config = load_runtime_config()
    target_url = args.url or config.tistory_manage_url or config.tistory_write_url or config.tistory_blog_url
    if not target_url:
        raise SystemExit("TISTORY_MANAGE_URL, TISTORY_WRITE_URL, or TISTORY_BLOG_URL is required")

    state_path = resolve_project_path(config.playwright_storage_state)
    state_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("playwright is not installed. Run `python -m pip install playwright`.") from exc

    print(f"Opening Tistory login page: {target_url}", flush=True)
    print("Log in in the browser. The session will be saved after a /manage page is detected.", flush=True)
    print(f"Storage state target: {state_path}", flush=True)

    with sync_playwright() as playwright:
        browser = None
        if args.browser == "brave":
            user_data_dir = brave_playwright_profile_dir(state_path)
            assert_isolated_browser_profile_dir(user_data_dir)
            user_data_dir.mkdir(parents=True, exist_ok=True)
            print(f"Using isolated Brave profile for session capture: {user_data_dir}", flush=True)
            context = playwright.chromium.launch_persistent_context(
                str(user_data_dir),
                executable_path=str(brave_executable_path()),
                headless=False,
            )
        else:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
        page = context.new_page()
        page.goto(target_url, wait_until="domcontentloaded")
        if args.save_after > 0:
            print(f"Saving storage state in {args.save_after} seconds without URL detection.", flush=True)
            time.sleep(args.save_after)
            context.storage_state(path=str(state_path))
            print(f"Saved Tistory storage state: {state_path}", flush=True)
            context.close()
            if browser:
                browser.close()
            return 0

        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline:
            for open_page in context.pages:
                url = open_page.url
                if is_logged_in_manage_url(url):
                    context.storage_state(path=str(state_path))
                    print(f"Saved Tistory storage state: {state_path}", flush=True)
                    context.close()
                    if browser:
                        browser.close()
                    return 0
            time.sleep(2)

        screenshot_path = state_path.parent / "tistory-session-timeout.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        context.close()
        if browser:
            browser.close()
        raise SystemExit(
            "Tistory login was not detected before timeout. "
            f"Screenshot saved: {screenshot_path}"
        )


def is_logged_in_manage_url(url: str) -> bool:
    """Return whether a URL indicates the Tistory admin page is open."""
    return "tistory.com/manage" in url and "/auth/login" not in url


def brave_executable_path() -> Path:
    """Return the default macOS Brave executable path."""
    path = Path("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser")
    if not path.exists():
        raise SystemExit(f"Brave executable not found: {path}")
    return path


def assert_isolated_browser_profile_dir(user_data_dir: Path) -> None:
    """Refuse to run Playwright against a real daily-use browser profile."""
    candidate = user_data_dir.expanduser().resolve(strict=False)
    for forbidden in known_real_browser_profile_dirs():
        forbidden_path = forbidden.expanduser().resolve(strict=False)
        if candidate == forbidden_path or forbidden_path in candidate.parents:
            raise SystemExit(
                "Refusing to use a real browser profile for Playwright automation: "
                f"{candidate}. Use an isolated profile under outputs/broadcasting/session instead."
            )


def known_real_browser_profile_dirs() -> tuple[Path, ...]:
    """Return browser profile roots that must never be automated directly."""
    home = Path.home()
    return (
        home / "Library" / "Application Support" / "BraveSoftware" / "Brave-Browser",
        home / "Library" / "Application Support" / "Google" / "Chrome",
        home / "Library" / "Application Support" / "Chromium",
        home / ".config" / "BraveSoftware" / "Brave-Browser",
        home / ".config" / "google-chrome",
        home / ".config" / "chromium",
    )


def brave_playwright_profile_dir(state_path: Path) -> Path:
    """Return the dedicated Brave profile directory used only for session capture."""
    return state_path.parent / "brave-playwright-profile"


if __name__ == "__main__":
    raise SystemExit(main())

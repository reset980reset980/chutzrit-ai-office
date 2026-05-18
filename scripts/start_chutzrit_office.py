#!/usr/bin/env python3
"""Start Chutzrit office runtime services and run readiness checks."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_ROOT = PROJECT_ROOT / "apps" / "office-dashboard"
LOG_DIR = PROJECT_ROOT / "outputs" / "broadcasting" / "logs"
TELEGRAM_SCREEN = "chutzrit-telegram-bot"
DASHBOARD_SCREEN = "chutzrit-office-dashboard"
DASHBOARD_URL = "http://127.0.0.1:5173/"


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-checks", action="store_true", help="Start services without integration checks")
    parser.add_argument("--dashboard-url", default=DASHBOARD_URL, help="Dashboard health URL")
    return parser.parse_args()


def main() -> int:
    """Start services and report readiness."""
    args = parse_args()
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    results: list[tuple[str, bool, str]] = []
    results.append(ensure_telegram_bot())
    results.append(ensure_dashboard(args.dashboard_url))

    if not args.skip_checks:
        results.append(run_integration_checks())

    print()
    print("후츠릿 오피스 실행 점검 결과")
    failed = False
    for name, ok, detail in results:
        mark = "ok" if ok else "fail"
        print(f"[{mark}] {name}: {detail}")
        failed = failed or not ok

    if failed:
        return 1

    print(f"[ok] office dashboard: {args.dashboard_url}")
    print("[ok] Telegram 입력 테스트 가능")
    return 0


def ensure_telegram_bot() -> tuple[str, bool, str]:
    """Start the Telegram bot unless it is already running."""
    if process_running("apps/telegram-bot/bot.py"):
        return ("telegram bot", True, "이미 실행 중이라 재시작하지 않음")

    command = (
        f"cd {shell_quote(PROJECT_ROOT)} && "
        ".venv/bin/python apps/telegram-bot/bot.py "
        ">> outputs/broadcasting/logs/telegram-bot.log 2>&1"
    )
    start_screen(TELEGRAM_SCREEN, command)
    if wait_for_process("apps/telegram-bot/bot.py", timeout=10):
        return ("telegram bot", True, "새 screen 세션으로 실행")
    return ("telegram bot", False, "실행 확인 실패")


def ensure_dashboard(url: str) -> tuple[str, bool, str]:
    """Start the office dashboard dev server unless it already responds."""
    if http_ok(url):
        return ("office dashboard", True, "이미 응답 중")

    if not (DASHBOARD_ROOT / "node_modules").exists():
        return (
            "office dashboard",
            False,
            "node_modules가 없음. apps/office-dashboard에서 npm install 필요",
        )

    command = (
        f"cd {shell_quote(DASHBOARD_ROOT)} && "
        "npm run dev >> ../../outputs/broadcasting/logs/office-dashboard.log 2>&1"
    )
    start_screen(DASHBOARD_SCREEN, command)
    if wait_for_http(url, timeout=20):
        return ("office dashboard", True, "새 screen 세션으로 실행")
    return ("office dashboard", False, f"{url} 응답 확인 실패")


def run_integration_checks() -> tuple[str, bool, str]:
    """Run Telegram, OpenAI, and Tistory readiness checks."""
    python_bin = PROJECT_ROOT / ".venv" / "bin" / "python"
    if not python_bin.exists():
        python_bin = Path(sys.executable)

    completed = subprocess.run(
        [str(python_bin), "scripts/check_integrations.py", "--all"],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=90,
        check=False,
    )
    output = completed.stdout.strip().splitlines()
    detail = output[-1] if output else "출력 없음"
    if completed.returncode == 0:
        return ("integrations", True, "Telegram, OpenAI, Tistory 검증 통과")
    return ("integrations", False, detail)


def start_screen(name: str, command: str) -> None:
    """Start a detached screen session."""
    subprocess.run(
        ["screen", "-dmS", name, "zsh", "-lc", command],
        cwd=PROJECT_ROOT,
        check=False,
    )


def process_running(pattern: str) -> bool:
    """Return whether a process matching pattern is running."""
    completed = subprocess.run(
        ["ps", "-ef"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return any(pattern in line and "start_chutzrit_office.py" not in line for line in completed.stdout.splitlines())


def wait_for_process(pattern: str, *, timeout: int) -> bool:
    """Wait until a process appears."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process_running(pattern):
            return True
        time.sleep(0.5)
    return False


def http_ok(url: str) -> bool:
    """Return whether an HTTP URL responds successfully."""
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return 200 <= response.status < 500
    except Exception:  # noqa: BLE001
        return False


def wait_for_http(url: str, *, timeout: int) -> bool:
    """Wait until an HTTP URL responds."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if http_ok(url):
            return True
        time.sleep(1)
    return False


def shell_quote(path: Path) -> str:
    """Quote a filesystem path for zsh -lc."""
    return "'" + str(path).replace("'", "'\\''") + "'"


if __name__ == "__main__":
    raise SystemExit(main())

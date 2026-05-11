"""Generate one broadcasting content package from local input."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_runtime_config
from .generator import generate_content_package
from .storage import save_content_package
from .webhook import send_broadcasting_report


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", help="Raw memo or link to turn into content")
    parser.add_argument("--file", help="File containing raw memo or link")
    parser.add_argument("--no-webhook", action="store_true", help="Do not send Discord webhook report")
    return parser.parse_args()


def read_source(args: argparse.Namespace) -> str:
    """Read the source message from arguments."""
    if args.text:
        return args.text
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    raise SystemExit("Provide --text or --file")


def main() -> int:
    """Run one content generation job."""
    args = parse_args()
    config = load_runtime_config()
    package = generate_content_package(read_source(args), config)
    output_path = save_content_package(package)

    if not args.no_webhook:
        send_broadcasting_report(config.discord_webhook_url, package=package, output_path=output_path)

    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

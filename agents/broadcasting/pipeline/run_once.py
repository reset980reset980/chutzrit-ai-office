"""Generate one broadcasting content package from local input."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_runtime_config
from .generator import generate_content_package
from .storage import refresh_publish_files, save_content_package
from .visuals import generate_visual_assets_for_saved_package
from .webhook import send_broadcasting_report
from agents.broadcasting.agents import PublishAgent


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", help="Raw memo or link to turn into content")
    parser.add_argument("--file", help="File containing raw memo or link")
    parser.add_argument("--publish", action="store_true", help="Execute enabled external publishers after saving")
    parser.add_argument("--no-webhook", action="store_true", help="Do not send legacy webhook report")
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
    config = load_runtime_config(require_discord=False, require_telegram=False)
    package = generate_content_package(read_source(args), config)
    output_path = save_content_package(package)
    generate_visual_assets_for_saved_package(package, config, output_path)
    if args.publish:
        package["publish_plan"] = PublishAgent(config).execute(package, output_path)
        refresh_publish_files(package, output_path)

    if not args.no_webhook and config.discord_webhook_url:
        send_broadcasting_report(config.discord_webhook_url, package=package, output_path=output_path)

    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

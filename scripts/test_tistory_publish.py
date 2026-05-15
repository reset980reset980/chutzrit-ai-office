#!/usr/bin/env python3
"""Publish a short Tistory post to verify the real publishing path."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from urllib.error import URLError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.broadcasting.pipeline.config import load_runtime_config  # noqa: E402
from agents.broadcasting.publishers.tistory import TistoryPublisher  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default="outputs/broadcasting/logs/tistory-publish-test",
        help="Directory for publisher screenshots and test metadata",
    )
    parser.add_argument(
        "--title-prefix",
        default="후츠릿 AI 오피스 티스토리 배포 테스트",
        help="Title prefix for the public test post",
    )
    parser.add_argument(
        "--skip-url-check",
        action="store_true",
        help="Skip the final public URL HTTP check",
    )
    return parser.parse_args()


def main() -> int:
    """Run a real Tistory public publishing test."""
    args = parse_args()
    config = load_runtime_config()
    if not config.tistory_auto_publish:
        print("[error] TISTORY_AUTO_PUBLISH=true is required for a public publish test", file=sys.stderr)
        return 1
    if config.tistory_publish_mode.lower() != "public":
        print("[error] TISTORY_PUBLISH_MODE=public is required for a public publish test", file=sys.stderr)
        return 1

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    markdown = build_test_markdown(f"{args.title_prefix} {now}")
    output_dir = PROJECT_ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    publisher = TistoryPublisher(
        manage_url=config.tistory_manage_url,
        blog_url=config.tistory_blog_url,
        write_url=config.tistory_write_url,
        storage_state=config.playwright_storage_state,
        headless=config.playwright_headless,
        publish_mode=config.tistory_publish_mode,
    )
    result = publisher.publish(markdown, output_dir=output_dir)
    payload = {"channel": result.channel, **result.to_dict()}

    if result.status != "published":
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    if not args.skip_url_check:
        status_code = check_public_url(result.url)
        payload["details"] = {**payload.get("details", {}), "public_url_status": status_code}

    (output_dir / "latest-result.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def build_test_markdown(title: str) -> str:
    """Build the public test post body."""
    return f"""# {title}

## 테스트 목적

이 글은 후츠릿 AI 오피스의 티스토리 Playwright 공개 발행 경로가 실제로 작동하는지 확인하기 위한 테스트 글이다.

## 확인 항목

- 저장된 Playwright 세션으로 관리자 화면에 접근한다.
- Markdown 본문을 HTML로 변환해 WYSIWYG 에디터에 입력한다.
- 공개 발행 후 실제 게시 URL을 회수한다.

## 결과

이 글이 공개 URL로 열리면 티스토리 배포 테스트는 성공이다.
"""


def check_public_url(url: str) -> int:
    """Return the HTTP status for the public Tistory post URL."""
    request = Request(url, headers={"User-Agent": "ChutzritAIOffice/0.1 (tistory-publish-test)"})
    try:
        with urlopen(request, timeout=20) as response:
            if not 200 <= response.status < 400:
                raise RuntimeError(f"Unexpected public URL status: {response.status}")
            return response.status
    except URLError as exc:
        raise RuntimeError(f"Public URL check failed: {exc.reason}") from exc


if __name__ == "__main__":
    raise SystemExit(main())

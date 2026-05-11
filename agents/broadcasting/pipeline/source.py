"""Source message parsing for broadcasting requests."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import Request, urlopen


URL_PATTERN = re.compile(r"https?://[^\s<>\"]+")


@dataclass(frozen=True)
class SourceContext:
    """Parsed user input and optional linked page metadata."""

    raw_text: str
    urls: list[str]
    link_summaries: list[str]

    def to_prompt_text(self) -> str:
        """Render source context for prompting."""
        links = "\n".join(f"- {url}" for url in self.urls) or "- 없음"
        summaries = "\n\n".join(self.link_summaries) or "없음"
        return (
            f"[사용자 입력]\n{self.raw_text.strip()}\n\n"
            f"[감지된 링크]\n{links}\n\n"
            f"[링크 메타데이터]\n{summaries}"
        )


def parse_source_context(text: str, *, fetch_links: bool = True) -> SourceContext:
    """Parse URLs from a message and fetch lightweight page metadata."""
    urls = URL_PATTERN.findall(text)
    summaries = [fetch_link_summary(url) for url in urls] if fetch_links else []
    summaries = [summary for summary in summaries if summary]
    return SourceContext(raw_text=text, urls=urls, link_summaries=summaries)


def fetch_link_summary(url: str) -> str:
    """Fetch title and description from a URL when possible."""
    req = Request(
        url,
        headers={
            "User-Agent": "ChutzritAIOffice/0.1 (source-fetch; Python urllib)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    try:
        with urlopen(req, timeout=12) as response:
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                return f"{url}\n콘텐츠 타입: {content_type or 'unknown'}"
            body = response.read(300_000).decode("utf-8", errors="replace")
    except (URLError, TimeoutError, ValueError) as exc:
        return f"{url}\n링크 메타데이터 수집 실패: {exc}"

    title = extract_html_title(body) or "제목 없음"
    description = extract_meta_description(body) or "설명 없음"
    return f"{url}\n제목: {title}\n설명: {description}"


def extract_html_title(body: str) -> str:
    """Extract an HTML title."""
    match = re.search(r"<title[^>]*>(.*?)</title>", body, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return clean_html_text(match.group(1))


def extract_meta_description(body: str) -> str:
    """Extract meta description or og:description."""
    patterns = (
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
        r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']',
        r'<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']description["\']',
        r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:description["\']',
    )
    for pattern in patterns:
        match = re.search(pattern, body, re.IGNORECASE | re.DOTALL)
        if match:
            return clean_html_text(match.group(1))
    return ""


def clean_html_text(value: str) -> str:
    """Normalize text extracted from HTML."""
    return re.sub(r"\s+", " ", html.unescape(value)).strip()[:800]

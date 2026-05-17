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
    input_type: str

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
    return SourceContext(raw_text=text, urls=urls, link_summaries=summaries, input_type=detect_input_type(text, urls))


def detect_input_type(text: str, urls: list[str]) -> str:
    """Detect whether an input is a memo, link, or link with memo."""
    note_text = text
    for url in urls:
        note_text = note_text.replace(url, "")

    if urls and note_text.strip():
        return "link_with_memo"
    if urls:
        return "link"
    return "memo"


def fetch_link_summary(url: str) -> str:
    """Fetch title, description, and lightweight content summary from a URL."""
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
            body = response.read(600_000).decode("utf-8", errors="replace")
    except (URLError, TimeoutError, ValueError) as exc:
        return f"{url}\n링크 메타데이터 수집 실패: {exc}"

    title = extract_html_title(body) or "제목 없음"
    description = extract_meta_description(body) or "설명 없음"
    content_summary = summarize_html_content(body)
    return f"{url}\n제목: {title}\n설명: {description}\n핵심 내용: {content_summary}"


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


def summarize_html_content(body: str, *, max_sentences: int = 3) -> str:
    """Extract a short, deterministic summary from visible HTML text."""
    text = extract_visible_text(body)
    if not text:
        return "본문 핵심 내용 추출 실패"

    sentences = split_sentences(text)
    useful_sentences = [
        sentence
        for sentence in sentences
        if 30 <= len(sentence) <= 260 and not looks_like_navigation(sentence)
    ]
    selected = useful_sentences[:max_sentences] or sentences[:max_sentences]
    summary = " ".join(selected).strip()
    return compact_summary(summary, 700) if summary else "본문 핵심 내용 추출 실패"


def extract_visible_text(body: str) -> str:
    """Extract rough visible text from HTML without adding parser dependencies."""
    cleaned = re.sub(r"(?is)<(script|style|noscript|svg|canvas|iframe).*?</\1>", " ", body)
    cleaned = re.sub(r"(?is)<!--.*?-->", " ", cleaned)
    cleaned = re.sub(r"(?is)</(p|div|section|article|h[1-6]|li|br)>", ". ", cleaned)
    cleaned = re.sub(r"(?is)<[^>]+>", " ", cleaned)
    cleaned = html.unescape(cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def split_sentences(text: str) -> list[str]:
    """Split Korean/English text into sentence-like chunks."""
    chunks = re.split(r"(?<=[.!?。！？다요죠음임])\s+", text)
    return [chunk.strip(" .") for chunk in chunks if chunk.strip(" .")]


def looks_like_navigation(sentence: str) -> bool:
    """Filter common page chrome text."""
    lower = sentence.lower()
    blocked_terms = (
        "로그인",
        "회원가입",
        "구독",
        "공유",
        "댓글",
        "이전 글",
        "다음 글",
        "copyright",
        "privacy",
        "terms",
        "menu",
        "navigation",
    )
    return any(term in lower for term in blocked_terms)


def compact_summary(value: str, limit: int) -> str:
    """Trim a summary without cutting too aggressively."""
    normalized = re.sub(r"\s+", " ", value).strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."

"""Tistory Playwright publisher."""

from __future__ import annotations

from contextlib import suppress
import html
import re
from pathlib import Path
from urllib.parse import urlparse

from agents.broadcasting.pipeline.config import PROJECT_ROOT

from .base import PublishResult


TITLE_SELECTORS = (
    'textarea[placeholder*="제목"]',
    'input[placeholder*="제목"]',
    "#post-title-inp",
    "textarea#title",
    'input[name="title"]',
    '[contenteditable="true"][data-placeholder*="제목"]',
)

BODY_SELECTORS = (
    'div.ProseMirror[contenteditable="true"]',
    '[contenteditable="true"][aria-label*="본문"]',
    '[contenteditable="true"][data-placeholder*="내용"]',
    ".mce-content-body",
    'textarea[placeholder*="내용"]',
    "textarea",
    '[contenteditable="true"]',
)

IFRAME_BODY_SELECTORS = (
    "body#tinymce",
    "body.mce-content-body",
    ".mce-content-body",
    '[contenteditable="true"]',
)


class TistoryPublisher:
    """Publish a blog post through Tistory's browser editor."""

    provider = "tistory_playwright"

    def __init__(
        self,
        *,
        manage_url: str,
        storage_state: str,
        headless: bool,
        publish_mode: str,
        blog_url: str = "",
        write_url: str = "",
    ) -> None:
        self.manage_url = manage_url.rstrip("/")
        self.storage_state = storage_state
        self.headless = headless
        self.publish_mode = publish_mode
        self.blog_url = (blog_url or derive_blog_url(manage_url)).rstrip("/")
        self.write_url = write_url or derive_write_url(manage_url, self.blog_url)

    def publish(self, markdown: str, *, output_dir: Path) -> PublishResult:
        """Publish Markdown content through the Tistory web editor."""
        storage_state = resolve_project_path(self.storage_state)
        if not storage_state.exists():
            return PublishResult(
                channel="blog",
                status="not_connected",
                provider=self.provider,
                reason=f"Playwright 로그인 세션 파일이 없다: {storage_state}",
            )

        try:
            from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
            from playwright.sync_api import sync_playwright
        except ImportError:
            return PublishResult(
                channel="blog",
                status="dependency_missing",
                provider=self.provider,
                reason="playwright 패키지가 설치되어 있지 않다. `python -m pip install playwright` 후 `python -m playwright install chromium`이 필요하다.",
            )

        title, body = split_markdown_title(markdown)
        output_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = output_dir / "tistory-publish-error.png"

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=self.headless)
            context = browser.new_context(storage_state=str(storage_state))
            page = context.new_page()
            page.set_default_timeout(30_000)
            page.on("dialog", lambda dialog: dialog.dismiss())

            try:
                page.goto(self.write_url, wait_until="domcontentloaded")
                with suppress(Exception):
                    page.wait_for_load_state("networkidle", timeout=10_000)
                page.wait_for_timeout(1_000)
                fill_first_matching(page, TITLE_SELECTORS, title, min_height=0, field_name="제목")
                fill_body_editor(page, body)

                if self.publish_mode.lower() == "draft":
                    click_button(page, ("임시저장", "저장"), required=True)
                    return PublishResult(
                        channel="blog",
                        status="draft_saved",
                        provider=self.provider,
                        reason="Tistory 글을 임시저장했다.",
                    )

                click_button(page, ("완료", "발행", "게시", "출간"), required=True)
                page.wait_for_timeout(1_000)
                click_optional_text(page, ("공개", "전체 공개"))
                click_button(page, ("공개 발행", "발행", "게시", "출간"), required=False)
                page.wait_for_load_state("domcontentloaded", timeout=10_000)
                page.wait_for_timeout(2_000)

                post_url = extract_public_post_url(page, self.blog_url)
                if not post_url:
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    return PublishResult(
                        channel="blog",
                        status="failed",
                        provider=self.provider,
                        reason="Tistory 발행 후 공개 URL을 찾지 못했다.",
                        details={"screenshot": str(screenshot_path)},
                    )

                return PublishResult(
                    channel="blog",
                    status="published",
                    provider=self.provider,
                    url=post_url,
                    reason="Tistory 공개 발행이 완료됐다.",
                )
            except PlaywrightTimeoutError as exc:
                page.screenshot(path=str(screenshot_path), full_page=True)
                return PublishResult(
                    channel="blog",
                    status="failed",
                    provider=self.provider,
                    reason=f"Tistory UI 대기 시간이 초과됐다: {exc}",
                    details={"screenshot": str(screenshot_path)},
                )
            except Exception as exc:  # noqa: BLE001
                page.screenshot(path=str(screenshot_path), full_page=True)
                return PublishResult(
                    channel="blog",
                    status="failed",
                    provider=self.provider,
                    reason=f"Tistory 발행 중 오류가 발생했다: {type(exc).__name__}: {exc}",
                    details={"screenshot": str(screenshot_path)},
                )
            finally:
                with suppress(Exception):
                    page.close()
                with suppress(Exception):
                    context.close()
                with suppress(Exception):
                    browser.close()


def resolve_project_path(value: str) -> Path:
    """Resolve a path relative to the repository root."""
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def derive_blog_url(manage_url: str) -> str:
    """Derive the public blog origin from a Tistory manage URL."""
    parsed = urlparse(manage_url)
    if not parsed.scheme or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}"


def derive_write_url(manage_url: str, blog_url: str) -> str:
    """Derive the Tistory new-post URL."""
    if blog_url:
        return f"{blog_url.rstrip('/')}/manage/newpost"
    return manage_url.rstrip("/") + "/newpost"


def split_markdown_title(markdown: str) -> tuple[str, str]:
    """Split the first Markdown H1 into Tistory title and body."""
    lines = markdown.strip().splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            body = "\n".join(lines[:index] + lines[index + 1 :]).strip()
            return title, body

    for line in lines:
        stripped = line.strip().lstrip("#").strip()
        if stripped:
            return stripped[:80], markdown.strip()
    return "후츠릿 콘텐츠", markdown.strip()


def fill_body_editor(page, text: str) -> None:
    """Fill Tistory's body editor in either the main page or an editor iframe."""
    html_content = markdown_to_tistory_html(text)
    if try_fill_first_matching(page, BODY_SELECTORS, text, min_height=80, keyboard_page=page, html_content=html_content):
        return

    for frame in page.frames:
        if frame == page.main_frame:
            continue
        if try_fill_first_matching(frame, IFRAME_BODY_SELECTORS, text, min_height=0, keyboard_page=page, html_content=html_content):
            return

    raise RuntimeError("입력 가능한 Tistory 본문 영역을 찾지 못했다.")


def fill_first_matching(
    page,
    selectors: tuple[str, ...],
    text: str,
    *,
    min_height: int,
    field_name: str = "입력",
) -> None:
    """Fill the first visible input/editor matching one of the selectors."""
    if try_fill_first_matching(page, selectors, text, min_height=min_height, keyboard_page=page):
        return
    raise RuntimeError(f"입력 가능한 Tistory {field_name} 영역을 찾지 못했다.")


def try_fill_first_matching(
    root,
    selectors: tuple[str, ...],
    text: str,
    *,
    min_height: int,
    keyboard_page,
    html_content: str = "",
) -> bool:
    """Try to fill the first visible input/editor for a page or frame."""
    for selector in selectors:
        try:
            locator = root.locator(selector)
            count = locator.count()
        except Exception:  # noqa: BLE001
            continue

        for index in range(count):
            candidate = locator.nth(index)
            try:
                if not candidate.is_visible():
                    continue
                box = candidate.bounding_box()
            except Exception:  # noqa: BLE001
                continue

            if min_height and box and box.get("height", 0) < min_height:
                continue
            fill_locator(keyboard_page, candidate, text, html_content=html_content)
            return True
    return False


def fill_locator(page, locator, text: str, *, html_content: str = "") -> None:
    """Fill an input, textarea, or contenteditable editor."""
    tag_name = locator.evaluate("element => element.tagName.toLowerCase()")
    if tag_name in {"input", "textarea"}:
        locator.fill(text)
        return

    locator.click()
    if html_content:
        locator.evaluate(
            """(element, html) => {
                const doc = element.ownerDocument;
                const win = doc.defaultView || window;
                element.focus();

                const selection = win.getSelection();
                const range = doc.createRange();
                range.selectNodeContents(element);
                selection.removeAllRanges();
                selection.addRange(range);

                let inserted = false;
                try {
                    inserted = doc.execCommand && doc.execCommand('insertHTML', false, html);
                } catch (error) {
                    inserted = false;
                }
                if (!inserted) {
                    element.innerHTML = html;
                }

                element.dispatchEvent(new InputEvent('input', {
                    bubbles: true,
                    inputType: 'insertHTML',
                    data: html
                }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
                element.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
            }""",
            html_content,
        )
        return

    page.keyboard.press("ControlOrMeta+A")
    page.keyboard.insert_text(text)


def markdown_to_tistory_html(markdown: str) -> str:
    """Convert the blog Markdown subset into HTML for Tistory's WYSIWYG editor."""
    lines = markdown.strip().splitlines()
    output: list[str] = []
    paragraph: list[str] = []
    list_type = ""
    in_code = False
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            output.append(f"<p>{render_inline_markdown(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            output.append(f"</{list_type}>")
            list_type = ""

    def open_list(next_type: str) -> None:
        nonlocal list_type
        if list_type != next_type:
            close_list()
            output.append(f"<{next_type}>")
            list_type = next_type

    for line in lines:
        stripped = line.strip()

        fence_match = re.match(r"^```", stripped)
        if fence_match:
            if in_code:
                output.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines.clear()
                in_code = False
            else:
                flush_paragraph()
                close_list()
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not stripped:
            flush_paragraph()
            close_list()
            continue

        heading_match = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading_match:
            flush_paragraph()
            close_list()
            level = len(heading_match.group(1))
            output.append(f"<h{level}>{render_inline_markdown(heading_match.group(2).strip())}</h{level}>")
            continue

        if re.match(r"^[-*_]{3,}$", stripped):
            flush_paragraph()
            close_list()
            output.append("<hr>")
            continue

        bullet_match = re.match(r"^[-*]\s+(.+)$", stripped)
        if bullet_match:
            flush_paragraph()
            open_list("ul")
            output.append(f"<li>{render_inline_markdown(bullet_match.group(1).strip())}</li>")
            continue

        ordered_match = re.match(r"^\d+\.\s+(.+)$", stripped)
        if ordered_match:
            flush_paragraph()
            open_list("ol")
            output.append(f"<li>{render_inline_markdown(ordered_match.group(1).strip())}</li>")
            continue

        paragraph.append(stripped)

    if in_code:
        output.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
    flush_paragraph()
    close_list()
    return "\n".join(output)


def render_inline_markdown(text: str) -> str:
    """Render a conservative subset of inline Markdown as HTML."""
    link_pattern = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
    rendered_parts: list[str] = []
    last = 0
    for match in link_pattern.finditer(text):
        rendered_parts.append(html.escape(text[last : match.start()]))
        label = html.escape(match.group(1))
        url = html.escape(match.group(2), quote=True)
        rendered_parts.append(f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a>')
        last = match.end()
    rendered_parts.append(html.escape(text[last:]))
    rendered = "".join(rendered_parts)
    rendered = re.sub(r"`([^`]+)`", r"<code>\1</code>", rendered)
    rendered = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", rendered)
    return rendered


def click_button(page, labels: tuple[str, ...], *, required: bool) -> bool:
    """Click the first visible button-like element matching one of the labels."""
    for label in labels:
        role_locator = page.get_by_role("button", name=re.compile(label)).first
        try:
            if role_locator.is_visible(timeout=1_000):
                role_locator.click()
                return True
        except Exception:  # noqa: BLE001
            pass

        text_locator = page.get_by_text(label, exact=False).first
        try:
            if text_locator.is_visible(timeout=1_000):
                text_locator.click()
                return True
        except Exception:  # noqa: BLE001
            pass

    if required:
        raise RuntimeError(f"버튼을 찾지 못했다: {', '.join(labels)}")
    return False


def click_optional_text(page, labels: tuple[str, ...]) -> None:
    """Click an optional visibility option when present."""
    for label in labels:
        locator = page.get_by_text(label, exact=True).first
        try:
            if locator.is_visible(timeout=1_000):
                locator.click()
                return
        except Exception:  # noqa: BLE001
            continue


def extract_public_post_url(page, blog_url: str) -> str:
    """Extract a public Tistory post URL after publishing."""
    current_url = page.url
    if is_public_tistory_url(current_url, blog_url):
        return current_url

    manage_match = re.search(r"/manage/(?:post|posts)/(\d+)", current_url)
    if manage_match and blog_url:
        return f"{blog_url.rstrip('/')}/{manage_match.group(1)}"

    anchors = page.locator("a[href]").evaluate_all("nodes => nodes.map(node => node.href)")
    for href in anchors:
        if is_public_tistory_url(str(href), blog_url):
            return str(href)
    return ""


def is_public_tistory_url(value: str, blog_url: str) -> bool:
    """Return whether a URL looks like a public Tistory post URL."""
    if not value or "/manage" in value:
        return False
    if blog_url and not value.startswith(blog_url.rstrip("/")):
        return False
    return bool(re.search(r"/\d+(?:$|[/?#])", value))

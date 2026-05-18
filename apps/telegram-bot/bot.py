#!/usr/bin/env python3
"""Telegram bot entrypoint for Chutzrit AI Office."""

from __future__ import annotations

import asyncio
import json
import signal
import sys
import time
from collections.abc import Callable
from contextlib import suppress
from pathlib import Path

from telegram import Message, Update
from telegram.constants import ChatAction
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.broadcasting.agents import PublishAgent  # noqa: E402
from agents.broadcasting.pipeline.config import load_runtime_config  # noqa: E402
from agents.broadcasting.pipeline.generator import generate_content_package  # noqa: E402
from agents.broadcasting.pipeline.progress import format_multi_platform_publish_report  # noqa: E402
from agents.broadcasting.pipeline.runtime_status import (  # noqa: E402
    complete_runtime_status,
    fail_runtime_status,
    record_runtime_progress,
    start_runtime_status,
)
from agents.broadcasting.pipeline.storage import (  # noqa: E402
    record_telegram_dispatch,
    refresh_publish_files,
    save_content_package,
)
from agents.broadcasting.pipeline.visuals import generate_visual_assets_for_saved_package  # noqa: E402


config = load_runtime_config(require_discord=False, require_telegram=True, require_openai=False)
active_job_count = 0
shutdown_requested = False
application: Application | None = None


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Turn Telegram chat messages into content packages."""
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if message is None or chat is None or user is None:
        return

    print(
        "Received Telegram message "
        f"chat_id={chat.id} "
        f"user_id={user.id} "
        f"is_bot={user.is_bot} "
        f"text_len={len(message.text or message.caption or '')}",
        flush=True,
    )

    if user.is_bot:
        print("Ignored Telegram message: sender is a bot", flush=True)
        return

    if config.telegram_broadcasting_chat_id and str(chat.id) != config.telegram_broadcasting_chat_id:
        print(
            "Ignored Telegram message: chat mismatch "
            f"expected={config.telegram_broadcasting_chat_id} actual={chat.id}",
            flush=True,
        )
        return

    allowed_users = config.telegram_allowed_user_ids or set()
    if allowed_users and str(user.id) not in allowed_users:
        print(f"Ignored Telegram message: user {user.id} is not allowed", flush=True)
        await message.reply_text("이 채팅방의 자동화 실행 권한이 없는 사용자입니다.")
        return

    source_text = await build_source_text(message, context)
    if not source_text.strip():
        print("Ignored Telegram message: empty source text", flush=True)
        return

    await message.reply_text("글 작성중입니다. 입력을 분석하고 있습니다.")

    progress_queue: asyncio.Queue[str | None] = asyncio.Queue()
    loop = asyncio.get_running_loop()
    run_id = f"telegram-{chat.id}-{message.message_id}-{int(time.time())}"
    start_runtime_status(
        run_id=run_id,
        source="telegram",
        source_summary=source_text[:220],
    )

    def emit_progress(update_text: str) -> None:
        record_runtime_progress(run_id=run_id, source="telegram", message=update_text)
        loop.call_soon_threadsafe(progress_queue.put_nowait, update_text)

    worker = asyncio.create_task(asyncio.to_thread(process_message, source_text, emit_progress))
    relay = asyncio.create_task(relay_progress(chat.id, context, progress_queue, worker))
    typing_task = asyncio.create_task(keep_typing(chat.id, context, worker))

    try:
        await set_working_state(True)
        output_path = await worker
    except Exception as exc:  # noqa: BLE001
        if not relay.done():
            relay.cancel()
            with suppress(asyncio.CancelledError):
                await relay
        fail_runtime_status(run_id=run_id, error=str(exc))
        await message.reply_text(f"초안 생성에 실패했습니다: {exc}")
        return
    finally:
        if not typing_task.done():
            typing_task.cancel()
            with suppress(asyncio.CancelledError):
                await typing_task
        await set_working_state(False)

    progress_queue.put_nowait(None)
    await relay

    await message.reply_text(f"콘텐츠 생성이 완료됐습니다.\n파일 {output_path}")
    await send_draft_previews(chat.id, context, output_path)
    newsletter_chat_id = config.telegram_newsletter_chat_id or config.telegram_broadcasting_chat_id or str(chat.id)
    telegram_url = await send_telegram_newsletter(newsletter_chat_id, context, output_path)
    record_telegram_dispatch(output_path, telegram_url)
    complete_runtime_status(run_id=run_id, output_path=output_path)
    publish_plan, title = load_publish_report_context(output_path)
    await send_long_message(
        chat.id,
        context,
        format_multi_platform_publish_report(publish_plan, output_path=output_path, title=title),
    )

    if shutdown_requested and active_job_count == 0 and application:
        await application.stop()


async def build_source_text(message: Message, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Build source text from a Telegram message and supported attachments."""
    parts = [message.text or message.caption or ""]
    file_ids = collect_file_ids(message)

    for file_id in file_ids:
        try:
            telegram_file = await context.bot.get_file(file_id)
        except Exception as exc:  # noqa: BLE001
            parts.append(f"Telegram 첨부파일 메타데이터 수집 실패: {type(exc).__name__}")
            continue

        if telegram_file.file_path:
            parts.append(str(telegram_file.file_path))
        else:
            parts.append(f"telegram-file-id:{file_id}")

    return "\n\n".join(part for part in parts if part).strip()


def collect_file_ids(message: Message) -> list[str]:
    """Collect Telegram attachment file IDs from a message."""
    file_ids: list[str] = []
    if message.photo:
        file_ids.append(message.photo[-1].file_id)
    if message.document:
        file_ids.append(message.document.file_id)
    if message.video:
        file_ids.append(message.video.file_id)
    if message.animation:
        file_ids.append(message.animation.file_id)
    if message.audio:
        file_ids.append(message.audio.file_id)
    if message.voice:
        file_ids.append(message.voice.file_id)
    return file_ids


def process_message(source_text: str, progress_callback: Callable[[str], None] | None = None) -> Path:
    """Generate, save, and publish a content package."""
    if not config.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY가 설정되어야 콘텐츠를 생성할 수 있습니다.")

    print(f"Telegram worker started source_len={len(source_text)}", flush=True)
    package = generate_content_package(source_text, config, progress_callback=progress_callback)
    output_path = save_content_package(package)
    generate_visual_assets_for_saved_package(
        package,
        config,
        output_path,
        progress_callback=progress_callback,
    )
    package["publish_plan"] = PublishAgent(config).execute(
        package,
        output_path,
        progress_callback=progress_callback,
    )
    refresh_publish_files(package, output_path)
    if callable(progress_callback):
        progress_callback(f"파일 저장 완료\n{output_path}")
        progress_callback("최종 배포물을 Telegram 채팅방에 발송합니다.")
    return output_path


async def relay_progress(
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE,
    queue: asyncio.Queue[str | None],
    worker: asyncio.Task[Path],
) -> None:
    """Relay worker-thread progress updates to Telegram."""
    while True:
        try:
            update_text = await asyncio.wait_for(queue.get(), timeout=25)
        except asyncio.TimeoutError:
            if not worker.done():
                await send_typing(chat_id, context)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="아직 작성 중입니다. 원고 생성 또는 평가 단계가 오래 걸리고 있습니다.",
                )
                continue
            break

        if update_text is None:
            break

        await send_typing(chat_id, context)
        await send_long_message(chat_id, context, update_text)


async def keep_typing(chat_id: int, context: ContextTypes.DEFAULT_TYPE, worker: asyncio.Task[Path]) -> None:
    """Keep Telegram's native typing indicator visible while the job is running."""
    while not worker.done():
        await send_typing(chat_id, context)
        await asyncio.sleep(4)


async def send_typing(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send Telegram typing action."""
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    except Exception as exc:  # noqa: BLE001
        print(f"Telegram typing action failed: {type(exc).__name__}", flush=True)


async def send_draft_previews(chat_id: int, context: ContextTypes.DEFAULT_TYPE, output_path: Path) -> None:
    """Send draft previews to the operations chat."""
    await send_draft_preview(chat_id, context, "블로그 원고", output_path / "blog.md", attach_file=True)
    await send_draft_preview(chat_id, context, "LinkedIn 원고", output_path / "linkedin.md")


async def send_draft_preview(
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE,
    title: str,
    path: Path,
    *,
    attach_file: bool = False,
) -> None:
    """Send one draft preview, attaching the full file when useful."""
    text = path.read_text(encoding="utf-8").strip()
    max_preview_chars = 3200
    if len(text) > max_preview_chars:
        preview = text[:max_preview_chars].rstrip() + "\n\n..."
        await send_long_message(chat_id, context, f"{title}\n\n{preview}\n\n전체 글은 산출물 파일에서 확인하세요.")
        if attach_file:
            await context.bot.send_document(chat_id=chat_id, document=path.open("rb"), filename=path.name)
        return

    await send_long_message(chat_id, context, f"{title}\n\n{text}")


async def send_telegram_newsletter(
    chat_id: str,
    context: ContextTypes.DEFAULT_TYPE,
    output_path: Path,
) -> str:
    """Publish the reader-facing newsletter draft to Telegram."""
    newsletter_path = output_path / "telegram.md"
    if not newsletter_path.exists():
        newsletter_path = output_path / "discord.md"
    newsletter_text = newsletter_path.read_text(encoding="utf-8").strip()
    messages = await send_long_message(int(chat_id), context, newsletter_text)
    if messages:
        return build_telegram_message_url(messages[-1])
    return ""


async def send_long_message(chat_id: int, context: ContextTypes.DEFAULT_TYPE, text: str) -> list[Message]:
    """Send text while respecting Telegram message length limits."""
    remaining = text.strip()
    messages: list[Message] = []
    while remaining:
        chunk = remaining[:3900]
        split_at = chunk.rfind("\n")
        if split_at > 1800 and len(remaining) > 3900:
            chunk = chunk[:split_at]
        messages.append(await context.bot.send_message(chat_id=chat_id, text=chunk))
        remaining = remaining[len(chunk) :].lstrip()
    return messages


def build_telegram_message_url(message: Message) -> str:
    """Build a best-effort Telegram message URL."""
    chat = message.chat
    if chat.username:
        return f"https://t.me/{chat.username}/{message.message_id}"

    chat_id = str(chat.id)
    if chat_id.startswith("-100"):
        return f"https://t.me/c/{chat_id[4:]}/{message.message_id}"
    return f"telegram:chat:{chat_id}/message/{message.message_id}"


def load_publish_report_context(output_path: Path) -> tuple[dict, str]:
    """Load publish plan and title for the final report."""
    publish_plan = read_json_file(output_path / "publish-plan.json")
    metadata = read_json_file(output_path / "metadata.json")
    return publish_plan, str(metadata.get("title") or output_path.name)


def read_json_file(path: Path) -> dict:
    """Read a JSON object from disk, returning an empty object when absent."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


async def set_working_state(active: bool) -> None:
    """Track active Telegram jobs for deferred shutdown."""
    global active_job_count
    if active:
        active_job_count += 1
    else:
        active_job_count = max(0, active_job_count - 1)


async def on_startup(app: Application) -> None:
    """Log startup status."""
    bot = await app.bot.get_me()
    print(f"Logged in as Telegram bot @{bot.username} ({bot.id})", flush=True)
    if config.telegram_broadcasting_chat_id:
        print(f"Watching Telegram broadcasting chat: {config.telegram_broadcasting_chat_id}", flush=True)
    else:
        print("Watching all Telegram chats because TELEGRAM_BROADCASTING_CHAT_ID is not set", flush=True)


def install_signal_handlers(app: Application) -> None:
    """Defer shutdown while a content generation job is running."""

    def handle_shutdown(signum: int, _frame: object) -> None:
        global shutdown_requested
        signal_name = signal.Signals(signum).name
        if active_job_count > 0:
            shutdown_requested = True
            print(
                f"Shutdown signal {signal_name} received while {active_job_count} job(s) are running; "
                "deferring shutdown until the current job completes.",
                flush=True,
            )
            return

        print(f"Shutdown signal {signal_name} received; stopping Telegram bot.", flush=True)
        app.create_task(app.stop())

    for signal_number in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        with suppress(ValueError):
            signal.signal(signal_number, handle_shutdown)


def main() -> int:
    """Run the Telegram bot."""
    global application
    application = (
        ApplicationBuilder()
        .token(config.telegram_bot_token)
        .post_init(on_startup)
        .build()
    )
    install_signal_handlers(application)
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, on_message))
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

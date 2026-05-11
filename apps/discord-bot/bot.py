#!/usr/bin/env python3
"""Discord bot entrypoint for Chutzrit AI Office."""

from __future__ import annotations

import asyncio
import sys
from collections.abc import Callable
from contextlib import suppress
from pathlib import Path

import discord


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.broadcasting.pipeline.config import load_runtime_config  # noqa: E402
from agents.broadcasting.pipeline.generator import generate_content_package  # noqa: E402
from agents.broadcasting.pipeline.storage import save_content_package  # noqa: E402


def build_client() -> discord.Client:
    """Build the Discord client."""
    intents = discord.Intents.default()
    intents.message_content = True
    return discord.Client(intents=intents)


client = build_client()
config = load_runtime_config()
active_job_count = 0


@client.event
async def on_ready() -> None:
    """Log startup status."""
    if client.user:
        print(f"Logged in as {client.user} ({client.user.id})")
    print("Watching Discord team channel: broadcasting")


@client.event
async def on_message(message: discord.Message) -> None:
    """Turn broadcasting channel messages into content packages."""
    if message.author.bot:
        return

    if str(message.channel.id) != config.discord_broadcasting_channel_id:
        return

    if config.discord_allowed_user_ids and str(message.author.id) not in config.discord_allowed_user_ids:
        await message.reply("이 채널의 자동화 실행 권한이 없는 사용자입니다.", mention_author=False)
        return

    source_text = build_source_text(message)
    if not source_text.strip():
        return

    await message.reply("📝 글 작성중입니다. 입력을 분석하고 있습니다.", mention_author=False)

    progress_queue: asyncio.Queue[str | None] = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def emit_progress(update: str) -> None:
        loop.call_soon_threadsafe(progress_queue.put_nowait, update)

    worker = asyncio.create_task(asyncio.to_thread(process_message, source_text, emit_progress))
    relay = asyncio.create_task(relay_progress(message.channel, progress_queue, worker))
    typing_task = asyncio.create_task(keep_typing(message.channel, worker))
    presence_active = False

    try:
        await set_working_presence(True)
        presence_active = True
        output_path = await worker
    except Exception as exc:  # noqa: BLE001
        if not relay.done():
            relay.cancel()
            with suppress(asyncio.CancelledError):
                await relay
        if presence_active:
            await set_working_presence(False)
        await message.reply(f"❌ 초안 생성에 실패했습니다: {exc}", mention_author=False)
        return
    finally:
        if not typing_task.done():
            typing_task.cancel()
            with suppress(asyncio.CancelledError):
                await typing_task

    progress_queue.put_nowait(None)
    try:
        await relay
        await message.reply(f"✅ 콘텐츠 생성이 완료됐습니다.\n파일 {output_path}", mention_author=False)
        await send_publish_bundle(message.channel, output_path)
    finally:
        if presence_active:
            await set_working_presence(False)


def build_source_text(message: discord.Message) -> str:
    """Build source text from a Discord message and attachments."""
    attachment_urls = [attachment.url for attachment in message.attachments]
    if not attachment_urls:
        return message.content

    return message.content + "\n\n" + "\n".join(attachment_urls)


def process_message(source_text: str, progress_callback: Callable[[str], None] | None = None) -> Path:
    """Generate, save, and report a content package."""
    package = generate_content_package(source_text, config, progress_callback=progress_callback)
    output_path = save_content_package(package)
    if callable(progress_callback):
        progress_callback(f"💾 파일 저장 완료\n{output_path}")
        progress_callback("🚀 최종 배포물을 채널에 발송합니다.")
    return output_path


async def relay_progress(
    channel: discord.abc.Messageable,
    queue: asyncio.Queue[str | None],
    worker: asyncio.Task[Path],
) -> None:
    """Relay worker-thread progress updates to Discord."""
    while True:
        try:
            update = await asyncio.wait_for(queue.get(), timeout=25)
        except asyncio.TimeoutError:
            if not worker.done():
                await channel.send("⏳ 아직 작성 중입니다. 원고 생성 또는 평가 단계가 오래 걸리고 있습니다.")
                continue
            break
        if update is None:
            break

        await send_long_message(channel, update)


async def keep_typing(channel: discord.abc.Messageable, worker: asyncio.Task[Path]) -> None:
    """Keep Discord's native typing indicator visible while the job is running."""
    while not worker.done():
        async with channel.typing():
            await asyncio.sleep(8)


async def set_working_presence(active: bool) -> None:
    """Show a temporary bot activity while AI writing is running."""
    global active_job_count
    if active:
        active_job_count += 1
        if active_job_count == 1:
            await client.change_presence(
                status=discord.Status.online,
                activity=discord.Activity(type=discord.ActivityType.watching, name="글 작성중입니다"),
            )
        return

    active_job_count = max(0, active_job_count - 1)
    if active_job_count == 0:
        await client.change_presence(status=discord.Status.online, activity=None)


async def send_publish_bundle(channel: discord.abc.Messageable, output_path: Path) -> None:
    """Send generated drafts and publish the Discord newsletter immediately."""
    await send_draft_preview(channel, "📝 블로그 원고", output_path / "blog.md", attach_file=True)
    await send_draft_preview(channel, "💼 LinkedIn 원고", output_path / "linkedin.md")

    discord_text = (output_path / "discord.md").read_text(encoding="utf-8").strip()
    await channel.send("## 📣 Discord 뉴스레터 발송")
    await send_long_message(channel, discord_text)


async def send_draft_preview(
    channel: discord.abc.Messageable,
    title: str,
    path: Path,
    *,
    attach_file: bool = False,
) -> None:
    """Send one draft preview, attaching the full file when useful."""
    text = path.read_text(encoding="utf-8").strip()
    max_preview_chars = 1600
    if len(text) > max_preview_chars:
        preview = text[:max_preview_chars].rstrip() + "\n\n..."
        file = discord.File(path, filename=path.name) if attach_file else None
        content = f"## {title}\n{preview}\n\n전체 글은 첨부 파일에서 확인하세요."
        if file:
            await channel.send(content, file=file)
        else:
            await channel.send(content)
        return

    await channel.send(f"## {title}\n{text}")


async def send_long_message(channel: discord.abc.Messageable, text: str) -> None:
    """Send text while respecting Discord message length limits."""
    remaining = text.strip()
    while remaining:
        chunk = remaining[:1900]
        split_at = chunk.rfind("\n")
        if split_at > 1000 and len(remaining) > 1900:
            chunk = chunk[:split_at]
        await channel.send(chunk)
        remaining = remaining[len(chunk) :].lstrip()


def main() -> int:
    """Run the Discord bot."""
    client.run(config.discord_bot_token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Discord bot entrypoint for Chutzrit AI Office."""

from __future__ import annotations

import asyncio
import json
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
from agents.broadcasting.pipeline.progress import format_multi_platform_publish_report  # noqa: E402
from agents.broadcasting.pipeline.storage import (  # noqa: E402
    record_discord_dispatch,
    refresh_publish_files,
    save_content_package,
)
from agents.broadcasting.agents import PublishAgent  # noqa: E402


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
    print(f"Watching Discord team channel: broadcasting ({config.discord_broadcasting_channel_id})")


@client.event
async def on_message(message: discord.Message) -> None:
    """Turn broadcasting channel messages into content packages."""
    print(
        "Received message event "
        f"channel_id={message.channel.id} "
        f"author_id={message.author.id} "
        f"author_bot={message.author.bot} "
        f"content_len={len(message.content or '')} "
        f"attachments={len(message.attachments)}",
        flush=True,
    )
    if message.author.bot:
        print("Ignored message: author is a bot", flush=True)
        return

    if str(message.channel.id) != config.discord_broadcasting_channel_id:
        print(
            "Ignored message: channel mismatch "
            f"expected={config.discord_broadcasting_channel_id} actual={message.channel.id}",
            flush=True,
        )
        return

    if config.discord_allowed_user_ids and str(message.author.id) not in config.discord_allowed_user_ids:
        print(f"Ignored message: author {message.author.id} is not allowed", flush=True)
        await message.reply("이 채널의 자동화 실행 권한이 없는 사용자입니다.", mention_author=False)
        return

    source_text = build_source_text(message)
    if not source_text.strip():
        print("Ignored message: empty source text", flush=True)
        return

    print("Accepted broadcasting request", flush=True)
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
        await send_draft_previews(message.channel, output_path)
        newsletter_channel = await get_configured_channel(config.discord_newsletter_channel_id)
        discord_url = await send_discord_newsletter(newsletter_channel, output_path)
        record_discord_dispatch(output_path, discord_url)
        publish_plan, title = load_publish_report_context(output_path)
        await send_long_message(
            message.channel,
            format_multi_platform_publish_report(publish_plan, output_path=output_path, title=title),
        )
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
    print(f"Worker started source_len={len(source_text)}", flush=True)
    package = generate_content_package(source_text, config, progress_callback=progress_callback)
    print("Worker generated package", flush=True)
    output_path = save_content_package(package)
    print(f"Worker saved package output_path={output_path}", flush=True)
    package["publish_plan"] = PublishAgent(config).execute(
        package,
        output_path,
        progress_callback=progress_callback,
    )
    refresh_publish_files(package, output_path)
    print("Worker executed publish agent", flush=True)
    if callable(progress_callback):
        progress_callback(f"💾 파일 저장 완료\n{output_path}")
        progress_callback("🚀 최종 배포물을 채널에 발송합니다.")
    return output_path


def load_publish_report_context(output_path: Path) -> tuple[dict, str]:
    """Load publish plan and title for the final Discord report."""
    publish_plan = read_json_file(output_path / "publish-plan.json")
    metadata = read_json_file(output_path / "metadata.json")
    return publish_plan, str(metadata.get("title") or output_path.name)


def read_json_file(path: Path) -> dict:
    """Read a JSON object from disk, returning an empty object when absent."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


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
                print("Relay timeout: worker still running", flush=True)
                await trigger_typing_once(channel)
                await channel.send("⏳ 아직 작성 중입니다. 원고 생성 또는 평가 단계가 오래 걸리고 있습니다.")
                continue
            print("Relay timeout: worker is done", flush=True)
            break
        if update is None:
            break

        await trigger_typing_once(channel)
        await send_long_message(channel, update)


async def keep_typing(channel: discord.abc.Messageable, worker: asyncio.Task[Path]) -> None:
    """Keep Discord's native typing indicator visible while the job is running."""
    while not worker.done():
        await trigger_typing_once(channel)
        await asyncio.sleep(4)


async def trigger_typing_once(channel: discord.abc.Messageable) -> None:
    """Trigger Discord's native typing indicator without interrupting the job."""
    try:
        trigger_typing = getattr(channel, "trigger_typing", None)
        if callable(trigger_typing):
            await trigger_typing()
            return

        async with channel.typing():
            await asyncio.sleep(0.2)
    except Exception as exc:  # noqa: BLE001
        print(f"Typing indicator failed: {type(exc).__name__}", flush=True)


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


async def get_configured_channel(channel_id: str) -> discord.abc.Messageable:
    """Return a configured Discord channel for sending messages."""
    channel = client.get_channel(int(channel_id))
    if channel is None:
        channel = await client.fetch_channel(int(channel_id))
    if not hasattr(channel, "send"):
        raise RuntimeError(f"Configured Discord channel is not messageable: {channel_id}")
    return channel


async def send_draft_previews(channel: discord.abc.Messageable, output_path: Path) -> None:
    """Send internal draft previews to the operations channel."""
    await send_draft_preview(channel, "📝 블로그 원고", output_path / "blog.md", attach_file=True)
    await send_draft_preview(channel, "💼 LinkedIn 원고", output_path / "linkedin.md")


async def send_discord_newsletter(channel: discord.abc.Messageable, output_path: Path) -> str:
    """Publish the reader-facing Discord newsletter to the newsletter channel."""
    discord_text = (output_path / "discord.md").read_text(encoding="utf-8").strip()
    messages = await send_long_message(channel, discord_text)
    if messages:
        return messages[-1].jump_url
    return ""


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


async def send_long_message(channel: discord.abc.Messageable, text: str) -> list[discord.Message]:
    """Send text while respecting Discord message length limits."""
    remaining = text.strip()
    messages: list[discord.Message] = []
    while remaining:
        chunk = remaining[:1900]
        split_at = chunk.rfind("\n")
        if split_at > 1000 and len(remaining) > 1900:
            chunk = chunk[:split_at]
        messages.append(await channel.send(chunk))
        remaining = remaining[len(chunk) :].lstrip()
    return messages


def main() -> int:
    """Run the Discord bot."""
    client.run(config.discord_bot_token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

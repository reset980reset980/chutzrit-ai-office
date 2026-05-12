"""Multi-agent orchestration for the broadcasting team."""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from agents.broadcasting.agents.content_strategy import ContentStrategyAgent
from agents.broadcasting.agents.input_parser import InputParserAgent
from agents.broadcasting.agents.insight import InsightAgent
from agents.broadcasting.agents.publish import PublishAgent
from agents.broadcasting.agents.reflection import SelfReflectionAgent
from agents.broadcasting.agents.revision import RevisionAgent
from agents.broadcasting.agents.types import JSONClient
from agents.broadcasting.agents.writers.blog import BlogWriterAgent
from agents.broadcasting.agents.writers.discord import DiscordNewsletterWriterAgent
from agents.broadcasting.agents.writers.linkedin import LinkedInWriterAgent

from .config import RuntimeConfig
from .openai_client import OpenAIClient
from .progress import (
    format_final_gate_progress,
    format_insight_progress,
    format_publish_progress,
    format_reflection_progress,
    format_revision_progress,
    format_revision_start_progress,
    format_source_progress,
    format_strategy_progress,
    format_writer_progress,
)
from .quality import build_approval_state, channels_to_revise, normalize_drafts


ProgressCallback = Callable[[str], None]


def generate_content_package(
    source_text: str,
    config: RuntimeConfig,
    *,
    max_revision_loops: int = 3,
    progress_callback: ProgressCallback | None = None,
    client: JSONClient | None = None,
) -> dict[str, Any]:
    """Generate a content package through independent subagents."""
    llm_client = client or OpenAIClient(api_key=config.openai_api_key, model=config.openai_model)

    emit_progress(progress_callback, "🧾 Input Parser Agent가 입력을 분석 중입니다.")
    source_payload = InputParserAgent().run(source_text)
    emit_progress(progress_callback, format_source_progress(source_payload))

    strategy_agent = ContentStrategyAgent(llm_client)
    emit_progress(progress_callback, "🧭 Content Strategy Agent가 콘텐츠 방향을 설계합니다.")
    strategy_result = strategy_agent.run(source_payload)
    strategy = strategy_result.get("strategy", {})
    package: dict[str, Any] = {
        "title": strategy_result.get("title", ""),
        "source_summary": strategy_result.get("source_summary", ""),
        "source": source_payload,
        "strategy": strategy,
        "agent_architecture": {
            "mode": "multi_agent",
            "agents": [
                "InputParserAgent",
                "ContentStrategyAgent",
                "InsightAgent",
                "BlogWriterAgent",
                "LinkedInWriterAgent",
                "DiscordNewsletterWriterAgent",
                "SelfReflectionAgent",
                "RevisionAgent",
                "PublishAgent",
            ],
        },
    }
    emit_progress(progress_callback, format_strategy_progress(package))

    emit_progress(progress_callback, "💡 Insight Agent가 후츠릿다운 실무 관점을 정리합니다.")
    insight = InsightAgent(llm_client).run(source_payload, strategy)
    package["insight"] = insight
    emit_progress(progress_callback, format_insight_progress(package))

    emit_progress(progress_callback, "✍️ Platform Writer Agents가 병렬로 원고를 작성합니다.")
    package["drafts"] = run_writers_parallel(llm_client, source_payload, strategy, insight)
    normalize_drafts(package)
    emit_progress(progress_callback, format_writer_progress(package))

    reflection_agent = SelfReflectionAgent(llm_client)
    revision_agent = RevisionAgent(llm_client)
    revision_count = 0

    emit_progress(progress_callback, "🧪 Self Reflection Agent가 품질 평가를 시작합니다.")
    reflection = reflection_agent.run(package)
    emit_progress(progress_callback, format_reflection_progress(package, reflection, revision_count, max_revision_loops))

    while int(reflection.get("score", 0)) < 90 and revision_count < max_revision_loops:
        next_revision_count = revision_count + 1
        revise_channels = channels_to_revise(reflection)
        emit_progress(
            progress_callback,
            format_revision_start_progress(reflection, next_revision_count, max_revision_loops, revise_channels),
        )
        revisions = revision_agent.run(package, reflection, revise_channels)
        package["drafts"].update(revisions)
        normalize_drafts(package)
        revision_count = next_revision_count
        emit_progress(progress_callback, format_revision_progress(package, revision_count, max_revision_loops, revise_channels))
        emit_progress(progress_callback, f"🧪 Self Reflection Agent가 {revision_count}회차 수정본을 평가합니다.")
        reflection = reflection_agent.run(package)
        emit_progress(progress_callback, format_reflection_progress(package, reflection, revision_count, max_revision_loops))

    package["reflection"] = reflection
    package["revision_count"] = revision_count
    package["max_revision_loops"] = max_revision_loops
    package["approval"] = build_approval_state(package, config)
    emit_progress(progress_callback, format_final_gate_progress(reflection, revision_count, max_revision_loops))

    package["publish_plan"] = PublishAgent(config).run(package)
    emit_progress(progress_callback, format_publish_progress(package))
    return package


def run_writers_parallel(
    client: JSONClient,
    source: dict[str, Any],
    strategy: dict[str, Any],
    insight: dict[str, Any],
) -> dict[str, str]:
    """Run platform writers in parallel."""
    writers = {
        "blog": BlogWriterAgent(client),
        "linkedin": LinkedInWriterAgent(client),
        "discord": DiscordNewsletterWriterAgent(client),
    }
    drafts: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=len(writers)) as executor:
        futures = {
            executor.submit(writer.run, source, strategy, insight): channel
            for channel, writer in writers.items()
        }
        for future in as_completed(futures):
            channel = futures[future]
            drafts[channel] = future.result()
    return drafts


def emit_progress(progress_callback: ProgressCallback | None, message: str) -> None:
    """Emit a progress message when a callback is available."""
    if progress_callback:
        progress_callback(message)

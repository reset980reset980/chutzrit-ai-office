"""Broadcasting content generation workflow."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from .config import RuntimeConfig
from .openai_client import OpenAIClient
from .prompts import build_generation_prompt, build_reflection_prompt, build_revision_prompt
from .source import parse_source_context


ProgressCallback = Callable[[str], None]


def generate_content_package(
    source_text: str,
    config: RuntimeConfig,
    *,
    max_revision_loops: int = 3,
    progress_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    """Generate drafts once, then evaluate them against the quality gate."""
    client = OpenAIClient(api_key=config.openai_api_key, model=config.openai_model)
    emit_progress(progress_callback, "🧾 Input Parser가 입력을 분석 중입니다.")
    source = parse_source_context(source_text)
    source_payload = {
        "raw_text": source.raw_text,
        "urls": source.urls,
        "link_summaries": source.link_summaries,
    }
    emit_progress(progress_callback, format_source_progress(source_payload))

    emit_progress(progress_callback, "✍️ 전략, 인사이트, 블로그, LinkedIn, Discord 뉴스레터를 작성 중입니다.")
    package = client.create_json(build_generation_prompt(source))
    package["source"] = source_payload
    normalize_drafts(package)
    emit_progress(progress_callback, format_strategy_progress(package))
    emit_progress(progress_callback, format_insight_progress(package))
    emit_progress(progress_callback, format_writer_progress(package))
    emit_progress(progress_callback, "🧪 Self Reflection Agent가 품질 평가를 시작합니다.")

    reflection = normalize_reflection(client.create_json(build_reflection_prompt(package), max_output_tokens=4000))
    reflection = enforce_style_gates(package, reflection)
    revision_count = 0
    emit_progress(progress_callback, format_reflection_progress(package, reflection, revision_count, max_revision_loops))

    while int(reflection.get("score", 0)) < 90 and revision_count < max_revision_loops:
        next_revision_count = revision_count + 1
        emit_progress(
            progress_callback,
            format_revision_start_progress(reflection, next_revision_count, max_revision_loops),
        )
        package = client.create_json(build_revision_prompt(package, reflection))
        package["source"] = source_payload
        normalize_drafts(package)
        revision_count = next_revision_count
        emit_progress(progress_callback, format_revision_progress(package, revision_count, max_revision_loops))
        emit_progress(progress_callback, f"🧪 Self Reflection Agent가 {revision_count}회차 수정본을 평가합니다.")
        reflection = normalize_reflection(client.create_json(build_reflection_prompt(package), max_output_tokens=4000))
        reflection = enforce_style_gates(package, reflection)
        emit_progress(progress_callback, format_reflection_progress(package, reflection, revision_count, max_revision_loops))

    package["reflection"] = reflection
    package["revision_count"] = revision_count
    package["source"] = source_payload
    normalize_drafts(package)
    package["approval"] = build_approval_state(package, config)
    emit_progress(progress_callback, format_final_gate_progress(reflection, revision_count, max_revision_loops))
    return package


def emit_progress(progress_callback: ProgressCallback | None, message: str) -> None:
    """Emit a progress message when a callback is available."""
    if progress_callback:
        progress_callback(message)


def format_source_progress(source_payload: dict[str, Any]) -> str:
    """Format source parsing results for Discord."""
    raw_text = str(source_payload.get("raw_text", "")).strip()
    urls = source_payload.get("urls", [])
    link_summaries = source_payload.get("link_summaries", [])
    input_type = "링크 + 메모" if urls and raw_text else "링크" if urls else "메모"
    summary_status = f"{len(link_summaries)}개 수집" if urls else "해당 없음"
    return (
        "## 🧾 Input Parser 완료\n"
        f"입력 유형 {input_type}\n"
        f"감지한 링크 {len(urls)}개\n"
        f"링크 메타데이터 {summary_status}\n"
        f"입력 미리보기 {compact_text(raw_text, 180)}"
        f"{format_link_summary_progress(link_summaries)}"
    )


def format_link_summary_progress(link_summaries: Any) -> str:
    """Format fetched link summaries for the Input Parser Discord message."""
    if not isinstance(link_summaries, list) or not link_summaries:
        return ""

    lines = ["\n\n링크 핵심 내용"]
    for index, summary in enumerate(link_summaries[:3], start=1):
        parsed = parse_link_summary(str(summary))
        title = parsed.get("제목") or "제목 없음"
        core = parsed.get("핵심 내용") or parsed.get("설명") or "핵심 내용 추출 실패"
        url = parsed.get("url") or ""
        lines.append(f"{index}. {compact_text(title, 90)}")
        lines.append(f"   - {compact_text(core, 220)}")
        if url:
            lines.append(f"   - {url}")
    return "\n".join(lines)


def parse_link_summary(summary: str) -> dict[str, str]:
    """Parse link summary text into display fields."""
    result: dict[str, str] = {}
    lines = [line.strip() for line in summary.splitlines() if line.strip()]
    if lines:
        result["url"] = lines[0]
    for line in lines[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def format_strategy_progress(package: dict[str, Any]) -> str:
    """Format content strategy results for Discord."""
    strategy = package.get("strategy", {})
    directions = strategy.get("platform_directions", {})
    return (
        "## 🧭 Content Strategy Agent 완료\n"
        f"핵심 메시지 {compact_text(strategy.get('core_message', ''), 180)}\n"
        f"타깃 독자 {compact_text(strategy.get('target_reader', ''), 140)}\n"
        f"글의 주장 {compact_text(strategy.get('claim', ''), 180)}\n\n"
        "플랫폼 방향\n"
        f"- 블로그 {compact_text(directions.get('blog', ''), 120)}\n"
        f"- LinkedIn {compact_text(directions.get('linkedin', ''), 120)}\n"
        f"- Discord {compact_text(directions.get('discord', ''), 120)}"
    )


def format_insight_progress(package: dict[str, Any]) -> str:
    """Format insight results for Discord."""
    insight = package.get("insight", {})
    practical_points = insight.get("practical_points", [])
    examples = insight.get("examples", [])
    cautions = insight.get("cautions", [])
    return (
        "## 💡 Insight Agent 완료\n"
        f"관점 {compact_text(insight.get('chutzrit_insight', ''), 220)}\n\n"
        "적용 포인트\n"
        f"{format_short_bullets(practical_points, '없음')}\n\n"
        "예시와 주의점\n"
        f"- 예시 {compact_text(first_item(examples), 120)}\n"
        f"- 주의 {compact_text(first_item(cautions), 120)}"
    )


def format_writer_progress(package: dict[str, Any]) -> str:
    """Format platform writer results for Discord."""
    drafts = package.get("drafts", {})
    blog = str(drafts.get("blog", "")).strip()
    linkedin = str(drafts.get("linkedin", "")).strip()
    discord = str(drafts.get("discord", "")).strip()
    return (
        "## ✍️ Platform Writer Agents 완료\n"
        f"- 블로그 {len(blog)}자 / 첫 줄 {compact_text(first_line(blog), 90)}\n"
        f"- LinkedIn {len(linkedin)}자 / 첫 줄 {compact_text(first_line(linkedin), 90)}\n"
        f"- Discord 뉴스레터 {len(discord)}자 / 첫 줄 {compact_text(first_line(discord), 90)}"
    )


def format_reflection_progress(
    package: dict[str, Any],
    reflection: dict[str, Any],
    revision_count: int,
    max_revision_loops: int,
) -> str:
    """Format quality reflection for Discord progress updates."""
    score = reflection.get("score", "unknown")
    status = "통과" if reflection.get("passed") else "검토 필요"
    channel_scores = reflection.get("channel_scores", {})
    strengths = reflection.get("strengths", [])
    problems = reflection.get("problems", [])
    revision_instructions = reflection.get("revision_instructions", [])
    channel_score_text = ", ".join(
        f"{name} {value}" for name, value in channel_scores.items()
    ) or "없음"

    def bullet_list(items: Any, fallback: str) -> str:
        if not isinstance(items, list) or not items:
            return f"- {fallback}"
        return "\n".join(f"- {str(item)}" for item in items[:3])

    return (
        "## 🧪 콘텐츠배포팀 평가 결과\n"
        f"상태 {status}\n"
        f"제목 {package.get('title', '')}\n"
        f"총점 {score}\n"
        f"채널 점수 {channel_score_text}\n"
        f"수정 루프 {revision_count}/{max_revision_loops}회\n\n"
        "주요 피드백\n"
        f"{bullet_list(problems, '없음')}\n\n"
        "수정할 사항\n"
        f"{bullet_list(revision_instructions, '없음')}\n\n"
        "유지할 점\n"
        f"{bullet_list(strengths, '없음')}"
    )


def format_revision_start_progress(
    reflection: dict[str, Any],
    revision_count: int,
    max_revision_loops: int,
) -> str:
    """Format revision start progress with concrete feedback."""
    problems = reflection.get("problems", [])
    revision_instructions = reflection.get("revision_instructions", [])
    return (
        f"## 🔁 Revision Agent {revision_count}/{max_revision_loops}회차 시작\n"
        f"현재 점수 {reflection.get('score', 'unknown')}\n\n"
        "이번 수정에서 반영할 피드백\n"
        f"{format_short_bullets(problems, '없음')}\n\n"
        "수정 지시\n"
        f"{format_short_bullets(revision_instructions, '없음')}"
    )


def format_revision_progress(package: dict[str, Any], revision_count: int, max_revision_loops: int) -> str:
    """Format revision completion progress."""
    drafts = package.get("drafts", {})
    return (
        f"## 🛠️ Revision Agent {revision_count}/{max_revision_loops}회차 완료\n"
        f"제목 {package.get('title', '')}\n"
        f"- 블로그 첫 줄 {compact_text(first_line(str(drafts.get('blog', ''))), 100)}\n"
        f"- LinkedIn 첫 줄 {compact_text(first_line(str(drafts.get('linkedin', ''))), 100)}\n"
        f"- Discord 첫 줄 {compact_text(first_line(str(drafts.get('discord', ''))), 100)}"
    )


def format_final_gate_progress(
    reflection: dict[str, Any],
    revision_count: int,
    max_revision_loops: int,
) -> str:
    """Format final gate decision."""
    if reflection.get("passed"):
        return (
            "## ✅ Final Quality Gate 통과\n"
            f"최종 점수 {reflection.get('score', 'unknown')}\n"
            f"수정 루프 {revision_count}/{max_revision_loops}회\n"
            "파일 저장과 Discord 자동 발송을 준비합니다."
        )
    return (
        "## ⚠️ Final Quality Gate 기준 미달\n"
        f"최종 점수 {reflection.get('score', 'unknown')}\n"
        f"수정 루프 {revision_count}/{max_revision_loops}회\n"
        "최대 수정 루프를 모두 사용했습니다. 현재 결과를 저장하고 Discord에 발송합니다."
    )


def compact_text(value: Any, limit: int = 120) -> str:
    """Compact text for Discord progress messages."""
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if not text:
        return "없음"
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def first_line(value: str) -> str:
    """Return the first non-empty line."""
    for line in value.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def first_item(value: Any) -> str:
    """Return the first list item as text."""
    if isinstance(value, list) and value:
        return str(value[0])
    return ""


def format_short_bullets(value: Any, fallback: str) -> str:
    """Format up to three bullet items."""
    if not isinstance(value, list) or not value:
        return f"- {fallback}"
    return "\n".join(f"- {compact_text(item, 120)}" for item in value[:3])


def normalize_drafts(package: dict[str, Any]) -> None:
    """Apply deterministic cleanup for channel-specific formatting."""
    drafts = package.get("drafts")
    if not isinstance(drafts, dict):
        return

    urls = package.get("source", {}).get("urls", [])
    discord = str(drafts.get("discord", ""))
    if not urls:
        discord = re.sub(
            r"\n+\*\*참고\s*링크\*\*\s*\n(?:[-*]\s*.*\n?)*\s*$",
            "",
            discord,
            flags=re.MULTILINE,
        ).strip()
        drafts["discord"] = discord
    linkedin = str(drafts.get("linkedin", ""))
    drafts["linkedin"] = linkedin.replace("{BLOG_URL}", "[블로그 링크]").replace("BLOG_URL", "[블로그 링크]")


def build_approval_state(package: dict[str, Any], config: RuntimeConfig) -> dict[str, Any]:
    """Build approval state for generated platform drafts."""
    score = int(package.get("reflection", {}).get("score", 0))
    return {
        "quality_score": score,
        "quality_passed": score >= 90,
        "channels": {
            "blog": "auto_dispatch_to_discord",
            "linkedin": "auto_dispatch_to_discord",
            "discord": "auto_publish_to_discord",
        },
    }


def normalize_reflection(reflection: dict[str, Any]) -> dict[str, Any]:
    """Normalize model-provided reflection fields against the project quality gate."""
    score = int(reflection.get("score", 0))
    reflection["score"] = score
    reflection["passed"] = score >= 90
    if score >= 90:
        reflection["publish_status"] = "자동 발송 가능"
    elif score >= 80:
        reflection["publish_status"] = "수정 필요"
    else:
        reflection["publish_status"] = "재작성 필요"
    return reflection


def enforce_style_gates(package: dict[str, Any], reflection: dict[str, Any]) -> dict[str, Any]:
    """Apply deterministic project-specific gates before publishing decisions."""
    drafts = package.get("drafts", {})
    blog = str(drafts.get("blog", ""))
    linkedin = str(drafts.get("linkedin", ""))
    discord = str(drafts.get("discord", ""))
    public_text = f"{blog}\n{linkedin}"
    urls = package.get("source", {}).get("urls", [])
    github_urls = [url for url in urls if "github.com" in url.lower()]
    score = int(reflection.get("score", 0))
    problems = list(reflection.get("problems", []))
    revision_instructions = list(reflection.get("revision_instructions", []))

    def penalize(limit: int, problem: str, instruction: str) -> None:
        nonlocal score
        if problem not in problems:
            problems.append(problem)
        if instruction not in revision_instructions:
            revision_instructions.append(instruction)
        score = min(score, limit)

    if re.search(r"(합니다|습니다|입니다|됩니다|하세요|드립니다|바랍니다)", blog):
        penalize(
            79,
            "블로그 초안에 존댓말 종결이 남아 있어 후츠릿 블로그 문체와 맞지 않는다.",
            "블로그를 전부 문어체 평서형 반말로 다시 쓰고 존댓말 종결을 제거하라.",
        )

    casual_endings = (
        r"(?:하면|해도|해야|안\s*해도)\s*돼[.?!\s]",
        r"해\s*봐[.?!\s]",
        r"해봐[.?!\s]",
        r"거야[.?!\s]",
        r"거든[.?!\s]",
        r"잖아[.?!\s]",
        r"정해둬[.?!\s]",
        r"확인해[.?!\s]",
    )
    if re.search("|".join(casual_endings), blog):
        penalize(
            79,
            "블로그 초안에 대화체 종결이 남아 있어 후츠릿 블로그 문체와 맞지 않는다.",
            "블로그를 '다/이다/한다/된다/있다/없다' 중심의 문어체 평서형 반말로 다시 써라.",
        )

    if len(re.findall(r"^#{2,3}\s+\S+", blog, re.MULTILINE)) < 3:
        penalize(
            84,
            "블로그 초안이 충분히 구조화되지 않았다.",
            "블로그에 Markdown 소제목을 3개 이상 사용하고 줄글 문단을 쪼개라.",
        )

    if urls and ("참고자료" not in blog or not any(url in blog for url in urls)):
        penalize(
            84,
            "입력에 참고 링크가 있지만 블로그 맨 아래 참고자료 섹션이 부족하다.",
            "블로그 마지막에 '## 참고자료' 섹션을 만들고 입력 링크를 모두 정리하라.",
        )

    if github_urls and not any(url in blog for url in github_urls):
        penalize(
            86,
            "입력에 GitHub 링크가 있지만 기술 구현형 블로그에 저장소 링크가 반영되지 않았다.",
            "입력 GitHub 링크를 예제 코드 또는 GitHub 저장소 링크로 자연스럽게 넣어라.",
        )

    if not github_urls and re.search(r"https?://(?:www\.)?github\.com/\S+", blog, re.IGNORECASE):
        penalize(
            86,
            "입력에 없는 GitHub 링크가 블로그에 생성되었다.",
            "입력에 GitHub 링크가 없으면 GitHub 링크를 만들거나 추정하지 마라.",
        )

    if re.search(r"(\[?후츠릿(의)? 인사이트\]?|실무 적용 포인트|핵심 메시지:)", public_text):
        penalize(
            79,
            "공개 초안에 내부 라벨형 문구가 노출되어 있다.",
            "공개 초안에서는 라벨을 제거하고 결론 문장 자체로 관점을 전달하라.",
        )

    if not re.search(r"(핵심은|문제는|차이는|착각|갈린다|기준은|설계|검증|운영)", public_text):
        penalize(
            88,
            "후츠릿다운 구조적 판단 문장이 약하다.",
            "겉보기 해석과 실제 구조 변화를 대비시키고, 실무자가 가져야 할 판단 기준으로 마무리하라.",
        )

    if "블로그" not in linkedin or not re.search(r"(\[블로그 링크\]|https?://)", linkedin):
        penalize(
            88,
            "LinkedIn 초안에 블로그 전문 링크 유입 장치가 없다.",
            "LinkedIn 마지막에 블로그 전문 링크 또는 [블로그 링크] 자리표시자를 넣어라.",
        )

    if not re.search(r"(습니다|입니다|됩니다|하세요|드립니다|합니다)", linkedin):
        penalize(
            88,
            "LinkedIn 초안이 존댓말 기준을 충분히 만족하지 않는다.",
            "LinkedIn은 제목을 제외한 본문을 존댓말로 작성하라.",
        )

    if re.search(r"블로그\s*전문\s*:", linkedin):
        penalize(
            88,
            "LinkedIn 초안에 불필요한 콜론이 남아 있다.",
            "LinkedIn 링크 유도 문구는 '블로그 전문 [블로그 링크]'처럼 콜론 없이 작성하라.",
        )

    if re.search(r"(핵심\s*요약|왜\s*중요한가|바로\s*해볼\s*것)", discord):
        penalize(
            88,
            "Discord 뉴스레터에 고정 라벨형 제목이 노출되어 있다.",
            "Discord 뉴스레터는 제목 다음에 자연스러운 핵심 문단과 짧은 실행 목록으로 작성하라.",
        )

    if not re.match(r"^\s*#{1,2}\s+\S+", discord):
        penalize(
            88,
            "Discord 뉴스레터에 Markdown 제목이 없다.",
            "Discord 뉴스레터 맨 위에 '## 제목' 형식의 제목을 넣어라.",
        )

    if not re.search(r"(습니다|세요|드립니다|합니다)", discord):
        penalize(
            88,
            "Discord 뉴스레터가 존댓말 기준을 충분히 만족하지 않는다.",
            "Discord 뉴스레터는 타깃 독자에게 보내는 메시지이므로 존댓말로 작성하라.",
        )

    if urls and ("참고 링크" not in discord or not any(url in discord for url in urls)):
        penalize(
            88,
            "입력에 참고 링크가 있지만 Discord 뉴스레터 하단 참고 링크가 부족하다.",
            "Discord 뉴스레터 맨 아래에 '참고 링크' 섹션을 만들고 입력 링크를 정리하라.",
        )

    if not urls and re.search(r"(참고\s*링크|참고\s*자료는\s*없습니다|참고자료\s*없음)", discord):
        penalize(
            88,
            "입력에 참고 링크가 없는데 Discord 뉴스레터에 참고 링크 섹션이 생성되었다.",
            "참고 링크가 없으면 Discord 뉴스레터에 참고 링크 섹션을 만들지 마라.",
        )

    if re.search(r"\{BLOG_URL\}|BLOG_URL", discord):
        penalize(
            88,
            "Discord 뉴스레터에 블로그 URL placeholder가 들어갔다.",
            "Discord 뉴스레터에는 {BLOG_URL} placeholder를 넣지 마라.",
        )

    channel_scores = reflection.get("channel_scores", {})
    if isinstance(channel_scores, dict):
        low_channels = [
            name
            for name, channel_score in channel_scores.items()
            if isinstance(channel_score, int | float) and int(channel_score) < 90
        ]
        if low_channels:
            joined_channels = ", ".join(low_channels)
            penalize(
                89,
                f"채널별 품질 점수가 기준 미만이다: {joined_channels}.",
                "90점 미만 채널은 해당 플랫폼 문법과 훅을 다시 강화하라.",
            )

    reflection["score"] = score
    reflection["passed"] = score >= 90
    reflection["problems"] = problems
    reflection["revision_instructions"] = revision_instructions
    if score >= 90:
        reflection["publish_status"] = "자동 발송 가능"
    elif score >= 80:
        reflection["publish_status"] = "수정 필요"
    else:
        reflection["publish_status"] = "재작성 필요"
    return reflection

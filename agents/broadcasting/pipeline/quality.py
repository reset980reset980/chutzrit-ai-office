"""Quality gates and deterministic cleanup for broadcasting packages."""

from __future__ import annotations

import re
from typing import Any

from .config import RuntimeConfig


CHANNELS = ("blog", "linkedin", "telegram")


def normalize_drafts(package: dict[str, Any]) -> None:
    """Apply deterministic cleanup for channel-specific formatting."""
    drafts = package.get("drafts")
    if not isinstance(drafts, dict):
        return

    urls = package.get("source", {}).get("urls", [])
    telegram = str(drafts.get("telegram", drafts.get("discord", "")))
    if not urls:
        telegram = re.sub(
            r"\n+\*\*참고\s*링크\*\*\s*\n(?:[-*]\s*.*\n?)*\s*$",
            "",
            telegram,
            flags=re.MULTILINE,
        ).strip()
        drafts["telegram"] = telegram
    linkedin = str(drafts.get("linkedin", ""))
    drafts["linkedin"] = linkedin.replace("{BLOG_URL}", "[블로그 링크]").replace("BLOG_URL", "[블로그 링크]")


def build_approval_state(package: dict[str, Any], config: RuntimeConfig) -> dict[str, Any]:
    """Build approval state for generated platform drafts."""
    score = int(package.get("reflection", {}).get("score", 0))
    return {
        "quality_score": score,
        "quality_passed": score >= 90,
        "public_content_require_approval": config.public_content_require_approval,
        "channels": {
            "blog": "auto_dispatch_to_telegram",
            "linkedin": "auto_dispatch_to_telegram",
            "telegram": "auto_publish_to_telegram",
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


def channels_to_revise(reflection: dict[str, Any]) -> list[str]:
    """Return the channels that should be revised after a failed reflection."""
    channel_scores = reflection.get("channel_scores", {})
    if isinstance(channel_scores, dict):
        low_channels = [
            channel
            for channel, score in channel_scores.items()
            if channel in CHANNELS and isinstance(score, int | float) and int(score) < 90
        ]
        if low_channels:
            return low_channels
    return list(CHANNELS)


def enforce_style_gates(package: dict[str, Any], reflection: dict[str, Any]) -> dict[str, Any]:
    """Apply deterministic project-specific gates before publishing decisions."""
    drafts = package.get("drafts", {})
    blog = str(drafts.get("blog", ""))
    linkedin = str(drafts.get("linkedin", ""))
    telegram = str(drafts.get("telegram", drafts.get("discord", "")))
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

    if re.search(r"(핵심\s*요약|왜\s*중요한가|바로\s*해볼\s*것)", telegram):
        penalize(
            88,
            "Telegram 뉴스레터에 고정 라벨형 제목이 노출되어 있다.",
            "Telegram 뉴스레터는 제목 다음에 자연스러운 핵심 문단과 짧은 실행 목록으로 작성하라.",
        )

    if not re.match(r"^\s*#{1,2}\s+\S+", telegram):
        penalize(
            88,
            "Telegram 뉴스레터에 Markdown 제목이 없다.",
            "Telegram 뉴스레터 맨 위에 '## 제목' 형식의 제목을 넣어라.",
        )

    if not re.search(r"(습니다|세요|드립니다|합니다)", telegram):
        penalize(
            88,
            "Telegram 뉴스레터가 존댓말 기준을 충분히 만족하지 않는다.",
            "Telegram 뉴스레터는 타깃 독자에게 보내는 메시지이므로 존댓말로 작성하라.",
        )

    if urls and ("참고 링크" not in telegram or not any(url in telegram for url in urls)):
        penalize(
            88,
            "입력에 참고 링크가 있지만 Telegram 뉴스레터 하단 참고 링크가 부족하다.",
            "Telegram 뉴스레터 맨 아래에 '참고 링크' 섹션을 만들고 입력 링크를 정리하라.",
        )

    if not urls and re.search(r"(참고\s*링크|참고\s*자료는\s*없습니다|참고자료\s*없음)", telegram):
        penalize(
            88,
            "입력에 참고 링크가 없는데 Telegram 뉴스레터에 참고 링크 섹션이 생성되었다.",
            "참고 링크가 없으면 Telegram 뉴스레터에 참고 링크 섹션을 만들지 마라.",
        )

    if re.search(r"\{BLOG_URL\}|BLOG_URL", telegram):
        penalize(
            88,
            "Telegram 뉴스레터에 블로그 URL placeholder가 들어갔다.",
            "Telegram 뉴스레터에는 {BLOG_URL} placeholder를 넣지 마라.",
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

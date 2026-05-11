"""Prompt builders for the broadcasting pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .source import SourceContext


REFERENCE_FILES = (
    "docs/strategy/persona.md",
    "docs/strategy/audience.md",
    "docs/strategy/content-positioning.md",
    "docs/strategy/channel-style-guide.md",
    "agents/broadcasting/prompts/templates/blog.md",
    "agents/broadcasting/prompts/templates/linkedin.md",
    "agents/broadcasting/prompts/templates/discord.md",
)


def load_reference_context() -> str:
    """Load strategy and template references for content generation."""
    chunks: list[str] = []
    for relative_path in REFERENCE_FILES:
        path = PROJECT_ROOT / relative_path
        if not path.exists():
            continue
        chunks.append(f"--- {relative_path} ---\n{path.read_text(encoding='utf-8')}")
    return "\n\n".join(chunks)


def build_generation_prompt(source: SourceContext) -> str:
    """Build the initial content generation prompt."""
    return f"""
너는 후츠릿 AI 오피스의 콘텐츠배포팀이다.
아래 참고 문서와 사용자 입력을 바탕으로 블로그, LinkedIn, Discord 뉴스레터 초안을 생성한다.

중요 규칙:
- 한국어로 작성한다.
- 평가 후 여러 번 수정할 것을 전제로 쓰지 않는다. 첫 생성부터 바로 검토 가능한 최종 초안 품질로 작성한다.
- 단순 요약이 아니라 후츠릿다운 실무 인사이트를 추가한다.
- 블로그는 입력 성격에 따라 구현형, 개념 설명형, 인사이트형 중 적절한 형태를 선택한다.
- 블로그 초안은 무조건 문어체 평서형 반말로 쓴다.
- 블로그 문장 종결은 "다", "이다", "한다", "된다", "있다", "없다" 중심으로 쓴다.
- 블로그에는 "합니다", "습니다", "입니다", "됩니다", "하세요" 같은 존댓말 종결을 쓰지 않는다.
- 블로그에는 "하면 돼", "해봐", "거야", "거든", "잖아", "~해", "~돼" 같은 대화체 종결을 쓰지 않는다.
- 블로그 초안은 줄글로 쓰지 않고 Markdown 제목과 소제목을 사용해 구조화한다.
- 입력에 참고 링크가 있으면 블로그 맨 마지막에 "## 참고자료" 섹션으로 정리한다.
- 입력에 GitHub 링크가 있으면 기술 구현형 블로그에 GitHub 저장소 링크를 넣고, 없으면 GitHub 링크를 추정하지 않는다.
- 공개 초안에는 "[후츠릿 인사이트]", "후츠릿의 인사이트", "실무 적용 포인트" 같은 라벨형 문구를 쓰지 않는다.
- 인사이트는 일반론이 아니라 "겉보기 해석 -> 더 중요한 구조 변화 -> 실무자가 가져야 할 판단 기준"으로 뾰족하게 만든다.
- LinkedIn은 300~800자 중심으로 전문성과 관점을 보여준다.
- LinkedIn과 Discord 뉴스레터는 존댓말로 쓴다.
- LinkedIn 첫 문장은 설명형이 아니라 대비형 훅으로 쓴다.
- LinkedIn은 맨 위에 간결한 제목 한 줄을 두고, 블로그에서 뽑은 통찰을 구조화해서 압축한다.
- LinkedIn 본문에는 실무 판단 기준을 한 줄로 넣는다.
- LinkedIn 마지막에는 블로그 링크 자리를 넣는다. 아직 배포 전이면 [블로그 링크] 자리표시자를 사용한다.
- [블로그 링크] 자리표시자는 정상 유입 장치로 간주하며 평가에서 감점하지 않는다.
- LinkedIn에서 "블로그 전문:"처럼 불필요한 콜론을 쓰지 않는다. "블로그 전문 [블로그 링크]"처럼 쓴다.
- Discord 초안은 타깃 독자용 뉴스레터다. 존댓말, Markdown 제목, 짧은 구조를 지킨다.
- Discord 뉴스레터는 "핵심 요약", "왜 중요한가", "바로 해볼 것" 같은 고정 라벨을 쓰지 않는다.
- Discord 뉴스레터는 제목 다음에 자연스러운 핵심 문단과 짧은 실행 목록만 둔다.
- 입력에 참고 링크가 있으면 Discord 뉴스레터 맨 아래에 "참고 링크"로 정리한다.
- 입력에 참고 링크가 없으면 Discord 뉴스레터에 "참고 링크" 섹션이나 "참고 자료는 없습니다" 문구를 쓰지 않는다.
- Discord 뉴스레터에는 {{BLOG_URL}} placeholder를 넣지 않는다.
- 블로그 원고, LinkedIn 원고, Discord 뉴스레터는 생성 후 Discord 채널에 자동 발송되는 상태로 둔다.

반드시 JSON 객체만 반환한다. 코드블록을 쓰지 않는다.

JSON 형식:
{{
  "title": "콘텐츠 패키지 제목",
  "source_summary": "입력 요약",
  "strategy": {{
    "core_message": "핵심 메시지",
    "target_reader": "타깃 독자",
    "claim": "글의 주장",
    "platform_directions": {{
      "blog": "블로그 방향",
      "linkedin": "LinkedIn 방향",
      "discord": "Discord 뉴스레터 방향"
    }}
  }},
  "insight": {{
    "chutzrit_insight": "후츠릿 인사이트",
    "practical_points": ["실무 적용 포인트"],
    "examples": ["예시"],
    "cautions": ["주의점"]
  }},
  "drafts": {{
    "blog": "블로그 초안",
    "linkedin": "LinkedIn 초안",
    "discord": "Discord 뉴스레터 초안"
  }}
}}

[참고 문서]
{load_reference_context()}

{source.to_prompt_text()}
""".strip()


def build_reflection_prompt(package: dict[str, Any]) -> str:
    """Build the self-reflection prompt."""
    return f"""
너는 후츠릿 콘텐츠의 Self Reflection Agent다.
아래 콘텐츠 패키지를 100점 만점으로 평가한다.

평가 기준:
- 후츠릿 관점 20
- 실무 적용성 20
- 메시지 선명도 15
- 플랫폼 적합성 15
- 후킹력 10
- 구체성 10
- 신뢰성 5
- CTA 명확성 5

하드 게이트:
- 블로그가 문어체 평서형 반말이 아니면 80점 미만으로 평가한다.
- 블로그에 "하면 돼", "해봐", "거야", "거든", "잖아" 같은 대화체 종결이 있으면 80점 미만으로 평가한다.
- 블로그가 소제목 없이 줄글이면 85점 미만으로 평가한다.
- 입력에 참고 링크가 있는데 블로그 맨 아래 참고자료 섹션이 없으면 85점 미만으로 평가한다.
- LinkedIn에 블로그 전문 링크 또는 [블로그 링크] 자리표시자가 없으면 88점 미만으로 평가한다.
- 실제 발행 링크가 없는 테스트 생성에서는 LinkedIn의 [블로그 링크] 자리표시자를 정상 유입 장치로 간주한다.
- Discord 뉴스레터에 "핵심 요약", "왜 중요한가", "바로 해볼 것" 같은 고정 라벨이 보이면 88점 미만으로 평가한다.
- Discord 뉴스레터에 Markdown 제목이 없거나 참고 링크가 누락되면 88점 미만으로 평가한다.
- 단, 입력에 참고 링크가 없으면 블로그 참고자료 섹션과 Discord 참고 링크 섹션이 없어도 감점하지 않는다.
- 공개 초안에 "[후츠릿 인사이트]", "후츠릿의 인사이트", "실무 적용 포인트" 같은 라벨이 보이면 80점 미만으로 평가한다.
- 일반론 위주이고 구조적 해석이나 실무 판단 기준이 약하면 88점 미만으로 평가한다.

반드시 JSON 객체만 반환한다. 코드블록을 쓰지 않는다.

JSON 형식:
{{
  "score": 0,
  "passed": false,
  "channel_scores": {{
    "blog": 0,
    "linkedin": 0,
    "discord": 0
  }},
  "strengths": ["유지할 부분"],
  "problems": ["고쳐야 할 부분"],
  "revision_instructions": ["수정 지시"],
  "publish_status": "자동 발송 가능"
}}

[콘텐츠 패키지]
{json.dumps(package, ensure_ascii=False, indent=2)}
""".strip()


def build_revision_prompt(package: dict[str, Any], reflection: dict[str, Any]) -> str:
    """Build the revision prompt."""
    return f"""
너는 후츠릿 콘텐츠 Revision Agent다.
Self Reflection 피드백을 반영해 콘텐츠 패키지를 수정한다.

규칙:
- 기존 JSON 형식을 유지한다.
- 한국어로 작성한다.
- 후츠릿다운 관점, 실무 적용성, 메시지 선명도를 강화한다.
- 블로그는 무조건 문어체 평서형 반말로 다시 쓴다.
- 블로그 문장 종결은 "다", "이다", "한다", "된다", "있다", "없다" 중심으로 쓴다.
- 블로그에서 "하면 돼", "해봐", "거야", "거든", "잖아" 같은 대화체 종결을 제거한다.
- 블로그는 Markdown 소제목으로 구조화한다.
- 참고 링크가 있으면 블로그 맨 마지막에 "## 참고자료" 섹션을 넣는다.
- 공개 초안에는 "[후츠릿 인사이트]", "후츠릿의 인사이트", "실무 적용 포인트" 같은 라벨을 쓰지 않는다.
- 결론은 라벨이 아니라 임팩트 있는 문장으로 닫는다.
- LinkedIn에는 블로그 전문 링크 또는 [블로그 링크] 자리표시자를 넣는다.
- Discord 뉴스레터는 Markdown 제목, 존댓말, 참고 링크 하단 배치를 지킨다.
- Discord 뉴스레터에는 "핵심 요약", "왜 중요한가", "바로 해볼 것" 같은 고정 라벨을 넣지 않는다.
- 입력에 참고 링크가 없으면 Discord 뉴스레터에 참고 링크 섹션을 만들지 않는다.
- Discord 뉴스레터에는 {{BLOG_URL}} placeholder를 넣지 않는다.
- 블로그, LinkedIn, Discord 뉴스레터를 모두 수정한다.
- JSON 객체만 반환한다. 코드블록을 쓰지 않는다.

[기존 콘텐츠 패키지]
{json.dumps(package, ensure_ascii=False, indent=2)}

[Self Reflection]
{json.dumps(reflection, ensure_ascii=False, indent=2)}
""".strip()

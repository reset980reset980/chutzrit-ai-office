---
name: chutzrit-broadcasting
description: Use when generating, revising, evaluating, or implementing Chutzrit broadcasting content for blog, LinkedIn, or Discord. Enforces Korean blog 문어체 평서형 반말, structured markdown, sharp AI automation/developer insight, and no visible internal labels like "[후츠릿 인사이트]".
---

# Chutzrit Broadcasting

Use this skill for 콘텐츠배포팀 work: source memo/link intake, blog/LinkedIn/Discord draft generation, revision, quality scoring, and pipeline changes that affect those outputs.

## Input Parser Rules

- Treat every normal Discord message in the `broadcasting` channel as a content request.
- If URLs are present, detect them automatically and fetch lightweight metadata.
- For each link, summarize title, description, and a short 핵심 내용 before generation.
- Send the Input Parser Discord progress message with a `링크 핵심 내용` section when links are present.
- Preserve the user's own note/thought as the primary angle when a link and user comment appear together.
- Do not present link metadata as final insight; use it as source context for Strategy and Insight Agents.

## Required References

Before changing generation behavior or judging quality, read the relevant files:

- `docs/strategy/persona.md`
- `docs/strategy/audience.md`
- `docs/strategy/content-positioning.md`
- `docs/strategy/channel-style-guide.md`
- `agents/broadcasting/prompts/templates/blog.md`
- `agents/broadcasting/prompts/templates/linkedin.md`
- `agents/broadcasting/prompts/templates/discord.md`

## Output Rules

- Generate all MVP channels: blog, LinkedIn, Discord newsletter.
- Blog must be Korean 문어체 평서형 반말.
- Blog sentences should end mainly with `다`, `이다`, `한다`, `된다`, `있다`, `없다`.
- Blog must not sound conversational. Avoid endings like `하면 돼`, `해봐`, `거야`, `거든`, `잖아`, `~해`, `~돼`.
- Blog must use Markdown structure: title, `##` headings, short paragraphs, lists/code blocks when useful.
- Blog must not use polite endings such as `합니다`, `습니다`, `입니다`, `됩니다`, `하세요`, `드립니다`.
- Blog must end with `## 참고자료` when source/reference links are present.
- For technical implementation blogs, include a GitHub repository link only when the input contains one. Never invent a GitHub link.
- Public drafts must not show internal labels such as `[후츠릿 인사이트]`, `후츠릿의 인사이트`, `실무 적용 포인트`, or `핵심 메시지:`.
- LinkedIn must start with one concise title line, then structured short polite Korean paragraphs focused on the user's insight. It should drive readers to the blog with a real blog URL or `[블로그 링크]` placeholder.
- LinkedIn and Discord newsletter must use polite Korean.
- Avoid unnecessary colons in public messages, including `블로그 전문:`.
- Discord newsletter must not use forced labels such as `핵심 요약`, `왜 중요한가`, or `바로 해볼 것`; write natural short paragraphs under the title.
- Discord newsletter should be concise, polite Korean, Markdown-formatted, and include reference links at the bottom when present.

## Insight Standard

Do not stop at summary. Each public draft should expose:

1. What most people think the issue is.
2. What the real structural shift or failure mode is.
3. What a 실무자 should design, verify, automate, or avoid.

Good closing direction:

```text
프롬프트는 대화의 기술이고, 하네스는 운영의 기술이다.
AI를 잘 쓰는 사람은 답변을 받는 사람이 아니라, 실패해도 복구되는 구조를 만드는 사람이다.
```

## Quality Gate

Score below 90 if any of these are true:

- Blog uses polite endings.
- Blog uses casual conversational endings like `하면 돼`, `해봐`, `거야`.
- Blog is mostly continuous prose without enough headings.
- Public draft exposes internal labels.
- Insight is generic AI optimism without workflow, system design, or verification criteria.
- The post cannot be reduced to one sharp claim.

When a gate fails, revise automatically before asking for approval or reporting completion.

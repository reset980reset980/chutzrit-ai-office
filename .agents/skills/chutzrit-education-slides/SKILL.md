---
name: chutzrit-education-slides
description: Use when creating, revising, evaluating, or implementing Chutzrit lecture slides, PPT-style lecture materials, course decks, workshop decks, or HTML presentation files for the 강의운영팀. Preserves the ppt-maker web-slide-maker system: single-file dark-mode HTML/CSS/JS slides, Pretendard + GmarketSans, fixed slide patterns, and output under outputs/education/slides/.
---

# Chutzrit Education Slides

Use this skill for 강의운영팀 slide work: lecture source analysis, slide planning, HTML deck generation, example code cleanup, and lecture deck review.

This skill is the 후츠릿 AI 오피스 version of the `ppt-maker` web slide maker. Keep the code, design rules, and slide patterns equivalent unless the user explicitly asks to change the system.

## Required References

Before creating or changing slide output, read the relevant files:

- `agents/education/slide-maker/assets/base-template.html`
- `agents/education/slide-maker/references/design-rules.md`
- `agents/education/slide-maker/references/patterns.md`
- `docs/education/web-slide-research.md` when changing slide behavior or navigation
- `docs/education/figma-design-rules.md` when judging visual fidelity or layout

## Implementation Shape

- Treat `agents/education/` as the 강의운영팀 team folder.
- Keep slide-maker code and reusable rules under `agents/education/slide-maker/`.
- Store generated lecture decks under `outputs/education/slides/`.
- Store local-only source materials under `outputs/education/sources/`.
- Store generation logs or verification notes under `outputs/education/logs/`.
- Do not place generated slides inside `agents/education/`.
- Do not create a new frontend framework, bundler, or package setup for basic decks.

## Workflow

### 1. Analyze The Source

Extract:

- 강의명
- 주제와 대상
- 챕터/섹션 구조
- 각 슬라이드의 핵심 메시지
- 예제 코드, 실습 절차, 데모 흐름
- 오래됐거나 검증이 필요한 코드/명령/링크

Ask for the lecture name if it is missing.

### 2. Plan The Deck First

Before generating HTML, show the slide plan and wait for confirmation unless the user explicitly asks to skip confirmation.

Use this format:

```text
슬라이드 구성 (총 N장)
──────────────────────────────
 1. [A] 타이틀 — 강의명
 2. [F] 목차 — 챕터 1 · 챕터 2 · ...
 3. [B] 섹션 전환 — 챕터 1 제목
 4. [D] 개념 설명 — 핵심 개념 요약
 ...
N. [M] 클로징

예제/코드 변경 사항:
- 슬라이드 7: 기존 foo() 예제 → bar() 예제로 업데이트
```

### 3. Generate The HTML

- Start from `agents/education/slide-maker/assets/base-template.html`.
- Add slides inside `<div class="slide-deck" id="deck">`.
- Keep all CSS and JS inline in one HTML file.
- Follow `agents/education/slide-maker/references/patterns.md`.
- Use classes and tokens from `agents/education/slide-maker/references/design-rules.md`.
- Save to `outputs/education/slides/{lecture-slug}-slides.html`.

## Slide Pattern Rules

Use the same pattern set as `ppt-maker`:

- A: title
- B: section divider
- C: impact statement
- D: split concept + quote/stat
- E: numbered process
- F: agenda
- G-2/G-3/G-4: comparison grids
- J: solo numbered principles
- L: text + visual grid
- Code-A: full code block
- Code-B: explanation + code
- M: closing

## Quality Rules

- One message per slide.
- Split crowded slides instead of shrinking everything.
- No internal scroll except `pre` code blocks.
- No reveal animation that hides content needed for understanding.
- Keep section divider and statement slides footerless.
- Every other slide footer must be `<span>후츠릿 · {강의명}</span>`.
- Prevent orphan words in short metadata lines.
- Code blocks must use the existing syntax classes and highlighted-line convention.
- Output must work by opening the HTML file directly in a browser.

## Reporting

When done, report:

- generated slide path
- slide count
- source material used
- notable code/example updates
- any remaining validation gaps


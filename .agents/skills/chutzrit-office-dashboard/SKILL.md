---
name: chutzrit-office-dashboard
description: Use when designing, implementing, revising, or testing the Chutzrit AI Office dashboard: a live lecture-ready web dashboard that visualizes AI office agents in one office space with transparent PNG avatar characters, status badges, outputs-based broadcasting metrics, clickable detail panels, and optional current-status integration.
---

# Chutzrit Office Dashboard

Use this skill for 후츠릿 AI 오피스 대시보드 work: dashboard planning, frontend implementation, visual QA, outputs-based status data, current-status integration, and documentation updates.

## Required References

Before implementing or revising the dashboard, inspect:

- `docs/dashboard/office-dashboard.md`
- `docs/dashboard/references/office-concept.png`
- `docs/dashboard/references/agent-avatars.png`
- `agents/office-dashboard/README.md`
- `apps/office-dashboard/README.md`
- `agents/broadcasting/agents/` and `agents/broadcasting/pipeline/` when mapping real broadcasting agent state

Reference image interpretation:

- `office-concept.png` is the overall office/dashboard mood reference: one big neon tech office, not separate cards.
- `agent-avatars.png` is the avatar direction reference for each broadcasting agent.
- If image order or labels in the prompt are ambiguous, judge by visual content: office scene for layout, character sheet for avatars.
- Use references for mood, composition, and character direction only. Do not copy them exactly.

## Implementation Shape

- Prefer `apps/office-dashboard/` for the web app.
- Use React + Vite + TypeScript unless the repo already has a stronger frontend convention.
- Prefer React over plain JavaScript because the dashboard needs coordinated animation state, clickable agent details, generated outputs data, optional live status, and current-status file updates.
- Keep dashboard domain notes under `agents/office-dashboard/`.
- Keep human-readable design/spec docs under `docs/dashboard/`.
- Keep generated data separate from components, e.g. `src/data/generated/officeStatus.json`.
- Design the data shape so it reads `outputs/broadcasting/` packages now and can use `outputs/broadcasting/logs/current-status.json` when present.
- First version visualizes only the implemented `broadcasting` team. Add other teams only when their runtime is implemented.

Suggested components:

- `OfficeDashboard`
- `OfficeHeader`
- `TokenUsageWidget`
- `OfficeMap`
- `PipelineFlow`
- `AgentAvatar`
- `StatusBadge`
- `AgentDetailPanel`
- `MetricDetailPanel`
- `BottomStatusBar`

## Data Model

Use exactly four statuses:

```ts
type AgentStatus = "WORKING" | "IDLE" | "REVIEW" | "ERROR";

type Agent = {
  id: string;
  name: string;
  role: string;
  status: AgentStatus;
  avatar: string;
  motion: "typing" | "thinking" | "reading" | "reviewing" | "revising" | "publishing" | "resting" | "error";
  position: {
    x: number;
    y: number;
  };
  currentTask: string;
  recentOutput: string;
  nextTask: string;
  updatedAt: string;
  statusSource?: string;
};
```

Status colors:

- `WORKING`: green or mint, with subtle pulse animation
- `IDLE`: red, because it means rest
- `REVIEW`: orange
- `ERROR`: red

Generated top-level state should also include:

- Codex token usage from `current-status.json` when available; otherwise show a clearly labeled demo calculation
- Today input count
- Completed content count
- Review queue count
- Published count
- Overall progress
- System status
- Current time
- Pipeline stages: Discord Input -> Strategy -> Writers -> Review -> Publish

## Required Agents

Place broadcasting agents inside one shared office:

- Input Parser Agent: Discord input reception desk
- Content Strategy Agent: strategy meeting table
- Insight Agent: near strategy table or board
- Blog Writer Agent: writing desk
- LinkedIn Writer Agent: writing desk
- Discord Newsletter Agent: writing desk
- Self Reflection Agent: review desk
- Revision Agent: revision desk
- Publish Agent or publish board: right-side or lower shipping area

## Visual Rules

- Build an actual dashboard screen, not a landing page.
- The first viewport must be the operating dashboard itself.
- Use one large office space. Do not make the agents separate cards in a grid.
- Include reception desk, strategy table, writing desks, review desk, revision desk, and publish board as a continuous office layout.
- The result should feel like the AI office is actively running.
- The office must have natural motion. Agents should look like they are working, thinking, reviewing, publishing, or resting, not just blinking in place.
- Use a dark neon tech office mood, but keep it warm, cute, and readable.
- Agent avatars are the visual center, but UI information must remain legible.
- Add small arrows, labels, or glowing connector lines for the pipeline flow without splitting the office into huge sections.
- Add a top header with:
  - title: `후츠릿 AI 오피스`
  - subtitle: `24시간 무인 AI 콘텐츠 제작 파이프라인`
  - Codex token widget that shows actual values only when available
- Add a bottom status bar with operational metrics and current time.
- Bottom status bar metrics must be clickable and show actual package records from `outputs/broadcasting/`.
- Clicking an agent must open a right-side detail panel or modal with:
  - agent name
  - status
  - current task
  - recent output
  - next task
  - last updated time
  - status source
- If avatar image loading fails, show fallback initials/name and status badge.
- Keep text inside containers at desktop lecture resolution. No overlap, clipping, or unreadable labels.

## Motion Rules

Motion is a core requirement, not decoration.

- Use small looping CSS animations for each agent state:
  - `typing`: gentle hand/body bob and desk glow
  - `thinking`: slow head/halo glow, small idea pulse
  - `reading`: subtle page or screen scan motion
  - `reviewing`: checklist/check stamp pulse
  - `revising`: faster pen movement or focused shake
  - `publishing`: conveyor/board glow and outgoing signal
  - `resting`: slow breathing or chair idle motion
  - `error`: restrained red pulse, no aggressive flashing
- Do not show energy or work progress percentages near each agent on the main page.
- Show energy only in the side detail panel. Use real runtime values when available; otherwise use a stable status-based fallback.
- Main page agent labels should only show status and employee name. Put role and detailed status in the side panel.
- Add slow ambient movement to the office: monitor glow, connector line shimmer, pipeline arrow movement, token gauge motion.
- Keep motion subtle enough for a live lecture screen. Avoid distracting, fast, or full-screen animation.
- Respect `prefers-reduced-motion`: reduce animation to static highlights when enabled.
- Do not use random jumpy motion. Use calm, intentional loops tied to status and current task.

## Image Usage

- Manage image paths in one place, e.g. `src/data/assets.ts`.
- Use provided reference images as source direction. If using a large character sheet, crop into individual assets with image processing.
- Use transparent PNG assets for final avatars.
- Avatar images must not contain text. Put employee names, roles, and statuses in HTML.
- Do not make characters look like an existing protected character/IP.
- Do not rely only on SVG decoration. Use actual visual assets and office-space composition.

## Forbidden

- Do not build a marketing/landing page.
- Do not build a simple card list.
- Do not copy the reference images exactly.
- Do not make each agent area a fully separate card.
- Do not make a multi-box layout that no longer reads as one office.
- Do not use only abstract SVG or gradient decoration in place of avatars and office scene.
- Do not invent main-page energy, battery, or work progress values.
- Do not let labels, badges, avatars, panels, or bottom bars overlap.

## Validation

Before finishing implementation:

- Run the dev server and provide the local URL.
- Open the dashboard in a browser.
- Verify the full office, header, token widget, pipeline flow, bottom status bar, and all visible agents fit in desktop view.
- Click multiple agents and verify the detail panel updates.
- Click bottom metrics and verify the detail panel shows actual output records.
- Check that `WORKING` agents have natural work motion when real status data marks them working.
- Check that `IDLE`, `REVIEW`, and `ERROR` states have distinct but restrained motion.
- Check `prefers-reduced-motion` does not break layout.
- Check image fallback behavior if practical.
- Use screenshots or browser inspection to confirm no major text overlap.
- Run relevant lint/build/test scripts if present.

## Reporting

When done, report:

- dashboard app path
- local dev server URL
- reference assets used
- generated data file path and current-status integration point
- verification commands and browser checks
- any remaining visual or data-integration gaps

---
name: chutzrit-broadcasting
description: Use when generating, revising, evaluating, publishing, or implementing Chutzrit broadcasting content for blog, LinkedIn, or Discord. Enforces Korean blog 문어체 평서형 반말, structured markdown, sharp AI automation/developer insight, no visible internal labels, and the Tistory-first publishing flow.
---

# Chutzrit Broadcasting

Use this skill for 콘텐츠배포팀 work: source memo/link intake, blog/LinkedIn/Discord draft generation, revision, quality scoring, publishing, and pipeline changes that affect those outputs.

## Implementation Shape

- Treat `agents/broadcasting/` as the 콘텐츠배포팀 team folder, not a single agent.
- Keep actual runtime subagents under `agents/broadcasting/agents/`.
- Keep orchestration, progress formatting, quality gates, and storage under `agents/broadcasting/pipeline/`.
- Content Strategy Agent and Insight Agent run sequentially.
- Blog Writer Agent, LinkedIn Writer Agent, and Discord Newsletter Writer Agent run in parallel.
- Self Reflection Agent evaluates the combined package.
- Revision Agent revises failed channels first; if channel-level failures are unavailable, revise all channels.
- Publish Agent runs after the final quality gate, records Discord dispatch, and executes enabled external publishers after package files are saved.
- Do not collapse strategy, insight, and all platform writing back into one generation prompt unless the user explicitly asks for a single-call fallback.

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
- `docs/operations/approval-policy.md` when changing approval or publishing behavior
- `docs/operations/credentials.md` when changing platform publishing credentials

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
- Use emojis only as readability markers. Prefer `✅`, `⚠️`, `🔍`, `🧩`, `🚀`, `📌`, `🔗`.
- Do not add emojis to every line or every heading.
- Blog should use roughly 3-5 emojis total, only for key sections such as conclusion, caution, execution, and references.
- LinkedIn should use roughly 2-4 emojis total, mainly for the title/hook, short checklist, or blog link.
- Discord newsletter can use roughly 2-5 emojis total, mainly in the title, action items, and reference link section.
- LinkedIn must start with one concise title line, then structured short polite Korean paragraphs focused on the user's insight. It should drive readers to the blog with a real blog URL or `[블로그 링크]` placeholder.
- LinkedIn and Discord newsletter must use polite Korean.
- Avoid unnecessary colons in public messages, including `블로그 전문:`.
- Discord newsletter must not use forced labels such as `핵심 요약`, `왜 중요한가`, or `바로 해볼 것`; write natural short paragraphs under the title.
- Discord newsletter should be concise, polite Korean, Markdown-formatted, and include reference links at the bottom when present.

## Publishing Rules

Current project state:

- Discord newsletter auto-posting goes to the configured newsletter channel. The `broadcasting` channel is for input and operational reports.
- Publish Agent records publishing status in `publish-plan.json`.
- Generated packages are saved under both `outputs/broadcasting/drafts/` and `outputs/broadcasting/final/`.
- Tistory Playwright and LinkedIn Posts API publishers are implemented. When credentials, browser dependencies, or login session files are not connected, send the final drafts to Discord and mark external publishing as not connected or failed.
- Keep saved blog files in Markdown, but convert Markdown to Tistory editor HTML at publish time. Tistory WYSIWYG must receive rendered HTML headings such as `<h2>`, not raw text like `## heading`.

When external publishing adapters are connected and enabled:

1. Publish the blog first.
2. Use Tistory Playwright browser automation for blog publishing. Do not assume Tistory Open API publishing.
3. Use the Chrome Playwright channel for every Tistory session capture, validation, and publish run.
4. Publish Tistory as public when `TISTORY_PUBLISH_MODE=public` and `TISTORY_AUTO_PUBLISH=true`.
5. Convert the Markdown body into editor HTML before filling Tistory. Headings, lists, links, code blocks, and paragraphs must render visually in the published post.
6. Capture the actual Tistory post URL.
7. Replace LinkedIn `[블로그 링크]` with the actual Tistory URL.
8. Publish LinkedIn through the LinkedIn Posts API when `LINKEDIN_AUTO_PUBLISH=true`.
9. LinkedIn API publishing is public publishing, not draft saving.
10. Post the Discord newsletter to `DISCORD_NEWSLETTER_CHANNEL_ID`.
11. Report one consolidated multi-platform result after all publish attempts finish. Include Tistory URL, LinkedIn URL, Discord message link, failed/blocked channel reasons, and output path in one readable message.

Do not publish LinkedIn with a `[블로그 링크]` placeholder unless the user explicitly allows that fallback. If blog publishing fails, preserve drafts, report the failure, and block LinkedIn publishing by default.

### Browser Profile Safety

Never attach Playwright or any browser automation to the user's real daily browser profile.

Forbidden patterns:

- Do not call `launch_persistent_context` with the real Brave, Chrome, Chromium, Edge, or Safari user data directory.
- Do not pass `--user-data-dir` pointing at `~/Library/Application Support/BraveSoftware/Brave-Browser`, `~/Library/Application Support/Google/Chrome`, `~/.config/BraveSoftware/Brave-Browser`, `~/.config/google-chrome`, or any equivalent real profile root.
- Do not automate or close the user's already-running Brave window for publishing.
- Do not clear cookies, cache, localStorage, sessionStorage, IndexedDB, browser history, or site data.
- Do not click logout, sign out, account switch, reset session, clear browsing data, or similar UI.

Required pattern:

- Publishing runtime must use `PLAYWRIGHT_STORAGE_STATE` with an isolated Chrome Playwright browser context.
- Visible browser debugging or session capture must use the dedicated isolated Chrome profile under `outputs/broadcasting/session/chrome-playwright-profile/`, never the user's actual browser profile.
- Do not use Brave or Safari for Tistory Playwright automation.
- Closing automation may only close the isolated Playwright page/context it created. It must not close the user's real browser app or tabs.
- If a task seems to require real browser profile access, stop and ask for explicit approval with a safer alternative.

Publishing requires:

- Quality score meets the configured gate or revision loop is exhausted.
- Final files are saved under `outputs/broadcasting/`.
- Required environment variables are present.
- `PUBLIC_CONTENT_REQUIRE_APPROVAL=false` or the user has explicitly approved publishing.

Publishing still requires user approval for:

- Payment, ads, purchases, subscriptions
- Account permission changes
- Credential creation or rotation
- Deleting external content
- Any irreversible or brand-risky action outside already configured posting

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

After the gate passes, follow the Publishing Rules. If publishing is unavailable, do not pretend it succeeded; send the drafts and a clear Discord status instead.

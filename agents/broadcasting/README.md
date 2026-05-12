# 콘텐츠배포팀

콘텐츠배포팀은 하나의 입력 소스를 여러 플랫폼에 맞는 콘텐츠로 변환하고, 저장, Discord 자동 발송, 보고까지 담당합니다.

현재 후츠릿 AI 오피스의 1차 MVP 팀입니다.

## MVP 흐름

```text
Discord `broadcasting` 팀 채널 메시지 수신
-> "글 작성중입니다" 즉시 응답
-> Discord 기본 typing 표시와 봇 작업 상태 표시
-> URL 포함 여부 자동 감지
-> 원문/링크/사용자 생각 정리
-> 링크 입력이면 핵심 내용 간략 요약
-> Input Parser 결과 요약 메시지
-> 콘텐츠 전략 Agent가 방향 설계
-> 콘텐츠 전략 결과 요약 메시지
-> 인사이트 Agent가 후츠릿다운 관점 추가
-> 인사이트 결과 요약 메시지
-> 플랫폼별 Writer Agent가 병렬 초안 생성
-> 채널별 원고 결과 요약 메시지
-> Self Reflection Agent가 품질 평가
-> 평가 결과 중간 보고
-> 기준 미달 시 Revision Agent가 수정
-> 품질 기준 통과
-> 초안 패키지 저장
-> 품질 상태 생성
-> Discord 자동 발송
-> Discord 보고
```

## 입력 방식

MVP 입력은 Discord `broadcasting` 팀 채널에 작성된 일반 메시지입니다.

사용자는 별도의 명령어, 접두어, 채널명을 붙이지 않습니다.

지원하는 입력:

- 자연어 메모
- 뉴스, YouTube, 블로그 등 외부 콘텐츠 링크
- 링크와 함께 적은 사용자의 생각

```text
AI 에이전트 시대에는 프롬프트보다 하네스 설계가 더 중요해진다.
```

```text
https://example.com/news-or-video

이 흐름은 결국 AI 자동화 실무자에게 필요한 역량이 바뀐다는 뜻인 것 같다.
```

처리 기준:

- URL이 있으면 링크 입력으로 자동 감지합니다.
- URL이 없으면 원본 메모로 처리합니다.
- 링크와 사용자의 생각이 함께 있으면 사용자의 생각을 핵심 관점으로 우선 적용합니다.
- 기본값은 블로그, LinkedIn, Discord 뉴스레터용 콘텐츠 전체 초안 생성입니다.
- 링크 입력은 원문을 가져와 단순 요약하지 않고, 후츠릿 페르소나와 채널별 템플릿에 맞춰 재해석합니다.
- 링크 입력은 Input Parser 단계에서 URL, 제목, 설명, 핵심 내용을 간략히 정리해 Discord에 먼저 보고합니다.

## 현재 구현 구조

`agents/broadcasting/`은 단일 에이전트 폴더가 아니라 콘텐츠배포팀 팀 폴더입니다.

실제 서브에이전트는 `agents/broadcasting/agents/` 아래에 있습니다.

```text
agents/broadcasting/
├── agents/
│   ├── input_parser.py
│   ├── content_strategy.py
│   ├── insight.py
│   ├── writers/
│   │   ├── blog.py
│   │   ├── linkedin.py
│   │   └── discord.py
│   ├── reflection.py
│   ├── revision.py
│   └── publish.py
├── pipeline/
│   ├── orchestrator.py
│   ├── generator.py
│   ├── prompts.py
│   ├── quality.py
│   ├── progress.py
│   └── storage.py
```

`pipeline/orchestrator.py`는 각 서브에이전트를 호출하는 실행 흐름만 담당합니다. 전략과 인사이트는 순차 실행하고, Blog/LinkedIn/Discord Writer Agent는 병렬 실행합니다. 따라서 현재 구조는 한 번의 LLM 호출로 모든 결과를 만드는 방식이 아니라, 역할별 프롬프트와 출력 스키마를 가진 여러 LLM 호출을 조합하는 방식입니다.

## 내부 처리 단계

아래 역할들은 실제 서브에이전트 모듈로 분리되어 있고, `pipeline/`은 이들을 오케스트레이션합니다.

### 콘텐츠 전략

글을 바로 쓰기 전에 방향을 결정합니다.

출력:

- 핵심 메시지
- 독자 타깃
- 글의 주장
- 플랫폼별 강조 방향

### 인사이트

단순 요약을 후츠릿다운 실무 관점으로 바꿉니다.

출력:

- 후츠릿 인사이트
- 실무 적용 포인트
- AI 자동화/개발툴 활용 관점
- 예시, 비유, 주의점

### 플랫폼별 작성

전략과 인사이트를 바탕으로 플랫폼별 글을 병렬 생성합니다.

- Blog Writer Agent
- LinkedIn Writer Agent
- Discord Writer Agent

### Self Reflection

완성본을 평가하고 수정 피드백을 작성합니다.

기본 기준:

- 90점 이상: 자동 발송 가능
- 기준 미달: 최대 3회까지 Revision 실행
- 각 평가 결과와 수정 지시를 Discord에 중간 보고
- 최대 수정 루프 이후에도 기준 미달이면 현재 결과를 저장하고 Discord에 발송하되, 기준 미달 상태를 명확히 표시

### Revision

Self Reflection 피드백을 반영해 글을 수정합니다. 각 회차는 `Revision Agent 1/3회차`처럼 회차를 표시하고, 어떤 피드백을 반영하는지 Discord에 요약합니다. 채널별 점수가 낮으면 기준 미달 채널만 우선 수정하고, 채널별 점수가 없으면 전체 채널을 수정 대상으로 봅니다.

### Publish

Publish Agent는 품질 게이트 이후 발송과 외부 배포 상태를 구조화하고, 저장된 산출물을 기준으로 활성화된 외부 배포를 실행합니다.

`agents/broadcasting/agents/publish.py`는 배포 순서, 의존성, 채널별 가능 상태를 판단하고 실행하는 오케스트레이터 역할입니다. 실제 티스토리 클릭 자동화나 LinkedIn API 호출은 `agents/broadcasting/publishers/` 아래의 플랫폼별 Publisher 어댑터가 담당합니다.

현재 연결 상태:

- Discord: 봇이 `broadcasting` 채널에 자동 발송
- 티스토리: Playwright 게시 어댑터가 연결되어 있으며, 세션 파일과 Playwright 실행 환경이 준비되면 공개 발행
- LinkedIn: 티스토리 실제 URL이 없으면 `[블로그 링크]` 상태로 공개 게시하지 않고 `blocked_until_blog_url`로 기록

Publish Agent는 외부 API 배포가 연결되지 않았을 때 성공으로 표시하지 않습니다.

배포는 병렬이 아니라 순차 방식입니다. LinkedIn 원고에는 티스토리 실제 발행 URL이 필요하므로 `티스토리 발행 -> URL 확보 -> LinkedIn 링크 치환/게시 -> Discord 보고` 순서로 처리합니다.

## 대상 채널

- 블로그
- LinkedIn
- Discord 뉴스레터

다음 배포 흐름은 티스토리 공개 발행을 먼저 수행한 뒤 LinkedIn을 발행합니다.

```text
티스토리 공개 발행
-> 티스토리 글 URL 확보
-> LinkedIn 원고의 [블로그 링크] 치환
-> LinkedIn API 공개 발행
-> Discord 뉴스레터 발송
-> Discord에 블로그, LinkedIn, Discord 링크 보고
```

티스토리는 Open API 종료 안내가 있으므로 Playwright 브라우저 자동화로 처리합니다. 기본 배포는 저장된 로그인 세션을 격리된 headless Chrome 컨텍스트에서 사용하며, 실제 사용 중인 브라우저 프로필을 직접 조작하거나 로그아웃하지 않습니다. 티스토리 자동화는 Chrome Playwright 채널만 사용합니다.

티스토리 자동 발행 준비 여부는 `PLAYWRIGHT_STORAGE_STATE` 파일 존재만으로 판단하지 않습니다. 발행 전 `TISTORY_MANAGE_URL`에 실제 접속해 로그인 유지 상태를 확인하고, 로그인 페이지로 이동하면 `session_expired`로 기록한 뒤 LinkedIn 공개 게시를 중단합니다.

LinkedIn은 Posts API로 공개 게시하며, API 토큰과 Author URN 설정이 필요합니다.

CLI에서 외부 배포까지 실행하려면 `--publish`를 붙입니다.

```bash
python -m agents.broadcasting.pipeline.run_once --text "메모" --publish
```

Discord 봇은 메시지 처리 후 저장된 패키지를 기준으로 Publish Agent를 실행합니다. 티스토리 발행에 성공하면 LinkedIn 원고의 `[블로그 링크]`를 실제 티스토리 URL로 치환하고, 수정된 `linkedin.md`, `publish-plan.json`, `metadata.json`을 draft/final 양쪽에 다시 기록합니다.

배포 보고는 멀티플랫폼 전체 배포 시도 후 하나의 최종 메시지로 통합합니다. 티스토리 URL, LinkedIn URL, Discord 뉴스레터 메시지 링크와 실패 또는 중단 사유를 한 번에 보여줍니다.

## 하위 폴더

- `agents/`: 콘텐츠배포팀 실제 서브에이전트
- `pipeline/`: 서브에이전트 오케스트레이션, 품질 게이트, 저장
- `prompts/`: 페르소나, 플랫폼, 목적별 프롬프트
- `prompts/templates/`: 실제 후츠릿 글에서 추출한 채널별 작성 템플릿
- `publishers/`: 티스토리 Playwright, LinkedIn Posts API, Discord 발송 같은 실제 플랫폼별 배포/발송 어댑터
- `schemas/`: 메타데이터, 품질 평가, 발송 상태 스키마

전략, 인사이트, 플랫폼별 작성, 평가, 수정, 배포 판단은 `agents/` 내부 서브에이전트로 구현하고, `pipeline/`은 실행 순서와 병렬화를 관리합니다.

## 채널별 템플릿

Writer Agent는 아래 템플릿을 참고해 입력 메시지에 맞는 글 구조를 선택합니다.

- `prompts/templates/blog.md`: 구현형, 개념 설명형, 인사이트형 블로그 템플릿
- `prompts/templates/linkedin.md`: LinkedIn 인사이트 포스트 템플릿
- `prompts/templates/discord.md`: Discord 뉴스레터 템플릿

## 산출물 위치

콘텐츠배포팀 산출물은 에이전트 코드 폴더 안에 저장하지 않습니다.

산출물은 팀별 결과물 폴더에 저장합니다.

```text
outputs/broadcasting/
├── drafts/
├── final/
├── approvals/
└── logs/
```

`approvals/`는 향후 결제, 계정 변경, 되돌리기 어려운 외부 작업처럼 별도 승인이 필요한 작업의 기록용입니다. 현재 콘텐츠 MVP의 블로그 원고, LinkedIn 원고, Discord 뉴스레터는 승인 없이 자동 발송합니다.

콘텐츠 1건의 초안 패키지는 아래 구조를 따릅니다.

```text
outputs/broadcasting/drafts/YYYY-MM-DD-slug/
├── source.md
├── strategy.md
├── insight.md
├── blog.md
├── linkedin.md
├── discord.md
├── reflection.md
├── reflection.json
├── metadata.json
├── approval-status.json
└── publish-plan.json
```

## 실행 방법

로컬에서 메모 하나를 콘텐츠 패키지로 생성하려면 아래 명령을 사용합니다.

```bash
.venv/bin/python -m agents.broadcasting.pipeline.run_once --text "AI 에이전트 시대에는 프롬프트보다 하네스 설계가 더 중요해진다."
```

생성 결과는 `outputs/broadcasting/drafts/`와 `outputs/broadcasting/final/` 아래에 같은 패키지 ID로 저장되고, 기본값으로 Discord Webhook 보고가 전송됩니다.

Discord 입력 테스트 전에 아래 검증이 모두 통과해야 합니다.

```bash
.venv/bin/python scripts/check_integrations.py --all
```

이 검증은 Discord 입력 채널 접근, Discord Webhook 보고, OpenAI 호출, 티스토리 Playwright 세션 유효성을 확인합니다. 이 중 하나라도 실패하면 `broadcasting` 채널에 테스트 메시지를 보내기 전에 먼저 환경을 복구합니다.

Discord 봇으로 실행한 경우 블로그 원고와 LinkedIn 원고 미리보기는 `broadcasting` 채널에 남기고, Discord 뉴스레터 본문은 `DISCORD_NEWSLETTER_CHANNEL_ID`로 지정한 뉴스레터 채널에 발송합니다.

봇은 메시지를 받자마자 작업 시작 알림을 보내고, Discord 기본 typing 표시와 `글 작성중입니다` 활동 상태를 유지합니다. 각 논리 Agent가 끝날 때마다 이모지와 함께 결과를 메시지용으로 요약해 보낸 뒤 최종 원고를 발송합니다.

Publish Agent는 티스토리 Playwright, LinkedIn Posts API, Discord 뉴스레터 발송 결과를 채널별로 기록하고, 전체 배포 시도가 끝난 뒤 `broadcasting` 채널에 통합 결과를 보고합니다.

## 구현 우선순위

1. 티스토리 Playwright Publisher 어댑터 연결
2. LinkedIn Posts API Publisher 어댑터 연결
3. Discord 수정 요청을 특정 패키지와 채널에 반영하는 Revision 명령 추가
4. 실제 발송 결과와 사용자 수정 요청을 반영한 Self Reflection 기준 보정

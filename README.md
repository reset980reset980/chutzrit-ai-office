# 후츠릿 AI 오피스

후츠릿 AI 오피스는 Codex와 자동화 에이전트로 운영되는 24시간 무인 AI 오피스입니다.

사용자는 CEO이자 디렉터입니다. Codex와 각 팀 에이전트는 실행 직원처럼 동작하며, 기획된 업무를 구현하고 테스트하고 보고합니다. Discord는 보고, 수정 요청, 명령 입력을 담당하는 중앙 관제실입니다.

## 현재 MVP

현재 1차 구현 대상은 **콘텐츠배포팀**입니다.

목표는 단편화된 메모나 거친 입력을 받아서 여러 플랫폼용 콘텐츠로 변환하고, 결과물을 저장한 뒤, Discord 채널에 바로 발송하고 보고하는 것입니다.

MVP 기본 흐름:

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
-> 인사이트 Agent가 후츠릿다운 실무 관점 추가
-> 인사이트 결과 요약 메시지
-> 플랫폼별 Writer Agent가 병렬 초안 생성
-> 채널별 원고 결과 요약 메시지
-> Self Reflection Agent가 품질 평가
-> 평가 결과 중간 보고
-> 기준 미달 시 Revision Agent가 수정
-> 품질 기준 통과
-> outputs/broadcasting/drafts/ 저장
-> 품질 평가
-> Discord 자동 발송
-> outputs/broadcasting/final/ 저장
-> Discord 결과 보고
```

초기에는 자동 리서치로 주제를 고르는 방식보다, 사용자가 Discord `broadcasting` 팀 채널에 자연스럽게 작성한 메모, 링크, 생각을 콘텐츠로 확장하는 방식으로 시작합니다. 자동 주제 선정은 콘텐츠 생성, 승인, 배포, 보고 흐름이 안정화된 뒤 추가합니다.

초기 입력 원칙:

- 별도의 명령어, 접두어, 채널명을 쓰지 않습니다.
- `broadcasting` 채널에 글을 쓰면 자동화가 실행됩니다.
- URL이 있으면 링크 입력으로 자동 감지합니다.
- 링크와 사용자의 생각이 함께 있으면 사용자의 생각을 핵심 관점으로 우선 적용합니다.
- 기본값은 블로그, LinkedIn, Discord 뉴스레터용 콘텐츠 전체 초안 생성입니다.

## 주요 문서

- [AGENTS.md](./AGENTS.md): 에이전트가 따라야 하는 프로젝트 운영 규칙
- [docs/architecture/folder-structure.md](./docs/architecture/folder-structure.md): 폴더 구조 설계
- [docs/operations/approval-policy.md](./docs/operations/approval-policy.md): 승인 정책
- [docs/operations/credentials.md](./docs/operations/credentials.md): 자격증명 설정 방법
- [docs/strategy/persona.md](./docs/strategy/persona.md): 후츠릿 콘텐츠 페르소나 초안
- [docs/strategy/audience.md](./docs/strategy/audience.md): 타깃 독자 정의
- [docs/strategy/content-positioning.md](./docs/strategy/content-positioning.md): 콘텐츠 포지셔닝
- [docs/strategy/channel-style-guide.md](./docs/strategy/channel-style-guide.md): 채널별 글쓰기 스타일
- [docs/content/references/source-materials.md](./docs/content/references/source-materials.md): 참고자료 목록
- [docs/education/slide-maker.md](./docs/education/slide-maker.md): 강의운영팀 슬라이드 제작 시스템
- [configs/channels.example.yaml](./configs/channels.example.yaml): 채널별 배포/승인 설정 예시
- [.env.example](./.env.example): 필요한 환경변수 예시

## 문서 용도

`README.md` 파일은 사람이 프로젝트와 하위 모듈을 이해하기 위한 안내 문서입니다. 이 프로젝트의 모든 `README.md`는 한글로 작성합니다.

에이전트가 따라야 하는 작업 규칙, 자율 실행 기준, 승인 기준, 문서 작성 규칙은 `AGENTS.md`에 기록합니다.

## 폴더 구조

```text
.
├── AGENTS.md
├── README.md
├── .env.example
├── .agents/
│   └── skills/
│       ├── chutzrit-broadcasting/
│       │   └── SKILL.md              # Codex용 콘텐츠배포팀 작업 Skill
│       └── chutzrit-education-slides/
│           └── SKILL.md              # Codex용 강의운영팀 슬라이드 Skill
├── configs/
├── agents/
│   ├── broadcasting/
│   │   ├── agents/                  # 콘텐츠배포팀 실제 서브에이전트
│   │   ├── pipeline/                # 서브에이전트 오케스트레이션
│   │   ├── prompts/
│   │   ├── publishers/
│   │   └── schemas/
│   ├── chief-of-staff/
│   ├── research/
│   ├── dev/
│   ├── education/
│   │   └── slide-maker/              # 강의 슬라이드 템플릿과 패턴 규칙
│   └── youtube/
├── apps/
│   └── discord-bot/
├── automations/
│   └── n8n/
├── docs/
│   ├── architecture/
│   ├── content/
│   ├── education/
│   ├── operations/
│   ├── reports/
│   └── strategy/
│       ├── persona.md                 # 후츠릿 페르소나와 콘텐츠 판단 기준
│       ├── audience.md                # 타깃 독자 정의와 우선순위
│       ├── content-positioning.md     # 콘텐츠 포지셔닝과 차별화 방향
│       └── channel-style-guide.md     # 채널별 글쓰기 스타일 기준
├── outputs/
│   ├── broadcasting/
│   │   ├── drafts/
│   │   ├── final/
│   │   ├── approvals/
│   │   └── logs/
│   └── education/
│       ├── slides/
│       ├── logs/
│       └── sources/
├── scripts/
└── tests/
```

## 폴더 역할

### `.agents/skills/`

Codex 공식 Agent Skills를 저장하는 위치입니다.

후츠릿 업무를 Codex의 재사용 가능한 Skill로 정의한 파일은 아래에 있습니다.

```text
.agents/skills/chutzrit-broadcasting/SKILL.md
.agents/skills/chutzrit-education-slides/SKILL.md
```

`agents/broadcasting/`은 프로젝트 내부 구현 모듈이고, `.agents/skills/`는 Codex가 작업 전에 발견하고 필요할 때 로드하는 Skill 위치입니다.

### `agents/`

팀별 에이전트 로직을 둡니다.

현재 우선순위는 `agents/broadcasting/`입니다.

- `agents/broadcasting/agents/`: Input Parser, Content Strategy, Insight, Platform Writer, Self Reflection, Revision, Publish 서브에이전트
- `agents/broadcasting/pipeline/`: 콘텐츠 생성 파이프라인
- `agents/broadcasting/prompts/`: 페르소나/플랫폼별 프롬프트
- `agents/broadcasting/prompts/templates/`: 실제 후츠릿 글에서 추출한 채널별 작성 템플릿
- `agents/broadcasting/publishers/`: 블로그, LinkedIn, Discord 뉴스레터 배포/발송 어댑터
- `agents/broadcasting/schemas/`: 메타데이터, 품질 평가, 발송 상태 스키마

`pipeline/`은 단일 두뇌가 모든 글을 한 번에 만드는 위치가 아니라, `agents/`의 서브에이전트를 순서대로 호출하는 오케스트레이터입니다. 전략과 인사이트는 순차 실행하고, Blog/LinkedIn/Discord Writer Agent는 병렬 실행합니다.

강의운영팀은 `agents/education/` 아래에 둡니다.

- `agents/education/slide-maker/`: 강의 슬라이드 제작용 베이스 템플릿, 디자인 규칙, 슬라이드 패턴
- `agents/education/slide-maker/assets/base-template.html`: 단일 HTML 슬라이드의 기준 CSS와 JavaScript
- `agents/education/slide-maker/references/`: `ppt-maker`에서 가져온 디자인 규칙과 14개 슬라이드 패턴

강의 자료 슬라이드는 기존 `ppt-maker` 시스템과 동일하게 순수 HTML/CSS/JavaScript 단일 파일로 생성합니다.

### `apps/`

실행 앱을 둡니다.

현재는 `apps/discord-bot/`을 Discord 보고, 진행 알림, 명령 입력 인터페이스로 사용합니다. MVP에서는 `broadcasting` 채널 메시지를 감지해 콘텐츠배포팀 파이프라인을 실행합니다.

### `automations/`

n8n 같은 외부 자동화 워크플로우를 둡니다.

정기 실행, 단순 알림 라우팅, 외부 서비스 연결처럼 n8n이 더 효율적인 작업을 여기에 보관합니다.

### `configs/`

비밀값이 없는 설정 예시를 둡니다.

실제 API 키, 토큰, 계정 정보는 커밋하지 않고 환경변수나 로컬 설정 파일로 관리합니다.

### `docs/`

사람이 읽는 전략, 정책, 설계, 리포트 문서를 둡니다.

- `docs/architecture/`: 시스템 구조 문서
- `docs/content/`: 콘텐츠 전략과 편집 기준
- `docs/education/`: 강의 자료 제작 기준과 슬라이드 시스템 문서
- `docs/operations/`: 운영 정책과 승인 규칙
- `docs/reports/`: 오피스 운영 리포트
- `docs/strategy/`: 페르소나, 채널 전략, 포지셔닝

### `outputs/`

에이전트가 생성한 결과물을 팀별로 저장합니다.

현재 활성화된 산출물 영역은 콘텐츠배포팀과 강의운영팀입니다.

```text
outputs/broadcasting/
├── drafts/
├── final/
├── approvals/
└── logs/

outputs/education/
├── slides/
├── logs/
└── sources/
```

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

강의운영팀 슬라이드 결과물은 아래에 저장합니다.

```text
outputs/education/slides/{lecture-slug}-slides.html
```

원본 강의 자료는 `outputs/education/sources/`에 로컬 보관할 수 있으며 Git에 올리지 않습니다.

## 승인 정책

기본 원칙은 **자율 실행, 위험 작업만 승인**입니다.

승인 없이 진행 가능한 작업:

- 콘텐츠 초안 생성
- 로컬 파일 저장
- 내부 Discord 보고
- 테스트 실행
- 코드 수정과 개선
- 테스트 통과까지 반복 수정
- 안전하게 설정된 배포

승인이 필요한 작업:

- LinkedIn 공개 게시
- 자동 배포가 허용되지 않은 블로그 게시
- 결제, 광고비, 구독, 구매
- 외부 콘텐츠 삭제
- 계정, DNS, 결제, 권한, 토큰, 운영 인프라 변경

## 콘텐츠배포팀 대상 채널

초기 대상 채널은 다음과 같습니다.

- 블로그
- LinkedIn
- Discord 뉴스레터

다음 구현 목표는 실제 배포 흐름입니다.

```text
티스토리 공개 발행
-> 실제 블로그 URL 확보
-> LinkedIn 원고의 [블로그 링크]를 실제 URL로 치환
-> LinkedIn API 공개 발행
-> Discord 뉴스레터 발송
-> Discord에 플랫폼별 링크 보고
```

티스토리 Open API는 공식 종료 안내가 있으므로 블로그 배포는 Playwright 브라우저 자동화로 처리합니다. 기본값은 저장된 로그인 세션을 격리된 headless Chromium 컨텍스트에 주입하는 방식이며, 실제 사용 중인 Brave 프로필을 직접 조작하거나 로그아웃하지 않습니다.

LinkedIn은 Posts API를 사용해 공개 게시합니다. 게시에는 `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_AUTHOR_URN`, `LINKEDIN_VERSION`이 필요합니다.

LinkedIn Access Token은 로컬 callback 서버로 발급합니다.

```bash
.venv/bin/python scripts/linkedin_oauth_server.py
```

## 구현 원칙

각 기능에 가장 적합한 도구를 사용합니다.

- Python: 콘텐츠 파이프라인, 파일 처리, AI orchestration, 통합 스크립트
- OpenAI SDK: 콘텐츠 생성, Self Reflection, Revision의 Responses API 호출
- Node.js/TypeScript: Discord 봇, API 서버, 대시보드
- n8n: 정기 실행, 승인 라우팅, 단순 외부 연동
- LangChain 등: 에이전트 메모리, 검색, 도구 호출, 복잡한 멀티스텝 작업이 필요할 때만 사용

한 가지 기술 스택을 모든 팀에 강제하지 않습니다.

## 실행 방법

로컬에서 메모 하나를 콘텐츠 패키지로 생성하려면 아래 명령을 사용합니다.

```bash
.venv/bin/python -m agents.broadcasting.pipeline.run_once --text "AI 에이전트 시대에는 프롬프트보다 하네스 설계가 더 중요해진다."
```

Discord 봇을 실행하려면 먼저 Discord 봇 의존성을 설치합니다.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r apps/discord-bot/requirements.txt
.venv/bin/python apps/discord-bot/bot.py
```

봇이 실행 중이면 Discord `broadcasting` 채널에 적은 일반 메시지가 콘텐츠 생성 요청으로 처리됩니다.

현재 Discord 봇은 `broadcasting` 채널에서 입력을 받고 진행 상황과 평가 내용을 보고합니다. 블로그 원고와 LinkedIn 원고 미리보기는 `broadcasting` 채널에 남기고, 독자용 Discord 뉴스레터 본문은 `DISCORD_NEWSLETTER_CHANNEL_ID`로 지정한 뉴스레터 채널에 발송합니다. 생성 결과는 `outputs/broadcasting/drafts/`와 `outputs/broadcasting/final/`에 함께 저장됩니다.

봇은 메시지를 받자마자 `글 작성중입니다` 응답을 보내고, Discord 기본 typing 표시와 봇 활동 상태를 켭니다. 이후 Input Parser, Content Strategy Agent, Insight Agent, 병렬 Platform Writer Agents, Self Reflection Agent, Revision Agent, Publish Agent 결과를 이모지와 함께 메시지용으로 요약합니다. 평가 점수가 기준 미달이면 최대 3회까지 Revision Agent가 기준 미달 채널을 중심으로 수정하고, 회차별 점수와 수정 피드백을 공유한 뒤 최종 배포물을 발송합니다.

Publish Agent는 티스토리, LinkedIn, Discord 뉴스레터 채널별 배포 상태를 구조화하고, 전체 배포 시도가 끝난 뒤 Discord에 하나의 최종 결과 메시지로 보고합니다. 준비되지 않은 채널은 외부 게시 성공으로 표시하지 않습니다.

## 다음 구현 순서

1. Discord 봇을 백그라운드 프로세스 또는 서비스로 실행
2. 티스토리 Playwright Publisher 어댑터 연결
3. LinkedIn Posts API Publisher 어댑터 연결
4. Discord 수정 요청을 특정 패키지와 채널에 반영하는 Revision 명령 추가
5. 승인/수정 데이터를 반영한 Self Reflection 기준 보정

## 연결 테스트

`.env` 값을 설정한 뒤 아래 명령으로 Discord와 OpenAI 연결 상태를 확인합니다.

```bash
python3 scripts/check_integrations.py --all
```

토큰 값은 출력하지 않고, Discord 봇 토큰, `broadcasting` 채널 접근, Discord Webhook 보고, OpenAI Responses API 호출만 검증합니다.

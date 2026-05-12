# 폴더 구조

이 문서는 후츠릿 AI 오피스의 현재 폴더 구조와 각 폴더의 책임을 설명합니다.

## 기본 원칙

- `agents/`: 팀별 에이전트 로직과 도메인 워크플로우
- `apps/`: Discord 봇, 대시보드처럼 실행되는 앱
- `automations/`: n8n 등 외부 자동화 워크플로우
- `configs/`: 비밀값이 없는 설정 예시
- `docs/`: 사람이 읽는 전략, 정책, 설계, 운영 문서
- `outputs/`: 에이전트가 생성한 결과물
- `scripts/`: 로컬 보조 스크립트
- `tests/`: 프로젝트 테스트

## 현재 구조

```text
.
├── AGENTS.md
├── README.md
├── .env.example
├── .gitignore
├── .agents/
│   └── skills/
│       ├── chutzrit-broadcasting/
│       └── chutzrit-education-slides/
├── configs/
│   └── channels.example.yaml
├── agents/
│   ├── broadcasting/
│   │   ├── README.md
│   │   ├── agents/
│   │   ├── pipeline/
│   │   ├── prompts/
│   │   │   └── templates/
│   │   ├── publishers/
│   │   └── schemas/
│   ├── chief-of-staff/
│   ├── research/
│   ├── dev/
│   ├── education/
│   │   └── slide-maker/
│   └── youtube/
├── apps/
│   └── discord-bot/
│       └── README.md
├── automations/
│   └── n8n/
│       ├── README.md
│       └── workflows/
├── docs/
│   ├── architecture/
│   ├── content/
│   ├── education/
│   ├── operations/
│   ├── reports/
│   └── strategy/
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

## 문서 역할

### `README.md`

사람이 프로젝트와 하위 모듈을 이해하기 위한 안내 문서입니다.

이 프로젝트의 모든 `README.md`는 한글로 작성합니다.

### `AGENTS.md`

에이전트가 따라야 하는 프로젝트 운영 규칙입니다.

기획, 에이전트 구조, 폴더 구조, 산출물 구조, 승인 정책이 바뀌면 관련 문서도 함께 업데이트합니다.

### `.agents/skills/`

Codex 공식 Agent Skills 저장 위치입니다.

Codex는 현재 작업 폴더부터 저장소 루트까지의 `.agents/skills`를 스캔합니다.

후츠릿 업무를 재사용 가능한 Codex Skill로 정의한 파일은 아래 위치에 둡니다.

```text
.agents/skills/chutzrit-broadcasting/SKILL.md
.agents/skills/chutzrit-education-slides/SKILL.md
```

주의할 점:

- `agents/broadcasting/`은 프로젝트 내부 콘텐츠배포팀 구현 모듈입니다.
- `.agents/skills/`는 Codex가 작업 시작 시 발견하고 필요할 때 로드하는 Skill 위치입니다.
- `agents/broadcasting/SKILL.md`는 공식 repo-scoped Skill 발견 위치가 아닙니다.

## 강의운영팀 구조

강의운영팀은 `agents/education/`에 둡니다.

- `slide-maker/assets/base-template.html`: 단일 HTML 강의 슬라이드의 기준 CSS와 JavaScript
- `slide-maker/references/design-rules.md`: 다크모드 디자인 시스템과 컴포넌트 규칙
- `slide-maker/references/patterns.md`: 14가지 슬라이드 패턴과 HTML 구조

강의 자료 슬라이드 제작은 기존 `ppt-maker`의 웹 슬라이드 시스템을 유지합니다. 새 프레임워크나 빌드 시스템을 만들지 않고, 완성된 결과물을 `outputs/education/slides/`에 저장합니다.

## 콘텐츠배포팀 구조

현재 MVP는 `agents/broadcasting/`에 집중합니다.

- `agents/`: 콘텐츠배포팀 실제 서브에이전트. Input Parser, Content Strategy, Insight, Platform Writer, Self Reflection, Revision, Publish를 역할별 모듈로 분리
- `pipeline/`: 서브에이전트 오케스트레이션, 병렬 Writer 실행, 품질 게이트, 저장
- `prompts/`: 공통 프롬프트와 템플릿
- `prompts/templates/`: 실제 후츠릿 글에서 추출한 채널별 작성 템플릿
- `publishers/`: 실제 플랫폼별 배포 어댑터. Publish Agent가 정한 순서에 따라 티스토리 Playwright 발행, LinkedIn Posts API 게시, Discord 발송 결과 기록을 담당
- `schemas/`: 메타데이터, 승인 상태, 배포 상태 스키마

콘텐츠배포팀의 처리 흐름:

```text
단편 메모 입력
-> 콘텐츠 전략 Agent
-> 인사이트 Agent
-> 플랫폼별 Writer Agent 병렬 작성
-> Self Reflection Agent 평가
-> Revision Agent 수정 루프
-> 품질 기준 통과
-> Publish Agent 배포 상태 판단 및 활성화된 외부 배포 실행
-> 승인 또는 Discord 자동 발송/외부 배포
-> Discord 보고
```

`pipeline/`은 더 이상 단일 LLM 호출로 전략, 인사이트, 전체 원고를 한 번에 만드는 구조가 아니다. 각 서브에이전트가 독립 프롬프트와 출력 스키마를 가지고 실행되며, 플랫폼 Writer Agent는 병렬로 실행된다.

## Discord 봇

`apps/discord-bot/`은 Discord 보고, 명령 입력, 승인 요청, 수정 요청을 담당합니다.

Discord 채널명은 에이전트 팀 이름과 동일하게 설정합니다.

현재 콘텐츠배포팀의 팀 채널명은 `broadcasting`이며, MVP에서는 이 채널 하나가 입력, 보고, 승인 요청을 모두 담당합니다.

MVP에서는 webhook 보고와 Discord 채널 자동 발송부터 시작하고, 이후 slash command와 실제 플랫폼 배포를 추가합니다.

## n8n 자동화

`automations/n8n/`은 n8n 워크플로우 내보내기 파일을 보관합니다.

n8n은 정기 실행, 알림 라우팅, 승인 전달처럼 흐름 연결이 중요한 작업에 사용합니다.

콘텐츠 생성 로직과 플랫폼별 글 변환은 코드로 처리합니다.

## 산출물 구조

산출물은 코드 폴더 안에 저장하지 않습니다.

팀별로 `outputs/` 아래에 저장합니다.

현재 활성화된 팀 산출물은 콘텐츠배포팀과 강의운영팀입니다.

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

최종본은 아래 위치에 저장합니다.

```text
outputs/broadcasting/final/YYYY-MM-DD-slug/
```

승인 상태는 아래 위치에 저장합니다.

```text
outputs/broadcasting/approvals/YYYY-MM-DD-slug.json
```

강의운영팀 슬라이드 결과물은 아래 위치에 저장합니다.

```text
outputs/education/slides/{lecture-slug}-slides.html
```

강의 원본 자료는 아래 위치에 로컬 보관할 수 있으며 Git에 올리지 않습니다.

```text
outputs/education/sources/
```

## 확장 규칙

다른 팀은 실제 구현을 시작할 때 필요한 만큼만 구조를 추가합니다.

불필요하게 무거운 프레임워크 구조를 먼저 만들지 않습니다.

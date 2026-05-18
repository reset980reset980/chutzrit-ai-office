# 후츠릿 AI 오피스 에이전트 규칙

이 문서는 후츠릿 AI 오피스에서 Codex와 자동화 에이전트가 따라야 하는 기준 문서입니다.

`README.md`는 사람이 읽는 안내 문서입니다. 에이전트의 작업 규칙, 승인 기준, 자율 실행 기준, 문서 작성 규칙은 이 `AGENTS.md`를 기준으로 판단합니다.

## 프로젝트 정체성

후츠릿 AI 오피스는 Codex와 자동화 에이전트로 운영되는 24시간 무인 AI 오피스입니다.

사용자는 CEO이자 디렉터입니다. 에이전트는 실행 직원입니다.

기본 원칙:

- 사용자는 방향을 제시한다.
- Codex와 에이전트는 실행한다.
- Telegram는 보고, 수정 요청, 명령 입력을 담당하는 중앙 관제실이다.
- 외부 리스크가 큰 작업이 아니라면 에이전트는 스스로 구현, 테스트, 개선, 보고한다.

## 문서 작성 규칙

- 모든 `README.md`는 사람이 읽는 안내 문서로 작성한다.
- 이 프로젝트의 모든 `README.md`는 한글로 작성한다.
- 에이전트 운영 규칙은 `AGENTS.md`에 작성한다.
- 대화 중 기획, 에이전트 구조, 폴더 구조, 산출물 구조, 승인 정책이 바뀌면 사용자가 따로 지시하지 않아도 관련 문서를 함께 업데이트한다.
- 자동 업데이트 대상은 변경 범위에 따라 `AGENTS.md`, 루트 `README.md`, 해당 하위 폴더의 `README.md`, `docs/` 문서, 설정 예시 파일이다.
- 문서 업데이트 후에는 어떤 파일이 수정됐는지만 간결하게 보고한다.
- 사람이 읽는 전략, 정책, 설계 문서는 `docs/` 아래에 둔다.
- 생성된 결과물은 `outputs/` 아래에 팀별로 저장한다.
- 코드와 에이전트 로직은 `agents/`, `apps/`, `scripts/`, `automations/`에 둔다.
- 산출물을 에이전트 코드 폴더 안에 섞어 저장하지 않는다.
- `SKILL.md`는 Codex 공식 Agent Skills 포맷이다. 재사용 가능한 Codex 작업 능력과 워크플로우를 정의할 때 사용한다.
- 저장소 범위 Skill은 `.agents/skills/<skill-name>/SKILL.md`에 둔다. Codex는 현재 작업 폴더부터 저장소 루트까지의 `.agents/skills`를 스캔한다.
- `agents/broadcasting/SKILL.md`처럼 임의의 구현 폴더에 둔 `SKILL.md`는 Codex Skill로 자동 발견되는 위치가 아니다.
- 프로젝트 내부 런타임 에이전트나 파이프라인 단계의 규칙은 기본적으로 `AGENTS.md`, 해당 모듈 `README.md`, `prompts/`, `schemas/`에 나누어 기록한다.
- 후츠릿 콘텐츠 작업을 Codex의 재사용 Skill로 만들 때는 `.agents/skills/chutzrit-broadcasting/SKILL.md`를 만든다.
- 후츠릿 오피스 대시보드 작업을 Codex의 재사용 Skill로 만들 때는 `.agents/skills/chutzrit-office-dashboard/SKILL.md`를 만든다.

## 현재 MVP 우선순위

첫 구현 대상은 **콘텐츠배포팀**입니다.

MVP 목표:

1. Telegram의 `broadcasting` 팀 채널에 작성된 자연어 메모나 링크를 입력으로 받는다.
2. 입력을 여러 플랫폼용 콘텐츠로 변환한다.
3. 초안과 최종 결과물을 `outputs/broadcasting/` 아래에 저장한다.
4. MVP 범위에서는 생성된 원고를 Telegram 채널에 바로 발송한다.
5. 현재 코드 상태에서는 외부 공개 게시 어댑터가 아직 완전히 연결되지 않았으면 Telegram 자동 발송을 최종 처리로 본다.
6. 외부 공개 게시 어댑터가 연결된 채널은 승인 없이 자동 배포한다. 결제와 계정 변경처럼 리스크가 큰 작업만 승인 후 진행한다.
7. 작업 시작, Telegram 기본 typing 표시, 입력 분석, 에이전트별 결과 요약, 품질 평가, 자동 발송, 배포, 실패, 완료를 Telegram로 보고한다.
8. 콘텐츠 생성이나 Revision Agent 실행 중에는 Telegram 봇을 재시작하지 않는다. 종료 신호가 들어와도 현재 작업을 완료한 뒤 종료하도록 구현하고, 강제 종료로 저장 전 작업을 끊지 않는다.

초기 MVP는 자동 리서치 기반 주제 선정이 아니라 **사용자가 Telegram에 자연스럽게 작성한 메모, 링크, 생각을 콘텐츠로 확장하는 방식**으로 시작한다.

초기 입력 원칙:

- `broadcasting` 팀 채널에 작성된 모든 일반 메시지를 콘텐츠 생성 요청으로 본다.
- 사용자는 `[메모]`, `[링크]`, 채널명, 명령어를 붙이지 않는다.
- 메시지 안에 URL이 있으면 링크 입력으로 자동 감지하고, 함께 적힌 사용자의 생각을 우선 맥락으로 사용한다.
- URL 입력은 Input Parser 단계에서 제목, 설명, 핵심 내용을 간략히 정리해 Telegram에 먼저 보고한다.
- URL이 없으면 원본 메모로 처리한다.
- 기본 대상 채널은 블로그, LinkedIn, Telegram 뉴스레터다.

이유:

- 사용자의 톤과 페르소나를 더 정확히 반영할 수 있다.
- 품질 기준을 빠르게 학습할 수 있다.
- 배포 파이프라인을 먼저 안정화할 수 있다.
- 잘못된 주제 선정이나 과도한 자동화를 줄일 수 있다.

## 조직 구조

### 비서실

목표: CEO 효율 극대화와 전 부서 업무 조율.

역할:

- 매일 아침 우선순위 브리핑
- 저녁 성과 요약
- 팀별 진행 상황 감시
- 병목 현상 확인
- 스케줄과 할 일 우선순위 조정
- Telegram 보고

기본 흐름:

```text
전 부서 감시 -> 진행도 분석 -> 우선순위 조정 -> Telegram 보고
```

### 리서치팀

목표: 글로벌 AI 기술 변화와 트렌드를 포착해 의사결정 자료를 제공한다.

역할:

- 지정된 소스 모니터링
- 관심 정보 선별
- 핵심 요약 리포트 생성
- 출처와 신뢰도 표시

기본 흐름:

```text
타겟 스캔 -> 데이터 추출 -> 필터링 -> Telegram 브리핑
```

### 개발팀

목표: 아이디어를 실제 서비스, 코드, 자동화로 구현하고 배포한다.

역할:

- 기능별 최적 기술 선택
- 코드 작성
- 테스트 작성과 실행
- 테스트 통과까지 반복 수정
- 안전한 배포
- 배포 결과 Telegram 보고

자율성 규칙:

- 코드 구현, 테스트 수정, 로컬 리팩터링, 안전한 배포는 승인 없이 진행한다.
- 테스트가 실패하면 사용자에게 멈춰 묻지 말고 원인을 찾아 수정한다.
- 배포가 완료되면 반드시 Telegram로 보고한다.

### 콘텐츠배포팀

목표: 하나의 소스를 플랫폼별 콘텐츠로 변환하고 배포한다.

현재 MVP 대상 팀입니다.

역할:

- 단편 메모를 콘텐츠 초안으로 확장
- Telegram `broadcasting` 팀 채널의 새 메시지를 감지해 자동화 실행
- 메시지의 URL 포함 여부로 링크 입력 여부를 자동 감지
- 글쓰기 전에 핵심 메시지, 독자 타깃, 주장, 플랫폼별 방향을 설계
- 단순 요약이 아니라 후츠릿다운 실무 인사이트를 추가
- 플랫폼별 톤, 길이, CTA, 구조 변환
- 플랫폼별 Writer Agent는 `agents/broadcasting/prompts/templates/`의 채널별 템플릿을 참고한다.
- 블로그는 무조건 이론형으로 쓰지 않고, 입력 메시지에 따라 구현형, 개념 설명형, 인사이트형 중 적절한 구조를 선택한다.
- 블로그는 무조건 문어체 평서형 반말로 작성하고, 존댓말 종결이나 대화체 종결, 소제목 없는 줄글은 품질 기준 미달로 본다.
- 블로그 문장 종결은 `다`, `이다`, `한다`, `된다`, `있다`, `없다` 중심으로 쓴다.
- 블로그에서 `하면 돼`, `해봐`, `거야`, `거든`, `잖아` 같은 대화체를 쓰지 않는다.
- 공개 초안에는 `[후츠릿 인사이트]`, `후츠릿의 인사이트`, `실무 적용 포인트` 같은 내부 라벨을 쓰지 않는다.
- 공개 초안의 이모지는 가독성 보조 장치로만 제한적으로 쓴다.
- 이모지는 `✅`, `⚠️`, `🔍`, `🧩`, `🚀`, `📌`, `🔗` 정도를 우선 사용한다.
- 블로그는 전체 3~5개, LinkedIn은 2~4개, Telegram 뉴스레터는 2~5개 안쪽으로 제한한다.
- 모든 문장이나 모든 소제목에 이모지를 붙이지 않는다.
- 블로그는 입력에 참고 링크가 있으면 맨 마지막에 `참고자료` 섹션을 넣는다.
- 기술 구현형 블로그는 입력에 GitHub 링크가 있을 때만 GitHub 저장소 링크를 넣는다.
- LinkedIn은 간결한 제목 한 줄과 구조화된 짧은 본문으로 작성하고, 블로그 전문 링크로 유입시키는 목적을 둔다.
- Telegram 초안은 내부 보고가 아니라 타깃 독자용 Telegram 뉴스레터로 작성한다. 존댓말, Markdown 제목, 참고 링크 하단 배치를 지킨다.
- 플랫폼별 Writer Agent를 독립적으로 실행해 병렬 초안 생성
- Self Reflection Agent로 품질 평가 후 기준 미달이면 수정 루프 실행
- 품질 기준 통과 후 Visual Strategy Agent, Image Prompt Agent, Image Generator Agent, Visual Quality Agent로 대표 이미지를 생성하고 검수
- 모든 초안과 최종본 저장
- Telegram 채널 자동 발송
- Publish Agent는 별도 어댑터가 연결된 채널을 실제 외부 플랫폼에 자동 배포
- Telegram 결과 보고

대상 채널:

- 블로그
- LinkedIn
- Telegram 뉴스레터

기본 흐름:

```text
Telegram `broadcasting` 팀 채널 메시지 수신
-> URL 포함 여부 자동 감지
-> 원문/링크/사용자 생각 정리
-> 콘텐츠 전략 수립
-> 후츠릿 인사이트 추가
-> 플랫폼별 Writer Agent 병렬 작성
-> Self Reflection 평가
-> 기준 미달 시 Revision Agent 수정
-> 품질 기준 통과
-> 이미지 전략 수립
-> 채널별 이미지 프롬프트 작성
-> 초안 저장
-> 저장된 패키지 기준 대표 이미지 생성 및 시각 품질 평가
-> 품질 평가
-> Publish Agent 실행
-> Telegram 자동 발송 또는 외부 플랫폼 자동 배포
-> Telegram 보고
```

콘텐츠배포팀 내부 에이전트:

- Content Strategy Agent: 핵심 메시지, 독자 타깃, 글의 주장, 플랫폼별 방향을 결정한다.
- Insight Agent: 후츠릿다운 관점, 실무 적용 포인트, 예시, 비유, 주의점을 추가한다.
- Platform Writer Agents: 플랫폼별 문법에 맞게 독립적으로 글을 작성한다.
- Self Reflection Agent: 완성본을 평가하고 수정 피드백을 만든다.
- Revision Agent: 평가 피드백에 맞춰 글을 수정한다.
- Final Quality Gate: 기준 점수 통과 여부를 판단하고 자동 발송 또는 배포 단계로 넘긴다.
- Visual Strategy Agent: 글의 핵심 주장과 채널 목적에 맞는 이미지 콘셉트를 결정한다.
- Image Prompt Agent: 이미지 생성 API에 넣을 채널별 영어 프롬프트와 비율을 만든다.
- Image Generator Agent: OpenAI 이미지 생성 클라이언트로 대표 이미지를 만들고 `outputs/broadcasting/*/visuals/`에 저장한다.
- Visual Quality Agent: 이미지 메타데이터와 프롬프트가 글, 채널, 후츠릿 톤에 맞는지 평가한다.
- Publish Agent: Final Quality Gate 통과 후 Telegram 발송, 티스토리 공개 발행, LinkedIn 공개 게시, 발행 링크 보고를 담당한다.

구현 구조:

- `agents/broadcasting/`은 콘텐츠배포팀 팀 폴더다.
- 실제 서브에이전트는 `agents/broadcasting/agents/` 아래에 둔다.
- `agents/broadcasting/pipeline/`은 서브에이전트를 순서대로 호출하는 오케스트레이션, 품질 게이트, 저장 로직을 담당한다.
- 전략과 인사이트는 순차 실행한다.
- Blog Writer Agent, LinkedIn Writer Agent, Telegram Newsletter Writer Agent는 병렬 실행한다.
- Self Reflection 결과가 기준 미달이면 Revision Agent는 기준 미달 채널을 우선 수정한다.
- 이미지 생성은 `IMAGE_GENERATION_ENABLED=true`일 때만 실행하며, 텍스트 품질 게이트 통과 후 저장된 패키지를 기준으로 처리한다.
- Publish Agent는 외부 게시 조건이 준비되지 않으면 성공으로 표시하지 않고 `not_connected`, `dependency_missing`, `blocked_until_blog_url`, `failed` 같은 상태를 남긴다.

플랫폼별 Writer Agent:

- Blog Writer Agent
- LinkedIn Writer Agent
- Telegram Newsletter Writer Agent

Self Reflection 기준:

- 90점 이상: 자동 발송 또는 배포 단계로 이동
- 기본은 1회 생성 후 평가하고, 기준 미달이면 최대 3회까지 Revision Agent를 자동 실행한다.
- 평가 루프에만 기대지 않고, 최초 생성 프롬프트에서 채널별 기준을 최대한 만족해야 한다.
- 각 수정 루프는 회차, 현재 점수, 문제 파트, 수정할 사항을 Telegram에 중간 보고한다.
- 최대 수정 루프 이후에도 기준 미달이면 기준 미달 상태를 명확히 알리고 현재 결과를 저장 및 발송한다.

승인 기준:

- 초안 생성은 승인 없이 진행한다.
- Telegram 뉴스레터 본문은 독자용 뉴스레터 채널에 자동 발송한다.
- 티스토리와 LinkedIn 배포 어댑터가 연결되면 티스토리 공개 발행, LinkedIn API 공개 게시까지 자동 실행한다.
- 티스토리 발행 URL을 먼저 확보한 뒤 LinkedIn 원고의 `[블로그 링크]`를 실제 URL로 치환한다.
- 사용자가 자동 배포를 허용한 채널의 콘텐츠 공개 게시도 승인 없이 진행한다.
- 결제, 광고비, 구매, 구독, 계정 변경은 반드시 승인받는다.

Publish Agent 실행 규칙:

- 현재 어댑터가 연결되지 않은 상태에서는 외부 게시 성공으로 표시하지 않고, 최종 원고를 Telegram에 발송한 뒤 `외부 API 배포 미연결` 상태를 보고한다.
- 티스토리는 Open API가 아니라 Playwright 브라우저 자동화로 발행한다.
- 티스토리 발행은 `TISTORY_AUTO_PUBLISH=true`, `TISTORY_PUBLISH_MODE=public`, 로그인 세션 저장 상태가 준비된 경우에만 실행한다.
- 블로그 저장 파일은 Markdown으로 유지하되, 티스토리 WYSIWYG 에디터에는 발행 시점에 HTML로 변환해 입력한다. 공개 글에서 `## 소제목` 같은 Markdown 문법이 텍스트로 보이면 배포 품질 실패로 본다.
- 티스토리 발행 런타임은 Chrome Playwright 채널만 사용한다. 저장된 세션 파일을 격리된 headless Chrome 컨텍스트에 주입해 실행하며, 실제 사용 중인 브라우저 프로필을 직접 조작하거나 로그아웃하지 않는다.
- 티스토리 세션 저장과 디버깅도 Chrome Playwright 채널만 사용한다. Brave, Safari, 실제 Chrome 일상 프로필로 티스토리 자동화를 실행하지 않는다.
- 티스토리 발행 준비 여부는 세션 파일 존재만으로 판단하지 않는다. `PLAYWRIGHT_STORAGE_STATE`가 있어도 실제로 `TISTORY_MANAGE_URL`에 접속해 로그인 유지 상태가 확인되어야 준비 완료로 본다.
- 사용자가 "Telegram에 테스트 메시지를 보내도 되는지", "봇 띄워도 되는지", "콘텐츠팀 테스트해도 되는지"를 물으면 반드시 Telegram 입력 수신, Telegram Webhook/채널 보고, OpenAI 호출, 티스토리 Playwright 세션 유효성, 티스토리 실제 공개 발행 가능 여부를 검증한 뒤 답한다.
- 위 검증 중 하나라도 실패하면 "보내도 된다"고 답하지 않고, 실패 항목과 조치 명령을 먼저 보고한다.
- Playwright나 브라우저 자동화는 절대 사용자의 실제 Brave, Chrome, Chromium, Safari 일상 프로필 디렉터리에 연결하지 않는다.
- `launch_persistent_context`에 실제 브라우저 사용자 데이터 디렉터리를 넘기거나, 실제 프로필을 가리키는 `--user-data-dir`를 사용하는 구현은 금지한다.
- 자동화는 쿠키, 캐시, localStorage, sessionStorage, IndexedDB, 방문 기록, 사이트 데이터를 삭제하지 않는다.
- 자동화는 로그아웃, 계정 전환, 세션 초기화, 브라우징 데이터 삭제 UI를 누르지 않는다.
- 세션 저장이나 visible 디버깅이 필요하면 `outputs/broadcasting/session/chrome-playwright-profile/` 아래 전용 격리 Chrome 프로필만 사용한다.
- 티스토리 Playwright 실행 중 UI 변경, CAPTCHA, 2FA, 로그인 만료가 발생하면 발행 실패로 기록하고 LinkedIn 공개 게시를 중단한다.
- 티스토리 로그인 만료는 제목 입력 영역 실패처럼 일반 UI 오류로 숨기지 않는다. `session_expired` 상태로 기록하고 Telegram 최종 보고에 세션 갱신 필요를 명시한다.
- LinkedIn은 Posts API로 공개 게시한다. LinkedIn API는 임시저장 흐름이 아니라 공개 발행 흐름이다.
- LinkedIn 게시 전에는 반드시 티스토리 실제 URL을 확보하고 `[블로그 링크]` 자리표시자를 실제 URL로 치환한다.
- 티스토리 발행에 실패해 실제 블로그 URL이 없으면 LinkedIn 공개 게시를 기본 중단한다. 사용자가 명시적으로 허용하지 않는 한 `[블로그 링크]` 자리표시자 그대로 LinkedIn에 게시하지 않는다.
- Telegram 뉴스레터 본문은 `TELEGRAM_NEWSLETTER_CHANNEL_ID`로 지정한 독자용 `뉴스레터` 채널에 자동 발송한다. `broadcasting` 채널은 입력과 운영 보고용이다.
- 배포 보고는 채널별 즉시 보고가 아니라 멀티플랫폼 전체 배포 시도 후 최종 결과를 하나의 메시지로 통합해 보낸다.
- 최종 배포 보고에는 블로그 URL, LinkedIn URL, Telegram 메시지 링크, 실패 또는 중단 사유, 산출물 경로를 함께 담는다.
- 일부 채널만 성공하면 성공/실패를 채널별로 나누어 보고하고, 실패 채널은 원인과 재시도 조건을 함께 적는다.

### 강의운영팀

목표: 최신 기술을 실무 학습 자료로 전환한다.

역할:

- 실습 예제 업데이트
- PPT형 강의 슬라이드와 학습 보조 자료 제작
- 실습 코드 생성과 검증
- 수강생 기술 질의 대응

현재 강의 자료 슬라이드 제작은 `ppt-maker`의 웹 슬라이드 시스템을 후츠릿 AI 오피스 강의운영팀 구조로 재구성해 사용한다.

강의 슬라이드 제작 기준:

- 슬라이드 산출물은 `.pptx`가 아니라 단일 HTML/CSS/JavaScript 웹 프레젠테이션으로 만든다.
- `agents/education/slide-maker/assets/base-template.html`을 베이스 템플릿으로 사용한다.
- `agents/education/slide-maker/references/design-rules.md`와 `agents/education/slide-maker/references/patterns.md`의 코드, 디자인 규칙, 14개 슬라이드 패턴을 유지한다.
- 웹 PPT 작성 전 `agents/education/slide-maker/references/template-source/`의 템플릿 예시 HTML과 참고 이미지를 확인한다.
- 강의 슬라이드 작업용 Codex Skill은 `.agents/skills/chutzrit-education-slides/SKILL.md`에 둔다.
- 강의 원본 자료는 필요할 때 `outputs/education/sources/`에 로컬 보관하되 Git에 올리지 않는다.
- 완성된 슬라이드는 `outputs/education/slides/`에 저장한다.
- 강의 자료 생성 시 먼저 강의명, 대상, 챕터 구조, 핵심 메시지, 실습 예제를 분석하고 슬라이드 구성안을 만든다.
- 원본 시스템과 동일하게 구성 확인 후 HTML을 생성하는 흐름을 기본으로 한다.

기본 흐름:

```text
기술 발굴 -> 강의 원본 분석 -> 슬라이드 구성안 작성 -> HTML 슬라이드 제작 -> 실습 코드 검증 -> Telegram 보고
```

### 오피스 대시보드 에이전트

목표: 후츠릿 AI 오피스가 실제로 돌아가고 있다는 것을 라이브 강의용 웹 대시보드로 시각화한다.

역할:

- 후츠릿 AI 오피스 운영 대시보드 설계
- 콘텐츠배포팀 서브에이전트 상태 시각화
- 에이전트별 아바타, 상태 배지, 클릭 상세 패널 구성
- Codex 토큰 사용량 실제 소스 연결 여부 표시
- 하단 상태바, 전체 진행률, 클릭 가능한 산출물 상세 패널 구성
- `outputs/broadcasting/` 산출물 스냅샷과 `outputs/broadcasting/logs/current-status.json` 연동 구조 분리

현재 범위:

- 첫 버전은 실제 구현 완료된 `broadcasting` 콘텐츠배포팀만 표시한다.
- 다른 팀은 해당 팀 런타임 구현이 완료된 뒤 추가한다.

구현 위치:

- 대시보드 에이전트 기준 문서: `agents/office-dashboard/`
- 실제 웹앱: `apps/office-dashboard/`
- 설계 문서와 참고 이미지: `docs/dashboard/`
- Codex Skill: `.agents/skills/chutzrit-office-dashboard/SKILL.md`

참고 이미지:

- 전체 오피스 콘셉트: `docs/dashboard/references/office-concept.png`
- 에이전트 아바타 방향: `docs/dashboard/references/agent-avatars.png`

기본 화면 기준:

- 랜딩페이지가 아니라 실제 운영 대시보드로 만든다.
- 하나의 큰 오피스 공간 안에 접수 데스크, 전략 회의 테이블, 작성 책상, 검수 책상, 수정 책상, 배포 보드를 자연스럽게 배치한다.
- 상태는 `WORKING`, `IDLE`, `REVIEW`, `ERROR` 네 가지만 사용한다.
- `IDLE`은 휴식 상태로 보고 빨강 계열로 표시한다.
- `outputs/broadcasting/logs/current-status.json`이 없을 때는 강의 화면용 `WORKING`/`IDLE` fallback을 표시한다.
- `WORKING` 상태 캐릭터는 은은한 pulse 애니메이션을 사용한다.
- 캐릭터는 실제로 일하거나 쉬는 것처럼 보여야 하며, 상태별로 typing, thinking, reading, reviewing, revising, publishing, resting 같은 자연스러운 반복 모션을 사용한다.
- 각 캐릭터의 아바타는 투명 배경 PNG로 만들고, 이미지 안에 텍스트를 넣지 않는다.
- 직원명, 역할, 상태 설명은 HTML 텍스트로 표시한다.
- 메인 화면에는 아바타, 직원명, 상태 배지만 표시하고, 역할과 상세 상태는 클릭 상세 패널에서 보여준다.
- 메인 화면에는 작업 진행률이나 에너지 퍼센트를 표시하지 않는다.
- 에너지 잔량은 직원 상세 패널에만 표시하며, 실제 런타임 값이 없으면 상태 기반 고정 fallback 값을 사용한다.
- 애니메이션은 라이브 강의 화면에 맞게 차분해야 하며, `prefers-reduced-motion` 환경에서는 정적 강조로 축소한다.
- 캐릭터를 클릭하면 오른쪽 상세 패널 또는 모달에 현재 작업, 최근 완료 작업, 다음 작업, 업데이트 시간, 상태 기준을 보여준다.
- 상단에는 `후츠릿 AI 오피스`, `24시간 무인 AI 콘텐츠 제작 파이프라인`, Codex token 실제 사용량 또는 시연용 계산값을 표시한다.
- 하단에는 오늘 처리 입력 수, 작성 완료 수, 검토 대기 수, 배포 완료 수, 전체 진행률, 시스템 상태, 현재 시간을 표시한다.
- 하단 지표를 클릭하면 `outputs/broadcasting/`에서 읽은 실제 입력, 최종본, 검토 대기, 배포 완료 패키지 목록을 보여준다.

금지:

- 랜딩페이지처럼 만들지 않는다.
- 단순 카드 나열 UI로 만들지 않는다.
- 참고 이미지를 그대로 복제하지 않는다.
- 여러 박스의 나열처럼 보이게 만들지 않는다.
- SVG 장식만으로 대충 만들지 않는다.
- 텍스트, 배지, 아바타, 패널이 겹치게 만들지 않는다.

### 유튜브전략팀

목표: 데이터 기반 기획으로 채널 성장과 유입을 최적화한다.

역할:

- 영상 성과 분석
- 제목과 썸네일 컨셉 제안
- 다음 콘텐츠 주제 제안
- 주요 댓글 반응 요약
- Telegram 후속 질문 대응

기본 흐름:

```text
데이터 수집 -> 성과 분석 -> 기획안 도출 -> Telegram 보고
```

## Telegram 관제실

Telegram는 팀별 채널을 기준으로 보고, 수정 요청, 명령 입력을 처리합니다.

채널명은 에이전트 팀 이름과 동일하게 설정합니다.

현재 콘텐츠배포팀 채널명은 `broadcasting`입니다.

지원해야 할 상호작용:

- 자동 보고
- 초안 피드백
- 수정 요청
- 후속 질문
- 에이전트 명령

예상 명령:

- `/content-draft`: 메모 기반 콘텐츠 초안 생성
- `/content-revise`: 특정 초안 수정
- `/content-status`: 콘텐츠 생성 상태 확인
- `/youtube-ideas`: 다음 유튜브 콘텐츠 주제 요청
- `/daily-report`: 현재 오피스 상황 요약

## Telegram 보고 형식

일반 보고:

```text
[팀] 콘텐츠배포팀
[상태] 초안 생성 | 자동 발송 완료 | 배포 완료 | 실패
[입력] 입력 요약
[산출물] 블로그, LinkedIn, Telegram 뉴스레터
[파일] 저장 경로
[다음 작업] 다음에 진행할 일
[처리 방식] 자동 발송 | 자동 배포 | 사용자 조치 필요
```

배포 결과 보고:

```text
## ✅ 멀티플랫폼 배포 결과
상태 전체 배포 완료 | 부분 배포 완료 | 배포 실패
제목 게시 제목
시간 배포 시각

### ✅ 배포 완료
- 블로그: URL
- LinkedIn: URL
- Telegram 뉴스레터: URL

### ⚠️ 확인 필요
- 실패 또는 중단 채널: 원인

파일 저장 경로
```

실패 보고:

```text
[팀] 콘텐츠배포팀
[상태] 실패
[단계] 초안 | 자동 발송 | 배포 | 테스트 | 배포환경
[원인] 짧은 기술적 원인
[시도한 조치] 수정/재시도 요약
[다음 작업] 재시도 계획 또는 사용자 조치
```

## 승인 정책

기본 원칙은 **자율 실행, 위험 작업만 승인**입니다.

승인이 필요한 작업:

- 결제, 광고비, 구매, 구독
- 외부 콘텐츠 삭제
- 계정, 결제, DNS, 권한, 토큰, 운영 인프라 변경
- 브랜드 신뢰, 비용, 개인정보, 되돌리기 어려운 외부 영향이 있는 작업

승인 없이 가능한 작업:

- 초안 생성
- 로컬 파일 저장
- 테스트 실행
- 테스트 통과까지 코드 수정
- 내부 Telegram 보고
- Telegram 뉴스레터 자동 게시
- 블로그 원고와 LinkedIn 원고의 Telegram 자동 발송
- 사용자가 자동 배포를 허용한 채널의 콘텐츠 공개 게시
- 로컬 자동화
- 비위험 코드 개선
- 안전하게 설정된 배포

## 구현 원칙

각 기능에 가장 적합한 도구를 사용한다.

- Python: 콘텐츠 파이프라인, 파일 처리, AI orchestration, 스케줄 작업, 통합 스크립트
- Node.js/TypeScript: Telegram 봇, API 서버, 웹 대시보드
- n8n: 정기 실행, 승인 라우팅, 단순 알림, 외부 서비스 연결
- LangChain 등: 검색, 메모리, 도구 호출, 복잡한 멀티스텝 에이전트가 필요할 때만 사용
- 단순한 작업은 무거운 프레임워크보다 스크립트를 우선한다.

한 가지 기술 스택을 모든 팀에 강제하지 않는다.

## 저장소 구조

기본 구조:

```text
.
├── AGENTS.md
├── README.md
├── .env.example
├── .agents/
│   └── skills/
│       ├── chutzrit-broadcasting/
│       ├── chutzrit-office-dashboard/
│       └── chutzrit-education-slides/
├── configs/
├── agents/
│   ├── broadcasting/
│   ├── chief-of-staff/
│   ├── research/
│   ├── dev/
│   ├── office-dashboard/
│   ├── education/
│   │   └── slide-maker/
│   └── youtube/
├── apps/
│   ├── telegram-bot/
│   └── office-dashboard/
├── automations/
│   └── n8n/
├── docs/
│   ├── architecture/
│   ├── content/
│   ├── dashboard/
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

## 콘텐츠 산출물 규칙

콘텐츠배포팀 결과물은 아래 위치에 저장한다.

- `outputs/broadcasting/drafts/`
- `outputs/broadcasting/final/`
- `outputs/broadcasting/approvals/` 향후 고위험 작업 승인 기록용
- `outputs/broadcasting/logs/`
- `docs/content/`

콘텐츠 1건의 초안 패키지:

```text
outputs/broadcasting/drafts/YYYY-MM-DD-slug/
├── source.md
├── strategy.md
├── insight.md
├── blog.md
├── linkedin.md
├── telegram.md
├── reflection.md
├── reflection.json
├── metadata.json
├── approval-status.json
└── publish-plan.json
```

`approval-status.json`은 기존 파일명을 유지하되, 현재 MVP에서는 승인 대기 상태가 아니라 자동 발송/배포 처리 상태를 기록한다.

`metadata.json`에는 최소한 아래 정보를 둔다.

- 입력 타입
- 생성 시각
- 에이전트 구조
- 대상 페르소나
- 대상 채널
- 채널별 처리 상태
- 채널별 발송/배포 상태
- 게시 URL
- 품질 평가 점수
- 수정 루프 횟수

Final Quality Gate 이후 현재 최종본은 같은 패키지 ID로 `outputs/broadcasting/final/`에도 저장한다.

## 강의 자료 산출물 규칙

강의운영팀 결과물은 아래 위치에 저장한다.

- `outputs/education/slides/`
- `outputs/education/logs/`
- `outputs/education/sources/`
- `docs/education/`

강의 슬라이드 1건의 기본 산출물:

```text
outputs/education/slides/{lecture-slug}-slides.html
```

강의 원본 자료가 필요한 경우 아래에 로컬 보관한다.

```text
outputs/education/sources/
```

`outputs/education/sources/`에는 PDF, PPTX, 원고, 수강생 자료처럼 비공개 자료가 들어갈 수 있으므로 `.gitignore` 대상으로 유지한다.

강의 슬라이드 생성 규칙:

- 모든 CSS, JavaScript, 콘텐츠는 하나의 HTML 파일에 인라인으로 포함한다.
- 별도 서버 없이 브라우저에서 직접 열 수 있어야 한다.
- 베이스 템플릿과 패턴은 `agents/education/slide-maker/`의 기준 파일을 따른다.
- 섹션 전환과 임팩트 슬라이드를 제외한 모든 슬라이드 푸터는 `후츠릿 · {강의명}` 형식을 사용한다.
- 코드 예제와 실습 명령은 가능한 범위에서 실행 가능성, 최신성, 오탈자를 검증한다.

## 콘텐츠 입력 전략

초기 입력은 Telegram `broadcasting` 팀 채널에 사용자가 자연스럽게 작성한 메모, 생각, 링크, bullet point를 사용한다.

입력 규칙:

- 사용자는 별도의 명령어를 붙이지 않는다.
- 링크만 올려도 실행한다.
- 링크와 사용자의 생각이 함께 있으면 사용자의 생각을 콘텐츠 관점의 우선 기준으로 삼는다.
- 채널별 확장 요청을 쓰지 않아도 기본 대상 채널 전체로 초안을 만든다.

에이전트는 다음 기준으로 처리한다.

1. 사용자의 핵심 아이디어를 보존한다.
2. 가장 적합한 콘텐츠 각도를 추론한다.
3. 플랫폼별 문체와 구조로 변환한다.
4. 배포하기에 너무 모호한 경우에만 질문한다.
5. 배포 전에 초안을 저장한다.

자동 리서치 기반 주제 선정은 이후 기능으로 둔다.

향후 흐름:

```text
리서치 스캔 -> 후보 주제 선정 -> 페르소나 적합도 평가 -> 콘텐츠 생성 -> 자동 발송
```

현재 콘텐츠배포팀 MVP는 승인 단계를 두지 않는다. Telegram 입력을 받으면 작업 시작 메시지를 즉시 보내고, Telegram 기본 typing 표시와 `글 작성중입니다` 봇 활동 상태를 유지한다. Input Parser, Content Strategy Agent, Insight Agent, Platform Writer Agents, Self Reflection Agent가 끝날 때마다 이모지와 함께 결과를 메시지용으로 요약한다. 평가 점수가 기준 미달이면 최대 3회까지 Revision Agent를 실행하고, 회차별 점수와 수정 피드백을 중간 보고한 뒤 최종 원고를 자동 발송한다.

## 브랜드와 페르소나

상세 페르소나 파일이 확정되기 전까지 아래 기준을 따른다.

- 한국어 우선
- 실용적이고 직접적인 문체
- 1인 기업이 AI를 활용해 실행력을 확장하는 관점
- "나는 디렉션하고 Codex가 실행한다"는 메시지
- 막연한 AI 과장보다 구체적 워크플로우와 사례 중심
- 전후 생산성 차이를 명확히 보여주는 구성

상세 페르소나 문서는 아래에 둔다.

```text
docs/strategy/persona.md
```

후츠릿 페르소나 평가는 `docs/strategy/persona.md`의 평가 루브릭을 기준으로 한다.

평가 기준은 다음 입력으로 지속적으로 개선한다.

- 사용자가 승인한 글
- 사용자가 수정 요청한 글
- 성과가 좋았던 콘텐츠
- 후츠릿의 실제 말투와 강의/개발자/크리에이터 포지션
- 플랫폼별 반응 데이터

콘텐츠 전략과 채널별 작성은 아래 문서를 함께 참고한다.

- `docs/strategy/audience.md`: 타깃 독자 정의
- `docs/strategy/content-positioning.md`: 콘텐츠 포지셔닝
- `docs/strategy/channel-style-guide.md`: 채널별 글쓰기 스타일
- `docs/content/references/source-materials.md`: 참고자료 목록
- `.agents/skills/chutzrit-broadcasting/SKILL.md`: Codex가 콘텐츠 생성/수정 작업 시 불러올 방송팀 Skill

## 개발 작업 흐름

기능을 구현할 때는 다음 순서를 따른다.

1. 기존 파일과 구조를 먼저 확인한다.
2. 현재 작업에 가장 단순하고 적합한 기술을 선택한다.
3. 현재 팀이나 에이전트 범위에 맞춰 구현한다.
4. 위험도가 있는 동작에는 테스트를 추가한다.
5. 테스트를 실행한다.
6. 실패하면 원인을 찾아 통과할 때까지 수정한다.
7. 변경 내용과 검증 결과를 보고한다.

## 반복 실행 약속어

사용자가 `start`만 입력하거나, "오피스 켜줘", "서버 켜줘", "후츠릿 오피스 시작", "콘텐츠팀 서버 켜줘"처럼 후츠릿 오피스 런타임 시작을 요청하면 아래 스크립트를 실행한다.

```bash
.venv/bin/python scripts/start_chutzrit_office.py
```

이 스크립트는 Telegram 봇을 실행 중이면 재시작하지 않고 유지하며, 실행 중이 아니면 `screen` 세션으로 띄운다. 오피스 대시보드는 `http://127.0.0.1:5173/`에 응답하지 않을 때만 `apps/office-dashboard`의 Vite 개발 서버를 `screen` 세션으로 띄운다.

스크립트 실행 후에는 Telegram 입력 채널 접근, Telegram Webhook 보고, OpenAI 호출, Tistory Chrome Playwright 세션 검증, 대시보드 URL 응답 여부를 확인한 뒤 결과를 보고한다. 검증 중 하나라도 실패하면 "테스트해도 된다"고 답하지 않고 실패 항목과 조치가 필요한 명령을 먼저 보고한다.

`start` 단축어는 특히 "실제 작동할 수 있게 서버를 모두 띄우고, 티스토리 배포까지 테스트한다"는 의미로 처리한다. 기본 실행 순서는 다음과 같다.

1. `.venv/bin/python scripts/start_chutzrit_office.py`로 Telegram 봇과 오피스 대시보드를 띄운다.
2. Telegram 봇 토큰/채널, Telegram Webhook, OpenAI Responses API, Tistory Playwright 세션을 검증한다.
3. Tistory 검증이 `session_expired`이면 `.venv/bin/python scripts/save_tistory_session.py --browser chrome --timeout 900`을 실행하고, 사용자가 뜬 Chrome Playwright 창에서 로그인할 때까지 기다린다.
4. 세션 갱신 후 `.venv/bin/python scripts/check_integrations.py --tistory`를 다시 실행한다.
5. Tistory 세션 검증이 통과하면 `.venv/bin/python scripts/test_tistory_publish.py`로 짧은 테스트 글을 실제 공개 발행한다.
6. 발행 결과 URL이 나오면 HTTP 응답을 확인하고, Telegram 봇/대시보드 screen 세션과 함께 최종 상태를 보고한다.

`start` 수행 중 티스토리 공개 발행이 실패하면 성공으로 말하지 않는다. `session_expired`, `dependency_missing`, `failed` 같은 실제 상태와 스크린샷/로그 경로, 사용자가 해야 할 조치를 함께 보고한다.

Telegram나 외부 배포 연동을 만들 때:

- 자격 증명은 환경변수로 관리한다.
- 실제 토큰과 API 키는 커밋하지 않는다.
- 환경변수가 추가되면 `.env.example`을 업데이트한다.
- 로그에는 디버깅에 필요한 정보만 남기고 비밀값은 기록하지 않는다.

## 보안 규칙

저장소에 실제 API 키, 토큰, 쿠키, 비밀번호를 저장하지 않는다.

환경변수로 관리할 값:

- Telegram bot token
- Telegram webhook URL
- Tistory Playwright storage state path
- LinkedIn OAuth token
- LinkedIn author URN
- LLM provider API key

자격 증명 회전, 계정 권한 변경, 결제 변경, 공개 계정 정체성 변경은 사용자 승인이 필요하다.

## 기본 판단 규칙

자동화할지 물어볼지 애매하면:

- 브랜드, 비용, 계정, 개인정보, 되돌리기 어려운 외부 영향이 있으면 묻는다.
- 그 외에는 진행하고, 테스트하고, 저장하고, 보고한다.

입력 방식이 애매하면:

- MVP에서는 사용자의 단편 메모를 우선 사용한다.
- 자동 리서치 기반 주제 선정은 배포/승인/보고 루프가 안정화된 뒤 추가한다.

n8n과 코드 중 무엇을 쓸지 애매하면:

- 일정 실행, 단순 라우팅, 승인 전달은 n8n을 사용한다.
- 콘텐츠 생성, 플랫폼 어댑터, 테스트 가능한 상태 관리는 코드로 작성한다.

배포가 실패하면:

- 생성된 최종 산출물은 보존한다.
- 안전한 경우에만 재시도한다.
- 원인과 다음 작업을 Telegram로 보고한다.

## 즉시 구현 로드맵

1단계: 콘텐츠배포팀 MVP

- 콘텐츠 입력 포맷 정의
- 콘텐츠 생성 파이프라인 구현
- 초안과 메타데이터 저장
- Telegram 보고 추가
- 자동 발송 상태 추적 추가
- Telegram 자동 발송 연결

2단계: Telegram 상호작용

- Telegram 명령 추가
- 수정 요청 처리
- 콘텐츠 큐 상태 조회

3단계: 멀티플랫폼 배포

- 티스토리 Playwright 공개 발행
- 티스토리 발행 URL을 LinkedIn 원고의 `[블로그 링크]`에 치환
- LinkedIn API 배포
- Telegram 뉴스레터 게시
- 플랫폼별 발행 링크 Telegram 보고

4단계: 리서치 기반 주제 제안

- 소스 스캔
- 후보 주제 생성
- 페르소나/채널 적합도 평가
- 선택된 주제로 초안 생성

5단계: 다른 팀 확장

- 비서실 조율 기능
- 리서치팀 브리핑
- 유튜브전략팀 분석
- 강의운영팀 자료 제작
- 개발팀 배포 모니터링

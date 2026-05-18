# 후츠릿 오피스 대시보드 설계

후츠릿 오피스 대시보드는 콘텐츠배포팀 자동화가 실제로 작동하고 있다는 것을 한 화면에서 보여주는 라이브 운영 화면입니다.

첫 버전은 `outputs/broadcasting/` 산출물을 스캔한 실제 스냅샷 데이터로 구현합니다. `outputs/broadcasting/logs/current-status.json`이 있으면 실행 중인 파이프라인 상태를 우선 표시하고, 없으면 강의 화면용 `WORKING`/`IDLE` fallback을 표시합니다.

## 참고 이미지

- 전체 오피스 콘셉트: `docs/dashboard/references/office-concept.png`
- 에이전트 아바타 방향: `docs/dashboard/references/agent-avatars.png`

참고 이미지는 분위기와 방향만 사용합니다. 완전히 복제하지 않고, 웹 대시보드의 기능과 가독성에 맞게 재구성합니다.

## 목표

- 라이브 강의에서 보여줄 후츠릿 AI 오피스 운영 대시보드
- 단순 랜딩페이지가 아니라 실제 운영 화면
- Telegram 입력부터 발행까지 각 에이전트가 일하는 모습을 시각화
- 캐릭터들이 실제로 일하거나 쉬는 것처럼 보이는 자연스러운 애니메이션 흐름 구현
- 메인 화면에는 가짜 에너지나 임의 진행률을 만들지 않고 실제 산출물과 상태 파일 기준으로 표시
- 현재 구현 완료된 콘텐츠배포팀만 먼저 표시
- 다른 팀은 구현 완료 후 추가

## 화면 구조

### 상단 헤더

- 타이틀: `후츠릿 AI 오피스`
- 서브타이틀: `24시간 무인 AI 콘텐츠 제작 파이프라인`
- Codex token 사용량 위젯
  - 실제 사용량 소스가 있으면 Used, Limit, Usage percentage 표시
  - 실제 사용량 소스가 없으면 `outputs` 현황 기반 시연용 계산값 표시

### 오피스 공간

하나의 큰 사무실 공간 안에 아래 영역을 자연스럽게 배치합니다.

- Telegram 입력 접수 데스크
- 전략 회의 테이블
- 작성 책상
- 검수 책상
- 수정 책상
- 배포 보드 또는 출고 구역

각 영역을 카드처럼 완전히 분리하지 않습니다. 한눈에 하나의 AI 오피스로 읽혀야 합니다.

### 에이전트 배치

- Input Parser Agent: Telegram 입력 접수 데스크
- Content Strategy Agent: 전략 회의 테이블
- Insight Agent: 전략 회의 테이블 옆 또는 보드 앞
- Blog Writer Agent: 작성 책상
- LinkedIn Writer Agent: 작성 책상
- Telegram Newsletter Agent: 작성 책상
- Self Reflection Agent: 검수 책상
- Revision Agent: 수정 책상
- Publish Agent: 오른쪽 끝 또는 하단 출고 구역

### 상세 패널

각 캐릭터를 클릭하면 오른쪽 사이드 패널을 엽니다.

표시 항목:

- Agent
- Status
- Current Task
- Recent Output
- Next
- Updated
- 상태 기준 파일 또는 스냅샷 기준

### 진행 흐름

사무실 내부에 작은 라벨, 화살표, 빛나는 연결선으로 표시합니다.

```text
Telegram Input -> Strategy -> Writers -> Review -> Publish
```

현재 진행 중인 단계는 강조합니다.

### 하단 상태바

표시 항목:

- 오늘 처리한 입력 수
- 작성 완료 콘텐츠 수
- 검토 대기 수
- 배포 완료 수
- 전체 진행률
- 시스템 상태
- 현재 시간

하단 지표는 클릭할 수 있어야 합니다. 클릭 시 오른쪽 패널에서 해당 지표에 속한 실제 패키지 목록, 품질 점수, 수정 횟수, 채널별 배포 상태, 파일 경로, 게시 URL을 보여줍니다.

### 동작과 애니메이션

이 대시보드는 정적인 현황판이 아니라 살아 있는 오피스 화면이어야 합니다.

- `WORKING`: 손이나 몸이 은은하게 움직이고 책상, 화면, 상태 배지가 부드럽게 pulse 됩니다.
- `IDLE`: 천천히 숨 쉬는 듯한 idle 모션이나 의자에 쉬는 느낌을 줍니다.
- `REVIEW`: 체크리스트, 점수판, 검수 스탬프가 작게 강조됩니다.
- `ERROR`: 빠른 경고 깜빡임이 아니라 절제된 빨간 pulse로 사용자 확인 필요를 알립니다.

메인 화면에는 에이전트별 작업 진행률이나 에너지 퍼센트를 표시하지 않습니다.
에너지 잔량은 직원 상세 패널에만 표시합니다. 실제 런타임 값이 없으면 상태 기반 고정 fallback 값을 사용합니다.

에이전트 상세 패널에는 현재 동작 기준만 표시합니다.

- 현재 동작: typing, thinking, reading, reviewing, revising, publishing, resting, error
- 상태 기준: `outputs/broadcasting/logs/current-status.json` 또는 `outputs/broadcasting` 패키지 스캔 결과

사무실 전체에도 미세한 움직임을 둡니다.

- 모니터 glow
- pipeline 연결선 shimmer
- 화살표 흐름
- Codex token gauge 진행은 실제 사용량 소스가 있을 때만 표시
- 배포 보드 또는 컨베이어의 작은 흐름

움직임은 라이브 강의 화면에 적합하게 차분해야 합니다. 지나치게 빠르거나 시선을 빼앗는 애니메이션은 사용하지 않습니다. `prefers-reduced-motion` 환경에서는 정적인 강조 상태로 축소합니다.

## 상태 체계

상태는 네 개만 사용합니다.

| 상태 | 의미 | 색상 |
| --- | --- | --- |
| `WORKING` | 현재 작업 중 | 초록 또는 민트 |
| `IDLE` | 휴식 중 | 빨강 계열 |
| `REVIEW` | 검토 중 | 주황 |
| `ERROR` | 오류 또는 사용자 확인 필요 | 빨강 |

`WORKING` 캐릭터는 은은한 pulse 애니메이션을 사용합니다.

## 데이터 구조

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

생성 데이터는 컴포넌트와 분리합니다.

```text
apps/office-dashboard/src/data/generated/officeStatus.json
```

생성 기준:

- `outputs/broadcasting/drafts`: 오늘 입력과 검토 대기 계산
- `outputs/broadcasting/final`: 작성 완료와 배포 완료 계산
- `outputs/broadcasting/logs/current-status.json`: 있으면 에이전트별 실제 런타임 상태와 Codex 사용량 우선 적용
- 상태 파일이 없을 때는 시연용 `WORKING`/`IDLE` fallback 적용

## 금지

- 랜딩페이지처럼 만들지 않습니다.
- 에이전트 카드를 단순 나열하지 않습니다.
- 참고 이미지를 그대로 복제하지 않습니다.
- 여러 박스가 나열된 화면처럼 만들지 않습니다.
- 캐릭터별 구역을 완전히 분리된 카드로 만들지 않습니다.
- SVG 장식만으로 대체하지 않습니다.
- 아바타 이미지 안에 직원명이나 역할 텍스트를 넣지 않습니다.
- 메인 화면에 에너지 잔량이나 작업률을 노출하지 않습니다.
- 텍스트가 겹치거나 잘리게 만들지 않습니다.

## 완료 조건

- 로컬에서 실행 가능한 대시보드
- dev server URL 제공
- 실제 화면 확인
- 주요 요소 겹침 없음
- 캐릭터 클릭 시 상세 패널 열림
- 하단 지표 클릭 시 실제 outputs 상세 패널 열림
- 상단 Codex 토큰 사용량은 실제 소스가 없으면 시연용 계산값으로 표시

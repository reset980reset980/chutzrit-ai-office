# 후츠릿 오피스 대시보드 앱

후츠릿 AI 오피스 대시보드는 라이브 강의에서 보여줄 운영 화면입니다.

단순 설명 페이지나 랜딩페이지가 아니라, Discord 입력부터 콘텐츠 전략, 작성, 검수, 수정, 배포까지 콘텐츠배포팀 에이전트들이 하나의 사무실 안에서 일하는 모습을 시각화합니다.

## 구현 위치

대시보드 앱 코드는 이 폴더에 둡니다.

권장 스택:

- React
- Vite
- TypeScript

이 앱은 순수 JS보다 React가 적합합니다. 에이전트별 상태, 클릭 상세 패널, 자연스러운 모션, 산출물 기반 지표, 나중의 상태 파일 연동을 컴포넌트와 데이터 상태로 분리해서 다뤄야 하기 때문입니다.

## 실행 방법

```bash
npm install
npm run dev
```

기본 개발 서버 주소는 아래와 같습니다.

```text
http://127.0.0.1:5173/
```

후츠릿 오피스 전체 런타임을 시작할 때는 저장소 루트에서 아래 명령을 사용합니다.

```bash
.venv/bin/python scripts/start_chutzrit_office.py
```

이 명령은 Discord 봇, 오피스 대시보드, Discord/OpenAI/Tistory 연동 상태를 함께 확인합니다.

빌드 검증은 아래 명령으로 실행합니다.

```bash
npm run build
```

`npm run dev`와 `npm run build` 전에는 `npm run generate:data`가 자동 실행되어 `outputs/broadcasting/` 기준의 최신 스냅샷을 생성합니다. 개발 서버가 켜진 뒤에도 `outputs/broadcasting/` 아래 패키지나 `logs/current-status.json`이 바뀌면 Vite watcher가 스냅샷을 다시 만들고 화면을 새로고침합니다.

아바타 PNG를 다시 만들 때는 아래 명령을 실행합니다.

```bash
npm run generate:avatars
```

## 첫 구현 범위

- 상단 오피스 헤더
- Codex 토큰 사용량 실제 소스 연결 여부 표시
- 하나의 큰 오피스 공간
- 콘텐츠배포팀 에이전트별 투명 배경 PNG 아바타 배치
- 상태 배지 4종: `WORKING`, `IDLE`, `REVIEW`, `ERROR`
- 에이전트별 자연스러운 업무/휴식 애니메이션
- 클릭 가능한 에이전트 상세 패널
- 사무실 내부 pipeline flow 표시
- 하단 상태바와 클릭 가능한 실제 산출물 상세 패널
- `outputs/broadcasting/` 기반 생성 데이터 파일

## 현재 구현 구조

```text
.
├── scripts/
│   ├── create-avatar-assets.mjs
│   └── generate-office-status.mjs
└── src/
    ├── components/
    │   ├── AgentAvatar.tsx
    │   ├── AgentDetailPanel.tsx
    │   ├── BottomStatusBar.tsx
    │   ├── MetricDetailPanel.tsx
    │   ├── OfficeDashboard.tsx
    │   ├── OfficeHeader.tsx
    │   ├── OfficeMap.tsx
    │   ├── PipelineFlow.tsx
    │   ├── StatusBadge.tsx
    │   └── TokenUsageWidget.tsx
    ├── data/
    │   ├── assets.ts
    │   ├── generated/
    │   │   └── officeStatus.json
    │   └── officeStatus.ts
    ├── types.ts
    └── styles.css
```

`src/data/generated/officeStatus.json`은 `outputs/broadcasting/drafts`와 `outputs/broadcasting/final`을 스캔해 생성됩니다.
`src/data/officeStatus.ts`는 이 생성 데이터를 화면 배치 정보와 결합합니다.

## 실제 데이터 기준

현재 메인 화면은 가짜 에너지나 임의 진행률을 만들지 않습니다.

- 하단 지표는 `outputs/broadcasting/`의 실제 패키지 수를 기준으로 합니다.
- 직원 상태는 `outputs/broadcasting/logs/current-status.json`이 있으면 그 값을 우선 사용합니다.
- `current-status.json`이 없으면 마지막 outputs 스냅샷 기준으로 강의 화면용 `WORKING`/`IDLE` fallback을 표시합니다.
- Codex token 사용량은 실제 사용량 소스가 있으면 그 값을 표시합니다. 현재 소스가 없으면 `outputs` 현황 기반 시연용 계산값을 표시합니다.
- 에너지 잔량은 메인 화면에 표시하지 않고 직원 상세 패널에만 표시합니다. 현재는 상태 기반 고정 fallback 값입니다.

```text
outputs/broadcasting/logs/current-status.json
```

`current-status.json`에 `codexUsage` 또는 `codex_usage` 값이 있고 `used`, `limit` 숫자가 있으면 Codex 사용량 위젯이 실제 값으로 바뀝니다.

## 아바타 기준

- 직원 아바타는 `public/assets/avatars/*.png`의 투명 배경 PNG를 사용합니다.
- 직원명과 역할 식별 텍스트는 아바타 이미지에 넣지 않고 HTML로 표시합니다.
- 원본 참고 이미지의 캐릭터 소품에 이미 포함된 장식 텍스트는 캐릭터 보존을 위해 임의로 다시 그리거나 지우지 않습니다.
- 직원명과 역할은 HTML 텍스트로 표시합니다.
- 메인 화면에는 직원명만 표시하고, 역할과 상세 상태는 오른쪽 패널에서 확인합니다.

## 참고 문서

- `docs/dashboard/office-dashboard.md`
- `.agents/skills/chutzrit-office-dashboard/SKILL.md`
- `agents/office-dashboard/README.md`

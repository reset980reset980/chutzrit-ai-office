# 오피스 대시보드 에이전트

오피스 대시보드 에이전트는 후츠릿 AI 오피스가 실제로 돌아가고 있다는 것을 시각화하는 운영 화면을 담당합니다.

첫 구현 대상은 `broadcasting` 콘텐츠배포팀입니다. 다른 팀은 실제 런타임 구현이 완료된 뒤 대시보드에 추가합니다.

## 역할

- 라이브 강의에서 보여줄 AI 오피스 운영 대시보드 설계
- 콘텐츠배포팀 서브에이전트의 현재 상태 시각화
- 오피스 공간 안에 접수, 전략, 작성, 검수, 수정, 배포 영역 배치
- 에이전트별 아바타, 상태 배지, 클릭 상세 패널 정의
- 캐릭터가 실제로 일하거나 쉬는 것처럼 보이는 자연스러운 애니메이션 흐름 정의
- `outputs/broadcasting/` 기반 실제 산출물 지표 정의
- Codex 토큰 사용량 실제 소스 연결 여부 표시
- 하단 운영 상태바, 전체 진행률, 클릭 상세 데이터 정의
- `outputs/broadcasting/logs/current-status.json`이 있으면 실제 런타임 상태로 우선 표시

## 구현 기준

- 실제 앱은 `apps/office-dashboard/`에 둡니다.
- 대시보드 설계 문서는 `docs/dashboard/`에 둡니다.
- 참고 이미지는 `docs/dashboard/references/`에 둡니다.
- 생성 데이터와 컴포넌트는 분리합니다.
- 에이전트별 `progress`, `energy` 같은 임의 값을 만들지 않습니다.
- 메인 화면에는 아바타, 직원명, 상태 배지만 표시합니다.
- 역할, 현재 작업, 최근 완료, 다음 작업, 상태 기준, 에너지 잔량은 상세 패널에 표시합니다.
- 에너지 잔량은 실제 런타임 값이 없으면 상태 기반 고정 fallback 값을 사용합니다.
- 상태 파일이 없으면 outputs 스냅샷 기준으로 강의 화면용 `WORKING`/`IDLE` fallback을 표시합니다.
- 아바타는 투명 배경 PNG를 사용하고, 이미지 안에 텍스트를 넣지 않습니다.

## 현재 구현 상태

- `apps/office-dashboard/`에 React + TypeScript + Vite 앱을 구현했습니다.
- 첫 화면은 랜딩페이지가 아니라 운영 대시보드입니다.
- 콘텐츠배포팀 9개 에이전트를 하나의 오피스 공간 안에 배치했습니다.
- 각 에이전트는 `WORKING`, `IDLE`, `REVIEW`, `ERROR` 상태 체계와 상태별 `motion` 값을 가집니다.
- 에이전트 클릭 시 오른쪽 상세 패널이 현재 작업, 최근 완료, 다음 작업, 업데이트 시간을 보여줍니다.
- 하단 지표 클릭 시 오른쪽 패널이 실제 입력, 최종본, 검토 대기, 배포 완료 패키지 목록을 보여줍니다.
- 상태 생성 데이터는 `apps/office-dashboard/src/data/generated/officeStatus.json`에 분리했습니다.
- 아바타 자산은 `apps/office-dashboard/public/assets/avatars/*.png`에 투명 배경 PNG로 둡니다.

## 참고 이미지

- 전체 오피스 콘셉트: `docs/dashboard/references/office-concept.png`
- 에이전트 아바타 방향: `docs/dashboard/references/agent-avatars.png`

이미지는 분위기와 방향 참고용입니다. 그대로 복제하지 않고, 웹 운영 대시보드 목적에 맞게 재구성합니다.

## 상태 체계

상태는 네 개만 사용합니다.

- `WORKING`: 현재 작업 중
- `IDLE`: 휴식 중, 빨강 계열로 표시
- `REVIEW`: 검토 중
- `ERROR`: 오류 또는 사용자 확인 필요

`WORKING` 상태는 은은한 pulse 애니메이션을 사용합니다.

## 애니메이션 기준

- `WORKING`: 타이핑, 작성, 화면 glow
- `IDLE`: 천천히 쉬는 idle 모션과 빨강 계열 상태 강조
- `REVIEW`: 체크리스트나 점수판 강조
- `ERROR`: 절제된 빨간 pulse

움직임은 캐릭터와 업무 상태를 설명해야 합니다. 장식용으로 과하게 흔들거나 화면 전체를 산만하게 만들지 않습니다.

## 데이터 기준

- `npm run generate:data`는 `outputs/broadcasting/drafts`와 `outputs/broadcasting/final`을 스캔합니다.
- 오늘 입력, 작성 완료, 검토 대기, 배포 완료는 실제 패키지 기준으로 계산합니다.
- `outputs/broadcasting/logs/current-status.json`이 있으면 에이전트별 `status`, `currentTask`, `recentOutput`, `nextTask`, `updatedAt`을 우선 사용합니다.
- `current-status.json`에 `codexUsage.used`와 `codexUsage.limit`가 있으면 Codex 사용량을 실제 값으로 표시합니다.
- Codex 사용량 소스가 없으면 `outputs` 현황 기반 시연용 계산값을 표시합니다.

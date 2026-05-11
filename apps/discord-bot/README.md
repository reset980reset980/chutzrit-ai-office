# Discord 봇

Discord 봇은 후츠릿 AI 오피스의 중앙 관제 인터페이스입니다.

Discord는 단순 알림 채널이 아니라 보고, 수정 요청, 명령 입력을 처리하는 운영 공간입니다.

Discord 채널명은 에이전트 팀 이름과 동일하게 설정합니다. 콘텐츠배포팀의 MVP 채널명은 `broadcasting`입니다.

## 역할

- 메시지 수신 직후 작업 시작 알림
- 작업 중 Discord 기본 `typing` 표시 유지
- 작업 중 봇 활동 상태를 `글 작성중입니다`로 변경
- 입력 분석, 원고 작성, 품질 평가 진행 메시지를 이모지와 함께 발송
- 각 논리 Agent 완료 시 결과 요약 메시지 발송
- 기준 미달 시 최대 3회까지 Revision Agent 수정 루프 실행 및 회차별 보고
- 콘텐츠 초안 생성 결과 보고
- 자동 발송 성공/실패 알림
- 사용자의 수정 요청 수신
- 콘텐츠 생성 상태 조회
- 이후 다른 팀의 일일 보고와 진행 상황 보고 수신

## MVP 접근

현재 MVP 봇은 `broadcasting` 채널 메시지를 감지해 콘텐츠배포팀 파이프라인을 실행합니다.

```text
Discord broadcasting 채널 메시지 수신
-> "글 작성중입니다" 즉시 응답
-> Discord 기본 typing 표시와 봇 작업 상태 표시
-> Input Parser 결과 요약 메시지
-> Content Strategy Agent 결과 요약 메시지
-> Insight Agent 결과 요약 메시지
-> Platform Writer Agents 결과 요약 메시지
-> Self Reflection 평가 결과 메시지
-> 기준 미달 시 Revision Agent 회차별 수정
-> 수정본 재평가 결과 메시지
-> 초안 저장
-> 블로그, LinkedIn 원고 발송
-> Discord 뉴스레터 자동 발송
```

현재 실제 외부 플랫폼 API 배포는 붙이지 않았습니다.

오늘 MVP에서는 생성된 블로그 원고, LinkedIn 원고, Discord 뉴스레터를 `broadcasting` 채널에 바로 발송합니다.

## 실행 방법

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r apps/discord-bot/requirements.txt
.venv/bin/python apps/discord-bot/bot.py
```

## 이후 예상 명령

- `/content-draft`: 메모를 기반으로 콘텐츠 초안 생성
- `/content-revise`: 특정 초안 수정 요청
- `/content-status`: 현재 콘텐츠 생성 상태 확인
- `/daily-report`: 오피스 전체 상황 요약 요청

## 환경변수

필요한 환경변수 예시는 루트의 `.env.example`을 기준으로 관리합니다.

실제 토큰이나 웹훅 URL은 저장소에 커밋하지 않습니다.

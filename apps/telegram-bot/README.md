# Telegram Bot

Telegram 봇은 후츠릿 AI 오피스 콘텐츠배포팀의 입력, 진행 보고, 결과 발송 인터페이스입니다.

## 동작

- `TELEGRAM_BROADCASTING_CHAT_ID`에 들어온 일반 메시지를 콘텐츠 생성 요청으로 봅니다.
- 명령어는 필요 없습니다.
- URL이 있으면 링크 입력으로 자동 감지합니다.
- 사진, 문서, 영상 첨부가 있으면 가능한 경우 Telegram 파일 URL을 입력에 포함합니다.
- 작업 시작 시 `글 작성중입니다. 입력을 분석하고 있습니다.`를 즉시 답장합니다.
- 작업 중에는 Telegram `typing` 액션을 유지합니다.
- 서브에이전트 진행 상황을 같은 채팅방에 보고합니다.
- 최종 뉴스레터 원고는 `TELEGRAM_NEWSLETTER_CHAT_ID`로 발송합니다.

## 실행

```bash
cd /home/reset980/chutzrit-ai-office
python3 apps/telegram-bot/bot.py
```

## 필수 환경변수

```env
TELEGRAM_BOT_TOKEN=
TELEGRAM_BROADCASTING_CHAT_ID=
TELEGRAM_NEWSLETTER_CHAT_ID=
TELEGRAM_ALLOWED_USER_IDS=
OPENAI_API_KEY=
```

`TELEGRAM_ALLOWED_USER_IDS`가 비어 있으면 채팅방 기준으로만 필터링합니다.

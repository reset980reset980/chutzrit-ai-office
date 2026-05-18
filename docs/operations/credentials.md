# 자격증명 설정 방법

이 문서는 후츠릿 AI 오피스 실행에 필요한 키와 토큰을 어디서 얻는지 정리합니다.

실제 값은 `.env`에만 넣습니다. `.env.example`은 예시 파일이므로 비밀값을 넣지 않습니다.

공식 참고:

- Telegram Bot API: https://core.telegram.org/bots/api
- BotFather 봇 생성: https://core.telegram.org/bots/features#botfather
- Telegram 채널/그룹 ID 확인은 봇을 채팅방에 추가한 뒤 수신 로그 또는 `getUpdates` 응답으로 확인합니다.
- OpenAI API Key 관리: https://help.openai.com/en/articles/9186755-managing-your-work-in-the-api-platform-with-projects
- 티스토리 Open API 종료 안내: https://github.com/tistory/document-tistory-apis
- LinkedIn OAuth: https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow

## MVP 필수

### `TELEGRAM_BOT_TOKEN`

Telegram `broadcasting` 팀 채팅방의 메시지를 감지하기 위한 봇 토큰입니다.

발급 방법:

1. Telegram에서 `@BotFather`를 엽니다.
2. `/newbot`으로 새 봇을 만들거나 기존 봇을 선택합니다.
3. BotFather가 발급한 HTTP API token을 확인합니다.
5. `.env`의 `TELEGRAM_BOT_TOKEN`에 넣습니다.

필수 설정:

- 봇을 입력용 채팅방에 추가합니다.
- BotFather의 privacy mode가 켜져 있으면 그룹 일반 메시지를 받지 못할 수 있으므로 운영 방식에 맞게 `/setprivacy`를 확인합니다.
- 봇에는 메시지 읽기와 메시지 보내기 권한이 필요합니다.

### `TELEGRAM_BROADCASTING_CHAT_ID`

콘텐츠배포팀 전용 Telegram 채팅방 ID입니다.

채팅방명은 에이전트 팀 이름과 동일하게 `broadcasting`으로 설정합니다.

이 채팅방은 MVP에서 입력, 진행 보고, 배포 결과 보고를 담당합니다.

확인 방법:

1. 봇을 `broadcasting` 채팅방에 추가합니다.
2. 테스트 메시지를 하나 보냅니다.
3. 봇 로그의 `chat_id=` 값을 확인합니다.
4. `.env`의 `TELEGRAM_BROADCASTING_CHAT_ID`에 넣습니다.

### `TELEGRAM_NEWSLETTER_CHAT_ID`

독자용 Telegram 뉴스레터 본문을 발송할 채팅방 ID입니다.

현재 운영 기준:

- 서버: `Chutzrit AI Office`
- 채팅방: `뉴스레터`
- 채팅방 ID: 운영 `.env`에서 관리

`broadcasting` 채팅방은 입력과 운영 보고용이고, 뉴스레터 본문은 이 채팅방으로 분리해 발송합니다.

### `TELEGRAM_ALLOWED_USER_IDS`

팀 채널에서 자동화를 실행할 사용자 ID 목록입니다.

권장값:

- MVP에서는 후츠릿 본인 Telegram User ID만 넣습니다.

형식:

```text
TELEGRAM_ALLOWED_USER_IDS=123456789012345678
```

여러 명을 허용할 경우 쉼표로 구분합니다.

```text
TELEGRAM_ALLOWED_USER_IDS=123456789012345678,234567890123456789
```

User ID 확인 방법:

1. 봇 로그의 `user_id=` 값을 확인합니다.
2. 또는 Telegram의 사용자 ID 확인용 봇으로 본인 ID를 확인합니다.

### `OPENAI_API_KEY`

콘텐츠 전략, 인사이트 생성, 플랫폼별 초안 생성, Self Reflection에 사용할 OpenAI API 키입니다.

발급 방법:

1. OpenAI Platform에 접속합니다.
2. API keys 메뉴에서 새 secret key를 만듭니다.
3. 생성된 키를 안전한 곳에 저장합니다.
4. `.env`의 `OPENAI_API_KEY`에 넣습니다.

### `OPENAI_MODEL`

콘텐츠 생성에 사용할 OpenAI 모델 이름입니다.

기본값:

```text
OPENAI_MODEL=gpt-5.4-mini
```

OpenAI 공식 모델 문서 기준으로 `gpt-5.4-mini`는 고빈도 작업에 적합한 최신 mini 계열 모델입니다. 계정에서 해당 모델을 사용할 수 없다면 `.env`에서 사용 가능한 모델로 바꿉니다.

## 연결 테스트

`.env` 값을 넣은 뒤 아래 명령으로 Telegram, OpenAI, 티스토리 세션 연결을 확인합니다.

```bash
python3 scripts/check_integrations.py --all
```

이 명령은 토큰 값을 출력하지 않습니다. Telegram 봇 토큰, `broadcasting` 채팅방 접근, OpenAI Responses API 호출, Tistory Playwright 세션의 `/manage` 접근 가능 여부를 확인합니다.

콘텐츠팀 Telegram 입력 테스트를 시작하기 전에는 이 검증이 모두 통과해야 합니다. 특히 티스토리는 세션 파일 존재 여부만으로 정상이라고 보지 않습니다. `PLAYWRIGHT_STORAGE_STATE`가 있어도 실제 관리자 화면에 접근하지 못하면 세션 만료로 보고, Telegram 입력 테스트를 시작하지 않습니다.

## 공개 게시용

아래 값들은 실제 공개 게시 자동화를 붙일 때 설정합니다.

### 블로그

사용 변수:

- `BLOG_PUBLISHER`
- `TISTORY_BLOG_URL`
- `TISTORY_MANAGE_URL`
- `TISTORY_WRITE_URL`
- `TISTORY_PUBLISH_MODE`
- `TISTORY_AUTO_PUBLISH`
- `PLAYWRIGHT_STORAGE_STATE`
- `PLAYWRIGHT_HEADLESS`

주의:

- 티스토리 Open API는 공식 저장소에 종료 안내가 있으므로 신규 자동 게시 대상으로 전제하지 않습니다.
- 티스토리 자동 게시에는 Playwright 브라우저 자동화를 사용합니다.
- 현재 목표 흐름은 티스토리 공개 발행 후 실제 블로그 URL을 확보하고, 이 URL로 LinkedIn 원고의 `[블로그 링크]`를 치환하는 방식입니다.
- 최초 1회는 사용자가 브라우저에서 직접 로그인하고 `PLAYWRIGHT_STORAGE_STATE`에 로그인 세션을 저장합니다.
- 실제 발행 런타임은 Chrome Playwright 채널만 사용합니다. 저장된 세션 파일을 격리된 headless Chrome 컨텍스트에 주입해 실행하며, 사용 중인 브라우저 프로필을 직접 조작하지 않고 로그아웃 동작도 수행하지 않습니다.
- 운영 기본값은 `PLAYWRIGHT_HEADLESS=true`입니다. visible 모드는 티스토리 UI 디버깅이 필요할 때만 사용합니다.

브라우저 프로필 안전 규칙:

- Playwright 자동화에 실제 Brave, Chrome, Chromium, Safari 일상 프로필을 연결하지 않습니다.
- `launch_persistent_context`에 실제 브라우저 사용자 데이터 디렉터리를 넘기지 않습니다.
- 실제 프로필을 가리키는 `--user-data-dir`를 사용하지 않습니다.
- 자동화는 쿠키, 캐시, localStorage, sessionStorage, IndexedDB, 방문 기록, 사이트 데이터를 삭제하지 않습니다.
- 자동화는 로그아웃, 계정 전환, 세션 초기화, 브라우징 데이터 삭제 UI를 누르지 않습니다.
- 세션 저장과 visible 디버깅은 `outputs/broadcasting/session/` 아래 전용 격리 프로필에서만 수행합니다.

Playwright 실행 환경:

```bash
python -m pip install -r apps/telegram-bot/requirements.txt
python -m playwright install chrome
```

티스토리 로그인 세션 저장:

```bash
python scripts/save_tistory_session.py --browser chrome
```

명령을 실행하면 브라우저가 열립니다. 티스토리에 로그인한 뒤 관리자 페이지가 열리면 `PLAYWRIGHT_STORAGE_STATE` 경로에 세션이 저장됩니다.

세션 저장 스크립트는 저장소의 전용 Chrome Playwright 프로필을 사용합니다. 실제 Brave, Chrome, Chromium 일상 프로필을 직접 사용하지 않습니다. Brave나 Safari로 티스토리 자동화를 실행하지 않습니다.

`TISTORY_WRITE_URL`을 비워두면 `TISTORY_BLOG_URL` 또는 `TISTORY_MANAGE_URL`에서 `https://블로그주소/manage/newpost` 형식으로 자동 추론합니다. 티스토리 에디터 본문이 TinyMCE iframe 안에 렌더링되는 경우에도 자동 입력을 시도합니다. 티스토리 편집기 UI가 바뀌거나 CAPTCHA, 2FA, 추가 로그인 확인이 나타나면 자동 발행은 실패로 기록하고 `tistory-publish-error.png` 스크린샷을 산출물 폴더에 저장합니다.

세션 갱신 후에는 반드시 아래 명령으로 실제 로그인 유지 상태를 다시 확인합니다.

```bash
python3 scripts/check_integrations.py --tistory
```

### LinkedIn

사용 변수:

- `LINKEDIN_CLIENT_ID`
- `LINKEDIN_CLIENT_SECRET`
- `LINKEDIN_REDIRECT_URI`
- `LINKEDIN_SCOPES`
- `LINKEDIN_ACCESS_TOKEN`
- `LINKEDIN_TOKEN_EXPIRES_AT`
- `LINKEDIN_AUTHOR_URN`
- `LINKEDIN_VERSION`
- `LINKEDIN_AUTO_PUBLISH`

주의:

- LinkedIn API는 Developer Portal 앱 생성과 제품/API 권한 신청이 필요합니다.
- 개인 계정에 게시하려면 `w_member_social` 권한과 `urn:li:person:{id}` 형식의 Author URN이 필요합니다.
- 조직 페이지에 게시하려면 `w_organization_social` 권한과 `urn:li:organization:{id}` 형식의 Author URN이 필요합니다.
- LinkedIn Posts API는 생성 요청에서 `lifecycleState`를 `PUBLISHED`로 사용합니다. 초안 저장이 아니라 공개 게시 흐름입니다.
- 게시 성공 시 응답 헤더의 `x-restli-id`를 기반으로 LinkedIn 게시 URL을 만들어 Telegram에 보고합니다.
- 로컬 토큰 발급은 `scripts/linkedin_oauth_server.py`로 처리합니다. 이 스크립트는 LinkedIn callback을 받아 `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_AUTHOR_URN`, `LINKEDIN_TOKEN_EXPIRES_AT`을 `.env`에 저장합니다.

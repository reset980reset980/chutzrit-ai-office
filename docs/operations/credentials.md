# 자격증명 설정 방법

이 문서는 후츠릿 AI 오피스 실행에 필요한 키와 토큰을 어디서 얻는지 정리합니다.

실제 값은 `.env`에만 넣습니다. `.env.example`은 예시 파일이므로 비밀값을 넣지 않습니다.

공식 참고:

- Discord 봇 설치와 권한: https://docs.discord.com/developers/quick-start/getting-started
- Discord 메시지 ID, 서버 ID, 채널 ID 확인: https://support.discord.com/hc/en-us/articles/206346498
- Discord Webhook 생성: https://support.discord.com/hc/en-us/articles/228383668
- OpenAI API Key 관리: https://help.openai.com/en/articles/9186755-managing-your-work-in-the-api-platform-with-projects
- 티스토리 Open API 종료 안내: https://github.com/tistory/document-tistory-apis
- LinkedIn OAuth: https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow

## MVP 필수

### `DISCORD_BOT_TOKEN`

Discord `broadcasting` 팀 채널의 메시지를 감지하기 위한 봇 토큰입니다.

발급 방법:

1. Discord Developer Portal에 접속합니다.
2. 새 Application을 만들거나 기존 Application을 엽니다.
3. 왼쪽 메뉴에서 `Bot`으로 이동합니다.
4. `Reset Token` 또는 `Copy Token`으로 토큰을 확인합니다.
5. `.env`의 `DISCORD_BOT_TOKEN`에 넣습니다.

필수 설정:

- `Bot` 설정에서 `Message Content Intent`를 켭니다.
- 봇을 서버에 초대할 때 최소 권한은 `View Channels`, `Read Message History`, `Send Messages`입니다.
- 나중에 버튼 승인이나 slash command를 쓰려면 `applications.commands` scope도 함께 추가합니다.

### `DISCORD_GUILD_ID`

Discord 서버 ID입니다.

확인 방법:

1. Discord 앱에서 `User Settings -> Advanced -> Developer Mode`를 켭니다.
2. 서버 이름을 우클릭합니다.
3. `Copy Server ID`를 누릅니다.
4. `.env`의 `DISCORD_GUILD_ID`에 넣습니다.

### `DISCORD_BROADCASTING_CHANNEL_ID`

콘텐츠배포팀 전용 Discord 채널 ID입니다.

채널명은 에이전트 팀 이름과 동일하게 `broadcasting`으로 설정합니다.

이 채널은 MVP에서 입력, 진행 보고, 배포 결과 보고를 담당합니다.

확인 방법:

1. Discord Developer Mode를 켭니다.
2. `broadcasting` 채널을 우클릭합니다.
3. `Copy Channel ID`를 누릅니다.
4. `.env`의 `DISCORD_BROADCASTING_CHANNEL_ID`에 넣습니다.

### `DISCORD_WEBHOOK_URL`

Discord 보고 메시지를 간단히 보내기 위한 Webhook URL입니다.

발급 방법:

1. Discord 서버 또는 `broadcasting` 채널의 설정으로 이동합니다.
2. `Integrations -> Webhooks`로 이동합니다.
3. 새 Webhook을 만듭니다.
4. `broadcasting` 채널을 선택합니다.
5. `Copy Webhook URL`을 눌러 `.env`의 `DISCORD_WEBHOOK_URL`에 넣습니다.

참고:

- 봇으로 직접 보고하게 만들 수도 있지만, MVP에서는 Webhook 보고가 더 단순합니다.

### `DISCORD_ALLOWED_USER_IDS`

팀 채널에서 자동화를 실행할 사용자 ID 목록입니다.

권장값:

- MVP에서는 후츠릿 본인 Discord User ID만 넣습니다.

형식:

```text
DISCORD_ALLOWED_USER_IDS=123456789012345678
```

여러 명을 허용할 경우 쉼표로 구분합니다.

```text
DISCORD_ALLOWED_USER_IDS=123456789012345678,234567890123456789
```

User ID 확인 방법:

1. Discord Developer Mode를 켭니다.
2. 자신의 프로필 또는 메시지를 우클릭합니다.
3. `Copy User ID`를 누릅니다.

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

`.env` 값을 넣은 뒤 아래 명령으로 Discord와 OpenAI 연결을 확인합니다.

```bash
python3 scripts/check_integrations.py --all
```

이 명령은 토큰 값을 출력하지 않습니다. Discord 봇 토큰, `broadcasting` 채널 접근, Discord Webhook 보고, OpenAI Responses API 호출만 확인합니다.

## 공개 게시용

아래 값들은 실제 공개 게시 자동화를 붙일 때 설정합니다.

### 블로그

사용 변수:

- `BLOG_PUBLISHER`
- `TISTORY_MANAGE_URL`
- `TISTORY_PUBLISH_MODE`
- `TISTORY_AUTO_PUBLISH`
- `PLAYWRIGHT_STORAGE_STATE`
- `PLAYWRIGHT_HEADLESS`

주의:

- 티스토리 Open API는 공식 저장소에 종료 안내가 있으므로 신규 자동 게시 대상으로 전제하지 않습니다.
- 티스토리 자동 게시에는 Playwright 브라우저 자동화를 사용합니다.
- 현재 목표 흐름은 티스토리 공개 발행 후 실제 블로그 URL을 확보하고, 이 URL로 LinkedIn 원고의 `[블로그 링크]`를 치환하는 방식입니다.
- 최초 1회는 사용자가 브라우저에서 직접 로그인하고 `PLAYWRIGHT_STORAGE_STATE`에 로그인 세션을 저장합니다.

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
- 게시 성공 시 응답 헤더의 `x-restli-id`를 기반으로 LinkedIn 게시 URL을 만들어 Discord에 보고합니다.
- 로컬 토큰 발급은 `scripts/linkedin_oauth_server.py`로 처리합니다. 이 스크립트는 LinkedIn callback을 받아 `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_AUTHOR_URN`, `LINKEDIN_TOKEN_EXPIRES_AT`을 `.env`에 저장합니다.

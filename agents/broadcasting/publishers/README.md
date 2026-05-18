# 콘텐츠배포팀 Publisher 어댑터

이 폴더는 실제 외부 플랫폼 발행 어댑터를 둡니다.

`agents/broadcasting/agents/publish.py`는 Publish Agent입니다. Publish Agent는 품질 게이트 이후 어떤 순서로 어떤 채널을 발행할지 결정하고, 각 채널의 상태를 `publish-plan.json`에 기록합니다.

이 폴더의 Publisher 어댑터는 실제 플랫폼별 실행을 담당합니다.

현재 구조:

```text
agents/broadcasting/publishers/
├── base.py         # 플랫폼별 발행 결과 공통 타입
├── tistory.py      # Playwright로 티스토리 글쓰기/공개 발행/URL 확보
├── linkedin.py     # LinkedIn Posts API 공개 게시
└── telegram.py      # Telegram 채널 발송 결과 기록 보조
```

배포 순서는 순차 방식입니다.

```text
Tistory 발행
-> 실제 블로그 URL 확보
-> LinkedIn 원고의 [블로그 링크] 치환
-> LinkedIn 공개 게시
-> Telegram 뉴스레터 발송/보고
```

LinkedIn은 티스토리 실제 URL에 의존하므로 병렬 발행하지 않습니다. 티스토리 발행에 실패하거나 URL을 확보하지 못하면 LinkedIn 공개 게시를 기본 중단합니다.

티스토리는 Open API가 아니라 Playwright 브라우저 자동화로 발행합니다. 기본 배포는 저장된 `PLAYWRIGHT_STORAGE_STATE`를 격리된 headless Chrome 컨텍스트에 주입해 실행합니다. 티스토리 자동화는 Chrome Playwright 채널만 사용하며, 실제 사용 중인 브라우저 프로필을 직접 조작하지 않고 로그아웃 동작도 수행하지 않습니다.

저장 파일은 Markdown으로 유지하지만, 티스토리 WYSIWYG 에디터에 입력할 때는 Markdown을 HTML로 변환합니다. `## 소제목` 같은 원문 문법이 텍스트로 보이면 실패입니다. 실제 에디터에는 `<h2>소제목</h2>`, `<p>문단</p>`, `<ul>` 같은 HTML 구조가 들어가야 합니다.

로그인 세션, CAPTCHA, 2FA, UI 변경처럼 자동화가 안전하게 처리할 수 없는 상태가 나오면 발행을 멈추고 실패 상태를 보고해야 합니다. 티스토리 에디터가 본문을 TinyMCE iframe 안에 렌더링하는 경우에도 Publisher가 iframe 내부 본문 편집기를 찾아 HTML로 입력합니다.

## 브라우저 프로필 안전 규칙

Playwright Publisher는 사용자의 실제 일상 브라우저 프로필에 붙으면 안 됩니다.

- 실제 Brave, Chrome, Chromium, Safari 프로필 디렉터리를 `launch_persistent_context`에 넘기지 않습니다.
- 실제 프로필을 가리키는 `--user-data-dir`를 사용하지 않습니다.
- 쿠키, 캐시, localStorage, sessionStorage, IndexedDB, 방문 기록, 사이트 데이터를 삭제하지 않습니다.
- 로그아웃, 계정 전환, 세션 초기화, 브라우징 데이터 삭제 UI를 누르지 않습니다.
- visible 디버깅과 세션 저장은 `outputs/broadcasting/session/chrome-playwright-profile/` 아래 전용 격리 Chrome 프로필에서만 수행합니다.
- Brave나 Safari로 티스토리 자동화를 실행하지 않습니다.

## 실행 조건

티스토리 공개 발행은 아래 조건을 모두 만족할 때 실행합니다.

- `BLOG_PUBLISHER=tistory`
- `TISTORY_AUTO_PUBLISH=true`
- `TISTORY_PUBLISH_MODE=public`
- `TISTORY_MANAGE_URL` 또는 `TISTORY_WRITE_URL` 설정
- `PLAYWRIGHT_STORAGE_STATE` 파일 존재
- `playwright` 패키지와 Chrome Playwright 채널 설치

운영 기본값은 `PLAYWRIGHT_HEADLESS=true`입니다. 디버깅 목적으로 visible 모드를 쓸 때도 Playwright가 만든 별도 Chrome 창만 사용해야 하며, 실제 브라우저 프로필을 발행 런타임에 연결하지 않습니다.

LinkedIn 공개 게시는 아래 조건을 모두 만족할 때 실행합니다.

- 티스토리 공개 발행 성공
- 티스토리 실제 URL 확보
- LinkedIn 원고의 `[블로그 링크]` 치환 완료
- `LINKEDIN_AUTO_PUBLISH=true`
- `LINKEDIN_ACCESS_TOKEN` 설정
- `LINKEDIN_AUTHOR_URN` 설정

티스토리 발행에 실패하면 LinkedIn은 `blocked_until_blog_url`로 기록하고 공개 게시하지 않습니다.

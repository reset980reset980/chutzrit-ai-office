# 강의 슬라이드 메이커

이 폴더는 강의운영팀의 웹 슬라이드 제작 기준을 담습니다.

기준 시스템은 `ppt-maker`의 `web-slide-maker`와 동일합니다. 순수 HTML/CSS/JavaScript 단일 파일로 강의용 슬라이드를 만들고, 외부 프레임워크 없이 브라우저에서 바로 발표할 수 있게 합니다.

## 기준 파일

- `assets/base-template.html`: 모든 슬라이드의 베이스 CSS와 JavaScript
- `references/design-rules.md`: 색상, 타이포그래피, 레이아웃, 컴포넌트 규칙
- `references/patterns.md`: 14가지 슬라이드 패턴과 HTML 구조

## 생성 규칙

- 출력은 `outputs/education/slides/`에 저장합니다.
- 파일명은 `{강의명}-slides.html` 형식으로 만듭니다.
- 모든 CSS, JavaScript, 콘텐츠는 하나의 HTML 파일 안에 포함합니다.
- 새 슬라이드를 만들 때는 `base-template.html`을 시작점으로 사용합니다.
- 슬라이드 구성은 먼저 계획으로 정리하고, 확인 후 HTML을 생성합니다.
- 섹션 전환과 임팩트 슬라이드를 제외한 모든 슬라이드 푸터는 `후츠릿 · {강의명}` 형식을 사용합니다.

## 설계 참고 문서

- `docs/education/web-slide-research.md`
- `docs/education/figma-design-rules.md`
- `.agents/skills/chutzrit-education-slides/SKILL.md`


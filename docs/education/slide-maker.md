# 강의운영팀 슬라이드 제작 시스템

강의운영팀의 PPT형 강의 자료 제작은 기존 `ppt-maker`의 웹 슬라이드 시스템을 기준으로 운영합니다.

여기서 말하는 PPT형 자료는 `.pptx` 파일이 아니라, 발표자가 브라우저에서 바로 열어 사용할 수 있는 단일 HTML 프레젠테이션입니다. 시스템의 핵심 코드는 순수 HTML/CSS/JavaScript이며, 외부 프레임워크나 빌드 과정 없이 동작합니다.

## 기준

- 베이스 템플릿: `agents/education/slide-maker/assets/base-template.html`
- 디자인 규칙: `agents/education/slide-maker/references/design-rules.md`
- 슬라이드 패턴: `agents/education/slide-maker/references/patterns.md`
- 템플릿 참조 자료: `agents/education/slide-maker/references/template-source/`
- 리서치 문서: `docs/education/web-slide-research.md`
- Figma 분석 문서: `docs/education/figma-design-rules.md`
- Codex Skill: `.agents/skills/chutzrit-education-slides/SKILL.md`

## 처리 흐름

```text
강의 원본 자료 입력
-> 강의명, 대상, 챕터, 핵심 메시지 분석
-> template-source 예시 HTML과 참고 이미지 확인
-> 슬라이드 구성안 작성
-> 구성 확인
-> base-template.html 기반 HTML 생성
-> outputs/education/slides/ 저장
-> 필요 시 브라우저에서 레이아웃 확인
-> Discord 또는 작업 보고
```

## 저장 위치

```text
outputs/education/
├── slides/
├── logs/
└── sources/
```

- `slides/`: 완성된 단일 HTML 슬라이드
- `logs/`: 생성/검증 로그
- `sources/`: PDF, PPTX, 원고 등 로컬 원본 자료

`sources/`는 비공개 강의 자료가 들어갈 수 있으므로 Git에 올리지 않습니다.

## 운영 원칙

- `ppt-maker`의 코드와 규칙을 그대로 유지합니다.
- 슬라이드 산출물은 코드 폴더에 섞지 않습니다.
- 디자인 시스템을 새로 만들지 않고 기존 dark-mode teal 시스템을 사용합니다.
- 강의용 코드 예제는 실행 가능성과 최신성을 확인한 뒤 반영합니다.
- 사람이 읽는 안내 문서는 한글로 작성합니다.

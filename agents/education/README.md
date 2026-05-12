# 강의운영팀

강의운영팀은 최신 기술, 실습 코드, 강의 원고를 실무 학습 자료로 전환하는 팀입니다.

현재 강의 자료 슬라이드 제작은 `ppt-maker` 프로젝트의 웹 슬라이드 시스템을 후츠릿 AI 오피스 구조로 옮겨와 사용합니다. 결과물은 PowerPoint 바이너리 파일이 아니라, 브라우저에서 바로 발표할 수 있는 단일 HTML 슬라이드 파일입니다.

## 현재 범위

- 강의 원본 자료 분석
- 슬라이드 구성안 작성
- 다크모드 웹 슬라이드 HTML 생성
- 실습 코드와 예제 정리
- 산출물 저장

## 슬라이드 제작 시스템

```text
agents/education/slide-maker/
├── assets/
│   └── base-template.html
└── references/
    ├── design-rules.md
    └── patterns.md
```

`base-template.html`, `design-rules.md`, `patterns.md`는 기존 `ppt-maker`의 코드와 규칙을 그대로 가져온 기준 파일입니다. 슬라이드 제작 시 이 파일들을 기준으로 사용하고, 임의로 새 디자인 시스템을 만들지 않습니다.

## 산출물 위치

```text
outputs/education/
├── slides/
├── logs/
└── sources/
```

- `slides/`: 완성된 강의 슬라이드 HTML
- `logs/`: 생성 기록과 검증 로그
- `sources/`: 로컬 강의 원본 자료 보관 위치

`outputs/education/sources/`에는 PDF, PPTX, 원고처럼 비공개일 수 있는 원본 자료가 들어갈 수 있으므로 Git에 올리지 않습니다.


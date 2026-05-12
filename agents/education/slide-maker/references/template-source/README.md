# 슬라이드 템플릿 참조 자료

이 폴더는 강의운영팀 웹 PPT를 만들 때 참고하는 템플릿 원본 자료입니다.

루트에 임시로 두었던 `slide-temp/` 자료를 `agents/education/slide-maker/references/template-source/`로 옮긴 것입니다. 생성된 슬라이드 산출물이 아니라, 슬라이드 제작 기준을 보강하는 참조 자료로 취급합니다.

## 구성

```text
template-source/
├── examples/
│   ├── sample.html
│   └── template.html
└── images/
    └── *.png
```

- `examples/template.html`: 템플릿 코드의 주 참조 파일
- `examples/sample.html`: 실제 슬라이드 구성 예시
- `images/`: 템플릿 화면 참고 이미지

## 사용 규칙

- 웹 PPT를 작성하기 전에 `examples/template.html`, `examples/sample.html`, `images/`의 구성을 먼저 확인합니다.
- 실제 산출물은 이 폴더가 아니라 `outputs/education/slides/`에 저장합니다.
- 새 슬라이드 HTML은 여전히 `agents/education/slide-maker/assets/base-template.html`을 시작점으로 사용합니다.
- 템플릿 참조 자료와 기존 `design-rules.md`, `patterns.md`가 충돌하면 기본 디자인 시스템과 슬라이드 패턴을 우선합니다.
- 이미지 파일명은 외부 템플릿 추출명을 보존합니다. 필요할 때만 의미 있는 이름으로 복사해 사용합니다.

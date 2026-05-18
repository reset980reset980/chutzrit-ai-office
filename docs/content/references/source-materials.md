# 참고자료 목록

이 문서는 후츠릿 AI 오피스 콘텐츠 에이전트가 참고할 원본 자료를 정리합니다.

원본 전체를 복사하기보다, 어떤 자료에서 무엇을 추출해야 하는지 기록합니다.

## YouTube

채널:

- https://www.youtube.com/@chutzrit

채널 문구:

```text
도전하고 성장하는 삶을 개발합니다
```

성과가 좋았던 영상:

1. n8n 서버비 월 3만원? 평생 0원으로 돌리는 법 | GCP 무료 호스팅  
   https://www.youtube.com/watch?v=_yHlMo_FxaI
2. 개발자가 맥북사면 가장 먼저 하는일  
   https://www.youtube.com/watch?v=mba8cnGcgqE
3. 맥미니 사지 마세요 | n8n으로 끝내는 AI GitHub 에이전트 (1일 1커밋 자동화)  
   https://www.youtube.com/watch?v=D2qIc5rrUp8
4. 어메이징 미친 생산성의 Raycast (for Free)  
   https://www.youtube.com/watch?v=-4D2i3zCv6s

추출할 내용:

- 주제 카테고리
- 타깃 독자/시청자
- 문제 제기 방식
- 성과가 난 소재
- 후츠릿의 강점과 포지셔닝

사용하지 않을 내용:

- 블로그, LinkedIn, Telegram 뉴스레터의 문장 스타일을 YouTube 말투에서 복사하지 않는다.

## 블로그

블로그 샘플:

- https://chutzrit.tistory.com/15
- https://chutzrit.tistory.com/16
- https://chutzrit.tistory.com/17
- https://chutzrit.tistory.com/18
- https://chutzrit.tistory.com/19

추출할 내용:

- 입력 성격에 따라 블로그 글 형태를 다르게 고르는 방식
- 기술 구현형 글의 문제 제기, 결론 선제시, 단계별 구현, 운영 한계 작성 방식
- 기술 개념 설명형 글의 문제 상황, 개념 정의, 한계, 진화 흐름 작성 방식
- 인사이트/시장 해석형 글의 사건, 수치, 숨은 변화, 실무자 역량 도출 방식
- 코드 블록 사용 방식과 코드 아래 설명 방식
- 시행착오, 주의점, 실제 운영 경험을 넣는 방식
- 문어체 평서형 반말과 짧은 단락, 소제목 중심 구조
- `결론부터 말하면`, `왜 이렇게 해야 하는가?`, `실제 운영 경험`, `한계`, `결론`처럼 독자가 따라가기 쉬운 섹션 흐름
- 참고 링크가 있을 때 맨 마지막에 공식문서, 원문, GitHub 저장소를 정리하는 방식

템플릿 파일:

- `agents/broadcasting/prompts/templates/blog.md`

## LinkedIn

활동 링크:

- https://www.linkedin.com/in/chutzrit/recent-activity/all/

제공된 대표 글:

- AI를 활용하는것 vs AI에 의존하는 것
- 메타가 몰트북을 인수한 진짜 이유
- AI 엔지니어링의 무게중심이 바뀌고 있습니다

추출할 내용:

- 문제 제기 방식
- 뉴스/사건에서 관점을 뽑는 방식
- AI 시대 실무자에게 필요한 역량 정의
- 짧은 문단과 강한 결론
- 링크와 해시태그 사용 방식
- `AI 활용 vs AI 의존`, `지능의 시대 -> 실행의 시대 -> 연결의 시대`, `프롬프트 -> 컨텍스트 -> 하네스`처럼 대비와 단계로 메시지를 선명하게 만드는 방식
- 블로그 전문으로 유입시키기 위해 통찰을 짧게 압축하고 링크를 붙이는 방식

템플릿 파일:

- `agents/broadcasting/prompts/templates/linkedin.md`

## Telegram 뉴스레터

추출할 내용:

- 생성 결과를 짧게 보고하는 방식
- 승인 필요 여부와 다음 행동을 분리하는 방식
- 저장 경로, 링크, 실행 항목을 명확히 표시하는 방식

템플릿 파일:

- `agents/broadcasting/prompts/templates/telegram.md`

## 싫어하는 톤

- 인사이트 없이 내용 나열만 하는 글
- 너무 장황하고 한 문장에 너무 많은 내용을 담는 글
- 기승전결 없이 구구절절식으로 늘어놓는 글

## 사용자 프로필

- 8년차 개발자 겸 개발 크리에이터, 강사
- 비전공자 출신
- 여러 커리어를 거쳐 현재 AI 분야로 확장 중
- 목표: AI 강사, AI 기술 관련 저자, 기업 강사
- 철학: 남들이 어려워하는 기술을 가지고, 대중이 원하는 결과물을 가장 쉽게 만들어내고 가르치는 강사
- 핵심 강점: 문제 해결 끈기, 빠른 기술 습득 능력
- 포지셔닝: "누구나 AI를 활용해 자동화 시스템을 만들수 있다"

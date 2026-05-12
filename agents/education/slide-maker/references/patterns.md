# Slide Pattern Reference

## Pattern A — 타이틀 슬라이드

**When to use:** First slide of every deck.

```html
<article class="slide active" data-index="0">
  <header class="slide__header">
    <span class="slide__label">카테고리 · 연도</span>
    <h1 class="slide__title">
      메인 <span class="hl">키워드</span> 타이틀
    </h1>
    <p class="slide__sub">한 줄 부제</p>
  </header>
  <main class="slide__body">
    <div style="display:flex;align-items:baseline;gap:0.9rem;margin-top:0.45rem;">
      <span style="font-weight:700;font-size:clamp(1rem,1.8vw,1.2rem);">강사명</span>
      <span class="dim" style="font-size:0.85em;">·</span>
      <span class="dim" style="font-size:clamp(0.95rem,1.6vw,1.1rem);">강의명 · 날짜</span>
    </div>
    <p class="body-text dim" style="max-width:52ch;">강의 한 문단 소개</p>
    <div class="tip">
      <span style="white-space:nowrap;"><span class="kw">Space</span> 또는 <span class="kw">→</span> 키로 다음</span>&nbsp;·&nbsp;<span style="white-space:nowrap;"><span class="kw">←</span> 키로 이전</span>
    </div>
  </main>
  <footer class="slide__footer"><span>후츠릿 · 강의명</span></footer>
</article>
```

---

## Pattern B — 섹션 전환

**When to use:** Chapter/section dividers. Background: teal `#1A7A6E`. No footer.
Show all chapters; mark current with `section-item--active`.

```html
<article class="slide slide--section" data-index="N">
  <nav class="section-menu">
    <div class="section-item section-item--active">
      <span class="section-arrow">→</span>
      Chapter 1 · 현재 챕터명
    </div>
    <div class="section-item">
      <span class="section-arrow">→</span>
      Chapter 2 · 다음 챕터명
    </div>
    <!-- 나머지 챕터들 -->
  </nav>
</article>
```

---

## Pattern C — 임팩트 스테이트먼트

**When to use:** One powerful sentence that deserves a full slide. Centered, large display text. No footer.

```html
<article class="slide slide--statement" data-index="N">
  <p class="slide__label" style="margin-bottom:2.7rem;">컨텍스트 레이블</p>
  <h1 class="display">
    임팩트 있는<br><span style="color:var(--teal);">핵심 문장</span>
  </h1>
  <p class="body-text dim" style="margin-top:2.7rem;max-width:38ch;line-height:1.7;">
    보충 설명 1~2줄
  </p>
</article>
```

---

## Pattern D — 좌우 50/50 분할

**When to use:** Concept + supporting quote/stat. Left = text content, Right = colored panel with emphasis.

```html
<article class="slide slide--split" data-index="N">
  <div class="split-left">
    <span class="split__label">챕터 · 주제</span>
    <h2 class="split__title">제목 —<br><span class="hl">키워드</span></h2>
    <p class="body-text dim" style="max-width:38ch;">본문 설명</p>
    <ul class="bullet-list" style="max-width:38ch;">
      <li class="ok">항목 1</li>
      <li class="no">항목 2</li>
      <li class="note">항목 3</li>
    </ul>
  </div>
  <div class="split-right split-right--teal">  <!-- or --orange or --purple -->
    <span class="split__label" style="opacity:0.55;">레이블</span>
    <p class="panel-quote">"인용 또는<br>핵심 문구"</p>
    <p class="caption" style="color:rgba(255,255,255,0.25);">출처 또는 보충</p>
  </div>
</article>
```

For big number in right panel, replace `panel-quote` with:
```html
<div class="panel-stat" style="color:var(--orange);">42<span style="font-size:0.38em;">%</span></div>
```

---

## Pattern E — 30/70 번호 목록

**When to use:** Step-by-step process (3–5 items). Uses `grid-35-65` for left label + right list.

```html
<article class="slide" data-index="N">
  <header class="slide__header">
    <span class="slide__label">챕터 · 주제</span>
    <h1 class="slide__title">제목 <span class="hl">키워드</span></h1>
    <p class="slide__sub">부제</p>
  </header>
  <main class="slide__body">
    <div class="grid-35-65" style="align-items:start;">
      <div style="display:flex;flex-direction:column;gap:1.5rem;padding-top:0.4rem;">
        <p class="body-text dim" style="line-height:1.8;">
          짧은<br><span class="kw">핵심 문구</span><br>강조
        </p>
        <p class="caption muted">보조 설명</p>
      </div>
      <ul class="num-list">
        <li>
          <span class="num-circle">1</span>
          <div>
            <div style="font-weight:600;margin-bottom:0.3rem;font-size:clamp(1.1rem,2.1vw,1.5rem);">단계 제목</div>
            <div class="caption">단계 설명 — <code>명령어</code> 포함 가능</div>
          </div>
        </li>
        <!-- 반복 -->
      </ul>
    </div>
  </main>
  <footer class="slide__footer"><span>후츠릿 · 강의명</span></footer>
</article>
```

---

## Pattern F — 어젠다

**When to use:** Table of contents when 3+ sections. Uses `grid-35-65`. Mark current/upcoming section with `active` class.

```html
<article class="slide" data-index="N">
  <header class="slide__header">
    <span class="slide__label">목차</span>
    <h1 class="slide__title">강의 <span class="hl">구성</span></h1>
    <p class="slide__sub">총 N개 챕터</p>
  </header>
  <main class="slide__body">
    <div class="grid-35-65" style="align-items:start;">
      <div style="padding-top:0.4rem;">
        <p class="body-text dim" style="line-height:1.8;">짧은 안내 문구</p>
      </div>
      <ol class="agenda-list">
        <li><span class="agenda-num">01</span><span>챕터 1 제목</span></li>
        <li class="active"><span class="agenda-num">02</span><span>현재 챕터</span></li>
        <li><span class="agenda-num">03</span><span>챕터 3 제목</span></li>
      </ol>
    </div>
  </main>
  <footer class="slide__footer"><span>후츠릿 · 강의명</span></footer>
</article>
```

---

## Pattern G-2 — 2컬럼 그리드

**When to use:** Direct comparison of two concepts, modes, or options.

```html
<article class="slide" data-index="N">
  <header class="slide__header">...</header>
  <main class="slide__body">
    <div class="grid-2">
      <div class="col-card" style="border-color:var(--border-teal);">
        <span class="col-card__num">A</span>
        <div class="col-card__title">항목 A</div>
        <div class="col-card__body">설명</div>
        <ul class="bullet-list">
          <li class="ok">장점</li>
          <li class="no">단점</li>
        </ul>
      </div>
      <div class="col-card" style="border-color:var(--border-orange);">
        <span class="col-card__num col-card__num--orange">B</span>
        <div class="col-card__title">항목 B</div>
        <div class="col-card__body">설명</div>
        <ul class="bullet-list">...</ul>
      </div>
    </div>
  </main>
  <footer class="slide__footer"><span>후츠릿 · 강의명</span></footer>
</article>
```

---

## Pattern G-3 — 3컬럼 그리드

**When to use:** Three parallel concepts, features, or steps shown side by side.

Structure is identical to G-2 but use `class="grid-3"` and add a third `col-card`. Use `.col-card__num--purple` for the third item.

Add a `.tip` after the grid if there's a summary callout to include.

---

## Pattern G-4 — 4컬럼 그리드

**When to use:** 4 items — commands, phases, features. Titles are auto-smaller via CSS (`.grid-4 .col-card__title`).

Use `class="grid-4"` with 4 `col-card` divs. Keep card content shorter than G-3 to fit 4 columns.
Use different `col-card__num` colors across the 4 cards for visual separation.

---

## Pattern J — 솔로 번호 목록

**When to use:** 3 major principles or takeaways that need emphasis. No header — the list fills the full height.

```html
<article class="slide" data-index="N">
  <main class="slide__body" style="justify-content:center;">
    <ol class="num-list-solo">
      <li>
        <span class="num-circle-lg">1</span>
        <div>
          <div style="color:var(--teal);margin-bottom:0.4rem;">원칙 제목</div>
          <div class="caption" style="font-weight:400;">원칙 설명 1~2줄</div>
        </div>
      </li>
      <li>
        <span class="num-circle-lg num-circle-lg--orange">2</span>
        <div>
          <div style="color:var(--orange);margin-bottom:0.4rem;">원칙 제목</div>
          <div class="caption" style="font-weight:400;">원칙 설명</div>
        </div>
      </li>
      <li>
        <span class="num-circle-lg num-circle-lg--purple">3</span>
        <div>
          <div style="color:var(--purple);margin-bottom:0.4rem;">원칙 제목</div>
          <div class="caption" style="font-weight:400;">원칙 설명</div>
        </div>
      </li>
    </ol>
  </main>
</article>
```

---

## Pattern L — 텍스트 + 오른쪽 그리드

**When to use:** Left side has explanatory text + bullets; right side has a visual grid (language tags, icons, tags).

```html
<article class="slide" data-index="N">
  <header class="slide__header">...</header>
  <main class="slide__body">
    <div class="grid-2" style="align-items:start;">
      <div style="display:flex;flex-direction:column;gap:1.5rem;padding-top:0.4rem;">
        <p class="body-text dim" style="line-height:1.8;">설명 텍스트</p>
        <ul class="bullet-list">
          <li class="ok">항목</li>
        </ul>
      </div>
      <div class="lang-grid">
        <span class="lang-tag lang-tag--teal">Python</span>
        <span class="lang-tag lang-tag--orange">Rust</span>
        <span class="lang-tag lang-tag--purple">Swift</span>
        <span class="lang-tag lang-tag--green">React</span>
        <!-- 최대 16개 (4×4) -->
      </div>
    </div>
  </main>
  <footer class="slide__footer"><span>후츠릿 · 강의명</span></footer>
</article>
```

For non-language grids, use `col-card` or simple styled `div` elements inside a `grid-3` or `grid-4`.

---

## Pattern Code-A — 풀 코드 블록

**When to use:** Code is the main content and needs maximum vertical space.

```html
<article class="slide" data-index="N">
  <header class="slide__header">
    <span class="slide__label">챕터 · 주제</span>
    <h1 class="slide__title">함수명 또는 <span class="hl">개념</span></h1>
    <p class="slide__sub">코드 설명 한 줄</p>
  </header>
  <main class="slide__body">
    <div class="code-col">
      <pre>코드 내용 (syntax highlighted)</pre>
    </div>
  </main>
  <footer class="slide__footer"><span>후츠릿 · 강의명</span></footer>
</article>
```

The `slide__body > .code-col` CSS rule gives it `flex:1` automatically.

---

## Pattern Code-B — 좌 설명 + 우 코드

**When to use:** Code needs explanation alongside it.

```html
<article class="slide" data-index="N">
  <header class="slide__header">...</header>
  <main class="slide__body">
    <div class="grid-2">
      <div style="display:flex;flex-direction:column;gap:1.5rem;">
        <p class="body-text dim" style="max-width:32ch;">설명 텍스트</p>
        <ul class="bullet-list">
          <li class="ok"><code>관련 코드</code> 설명</li>
          <li class="note"><code>주의사항</code></li>
        </ul>
        <div class="tip">핵심 포인트</div>
      </div>
      <div class="code-col">
        <pre>코드 내용</pre>
      </div>
    </div>
  </main>
  <footer class="slide__footer"><span>후츠릿 · 강의명</span></footer>
</article>
```

---

## Pattern M — 클로징

**When to use:** Final slide. No footer. Uses display font for impact. Centered.

```html
<article class="slide slide--statement" data-index="N">
  <p class="slide__label" style="margin-bottom:2.1rem;">강의명 · 연도</p>
  <h1 class="display" style="font-size:clamp(3rem,8vw,6.5rem);">
    마무리<br><span style="color:var(--teal);">핵심 메시지</span>
  </h1>
  <p class="body-text dim" style="margin-top:2.7rem;max-width:40ch;line-height:1.7;">
    마무리 문장
  </p>
  <div style="margin-top:3rem;display:flex;align-items:center;gap:1.8rem;">
    <span style="font-weight:700;font-size:clamp(1rem,1.8vw,1.3rem);">후츠릿</span>
    <span class="muted">·</span>
    <span class="caption muted">이메일 또는 링크 (선택)</span>
  </div>
</article>
```

---

## Slide data-index Attribute

Every `<article class="slide">` needs `data-index="N"` starting from 0.
The first slide must have `class="slide active"`.
All others: `class="slide"`.

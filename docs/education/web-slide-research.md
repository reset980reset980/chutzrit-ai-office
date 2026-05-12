# 순수 바닐라 HTML/CSS/JS 강의용 웹 슬라이드 구현 리서치

> 외부 라이브러리(Reveal.js 등) 없이 순수 바닐라로 프로덕션급 강의 슬라이드를 구현하는 기술 가이드

---

## 1. 다크모드 강의용 레이아웃 & DOM 구조

### 1.1 16:9 Full-Viewport 레이아웃

**권장 방식 (현대 브라우저)**
```css
.slide-deck {
  position: fixed;
  top: 0; left: 0;
  width: 100vw;
  height: 100dvh;       /* dynamic viewport height - 모바일 주소바 대응 */
  overflow: hidden;
}

.slide {
  position: absolute;
  top: 0; left: 0;
  width: 100%;
  height: 100%;
  aspect-ratio: 16 / 9; /* 고정 비율 */
}

/* 폴백: aspect-ratio 미지원 환경 */
@supports not (aspect-ratio: 16 / 9) {
  .slide { height: calc(100vw * 9 / 16); }
}
```

**전체 스케일링이 필요한 경우 (Reveal.js 방식)**
```javascript
function scaleSlide() {
  const scaleX = window.innerWidth / 1920;
  const scaleY = window.innerHeight / 1080;
  const scale = Math.min(scaleX, scaleY);
  deck.style.transform = `scale(${scale})`;
  deck.style.transformOrigin = 'top left';
}
window.addEventListener('resize', scaleSlide);
```

### 1.2 색상 체계 (GitHub Dark 기준)

```css
:root {
  --bg-primary:   #0d1117;  /* 슬라이드 배경 */
  --bg-secondary: #161b22;  /* 카드, 패널 */
  --bg-tertiary:  #21262d;  /* 코드 블록 */

  --text-primary:   #e6edf3; /* 본문 - 대비비 16.8:1 ✓ AAA */
  --text-secondary: #8b949e; /* 보조 - 대비비 7.3:1 ✓ AA  */

  --accent-cyan:    #00ffcc; /* 핵심 키워드 */
  --accent-blue:    #88ddff; /* 정보, 부연 */
  --accent-orange:  #ffaa00; /* 경고, 주의 */
  --accent-green:   #00ff88; /* 성공, 완료 */
  --accent-red:     #ff7799; /* 에러, 부정 */

  --border:         #30363d;
}
```

### 1.3 슬라이드 DOM 구조

```html
<div class="slide-deck">
  <article class="slide" data-slide-index="0">
    <header class="slide__header">
      <h1 class="slide__title">제목</h1>
      <p class="slide__subtitle">부제목</p>
    </header>
    <main class="slide__body">
      <!-- 콘텐츠 -->
    </main>
    <footer class="slide__footer">
      <span class="slide__topic">주제 태그</span>
    </footer>
  </article>
</div>

<!-- 고정 UI (슬라이드 위층) -->
<nav class="slide-nav" aria-label="슬라이드 네비게이션">
  <button id="prev-btn" aria-label="이전 슬라이드">←</button>
  <button id="next-btn" aria-label="다음 슬라이드">→</button>
</nav>
<div class="progress-bar"><div class="progress-fill"></div></div>
```

```css
/* CSS Grid로 슬라이드 영역 분할 */
.slide {
  display: grid;
  grid-template-rows: auto 1fr auto;
  padding: clamp(2rem, 5vw, 4rem);
  gap: clamp(1rem, 2vh, 2rem);
}

/* 반응형 폰트: 미디어쿼리 없이 viewport 단위로 자동 조정 */
.slide__title    { font-size: clamp(2rem,   8vw, 4rem);   }
.slide__subtitle { font-size: clamp(1rem,   3vw, 1.5rem); }
.slide__body p   { font-size: clamp(1rem,   2.5vw, 1.5rem); }
.slide__body li  { font-size: clamp(0.95rem, 2.3vw, 1.4rem); }
```

---

## 2. 핵심 내용 강조 시각화 기법

### 2.1 키워드 강조 기법

#### Glow 효과 (네온)
```css
.keyword-glow {
  color: #00ffcc;
  font-weight: 600;
  text-shadow: 0 0 5px #00ffcc, 0 0 15px rgba(0,255,204,0.4);
}
```

#### 형광 마커 효과
```css
mark {
  background: linear-gradient(120deg,
    rgba(0,255,136,0.2) 0%, rgba(0,255,136,0.35) 50%, rgba(0,255,136,0.2) 100%
  );
  color: #00ffaa;
  padding: 2px 4px;
  border-radius: 2px;
  box-decoration-break: clone; /* 다중 줄 대응 */
}
```

#### 좌측 강조 바
```css
.emphasis-bar {
  border-left: 4px solid #00ffcc;
  padding-left: 12px;
  background: rgba(0,255,204,0.05);
  border-radius: 0 4px 4px 0;
}
```

#### 배지(Badge)
```css
.badge {
  display: inline-block;
  padding: 3px 10px;
  background: rgba(0,255,204,0.15);
  color: #00ffcc;
  border: 1px solid rgba(0,255,204,0.4);
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: 600;
}
.badge--warning { background: rgba(255,170,0,0.15); color: #ffaa00; border-color: rgba(255,170,0,0.4); }
.badge--danger  { background: rgba(255,119,153,0.15); color: #ff7799; border-color: rgba(255,119,153,0.4); }
.badge--success { background: rgba(0,255,136,0.15); color: #00ff88; border-color: rgba(0,255,136,0.4); }
```

### 2.2 코드 블록 스타일링

```css
pre {
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-left: 4px solid var(--accent-blue);
  border-radius: 6px;
  padding: 1.2rem 1.5rem;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: clamp(0.75rem, 1.5vw, 1rem);
  line-height: 1.6;
  overflow-x: auto;
}

/* 인라인 코드 */
code:not(pre code) {
  background: rgba(136,221,255,0.12);
  color: #79c0ff;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.9em;
}

/* 특정 줄 강조 */
.hl-line {
  display: block;
  background: rgba(0,255,136,0.1);
  border-left: 3px solid #00ff88;
  margin: 0 -1.5rem;
  padding: 0 1.5rem 0 calc(1.5rem - 3px);
}
```

### 2.3 계층 구조 시각화 (아이콘 없이)

```css
/* 커스텀 불릿 (::before) */
li { list-style: none; position: relative; padding-left: 1.5rem; }
li::before { content: '▸'; position: absolute; left: 0; color: var(--accent-cyan); }

/* 체크/X 불릿 */
li.check::before { content: '✓'; color: var(--accent-green); font-weight: 700; }
li.cross::before { content: '✕'; color: var(--accent-red);   font-weight: 700; }

/* 자동 번호 배지 */
ol { counter-reset: step-counter; list-style: none; }
li { counter-increment: step-counter; padding-left: 3rem; position: relative; }
li::before {
  content: counter(step-counter);
  position: absolute; left: 0;
  width: 2rem; height: 2rem;
  background: rgba(0,255,204,0.2);
  border: 2px solid var(--accent-cyan);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.85em; color: var(--accent-cyan);
}
```

### 2.4 색상별 사용 용도 정리

| 색상 | 헥스 | 용도 |
|------|------|------|
| 청록 `--accent-cyan`   | `#00ffcc` | 핵심 키워드, 브랜드 강조 |
| 파랑 `--accent-blue`   | `#88ddff` | 정보, 부연설명, 코드 |
| 주황 `--accent-orange` | `#ffaa00` | 경고, 주의사항 |
| 녹색 `--accent-green`  | `#00ff88` | 성공, Best Practice |
| 빨강 `--accent-red`    | `#ff7799` | 에러, 피해야 할 방법 |

---

## 3. 슬라이드 전환 & 네비게이션

### 3.1 CSS Fade 전환 (강의 최적)

강의 중 집중을 방해하지 않는 방식으로 **Fade(opacity)** 전환이 Slide보다 적합.  
전환 속도: **300~350ms** (200ms 이하 = 너무 빠름, 400ms 이상 = 답답함)

```css
.slide {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.32s ease-in-out;
  will-change: opacity;         /* GPU 힌트 */
  transform: translateZ(0);     /* 레이어 승격 */
  backface-visibility: hidden;
}

.slide.active {
  opacity: 1;
  pointer-events: auto;
}
```

### 3.2 이벤트 잠금 (isAnimating 패턴)

```javascript
class SlidePresentation {
  currentSlide = 0;
  currentStep  = 0;
  isAnimating  = false;          // 핵심 플래그

  goToSlide(index) {
    if (this.isAnimating) return;              // 잠금 확인
    if (index === this.currentSlide) return;

    this.isAnimating = true;
    const prev = this.slides[this.currentSlide];
    const next = this.slides[index];
    this.currentSlide = index;

    prev.classList.remove('active');
    next.classList.add('active');

    // transitionend로 완료 감지 (정확)
    next.addEventListener('transitionend', () => {
      this.isAnimating = false;
      this.updateUI();
    }, { once: true });

    // Fallback: transition 미발생 시 강제 해제
    setTimeout(() => { this.isAnimating = false; }, 400);
  }
}
```

### 3.3 키보드 & 터치 네비게이션

```javascript
// 키보드
document.addEventListener('keydown', e => {
  if (this.isAnimating) return;
  switch (e.key) {
    case 'ArrowRight': case ' ': e.preventDefault(); this.advance();  break;
    case 'ArrowLeft':             e.preventDefault(); this.previous(); break;
    case 'Home': e.preventDefault(); this.goToSlide(0);                    break;
    case 'End':  e.preventDefault(); this.goToSlide(this.totalSlides - 1); break;
  }
});

// 터치 스와이프
let touchStartX = 0, touchStartY = 0;
container.addEventListener('touchstart', e => {
  touchStartX = e.changedTouches[0].screenX;
  touchStartY = e.changedTouches[0].screenY;
});
container.addEventListener('touchend', e => {
  const dx = e.changedTouches[0].screenX - touchStartX;
  const dy = e.changedTouches[0].screenY - touchStartY;
  if (Math.abs(dx) < 50 || Math.abs(dy) > Math.abs(dx)) return; // 노이즈 필터
  dx < 0 ? this.advance() : this.previous();
});
```

### 3.4 진행률 & 점 네비게이터

```css
/* 상단 진행 바 */
.progress-bar {
  position: fixed; top: 0; left: 0;
  width: 100%; height: 3px;
  background: rgba(255,255,255,0.1);
  z-index: 100;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue));
  transition: width 0.3s ease-out;
  will-change: width;
}

/* 점 네비게이터 */
.dot { width: 8px; height: 8px; border-radius: 50%; background: rgba(255,255,255,0.3); transition: all 0.25s ease; }
.dot.active { width: 20px; border-radius: 4px; background: var(--accent-cyan); }
```

---

## 4. 강의용 콘텐츠 빌드 효과

### 4.1 data-step 방식 순차 Reveal

```html
<!-- HTML 마크업: 순서 지정 -->
<ul>
  <li data-step="1">첫 번째 항목</li>
  <li data-step="2">두 번째 항목</li>
  <li data-step="3">세 번째 항목</li>
</ul>
```

```css
/* 숨김 상태: visibility로 완전히 숨겨 탭 순서 제외 */
[data-step] {
  opacity: 0;
  visibility: hidden;
  transform: translateY(16px);
  transition: opacity 0.5s ease, transform 0.5s ease, visibility 0.5s;
  will-change: opacity, transform;
}

/* 공개 상태 */
[data-step].revealed {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

/* 이전 항목 dimming (선택) */
[data-step].past {
  opacity: 0.45;
}
```

```javascript
advance() {
  const maxStep = this.getMaxStep(); // 현재 슬라이드 최대 step
  if (this.currentStep < maxStep) {
    this.currentStep++;
    this.revealStep(this.currentStep);
  } else {
    this.nextSlide();         // 모든 step 공개 후 → 다음 슬라이드
  }
}

revealStep(step) {
  const slide = this.slides[this.currentSlide];
  slide.querySelectorAll('[data-step]').forEach(el => {
    const s = parseInt(el.dataset.step);
    el.classList.toggle('revealed', s <= step);
    el.classList.toggle('past',     s < step);
  });
}

resetSteps() {
  // 슬라이드 진입 시 초기화
  this.currentStep = 0;
  this.slides[this.currentSlide]
    .querySelectorAll('[data-step]')
    .forEach(el => el.classList.remove('revealed', 'past'));
}
```

### 4.2 애니메이션 패턴 선택 기준

| 상황 | 권장 방식 | 이유 |
|------|----------|------|
| 단순 등장 효과 | `CSS transition` | 메인 스레드 부담 없음 |
| 반복 애니메이션 | `CSS @keyframes` | 브라우저 엔진이 최적화 |
| 사용자 입력 반응 | `requestAnimationFrame` | 60fps 보장 |
| setInterval | **절대 금지** | 프레임 드롭, 불정확 |

### 4.3 GPU 가속 최적화

```css
/* GPU 가속: transform, opacity만 animate */
.slide, [data-step] { will-change: opacity, transform; }

/* 애니메이션 종료 후 해제 (메모리 절약) */
.slide:not(.active)       { will-change: auto; }
[data-step].revealed      { will-change: auto; }

/* 레이어 승격 */
.slide { transform: translateZ(0); backface-visibility: hidden; }
```

**절대 animate하면 안 되는 속성:** `width`, `height`, `left`, `top`, `margin`, `padding`  
→ 매 프레임 레이아웃 리플로우 발생, 성능 급락

---

## 5. 종합 구현 체크리스트

```
레이아웃
  ✓ aspect-ratio: 16/9 + width: 100vw
  ✓ 100dvh (동적 viewport height)
  ✓ clamp()로 폰트/간격 자동 조정 (미디어쿼리 불필요)
  ✓ CSS Grid: grid-template-rows: auto 1fr auto

색상 & 강조
  ✓ --bg-primary: #0d1117 기준 레이어 체계
  ✓ WCAG AAA 대비비 충족 색상 팔레트
  ✓ glow, marker, badge, 코드블록 강조 기법

전환 & 네비게이션
  ✓ opacity 전환 (300ms) + isAnimating 잠금
  ✓ transitionend 이벤트로 완료 감지
  ✓ 키보드: ArrowRight/Left, Space, Home, End
  ✓ 터치: touchstart/touchend 스와이프
  ✓ 상단 진행 바 + 점 네비게이터

콘텐츠 빌드
  ✓ data-step 속성으로 순차 공개
  ✓ visibility + opacity + transform 조합
  ✓ Space/→로 step 진행, 마지막 step 후 슬라이드 이동
  ✓ 슬라이드 진입 시 step 초기화

성능
  ✓ will-change: opacity, transform (시작 시 설정, 종료 시 해제)
  ✓ transform: translateZ(0), backface-visibility: hidden
  ✓ CSS transition 우선, RAF는 필요할 때만
  ✓ 레이아웃 리플로우 유발 속성 animate 금지
```

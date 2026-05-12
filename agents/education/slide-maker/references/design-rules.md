# Design Rules Reference

## Color Tokens (CSS Variables)

```css
/* Backgrounds */
--bg:        #0d1117   /* slide background */
--bg-card:   #161b22   /* card, panel */
--bg-code:   #1e2430   /* code block */
--bg-inset:  #252d3a   /* nested elements */

/* Text */
--text:      #e6edf3   /* primary */
--text-dim:  #8b949e   /* secondary, captions */
--text-muted:#484f58   /* very faint, footer */

/* Accents */
--teal:      #2DD4BF   /* primary accent — most elements */
--orange:    #FF6D3B   /* warning, secondary emphasis */
--yellow:    #F0B429   /* numbers, stats */
--purple:    #A78BFA   /* code concepts, info */
--green:     #4ADE80   /* success, checkmarks */

/* Borders */
--border:        rgba(255,255,255,0.08)
--border-teal:   rgba(45,212,191,0.25)
--border-orange: rgba(255,109,59,0.25)
--border-purple: rgba(167,139,250,0.25)
```

**Rule:** One accent color per slide. Use `--teal` for 80%+ of accents. Use others only when semantic role is clear (--orange = warning, --green = success, --purple = code/info).

---

## Typography Classes

| Class | Font | Size | Weight | Use |
|---|---|---|---|---|
| `.display` | GmarketSans | clamp(2.8rem,7vw,5.5rem) | 900 | Impact titles, closing |
| `.slide__title` | Pretendard | clamp(2rem,5.2vw,3.8rem) | 800 | Slide main title |
| `.split__title` | Pretendard | clamp(1.7rem,4.2vw,3rem) | 800 | Split layout title |
| `.h2` | Pretendard | clamp(1.3rem,2.8vw,2.1rem) | 700 | Section heads |
| `.col-card__title` | Pretendard | clamp(1.4rem,2.8vw,2rem) | 700 | Card titles (H3) |
| `.body-text` | Pretendard | clamp(1.1rem,2.1vw,1.5rem) | 400 | Body copy |
| `.caption` | Pretendard | clamp(0.9rem,1.45vw,1.15rem) | 400 | Captions, subtitles |
| `.slide__label` | Pretendard | clamp(0.58rem,0.85vw,0.72rem) | 700 | Chapter/category label |
| `.panel-quote` | GmarketSans | clamp(1.3rem,2.8vw,2.1rem) | 700 | Panel emphasis |
| `.panel-stat` | GmarketSans | clamp(4rem,9.5vw,7rem) | 900 | Big numbers |

**Modifiers:**
- `.dim` → color: var(--text-dim)
- `.muted` → color: var(--text-muted)
- `.kw` → teal keyword
- `.kw-orange` → orange keyword
- `.kw-purple` → purple keyword
- `.kw-green` → green keyword
- `.kw-yellow` → yellow keyword
- `.hl` → teal highlight (in titles: `<span class="hl">word</span>`)
- `.hl-orange` → orange highlight
- `.hl-purple` → purple highlight

---

## Layout Classes

### Grid
```
.grid-2      → 2 equal columns
.grid-3      → 3 equal columns
.grid-4      → 4 equal columns
.grid-35-65  → 30/70 split (left label, right content)
```

### Slide Variants
```
.slide               → standard 3-row grid (header / body / footer)
.slide--section      → full-screen teal, centered menu (no padding)
.slide--statement    → centered, large display text (no header/footer)
.slide--split        → side-by-side flex (no padding, left+right divs)
```

### Split Layout Components
```
.split-left          → flex column, justify-content:center, padded
.split-right         → fixed 48% width, flex column, padded
.split-right--teal   → background: #0d2420
.split-right--orange → background: #231408
.split-right--purple → background: #1a1030
```

---

## Component Classes

### Cards
```
.card               → dark card, 1px border
.card--teal         → teal left border + tinted bg
.card--orange       → orange left border + tinted bg
.card--green        → green left border + tinted bg
.card--purple       → purple left border + tinted bg
.card__label        → uppercase label inside card
```

### Column Cards (for grid layouts)
```
.col-card           → card for grid-2/3/4 columns
.col-card__num      → teal circle number badge
.col-card__num--orange / --purple / --green
.col-card__title    → H3 title inside col-card
.col-card__body     → body text inside col-card
```

### Lists
```
.num-list           → numbered list with circle badges
.num-circle         → teal circle (used inside .num-list li)
.num-circle--orange / --purple / --green

.num-list-solo      → large solo numbered list (J pattern, no header)
.num-circle-lg      → large circle for J pattern
.num-circle-lg--orange / --purple

.bullet-list        → dash-prefixed bullet list
  li.ok             → ✓ green
  li.no             → ✕ orange
  li.note           → → yellow
```

### Special Components
```
.tip                → teal bordered callout box
.divider            → 1px horizontal rule
.section-menu       → flex column for section slide
.section-item       → one item in section menu
.section-item--active → bold white, shows arrow
.agenda-list        → F-pattern agenda list
.lang-grid          → 4-col grid of language tags
.lang-tag           → individual language tag
.lang-tag--teal/--orange/--purple/--green
```

### Code
```
.code-col           → flex wrapper enabling full-height pre scroll
pre                 → code block (overflow-y:auto, overflow-x:hidden)
pre .hl             → highlighted line
pre .kw / .fn / .st / .cm / .nm / .op → syntax colors
```

---

## Spacing Rules

- **Slide padding:** `clamp(2.5rem,5.5vh,4.5rem)` vertical, `clamp(3.5rem,9vw,8rem)` horizontal
- **Slide gap:** `clamp(1.5rem,3.75vh,3rem)` (between header/body/footer)
- **Body gap:** `clamp(1.2rem,2.7vh,2.1rem)` (between elements in body)
- **Grid gap:** `clamp(1.2rem,3vw,2.1rem)` (grid-2/3/4)
- **Section menu gap:** `2.1rem`
- Never use fixed px values for spacing — use rem/vw/vh or clamp()

# BUILD INSTRUCTIONS — for the implementing model
Read `01_DESIGN_DOC.md` first. Follow this file **step by step, in order**. Do NOT add features, libraries, or pages not listed. Do NOT rename files. After each step, run the app and check the "DONE WHEN" line before moving on.

## 0. GOLDEN RULES (never break)
1. Never write a Swami Vivekananda quote yourself. Quotes only come from `src/data/quotes.json`.
2. Every AI-written text block carries the `<AiLabel/>` badge: "AI-written · not Swami Vivekananda's words".
3. Every Quote Card shows its source and a "Verified" chip.
4. All colours/fonts/radii come from CSS variables. **No hard-coded hex values in components.**
5. Mobile first (design at 375px, then scale up to 1280px).
6. Minimalist: max 1 accent colour per screen, generous whitespace, no extra decoration beyond the ornament kit.
7. If unsure, do the simpler thing.

## 1. Stack
- Vite + React 18 + TypeScript, react-router-dom v6, plain CSS (one `styles/` folder, CSS variables). No Tailwind, no UI library.
- Animation: CSS transitions/keyframes only (optional: `framer-motion` allowed ONLY for the reel player).
- Backend: single Node/Express file `server/index.ts` with `POST /api/reel`. (In Phase 1, can return mock JSON — see §9.)
- Google Fonts via `<link>` in `index.html`: Fraunces, Inter, Cormorant Garamond, DM Sans, DM Serif Display.

## 2. Folder structure (create exactly)
```
src/
  main.tsx  App.tsx
  styles/ tokens.css  base.css  components.css
  themes/ theme-kesari.css  theme-clay.css  theme-indigo.css
  data/ lessons.json  quotes.json  episodes.json
  components/ Nav.tsx TabBar.tsx AiLabel.tsx QuoteCard.tsx IkigaiWheel.tsx
              LessonListView.tsx PetalSheet.tsx ReelPlayer.tsx
              ThemeSwitcher.tsx MandalaWatermark.tsx ProgressRing.tsx Chip.tsx
  pages/ Home.tsx Journey.tsx Lesson.tsx Episode.tsx Sos.tsx SosResult.tsx About.tsx
  lib/ progress.ts  recommend.ts  api.ts  i18n.ts
server/index.ts
```

## 3. Theming (Step 1)
- `<html data-theme="kesari|clay|indigo">`. Default `kesari`. Store in localStorage `theme`.
- Each theme file defines, under `[data-theme="x"]`, these variables: `--bg --surface --ink --muted --accent --accent-2 --accent-soft --line --quote-bg --font-head --font-body --radius --shadow` using values from Design Doc §9.
- `ThemeSwitcher`: small 3-dot button group fixed bottom-left (so the user can compare the 3 themes live). Remove later via a single constant `SHOW_THEME_SWITCHER`.
- DONE WHEN: clicking the dots changes the whole app's colours/fonts instantly.

## 4. Base styles (Step 2)
`body{background:var(--bg);color:var(--ink);font-family:var(--font-body);line-height:1.5}`; headings use `--font-head`. Container: `max-width:1100px;margin:auto;padding:0 20px` (64px ≥1024px). Buttons: pill, height 48px, `--accent` bg, text on-accent (white for kesari/indigo-light? use `#fff` for A, `#2A1E17` for B, `#1F2A5C` for C → define `--on-accent` variable in each theme). Secondary button: transparent, 1px `--line` border. Card: `--surface`, 1px `--line`, radius `--radius`, padding 20px, `--shadow`.
Headings get an accent underline: `background:linear-gradient(var(--accent),var(--accent)) 0 100%/100% 3px no-repeat;display:inline;padding-bottom:2px`.

## 5. Navigation (Step 3)
- ≥768px: top `Nav` — logo "Arise" left; links Home, Journey; right: **SOS** pill button (accent).
- <768px: bottom `TabBar` with 3 items Home / Journey / SOS (SOS centre, raised circle, accent). Add `padding-bottom:80px` to body on mobile.
- DONE WHEN: routes switch, active item highlighted.

## 6. Data (Step 4)
`lessons.json`: array of 8 `{id:1..8, slug, title, painPoint, summary, icon, quoteIds[]}` exactly per Design Doc §5.
`quotes.json`: `{id, text, source, sourceUrl, verified:true|false, topics:[]}`; seed with the 5 candidates in Design Doc §13 and set `verified:false` with a `TODO verify` note until a human confirms. UI shows only `verified:true`; for dev, a constant `ALLOW_UNVERIFIED_IN_DEV=true` may show them with a red "UNVERIFIED" tag.
`episodes.json`: for each lesson 6 episodes `{lessonId, ep, title, hook, story, quoteId, meaning, tryThis, nextHook}`. Write placeholder copy that follows the arc in Design Doc §5; keep each field ≤40 words; stories are tagged `ai:true`.

## 7. Pages
### 7.1 Home
Order: Hero ("Arise. Awake." H1 with underline; subtitle "Swami Vivekananda, for the problems you actually have.") → two large cards side-by-side (stacked on mobile): Journey card (mini wheel SVG, text "8 lessons · 6 episodes each"), SOS card (pulsing ring, text "Stuck right now? Get a 45-second reel.") → Daily Quote (`QuoteCard`, index = dayOfYear % verifiedQuotes.length) → footer line with disclaimer and link to /about. `MandalaWatermark` behind hero at 6% opacity.

### 7.2 Journey — `IkigaiWheel` (the hero component)
- SVG viewBox 0 0 400 400. Centre (200,200). 8 petals: circles r=78 whose centres lie on a circle of radius 85 from centre, angles `i*45°-90°`. Fill `var(--accent)` with `fill-opacity` = 0.12 + 0.10*(episodesCompleted/6); stroke `var(--accent)`; `mix-blend-mode:multiply` (use `isolation:isolate` on svg).
- Number + one-word title as `<text>` placed at radius 135 along the same angle, text-anchor middle, `--font-head`.
- Centre circle r=46, fill `--surface`, shows `ProgressRing` + text "YOU" and "x/48".
- Interaction: hover (desktop) → petal scale 1.04 + opacity up; click/tap → open `PetalSheet` (desktop: side card; mobile: bottom sheet) with lesson title, painPoint in quotes, "6 episodes" and button "Begin" → `/journey/:id`. Keyboard: petals are `<a>`/`role=button` with tabindex and Enter.
- Idle rotation: `@keyframes spin{to{transform:rotate(360deg)}}` 120s on petals group only (labels counter-stay upright by NOT being in the group); disable under `prefers-reduced-motion`.
- Toggle "Wheel | List" above it; List = `LessonListView` (8 cards).
- Below: horizontal scroll chips "Start where it hurts": 8 painPoints → link to lesson.
- DONE WHEN: on 375px the wheel is fully visible, tappable, sheet opens.

### 7.3 Lesson page
Header: lesson number, title, painPoint, summary. Then 6 episode rows (number, title, check icon if done, lock look NOT used — all unlocked). "Continue" button → next incomplete episode.

### 7.4 Episode page (card-stack, one block per screen, swipe/Next button)
Blocks in order: 1 HOOK (large text) → 2 STORY (with `AiLabel`) → 3 TEACHING (`QuoteCard` + meaning) → 4 TRY THIS (checkbox "I did it") → 5 NEXT HOOK (italic cliffhanger + "Next episode →"). Top: segmented progress (5 segments). On finishing, call `markDone(lessonId, ep)`; after ep 6 show "Next lesson →".

### 7.5 SOS
Input screen exactly per Design Doc §7 screen 1. Textarea min 10 chars, max 400, counter. Chips fill the textarea. Language select (English, हिन्दी, বাংলা). Submit → show generating screen (steps advance every ~1.2s while awaiting API), then navigate to `/sos/result` with state. Error state: friendly message + retry. Crisis safety: if input contains self-harm keywords (list in `lib/safety.ts`: "suicide","kill myself","end my life","self harm", etc.) do NOT generate a reel; show a calm card with "You matter. Please talk to someone now" and India helplines (Tele-MANAS 14416, KIRAN 1800-599-0019). Verify numbers before shipping.

### 7.6 SOS Result
Per Design Doc §7 screen 3. `ReelPlayer` props: `scenes: {type:'hook'|'situation'|'quote'|'meaning'|'action'|'outro', text, quoteId?, durationMs}[]`, `lang`. Behaviour: 9:16 container (`aspect-ratio:9/16;max-width:420px`), auto-advance scenes, tap left/right to go back/forward, tap-hold to pause, Stories-style segmented bar, subtitle text bottom, background = theme gradient + MandalaWatermark with slow float animation, scene text fades up. Quote scene renders `QuoteCard` content (looks different: bordered, `--quote-bg`, "Verified · source"). Narration button uses `window.speechSynthesis` with `lang` mapping (en-IN, hi-IN, bn-IN). Under/next to player: Source card, language chips (re-calls API with new lang), Transcript accordion, **Recommended lesson card** (from `lib/recommend.ts` / API), and disclaimer strip. Share button uses `navigator.share` with fallback copy link.

### 7.7 About
Sections: What this is · How quotes are verified · What is AI-written · Sources (links: Belur Math official quotations, videos, fact-check) · Limitations.

## 8. Reusable components spec
- `AiLabel`: small pill, `--accent-soft` bg, text "AI-written · not Swami Vivekananda's words", ✨ icon.
- `QuoteCard`: left 4px accent border, `--quote-bg`, serif text 20–24px, big quote mark ornament, footer: source + "✓ Verified" chip + external link icon.
- `ProgressRing`: SVG circle stroke-dasharray.
- `Chip`: pill, 36px high, 1px `--line`, hover `--accent-soft`.

## 9. Recommendation + API contract
`POST /api/reel` body `{prompt:string, lang:'en'|'hi'|'bn'}` → response:
```json
{ "quoteId":"q3", "lessonId":3, "episode":2,
  "scenes":[{"type":"hook","text":"…","durationMs":6000}, …],
  "transcript":"…", "disclaimer":"Story is AI-written." }
```
Server steps: (1) safety check; (2) classify prompt to one of 8 lessons (LLM call or keyword score against `topics` — implement keyword fallback in `lib/recommend.ts` first); (3) pick verified quote for that lesson; (4) LLM writes hook/situation/meaning/action ONLY (prompt must forbid quoting the Swami; the server injects the quote text from the library into the quote scene); (5) translate non-quote text if lang≠en; (6) return JSON; validate shape, total duration 30–60s.
**Phase 1 (do this first):** server returns mock JSON built from `episodes.json` of the matched lesson, so the entire UI works with no AI key. Phase 2 swaps in the LLM call (key in `.env`, never in client).

## 10. Progress (`lib/progress.ts`)
localStorage `progress` = `{ "1":[1,2], "3":[1] }`; functions `markDone, getDone(lessonId), totalDone()`. No accounts.

## 11. Responsive rules
<768px: single column, bottom tab bar, wheel full width. 768–1100: two-column cards. ≥1100: container 1100px; SOS result = 2 columns (player left, details right).

## 12. QA checklist (must pass)
- [ ] Switching all 3 themes: no unreadable text, no hard-coded colours (grep for `#` in `components/` and `pages/` → none).
- [ ] 375px and 1280px screenshots of Home, Journey, Lesson, Episode, SOS, Result look right.
- [ ] Wheel works with keyboard and touch; list fallback works.
- [ ] Every quote shows source + Verified; every AI text shows AiLabel.
- [ ] Reel runs 30–60s, subtitles visible, pause works, language switch works.
- [ ] Recommended lesson card links to the correct episode.
- [ ] Crisis keywords → helpline card, no reel.
- [ ] Lighthouse accessibility ≥ 90; reduced-motion respected.
- [ ] No console errors.

## 13. Build order (summary)
1 scaffold + tokens/themes → 2 base styles + Nav/TabBar → 3 data JSON → 4 Home → 5 IkigaiWheel + Journey → 6 Lesson + Episode + progress → 7 SOS input + safety → 8 mock API + ReelPlayer + Result + recommendation → 9 About → 10 QA → 11 (optional) real LLM.

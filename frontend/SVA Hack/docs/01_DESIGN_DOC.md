# DESIGN DOC — "Arise" (working name): Vivekananda for Gen Z / Alpha
Case Study 06 — Teaching-to-Reel Generator. Web app, mobile-first, works on laptop.

---
## 1. Product in one line
Two doors into Swami Vivekananda's teachings: **Journey** (a calm, structured 8-lesson series) and **SOS** (type your problem → get a 30–60s reel + the closest Journey lesson).

## 2. Non-negotiable principles (from the problem statement)
1. **Never invent quotations.** Every quote shown comes from a verified library (`quotes.json`) with source (Complete Works vol/page, or Belur Math quotation card URL).
2. **AI text is always labelled** "AI-written story / interpretation — not Swami Vivekananda's words". Original quote is shown in a visually distinct "Quote Card" with source.
3. **Regional languages**: reel text/narration can be switched to Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Odia, Punjabi (MVP: English + Hindi + Bengali). Original English quote always stays visible alongside.
4. **Minimalist**: one idea per screen, big type, lots of whitespace, one accent colour, no clutter, no stock-photo spam.
5. **Not empty**: minimalist ≠ blank. Use ornament (mandala/petal line-art), grain, soft gradients, a daily quote, progress, and micro-animations.

## 3. Audience & tone
Gen Z / Alpha, 14–26. Tone: warm, direct, slightly witty older-sibling, never preachy. Second person ("you"). Short sentences. No Sanskrit jargon without a 5-word gloss.

## 4. Information architecture
```
/                Home (two doors + daily quote)
/journey         Ikigai wheel (8 lessons)
/journey/:id     Lesson page (episode list, 6 episodes)
/journey/:id/:ep Episode player (hook → story → teaching → next hook)
/sos             Emergency: prompt input
/sos/result      Reel player + recommended lesson + sources
/about           Method, sources, disclaimer (fact-check transparency)
```
Bottom tab bar (mobile) / top nav (laptop): **Home · Journey · SOS**. SOS is a visually distinct pill button (accent colour) in nav.

## 5. The 8 Life Lessons (pain point → Swami's idea)
| # | Pain point (user words) | Lesson title | Core teaching |
|---|---|---|---|
| 1 | "I'm scared of being judged" | **Fearlessness** | Fear is the root of misery; strength is life |
| 2 | "I'm not good enough" | **Self-Faith** | All power is within you |
| 3 | "My mind is everywhere" | **Focus** | Concentration is the key to knowledge |
| 4 | "I don't know what to do with my life" | **One Idea** | Take one idea, make it your life |
| 5 | "I failed / I want to quit" | **Persistence** | Rise after every fall; stop not till the goal |
| 6 | "I'm drained, anxious, burnt out" | **Strength** | Strong body + mind; be strong first |
| 7 | "Everyone is doing better than me" | **Self-Mastery** | Conquer yourself, not others; envy/anger dissolve |
| 8 | "Success feels empty / why bother" | **Service** | Serve others — it is the highest worship |

Each lesson = **6 episodes** (fixed for MVP; spec allows 5–8). Episode template:
1. **HOOK** (relatable modern situation, ≤25 words)
2. **STORY** (short scene — AI-written, labelled)
3. **THE TEACHING** (verified quote card + 1-line plain-English meaning)
4. **TRY THIS** (a 2-minute action)
5. **NEXT-EPISODE HOOK** (cliffhanger line + "Next →" button)

Episode arc per lesson: Ep1 The problem · Ep2 Why it happens · Ep3 Swami's idea · Ep4 A real incident from his life · Ep5 The practice · Ep6 The challenge (7-day mini-action). Ep6 ends by teasing the *next lesson*.

## 6. Journey UI — the "Ikigai Wheel"
Inspired by the ikigai diagram (overlapping circles around a centre), reinterpreted as an **8-petal lotus/mandala**:
- 8 overlapping translucent circles arranged around a centre (one every 45°), `mix-blend-mode: multiply` so overlaps look like an ikigai Venn.
- Centre circle: "YOU" + overall progress ring.
- Each petal: number, one-word title, small line icon. Tap/hover → petal lifts, shows pain-point sentence and "Begin" button.
- Completed episodes fill petal opacity gradually (6 steps).
- Mobile: wheel fits width (max 360px), tap petal → bottom sheet. Also provide **List view toggle** (accessibility).
- Subtle idle animation: wheel rotates 1 turn/120s; respects `prefers-reduced-motion`.
- Below wheel: "Start where it hurts" chips (the 8 pain-point phrases).

## 7. SOS UI — "Emergency" feature
**Screen 1 (input):** big heading "What's going on?"; multi-line textarea; quick chips ("Exam fear", "Can't focus", "Feeling like a failure", "Comparing myself", "Anxious", "Lost"); language selector; "Make my reel" button. Fillers so it isn't empty: daily quote card, "How it works" 3-step strip, soft mandala watermark.
**Screen 2 (generating):** 4 animated steps: *Understanding you → Finding a verified teaching → Writing the story → Building your reel*.
**Screen 3 (result):** 9:16 reel player (centered, max 420px; on laptop details panel on the right):
- Scenes (5–6 × ~8s = 30–60s): Hook · Modern situation · Quote Card (verified, source chip) · Meaning · Tiny action · Outro. Animated text over gradient/line-art backgrounds, subtitles, optional narration (browser TTS), Stories-style segmented progress bar.
- Panel/below: **Original source** (quote, citation, link), **Language switch**, **Transcript**, **Share**.
- **Recommended Journey lesson card**: "Your closest lesson: 3 · Focus — Episode 2" + Begin button.
- Disclaimer strip: "Story is AI-written. Quote in the gold card is verified."

## 8. Home
- Hero: serif line "Arise. Awake." + subline.
- Two big cards: **Journey** (mini wheel) · **SOS** (pulse ring).
- Daily verified quote (rotates by date).
- Footer: Sources (Belur Math), Fact-check link, disclaimer.

## 9. THREE THEMES (same layout; swap CSS variables only)

### Theme A — "KESARI" (light caramel + off-white) — warm, airy, sunrise
| token | value |
|---|---|
| --bg | #FBF6EC |
| --surface | #FFFFFF |
| --ink | #3B2A1A |
| --muted | #8A7358 |
| --accent | #E08A2E |
| --accent-2 | #F2C38A |
| --accent-soft | #FBE7C8 |
| --line | #E9DCC3 |
| --quote-bg | #FFF1D6 |
Fonts: headings "Fraunces", body "Inter". Radius 20px. Shadow `0 8px 30px rgba(224,138,46,.15)`.

### Theme B — "CHAI & CLAY" (brown, dark, grounded)
| token | value |
|---|---|
| --bg | #2A1E17 |
| --surface | #38291F |
| --ink | #F3E6D3 |
| --muted | #B59F86 |
| --accent | #C9894F |
| --accent-2 | #8C5A3C |
| --accent-soft | #4A3427 |
| --line | #4D3A2D |
| --quote-bg | #43322A |
Fonts: headings "Cormorant Garamond", body "DM Sans". Radius 14px. No shadows, 1px borders.

### Theme C — "INDIGO & MARIGOLD" (my pick; echoes the Belur Math site: indigo ink + gold underline)
| token | value |
|---|---|
| --bg | #F7F5EF |
| --surface | #FFFFFF |
| --ink | #1F2A5C |
| --muted | #6B7090 |
| --accent | #D9A21B |
| --accent-2 | #3B4A9B |
| --accent-soft | #ECEEFA |
| --line | #DDE0F0 |
| --quote-bg | #ECEEFA |
Fonts: headings "DM Serif Display", body "Inter". Radius 16px. Gold underline highlight on headings.

Recommendation: C for judges (trust/authenticity), A for youthful warmth.

## 10. Typography scale (mobile / desktop)
H1 36/56px · H2 26/36 · H3 20/24 · Body 16/17 · Caption 13. Line-height 1.5 body, 1.15 headings. Max text width 60ch.

## 11. Spacing, motion, accessibility
- 8px grid. Page padding 20px mobile / 64px desktop. Section gaps 48/96px.
- Motion 200–400ms ease-out; fade-up on scroll; no parallax; honour reduced motion.
- Contrast AA; tap targets ≥44px; aria-labels on icons; wheel has list fallback; subtitles always on.

## 12. Ornament kit (so it's never "empty")
Inline SVG: 8-petal mandala outline (watermark, 6% opacity), grain overlay (SVG noise, 4%), accent underline swash under headings, dotted separators, lotus icon. No photos of the Swami needed (avoid misrepresentation).

## 13. Content safety
- Quote library entries: `{id, text, source, sourceUrl, verified, topics[]}`. Only `verified:true` rendered as quotes.
- AI outputs JSON referencing `quoteId`; server never lets AI write the quote text itself — it injects the library string.
- Seed candidates (MUST be verified against the Complete Works / Belur Math cards before shipping; unverified → `verified:false`, don't display as quote):
  - "Arise, awake, and stop not till the goal is reached." (Katha Upanishad, popularised by him)
  - "All power is within you; you can do anything and everything."
  - "Take up one idea. Make that one idea your life; think of it, dream of it, live on that idea."
  - "Strength is life, weakness is death."
  - "You cannot believe in God until you believe in yourself."

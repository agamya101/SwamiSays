# SwamiSays — Vivekananda for Gen Z / Alpha

SwamiSays is a frontend web application that bridges Swami Vivekananda's core teachings to contemporary Gen Z and Gen Alpha challenges. Built with React 18, TypeScript, and pure CSS variables supporting three distinct design themes.

---

## Quick Start

### 1. Install & Run Dev Server
```bash
npm install
npm run dev
```
Open [http://localhost:5173/compare](http://localhost:5173/compare) (default landing route) to compare all three themes running live side-by-side in interactive device frames.

---

## How to Switch to Production Mode

To lock in your selected theme and remove the `/compare` view from the production build:
> **One-line change:** In `src/config.ts`, set `SHOW_COMPARE = false` and `DEFAULT_ROUTE = '/'`.

---

## Connecting the Real Backend

All backend requests route cleanly through `src/lib/api.ts`.
To connect the live backend:
1. Create a `.env` file in the project root:
   ```env
   VITE_USE_MOCK=false
   VITE_API_BASE_URL=https://your-backend-api.com
   ```
2. Ensure your backend implements the specification documented in `docs/API_CONTRACT.md`.

---

## Core Features & Architecture

1. **3 Themes via CSS Variables (Zero hardcoded colors in app components)**:
   - **Theme A (Kesari)**: Sunrise caramel, Fraunces serif, warm optimism.
   - **Theme B (Chai & Clay)**: Dark earthen palette, Cormorant Garamond, contemplative.
   - **Theme C (Indigo & Marigold)**: Belur Math legacy, DM Serif Display, gold accents.
2. **The Ikigai Wheel (`/journey`)**:
   - 8-petal sacred geometry mandala with interactive touch/keyboard navigation and smooth idle rotation.
   - Accessible List View toggle (`LessonListView`).
3. **8 Lessons & 48 Episodes**:
   - 5-part micro-learning arc: Hook → Modern Story (`<AiLabel />`) → Teaching (`<QuoteCard />`) → 2-minute Action → Next Cliffhanger.
4. **Emergency SOS Reel Generator (`/sos`)**:
   - Real-time crisis keyword interception redirecting to verified Indian helplines (Tele-MANAS `14416`, KIRAN `1800-599-0019`).
   - 9:16 vertical stories reel player with simulated latency, browser TTS narration, subtitles, and recommended lesson bridge.
5. **Multi-theme Compare View (`/compare`)**:
   - Live side-by-side embedded instances in phone and laptop frames with bi-directional navigation sync and quick-jump controls.

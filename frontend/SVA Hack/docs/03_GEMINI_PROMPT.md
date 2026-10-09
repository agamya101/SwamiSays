You are a senior front-end engineer. Build the web app "Arise" (Vivekananda for Gen Z/Alpha) in this workspace.

## Source of truth
Read these two files completely BEFORE writing any code and follow them exactly:
1. `docs/01_DESIGN_DOC.md` (product, content, 3 themes, layouts)
2. `docs/02_BUILD_INSTRUCTIONS.md` (stack, folder structure, step order, components, QA)
Do not add features, libraries or pages beyond them. If something is ambiguous, choose the simpler option and note it in `docs/DECISIONS.md`.

## Goal of THIS session
Deliver a working, polished FRONT-END with mock data, where I can see all 3 theme designs at the same time, compare them, and pick one. The backend is being built separately and will be integrated in a later session, so design for that now.

## Extra requirement 1: Compare view (most important)
- Add a route `/compare` (and make it the default landing page for this session via a `DEFAULT_ROUTE` constant).
- It shows THREE live instances of the full app side by side, one per theme (Kesari, Chai & Clay, Indigo & Marigold), each inside a phone-style frame (390x780, rounded, scaled with CSS `transform: scale()` to fit the viewport) using `<iframe src="/?theme=kesari&embed=1">`, `?theme=clay`, `?theme=indigo`. Each iframe is fully interactive and independent (own router state).
- Above each frame: theme name, a 5-swatch palette strip, one-line vibe description, and a "Choose this theme" button.
- Top bar of compare page: a **device toggle** (Phone / Laptop) that switches the frames between 390x780 and 1280x800 (frames stacked or horizontally scrollable on laptop mode), and a **"Sync navigation"** switch: when on, navigating in one frame navigates the other two to the same route (use `postMessage` from each embedded app to the parent, parent relays to the others).
- Quick-jump buttons: Home · Journey · Lesson · Episode · SOS · SOS Result, which drive all three frames to that screen at once.
- `?embed=1` hides the ThemeSwitcher and the compare-only chrome. `?theme=` sets `data-theme` before first paint (no flash).
- "Choose this theme" stores `localStorage.theme`, shows a confirmation toast, and sets a constant-driven mode that removes `/compare` and the ThemeSwitcher from the production build (`SHOW_COMPARE=false`). Provide a one-line README note on how to do that.
- On small screens (<900px) the compare page stacks frames in a horizontal snap-scroll carousel.

## Extra requirement 2: Backend-ready architecture
- All data access goes through `src/lib/api.ts` exposing typed functions: `getLessons()`, `getEpisodes(lessonId)`, `getDailyQuote()`, `generateReel({prompt, lang})`, `getProgress()/saveProgress()`.
- A single env flag `VITE_USE_MOCK=true|false`. When true, use local JSON and a mock `generateReel` (simulate 3–4s latency, matching the contract below). When false, call `import.meta.env.VITE_API_BASE_URL`.
- Define all types in `src/types.ts` (Lesson, Episode, Quote, ReelScene, ReelResponse). Validate API responses with a small runtime check (or zod) and show a friendly error + retry UI on failure.
- Contract for `POST /api/reel`:
  request `{ "prompt": string, "lang": "en"|"hi"|"bn" }`
  response `{ "quoteId": string, "quote": {"text":string,"source":string,"sourceUrl":string,"verified":true}, "lessonId": number, "episode": number, "scenes": [{"type":"hook|situation|quote|meaning|action|outro","text":string,"durationMs":number}], "transcript": string, "disclaimer": string }`
  Also accept optional `videoUrl` (if the backend renders a real video, the player uses it instead of the animated scenes).
- Document the contract in `docs/API_CONTRACT.md` so the backend developer can match it. If my backend differs, only `api.ts` should need changes.

## Hard rules (repeat of the docs; never break)
- Never invent Swami Vivekananda quotes. Use only `quotes.json`; unverified ones show an "UNVERIFIED (dev)" tag.
- Every AI-written text shows the AI label. Every quote shows source + Verified chip.
- No hard-coded colours in components; everything via CSS variables from the 3 theme files.
- Mobile first; minimalist; not empty (use the ornament kit).
- Self-harm keywords on SOS input -> helpline card, no reel.

## Content
Fill `lessons.json` (8 lessons) and `episodes.json` with real, good placeholder copy for ALL 8 lessons x 6 episodes (short, Gen-Z friendly, warm tone; stories labelled as AI-written; teaching blocks reference quoteIds only). Quote text itself only from `quotes.json`.

## Process
1. Scaffold and show the folder tree. 2. Build in the order in section 13 of the build instructions, but build `/compare` right after Home + Journey exist so it's usable early. 3. Run `npm run dev`, open the app, and verify with screenshots at 390px and 1280px for each theme; fix visual problems yourself. 4. Run the QA checklist in the build instructions and report pass/fail per item. 5. Finish with: how to run, URL of `/compare`, a list of known gaps, and exactly what I need to change to connect the real backend (`VITE_USE_MOCK=false` + `VITE_API_BASE_URL`).

Start now. Do not ask me questions unless something blocks you; make reasonable choices and log them.

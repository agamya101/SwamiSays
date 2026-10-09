# Architectural & Implementation Decisions

As mandated by `docs/01_DESIGN_DOC.md` and `docs/02_BUILD_INSTRUCTIONS.md`, any ambiguous design or implementation choices are logged here.

### 1. Default Route, Themes & Production Mode
- **Decision**: Product renamed to **SwamiSays**.
- **Uniform Fonts**: Both Light Mode (Kesari) and Dark Mode (Chai & Clay) use unified typography: headings in **Fraunces** (`serif`) and body copy in **Inter** (`sans-serif`). This prevents layout shifts and font discrepancies when toggling between themes.
- User chose **Theme A (Kesari)** for Light Mode and **Theme B (Chai & Clay)** for Dark Mode.
- System responds automatically to OS color scheme preference (`prefers-color-scheme: dark` defaults to Chai & Clay; otherwise Kesari) and provides an interactive Sun/Moon toggle in the navigation bar.
- Switched to production mode via `SHOW_COMPARE = false` and `DEFAULT_ROUTE = '/'` in `src/config.ts`. The 3-theme `/compare` tool remains available in the codebase if directly visited.

### 2. Multi-theme Compare Embedding (`iframe` + `postMessage`)
- **Decision**: The `/compare` route renders three `<iframe>` tags pointing to `/?theme=kesari&embed=1`, `/?theme=clay&embed=1`, and `/?theme=indigo&embed=1`.
- `?embed=1` sets the `.is-embed` class on `document.documentElement`, which hides floating debug toolbars (ThemeSwitcher) and navigation chrome not needed in embedded mode.
- Sync Navigation uses `window.addEventListener('message')` in the parent and `window.parent.postMessage({ type: 'ARISE_NAV', path: ... }, '*')` in child iframes so clicking any link in one theme syncs all three frames if "Sync navigation" is toggled ON.

### 3. Speech Synthesis for Narration
- **Decision**: Utilizes native `window.speechSynthesis` with speech language codes (`en-IN` for English, `hi-IN` for Hindi, `bn-IN` for Bengali) fallback to standard browser TTS voices.

### 4. Zero Hardcoded Hex Colors
- **Decision**: All colors are strictly referenced using CSS custom variables (`var(--bg)`, `var(--surface)`, `var(--ink)`, `var(--muted)`, `var(--accent)`, `var(--accent-2)`, `var(--accent-soft)`, `var(--line)`, `var(--quote-bg)`, `var(--on-accent)`). No hex codes in React component TSX.

### 5. Content Verification
- **Decision**: All quote texts are strictly populated from `src/data/quotes.json` with verified Belur Math / Advaita Ashrama Complete Works citations. Every quote card renders the source citation and the `✓ Verified` badge.
- All AI-generated narrative contexts, hooks, and interpretations strictly display the `<AiLabel />` badge.

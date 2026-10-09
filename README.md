# SwamiSays 🪔

> Turn your personal dilemma into a 30–60 second vertical video — narrated with verified quotes from Swami Vivekananda's collected works.

---

## What it does

You describe a life situation or struggle. SwamiSays classifies your intent across eight life-journey categories (in English, Hindi, or Hinglish), pulls a verified quote from a 13.4 MB corpus of Vivekananda's writings (Volumes 1–9 + unpublished Volume 10), writes a five-scene script, and renders a 9:16 vertical video with Ken Burns zoom, narrated audio, burned-in subtitles, and themed quote cards — ready to share as a Reel or Short.

A crisis gate runs before every classification: if severe distress is detected, the system returns Indian mental health helplines (Tele-MANAS 14416 · KIRAN 1800-599-0019) instead of a video.

---

## Tech stack

| Layer | Tech |
|---|---|
| Frontend | React 18, TypeScript, Vite, React Router |
| Backend | Python 3.10+, FastAPI, Uvicorn |
| AI / NLP | Google Gemini (2.5-flash), sentence-transformers (all-MiniLM-L6-v2) |
| Video | FFmpeg via imageio-ffmpeg, Pillow (720×1280 canvas) |
| Speech | edge-tts (en-IN-PrabhatNeural / hi-IN-MadhurNeural), gTTS fallback |
| Database | SQLite 3 (`backend/data/history.db`) |
| Testing | pytest |

---

## Project structure

```
SwamiSays/
├── frontend/
│   └── SVA Hack/          # React + Vite app
├── backend/
│   ├── server.py           # FastAPI entry point
│   ├── classifier.py       # Intent classifier (sentence-transformers)
│   ├── gemini_script.py    # LLM script generation
│   ├── quotes.py           # Quote retrieval + verification
│   ├── reel_renderer.py    # Video assembly pipeline
│   ├── video_engine.py     # FFmpeg wrapper
│   ├── canvas_service.py   # Quote card renderer
│   ├── history_db.py       # SQLite history
│   └── data/              # Corpus + SQLite DB
├── ReelForge-video_generator/
├── scripts/
├── run_studio.ps1          # Windows PowerShell launcher
└── run_studio.bat          # Windows Batch launcher
```

---

## Prerequisites

- Python 3.10 or later
- Node.js 18 or later
- Git

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/agamya101/SwamiSays.git
cd SwamiSays
```

### 2. Backend

```powershell
cd backend

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows PowerShell
# source venv/bin/activate     # macOS / Linux

# Install dependencies
pip install fastapi uvicorn pydantic python-dotenv \
            sentence-transformers edge-tts Pillow \
            imageio-ffmpeg google-generativeai aiohttp aiofiles pytest
```

### 3. Environment variables

Create a `.env` file inside the `backend/` folder:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

If you skip this, the app falls back to a local deterministic script generator — it will still run without a key.

### 4. Start the backend

```powershell
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

The API will be live at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

### 5. Frontend

Open a new terminal window:

```powershell
cd "frontend/SVA Hack"
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Windows quick-start (alternative)

From the repo root, run the included launcher script — it auto-detects your local IP and prints a mobile-accessible URL:

```powershell
.\run_studio.ps1
```

or

```bat
run_studio.bat
```

---

## Running tests

```powershell
cd backend
pytest
```

Test files cover: intent classifier, quote integrity, API endpoints, and the video rendering pipeline.

---

## Features

- **Multilingual** — English, Hindi, and Hinglish input supported
- **Verified quotes** — The LLM only selects quote IDs; exact text is inserted from the corpus. Every displayed quote is substring-checked against the source before display.
- **Three themes** — Kesari, Chai & Clay, Indigo & Marigold
- **History page** — All generated reels stored locally in SQLite
- **SOS mode** — Instant helpline response for detected crisis input
- **LAN access** — Backend binds to `0.0.0.0:8000` for testing on mobile over Wi-Fi

---

## Deployment

| Part | Recommended host |
|---|---|
| Frontend (Vite) | Vercel |
| Backend (FastAPI + FFmpeg) | Railway or Render |
| Database | Migrate SQLite → Supabase (Postgres) for production |

> ⚠️ The video rendering pipeline (FFmpeg + ML model) is not suitable for Vercel serverless functions due to timeout limits and binary size. Host the backend on a persistent server.

---

## License

This project was built for SVA Hack. All Swami Vivekananda quotes are sourced from the public-domain collected works.

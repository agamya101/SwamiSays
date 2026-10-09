"""
SwamiSays Backend Server
FastAPI application providing:
- 8-Journey classification and verified RAG quotes
- Gemini script generation with strict authenticity guardrails
- Native 9:16 video generation using FFmpeg + Edge-TTS
- Pre-rendered episode video streaming
- Responsive web app hosting (Phone & Desktop on LAN)
"""
import os
import sys
import json
import uuid

# Reconfigure console output to UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
os.environ["PYTHONIOENCODING"] = "utf-8"
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, BackgroundTasks, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env if present
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from quotes import get_all_enriched_quotes, get_quote_by_id, get_quotes_for_lesson
from classifier import classify_dilemma, check_crisis
from gemini_script import generate_reel_script
from reel_renderer import render_full_reel_video, RENDER_JOBS
from history_db import add_history_entry, get_history, get_history_entry, delete_history_entry, update_history_video, clear_history

app = FastAPI(title="SwamiSays API", version="1.0.0")

# Enable CORS for Vite dev server and mobile devices
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BACKEND_DIR = Path(__file__).resolve().parent
MEDIA_DIR = BACKEND_DIR.parent / "media"
DATA_DIR = BACKEND_DIR / "data"
FRONTEND_DIST = BACKEND_DIR.parent / "frontend" / "SVA Hack" / "dist"

# Inject ReelForge directory
REEL_FORGE_DIR = BACKEND_DIR.parent / "ReelForge-video_generator"
if str(REEL_FORGE_DIR) not in sys.path:
    sys.path.insert(0, str(REEL_FORGE_DIR))

import clip_library
import video_service
from pipeline import JOBS as FORGE_JOBS, update_job_status as update_forge_status, run_full_pipeline

os.makedirs(MEDIA_DIR / "episodes", exist_ok=True)
os.makedirs(MEDIA_DIR / "reels", exist_ok=True)
os.makedirs(REEL_FORGE_DIR / "output", exist_ok=True)

# Mount media and output directories for video and audio streaming
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
app.mount("/output", StaticFiles(directory=str(REEL_FORGE_DIR / "output")), name="output")
app.mount("/figures", StaticFiles(directory=str(REEL_FORGE_DIR / "assets" / "figures")), name="figures")


@app.on_event("startup")
def startup_event():
    """Warm up classifier model on startup for sub-second user queries."""
    try:
        classify_dilemma("Warmup query")
        print("Sentence-transformers classifier warmed up successfully.")
    except Exception as e:
        print(f"Classifier warmup notice: {e}")


# Request/Response schemas
class ReelRequest(BaseModel):
    prompt: str
    lang: Optional[str] = "en"
    name: Optional[str] = ""
    age: Optional[int] = None
    profession: Optional[str] = ""
    device_id: Optional[str] = None
    render_video: Optional[bool] = False  # If True, starts background MP4 video render
    subtitle_color: Optional[str] = "yellow"
    voice_id: Optional[str] = None
    music_track: Optional[str] = None


class ForgeGenerateRequest(BaseModel):
    prompt: str
    scene_count: Optional[int] = 4
    aspect_ratio: Optional[str] = "9:16"
    style: Optional[str] = "cinematic"
    voice_id: Optional[str] = "en-IN-PrabhatNeural"
    add_music: Optional[bool] = True
    subtitle_color: Optional[str] = "yellow"
    use_stock_clips: Optional[bool] = True
    music_track: Optional[str] = None


class ClassifyRequest(BaseModel):
    prompt: str


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "has_gemini_key": bool(os.environ.get("GEMINI_API_KEY")),
        "journeys": 8
    }


@app.get("/api/verify-gemini")
def verify_gemini_endpoint():
    """
    Verification endpoint to test live Gemini API connectivity,
    measure latency, and confirm model responsiveness.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return {
            "status": "error",
            "api_called": False,
            "message": "GEMINI_API_KEY is not configured"
        }

    import time
    import requests
    start = time.time()
    for model_name in ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-lite-latest", "gemini-3.8-flash", "gemini-2.5-flash"]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": "Generate a 1-sentence inspirational wisdom quote in JSON: {\"quote\": \"...\"}"}]}],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "maxOutputTokens": 2048,
                    "thinkingConfig": {"thinkingBudget": 256}
                }
            }
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=20)
            if res.status_code == 200:
                elapsed_ms = int((time.time() - start) * 1000)
                data = res.json()
                raw_txt = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                if raw_txt.startswith("```json"):
                    raw_txt = raw_txt[7:]
                if raw_txt.startswith("```"):
                    raw_txt = raw_txt[3:]
                if raw_txt.endswith("```"):
                    raw_txt = raw_txt[:-3]
                raw_txt = raw_txt.strip()
                parsed = json.loads(raw_txt)

                return {
                    "status": "verified",
                    "api_called": True,
                    "provider": "Google Generative Language API",
                    "model": model_name,
                    "latency_ms": elapsed_ms,
                    "tokens_used": data.get("usageMetadata", {}).get("totalTokenCount", 0),
                    "test_output": parsed,
                    "verified_at": json.dumps(data.get("usageMetadata", {}))
                }
        except Exception as e:
            continue

    return {
        "status": "failed",
        "api_called": False,
        "message": "Gemini API test call timed out or failed"
    }


@app.get("/api/lessons")
def get_lessons():
    with open(DATA_DIR / "lessons.json", "r", encoding="utf-8") as f:
        lessons = json.load(f)
    return lessons


@app.get("/api/episodes")
def get_episodes(lessonId: Optional[int] = Query(None)):
    with open(DATA_DIR / "episodes.json", "r", encoding="utf-8") as f:
        episodes = json.load(f)

    # Attach videoUrl if pre-rendered video exists in media/episodes
    for ep in episodes:
        l_id = ep.get("lessonId")
        e_num = ep.get("ep")
        video_path = MEDIA_DIR / "episodes" / f"L{l_id}_E{e_num}.mp4"
        if video_path.exists():
            ep["videoUrl"] = f"/media/episodes/L{l_id}_E{e_num}.mp4"

    if lessonId is not None:
        episodes = [e for e in episodes if e.get("lessonId") == lessonId]
    return episodes


@app.get("/api/quote/daily")
def get_daily_quote():
    quotes = get_all_enriched_quotes()
    import datetime
    now = datetime.datetime.now()
    day_of_year = now.timetuple().tm_yday
    return quotes[day_of_year % len(quotes)]


@app.post("/api/classify")
def classify_prompt(req: ClassifyRequest):
    return classify_dilemma(req.prompt)


@app.post("/api/reel")
def generate_reel_endpoint(req: ReelRequest, background_tasks: BackgroundTasks, request: Request):
    """
    Main AI Problem Solver endpoint:
    1. Classifies user dilemma into 1 of 8 journeys.
    2. Retrieves verified quotes.
    3. Calls Gemini for script text (with strict authenticity guardrails).
    4. Injects exact corpus quote.
    5. Optionally kicks off background MP4 video rendering.
    6. Persists to SQLite history database.
    """
    if len(req.prompt.strip()) < 8:
        raise HTTPException(status_code=400, detail="Prompt must be at least 8 characters")

    # 1. Classification
    classification = classify_dilemma(req.prompt)
    lesson_id = classification["lessonId"]

    # 2. Script generation with exact quote injection
    api_key = os.environ.get("GEMINI_API_KEY", "")
    reel_data = generate_reel_script(
        dilemma=req.prompt,
        lesson_id=lesson_id,
        name=req.name or "",
        age=req.age,
        profession=req.profession or "",
        lang=req.lang or "en",
        api_key=api_key
    )

    # Add journey and classification metadata
    reel_data["journey"] = classification["journey"]
    reel_data["confidence"] = classification["confidence"]
    reel_data["clarify"] = classification.get("clarify", False)
    reel_data["alternatives"] = classification.get("alternatives", [])
    reel_data["isCrisis"] = classification.get("isCrisis", False)

    # 3. Create job ID for video tracking
    job_id = str(uuid.uuid4())[:8]
    reel_data["jobId"] = job_id

    # 4. Save to SQLite history database
    client_dev_id = req.device_id or request.headers.get("x-device-id") or request.headers.get("X-Device-Id") or "default_device"
    status = "rendering" if req.render_video else "completed"
    try:
        h_entry = add_history_entry(
            device_id=client_dev_id,
            prompt=req.prompt,
            name=req.name or "",
            age=req.age,
            profession=req.profession or "",
            lang=req.lang or "en",
            journey=reel_data.get("journey", "Focus"),
            lesson_id=lesson_id,
            quote_id=reel_data.get("quoteId", "") or reel_data.get("quote", {}).get("id", ""),
            quote_text=reel_data.get("quote", {}).get("text", ""),
            quote_source=reel_data.get("quote", {}).get("source", ""),
            transcript=reel_data.get("transcript", ""),
            scenes=reel_data.get("scenes", []),
            job_id=job_id,
            video_url=None,
            status=status,
            api_model=reel_data.get("modelUsed", "gemini-2.5-flash"),
            api_verified=reel_data.get("apiVerified", True)
        )
        reel_data["historyId"] = h_entry["id"]
    except Exception as he:
        print(f"Warning: could not save to history DB: {he}")

    # If requested or automatic background render
    if req.render_video:
        background_tasks.add_task(
            render_full_reel_video,
            reel_data,
            job_id,
            req.lang or "en",
            subtitle_color=req.subtitle_color or "yellow",
            voice_id=req.voice_id,
            music_track=req.music_track
        )

    return reel_data


@app.post("/api/render-reel/{job_id}")
def trigger_render(job_id: str, reel_data: Dict[str, Any], background_tasks: BackgroundTasks, lang: str = "en"):
    """Explicitly triggers background MP4 video compilation for an existing reel."""
    try:
        update_history_video(job_id, "", status="rendering")
    except Exception:
        pass
    background_tasks.add_task(render_full_reel_video, reel_data, job_id, lang)
    return {"jobId": job_id, "status": "queued"}


@app.get("/api/job/{job_id}")
def get_job_status(job_id: str):
    """Polls video rendering progress."""
    job = RENDER_JOBS.get(job_id)
    if not job:
        # Check if file exists on disk
        video_file = MEDIA_DIR / "reels" / f"{job_id}.mp4"
        if video_file.exists():
            return {"status": "completed", "progress": 100, "videoUrl": f"/media/reels/{job_id}.mp4"}
        return {"status": "not_found", "progress": 0}
    return job


# ─────────────────────────────────────────────────────────────────────────────
# History Endpoints (SQLite Backed)
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/history")
def get_user_history(request: Request, device_id: Optional[str] = Query(None)):
    """Fetches all past SOS reels generated by this client."""
    dev_id = device_id or request.headers.get("x-device-id") or request.headers.get("X-Device-Id") or "default_device"
    return get_history(dev_id)


@app.get("/api/history/{entry_id}")
def get_single_history(entry_id: str):
    """Fetches full details of a specific history reel entry."""
    entry = get_history_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="History entry not found")
    return entry


@app.delete("/api/history")
def clear_all_history(request: Request, device_id: Optional[str] = Query(None)):
    """Deletes all history entries for this client device."""
    dev_id = device_id or request.headers.get("x-device-id") or request.headers.get("X-Device-Id") or "default_device"
    cleared_count = clear_history(dev_id)
    return {"cleared": True, "count": cleared_count}


@app.delete("/api/history/{entry_id}")
def delete_single_history(entry_id: str, request: Request, device_id: Optional[str] = Query(None)):
    """Deletes a history entry by ID."""
    dev_id = device_id or request.headers.get("x-device-id") or request.headers.get("X-Device-Id") or "default_device"
    deleted = delete_history_entry(entry_id, dev_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="History record not found or already deleted")
    return {"success": True, "id": entry_id}


# ─────────────────────────────────────────────────────────────────────────────
# ReelForge Studio Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/forge/status")
def get_forge_status():
    """Returns available ReelForge voices, stock clips count, styles, and music tracks."""
    import config as forge_config
    clip_lib = clip_library.load_library()
    figures = clip_library.load_figures()
    tracks = video_service.list_music_tracks()

    return {
        "status": "ready",
        "ffmpeg": forge_config.FFMPEG_PATH,
        "voices": forge_config.VOICES,
        "styles": list(forge_config.STYLES.keys()),
        "aspect_ratios": forge_config.DIMENSIONS,
        "stock_categories": {cat: len(clips) for cat, clips in clip_lib.items()},
        "total_clips": sum(len(clips) for clips in clip_lib.values()),
        "figures": list(figures.keys()),
        "music_tracks": tracks
    }


@app.get("/api/forge/templates")
def get_forge_templates():
    """Returns preset prompts/templates for creating inspirational reels."""
    return [
        {
            "id": "vivekananda",
            "title": "🔥 Arise & Awake (Vivekananda)",
            "description": "Powerful story of resilience turning failure into determination through Swamiji's eternal call.",
            "prompt": "TITLE: Arise. Awake.\n\nSCENE: Third attempt. Failed. Arjun stared at the rejection letter.\nCAPTION: 3rd attempt. Failed.\nFOOTAGE: mood_rain\n\nSCENE: He opened his phone and typed: I want to give up.\nCAPTION: I want to give up...\nFOOTAGE: urban_city, human_walk\n\nSCENE: Then he read it. Arise, awake, and stop not till the goal is reached. Swami Vivekananda.\nCAPTION: Arise. Awake. Stop not.\nFOOTAGE: nature_fire, mood_calm\n\nSCENE: Arjun sat up straight. Eyes clear. He opened the book again.\nCAPTION: Back to work.\nFOOTAGE: human_study, human_write\n\nSCENE: Ancient wisdom for today's youth. Arise.\nCAPTION: Arise. Awake.\nFOOTAGE: nature_sunrise, india_crowd"
        },
        {
            "id": "focus",
            "title": "🧠 Break the Phone Addiction (Focus)",
            "description": "Modern dilemma of digital distraction and regaining iron concentration.",
            "prompt": "TITLE: Master Your Attention\n\nSCENE: The screen glows at 2 AM. Another hour lost to endless scrolling.\nCAPTION: Trapped in distraction.\nFOOTAGE: human_study, urban_city\n\nSCENE: The mind is a restless ocean. But you are the captain, not the wave.\nCAPTION: You are the captain.\nFOOTAGE: nature_water, mood_calm\n\nSCENE: To succeed, you must concentrate. Take up one idea. Make that one idea your life.\nCAPTION: Take up one idea.\nFOOTAGE: nature_fire, human_write\n\nSCENE: Put the phone down. Take five deep breaths. Begin the work that matters.\nCAPTION: Begin now.\nFOOTAGE: human_write, nature_sunrise"
        },
        {
            "id": "discipline",
            "title": "⏰ Discipline Over Mood",
            "description": "Why motivation fades and daily consistency builds true character.",
            "prompt": "TITLE: Discipline Over Mood\n\nSCENE: Motivation got you started. It will not get you through Tuesday.\nCAPTION: Motivation fades.\nFOOTAGE: urban_city\n\nSCENE: Pick one habit. Do it badly, daily. In ninety days you will not recognise yourself.\nCAPTION: One habit. 90 days.\nFOOTAGE: human_write, human_study\n\nSCENE: All power is within you. You can do anything and everything. Swami Vivekananda.\nCAPTION: All power is within you.\nFOOTAGE: nature_fire, mood_calm\n\nSCENE: Discipline is the promise you finally keep to yourself. Arise and conquer.\nCAPTION: Keep your promise.\nFOOTAGE: nature_sunrise"
        },
        {
            "id": "fearless",
            "title": "🦁 Face the Brutes (Courage)",
            "description": "Swami Vivekananda's famous Vrindavan monkey encounter on overcoming fear.",
            "prompt": "TITLE: Face the Brutes\n\nSCENE: Walking down the temple path, fierce monkeys blocked his way, screeching.\nCAPTION: Trapped by fear.\nFOOTAGE: india_crowd, human_walk\n\nSCENE: He turned to run, but an old sanyasi called out: Face the brutes!\nCAPTION: Face the brutes!\nFOOTAGE: nature_fire, mood_calm\n\nSCENE: He stopped. Turned around. Stood his ground. The monkeys retreated.\nCAPTION: Stand your ground.\nFOOTAGE: nature_sunrise, human_walk\n\nSCENE: Never run from fear. Turn around, face it, and it vanishes.\nCAPTION: Fear vanishes.\nFOOTAGE: nature_sunrise"
        },
        {
            "id": "blank",
            "title": "📋 Custom Script Template",
            "description": "Start fresh with your own custom scene-by-scene script.",
            "prompt": "TITLE: Your Custom Reel\n\nSCENE: Hook the viewer in the first three seconds.\nCAPTION: The Hook.\nFOOTAGE: mood_rain\n\nSCENE: Introduce the dilemma or challenge.\nCAPTION: The Struggle.\nFOOTAGE: human_study, human_walk\n\nSCENE: Deliver the timeless wisdom or breakthrough.\nCAPTION: The Breakthrough.\nFOOTAGE: nature_fire, nature_sunrise\n\nSCENE: Give the viewer a single clear action to take today.\nCAPTION: Your next step.\nFOOTAGE: human_write, nature_sunrise"
        }
    ]


@app.post("/api/forge/generate")
def generate_forge_video(req: ForgeGenerateRequest, background_tasks: BackgroundTasks):
    """
    Kicks off an automated ReelForge video generation:
    Writes script, generates neural Edge-TTS voiceover, matches stock clips + historical figures,
    mixes ducked ambient music, and exports full MP4.
    """
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required")

    job_id = f"forge_{uuid.uuid4().hex[:8]}"
    update_forge_status(job_id, "queued", 0, f"ReelForge job queued for '{req.prompt[:40]}...'")

    api_key = os.environ.get("GEMINI_API_KEY", None)

    background_tasks.add_task(
        run_full_pipeline,
        prompt=req.prompt.strip(),
        job_id=job_id,
        scene_count=req.scene_count or 4,
        aspect_ratio=req.aspect_ratio or "9:16",
        style=req.style or "cinematic",
        voice_id=req.voice_id or "en-IN-PrabhatNeural",
        add_music=req.add_music if req.add_music is not None else True,
        subtitle_color=req.subtitle_color or "yellow",
        api_key=api_key,
        use_stock_clips=req.use_stock_clips if req.use_stock_clips is not None else True,
        music_track=req.music_track
    )

    return {"jobId": job_id, "status": "queued"}


@app.get("/api/forge/job/{job_id}")
def get_forge_job(job_id: str):
    """Polls live ReelForge pipeline status, stages, logs, and video URL."""
    job = FORGE_JOBS.get(job_id)
    if not job:
        # Check if video exists in output directory
        out_video = REEL_FORGE_DIR / "output" / f"{job_id}.mp4"
        if out_video.exists():
            return {
                "id": job_id,
                "completed": True,
                "progress": 100,
                "stage": "done",
                "message": "Video rendered and ready!",
                "video_url": f"/output/{job_id}.mp4",
                "logs": ["Video file found on disk."]
            }
        return {"id": job_id, "completed": False, "progress": 0, "stage": "not_found", "message": "Job not found"}
    return job


@app.get("/api/forge/showcase")
def get_forge_showcase():
    """Returns ready-made showcase reel."""
    viveka_reel = REEL_FORGE_DIR / "viveka_reel.mp4"
    return {
        "title": "Swami Vivekananda — Arise & Awake",
        "videoUrl": "/output/viveka_reel.mp4" if viveka_reel.exists() else None,
        "description": "Produced with ReelForge: Pexels stock footage, authentic historical portraits, neural voice, ducked ambient music."
    }



# Mount static build of frontend if exists (for single-port mobile access)
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend_spa(full_path: str):
        # Do not intercept api or media routes
        if full_path.startswith("api/") or full_path.startswith("media/"):
            raise HTTPException(status_code=404)
        file_path = FRONTEND_DIST / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")

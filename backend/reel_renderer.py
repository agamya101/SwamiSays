"""
Full Reel Video Pipeline powered by ReelForge:
Converts a ReelResponse JSON (scenes, quote, etc.) into a cinematic 9:16 MP4 video
using stock footage (Pexels), authentic Swami Vivekananda historical portraits,
neural voiceover (Edge-TTS Prabhat/Madhur), burned subtitles, and ducked ambient music.
"""
import os
import sys
import time
import uuid
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import asyncio
import edge_tts

# Inject ReelForge directory into sys.path
BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
REEL_FORGE_DIR = ROOT_DIR / "ReelForge-video_generator"
if str(REEL_FORGE_DIR) not in sys.path:
    sys.path.insert(0, str(REEL_FORGE_DIR))

import clip_library
import video_service
from tts_service import generate_scene_audio, generate_scene_srt
from quote_card_renderer import render_quote_card_image
from canvas_service import render_scene_canvas
from video_engine import FFMPEG_PATH

logger = logging.getLogger(__name__)

MEDIA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "media"))
REELS_DIR = os.path.join(MEDIA_DIR, "reels")
TEMP_DIR = os.path.join(MEDIA_DIR, "temp")
os.makedirs(REELS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# In-memory background jobs dictionary
RENDER_JOBS: Dict[str, Dict[str, Any]] = {}

LESSON_FOOTAGE_HINTS = {
    1: ["nature_fire", "nature_sunrise", "human_walk"],    # Fearlessness
    2: ["human_study", "mood_calm", "nature_water"],       # Self-Faith
    3: ["human_study", "human_write", "mood_calm"],        # Focus
    4: ["urban_city", "human_walk", "nature_water"],        # Purpose
    5: ["mood_rain", "human_walk", "nature_sunrise"],       # Persistence
    6: ["nature_fire", "mood_rain", "nature_sunrise"],      # Strength
    7: ["mood_calm", "human_write", "nature_water"],        # Self-Mastery
    8: ["india_crowd", "human_walk", "nature_sunrise"],     # Service
}


def get_voice_for_lang(lang: str) -> str:
    if lang == "hi":
        return "hi-IN-MadhurNeural"
    return "en-IN-PrabhatNeural"


def render_full_reel_video(
    reel_data: Dict[str, Any],
    job_id: str,
    lang: str = "en",
    subtitle_color: str = "yellow",
    voice_id: Optional[str] = None,
    music_track: Optional[str] = None
) -> str:
    """
    Renders all scenes of a reel using the ReelForge cinematic engine
    and concatenates them into an MP4 video with ambient music.
    """
    job_dir = os.path.join(TEMP_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    output_video_path = os.path.join(REELS_DIR, f"{job_id}.mp4")
    RENDER_JOBS[job_id] = {
        "status": "rendering",
        "progress": 5,
        "videoUrl": None,
        "error": None
    }

    try:
        scenes = reel_data.get("scenes", [])
        lesson_id = reel_data.get("lessonId", 3)
        quote_info = reel_data.get("quote", {})
        active_voice = voice_id or get_voice_for_lang(lang)
        sub_color = subtitle_color or "yellow"

        clip_lib = clip_library.load_library()
        figures = clip_library.load_figures()
        used_clips = set()
        lesson_hints = LESSON_FOOTAGE_HINTS.get(lesson_id, ["nature_sunrise", "human_study"])

        clip_paths = []
        total_duration = 0.0

        for idx, scene in enumerate(scenes):
            scene_type = scene.get("type", "scene")
            text = scene.get("text", "")
            is_quote = (scene_type == "quote")

            pct = 10 + int((idx / len(scenes)) * 75)
            RENDER_JOBS[job_id]["progress"] = pct

            # 1. Voiceover audio & SRT subtitles
            audio_path = os.path.join(job_dir, f"audio_{idx}.mp3")
            clean_audio_text = text.replace('"', '').replace('“', '').replace('”', '').strip()
            duration = generate_scene_audio(clean_audio_text, active_voice, audio_path)
            total_duration += duration

            srt_path = os.path.join(job_dir, f"scene_{idx}.srt")
            # For subtitles, use concise readable text
            sub_text = clean_audio_text
            generate_scene_srt(sub_text, duration, srt_path)

            clip_path = os.path.join(job_dir, f"clip_{idx}.mp4")

            # 2. Render visuals via ReelForge
            rendered_ok = False
            scene_dict = {
                "narration": clean_audio_text,
                "visual_prompt": text,
                "subtitle_text": sub_text,
                "text_overlay": quote_info.get("source", "Swami Vivekananda") if is_quote else ""
            }

            if is_quote and figures.get("vivekananda"):
                # Use authentic Swami Vivekananda historical photo with push-in & blurred background
                scene_dict["footage"] = "vivekananda"
                shots, shot_len = clip_library.shot_plan(max(3.0, duration + 0.3))
                clips = clip_library.pick_clips(
                    scene_dict, shots, shot_len, "9:16", used_clips,
                    scene_idx=idx, library=clip_lib, figures=figures
                )
                if clips and video_service.render_scene_video_clip(
                    clips=clips, audio_path=audio_path, output_path=clip_path,
                    scene_data=scene_dict, aspect_ratio="9:16", srt_path=srt_path,
                    duration=duration, scene_idx=idx, subtitle_color=sub_color,
                    add_text_overlay=True
                ):
                    rendered_ok = True

            elif clip_lib:
                # Use scene footage hint from Gemini if present, else lesson hints
                preferred_hint = scene.get("footage") or lesson_hints[idx % len(lesson_hints)]
                scene_dict["footage"] = preferred_hint
                shots, shot_len = clip_library.shot_plan(max(3.0, duration + 0.3))
                clips = clip_library.pick_clips(
                    scene_dict, shots, shot_len, "9:16", used_clips,
                    scene_idx=idx, library=clip_lib, figures=figures
                )
                if clips and video_service.render_scene_video_clip(
                    clips=clips, audio_path=audio_path, output_path=clip_path,
                    scene_data=scene_dict, aspect_ratio="9:16", srt_path=srt_path,
                    duration=duration, scene_idx=idx, subtitle_color=sub_color,
                    add_text_overlay=False
                ):
                    rendered_ok = True

            # Fallback if stock render failed
            if not rendered_ok or not os.path.exists(clip_path):
                img_path = os.path.join(job_dir, f"img_{idx}.jpg")
                if is_quote:
                    render_quote_card_image(
                        quote_text=quote_info.get("text", text),
                        source_citation=quote_info.get("source", "Complete Works of Swami Vivekananda"),
                        output_path=img_path,
                        lang=lang
                    )
                else:
                    render_scene_canvas(
                        lesson_id=lesson_id,
                        scene_type=scene_type,
                        prompt_hint=text,
                        output_path=img_path,
                        scene_idx=idx
                    )

                video_service.render_scene_clip(
                    image_path=img_path,
                    audio_path=audio_path,
                    output_path=clip_path,
                    duration=duration,
                    aspect_ratio="9:16",
                    scene_idx=idx,
                    subtitle_color=sub_color
                )

            if os.path.exists(clip_path):
                clip_paths.append(clip_path)

        # 3. Concatenate and mix ambient background score
        RENDER_JOBS[job_id]["progress"] = 90
        video_service.assemble_full_video(
            clip_paths=clip_paths,
            output_path=output_video_path,
            total_duration=total_duration,
            add_music=True,
            music_track=music_track or "motivational_ambient.mp3"
        )

        video_url = f"/media/reels/{job_id}.mp4"
        RENDER_JOBS[job_id] = {
            "status": "completed",
            "progress": 100,
            "videoUrl": video_url,
            "error": None
        }

        # Update SQLite history record
        try:
            from history_db import update_history_video
            update_history_video(job_id, video_url, status="completed")
        except Exception as he:
            logger.warning(f"Could not update history for job {job_id}: {he}")

        logger.info(f"✅ ReelForge generated finished reel at {output_video_path}")
        return video_url

    except Exception as e:
        logger.error(f"Reel video generation failed: {e}", exc_info=True)
        RENDER_JOBS[job_id] = {
            "status": "failed",
            "progress": 100,
            "videoUrl": None,
            "error": str(e)
        }
        try:
            from history_db import update_history_video
            update_history_video(job_id, "", status="failed")
        except Exception:
            pass
        return ""

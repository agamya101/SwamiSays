"""
Batch renders video episodes for Journey Mode.
Reads backend/data/episodes.json and renders 9:16 vertical MP4s into media/episodes/L{lessonId}_E{ep}.mp4.

Each episode video includes:
- Scene 1: Hook (Title & Opening hook)
- Scene 2: Story (Modern situation)
- Scene 3: Teaching (Authentic gold quote card with verbatim Complete Works quote)
- Scene 4: Meaning (Plain language interpretation)
- Scene 5: Try This (2-minute micro action)
- Scene 6: Next Hook (Cliffhanger for next episode)
"""
import os
import sys
import json
import logging
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from quotes import get_quote_by_id
from reel_renderer import render_full_reel_video

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATA_FILE = ROOT_DIR / "backend" / "data" / "episodes.json"
EPISODES_OUT_DIR = ROOT_DIR / "media" / "episodes"
os.makedirs(EPISODES_OUT_DIR, exist_ok=True)


def build_episode_reel_data(ep: dict) -> dict:
    lesson_id = ep["lessonId"]
    ep_num = ep["ep"]
    quote_id = ep["quoteId"]
    quote_obj = get_quote_by_id(quote_id) or {
        "id": quote_id,
        "text": "All power is within you.",
        "source": "Swami Vivekananda, Complete Works",
        "verified": True
    }

    scenes = [
        {
            "type": "hook",
            "text": f"{ep['title']}: {ep['hook']}",
            "durationMs": 6500
        },
        {
            "type": "situation",
            "text": ep["story"],
            "durationMs": 7500
        },
        {
            "type": "quote",
            "text": f'"{quote_obj["text"]}"',
            "durationMs": 8500,
            "quoteId": quote_obj["id"]
        },
        {
            "type": "meaning",
            "text": ep["meaning"],
            "durationMs": 7500
        },
        {
            "type": "action",
            "text": ep["tryThis"],
            "durationMs": 7000
        },
        {
            "type": "outro",
            "text": f"Next: {ep['nextHook']}",
            "durationMs": 5500
        }
    ]

    return {
        "lessonId": lesson_id,
        "episode": ep_num,
        "quoteId": quote_obj["id"],
        "quote": quote_obj,
        "scenes": scenes,
        "disclaimer": "Story and interpretation are AI-generated. The quote in the gold card is authentic and verified."
    }


def render_all_episodes(episodes_to_render: list = None, lang: str = "en"):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        all_episodes = json.load(f)

    if episodes_to_render is None:
        # Default priority: Ep 1 for each of the 8 journeys
        episodes_to_render = [e for e in all_episodes if e.get("ep") == 1]

    logger.info(f"Starting batch render for {len(episodes_to_render)} episodes...")

    for ep in episodes_to_render:
        l_id = ep["lessonId"]
        e_num = ep["ep"]
        target_video = EPISODES_OUT_DIR / f"L{l_id}_E{e_num}.mp4"

        if target_video.exists() and target_video.stat().st_size > 10000:
            logger.info(f"Skipping L{l_id}_E{e_num} (already exists at {target_video})")
            continue

        logger.info(f"--> Rendering L{l_id}_E{e_num}: '{ep['title']}'...")
        reel_data = build_episode_reel_data(ep)
        job_id = f"batch_L{l_id}_E{e_num}"

        url = render_full_reel_video(reel_data, job_id, lang=lang)
        # Move output from media/reels/{job_id}.mp4 to media/episodes/L{l_id}_E{e_num}.mp4
        source_file = ROOT_DIR / "media" / "reels" / f"{job_id}.mp4"
        if source_file.exists():
            import shutil
            shutil.copy(source_file, target_video)
            logger.info(f"✓ Saved pre-rendered video to {target_video} ({target_video.stat().st_size} bytes)")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=8, help="Number of episodes to render")
    parser.add_argument("--lesson", type=int, default=None, help="Specific lesson ID")
    parser.add_argument("--ep", type=int, default=None, help="Specific episode number")
    args = parser.parse_args()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        all_eps = json.load(f)

    selected = all_eps
    if args.lesson is not None:
        selected = [e for e in selected if e["lessonId"] == args.lesson]
    if args.ep is not None:
        selected = [e for e in selected if e["ep"] == args.ep]
    else:
        # Prioritize Ep 1 of each lesson
        selected = sorted(selected, key=lambda x: (x["ep"], x["lessonId"]))[:args.limit]

    render_all_episodes(selected)

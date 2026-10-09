"""
clip_library.py — Stock footage library for ReelForge.

Indexes the Pexels clips in reel_clips/ (downloaded by download_reel_clips.py)
and picks clips for a scene. Clips are named {category}{NN}.mp4, e.g.
nature_sunrise_03.mp4, so the category is everything before the trailing number.

Each scene is cut into shots of at most MAX_SHOT_SECONDS, one clip per shot.
Category for each scene:
  1. scene["footage"] — comma-separated categories from the prompt (cycled per shot)
  2. keyword scoring over visual_prompt (weighted x2), narration and emotion
  3. emotion fallback, then a rotation of versatile categories
Within a category, clips not yet used in the reel are preferred, then ones
matching the reel's orientation, then ones at least as long as the shot.
"""

import os
import re
import glob
import logging
import subprocess
from functools import lru_cache

from config import BASE_DIR, get_ffmpeg_executable

logger = logging.getLogger(__name__)

CLIPS_DIR = os.path.join(BASE_DIR, "reel_clips")
FIGURES_DIR = os.path.join(BASE_DIR, "assets", "figures")
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp")

# people with a photo folder in assets/figures/<name>/ and the words that mean them;
# any other folder there is matched by its own name
FIGURE_ALIASES = {
    "vivekananda": ["vivekananda", "vivekanand", "swamiji", "swami ji", "narendranath"],
}

# category -> (description for the LLM, matching keywords)
FOOTAGE_CATEGORIES = {
    "nature_sunrise": ("sunrise, sunset, sky, golden light, hope, new beginnings",
                       ["sunrise", "sunset", "dawn", "dusk", "morning", "sky", "sun", "golden hour",
                        "horizon", "clouds", "mountain", "new beginning", "hope", "light breaking"]),
    "nature_fire":    ("candle, flame, fire, diya, warm glow, prayer",
                       ["candle", "candlelight", "flame", "fire", "diya", "lamp", "burning", "ember",
                        "glow", "torch", "bonfire", "passion", "prayer"]),
    "nature_water":   ("ocean, waves, river, flowing water, vastness",
                       ["ocean", "sea", "wave", "waves", "water", "river", "beach", "shore", "tide",
                        "lake", "flow", "flowing", "waterfall"]),
    "mood_rain":      ("rain on a window, storm, sadness, loneliness, struggle",
                       ["rain", "raining", "rainy", "storm", "window", "sad", "sadness", "lonely",
                        "loneliness", "grief", "tears", "melancholy", "gloomy", "despair", "failure",
                        "failed", "rejection", "struggle", "heartbreak"]),
    "human_study":    ("person studying at a desk, books, exams, focus",
                       ["study", "studying", "student", "desk", "exam", "exams", "book", "books",
                        "reading", "library", "homework", "learning", "focus", "laptop", "college",
                        "school", "university"]),
    "human_walk":     ("person walking on a street, journey, moving forward",
                       ["walk", "walking", "street", "journey", "path", "road", "steps", "footsteps",
                        "commute", "crossroads", "moving forward", "wandering"]),
    "urban_city":     ("city at night, timelapse, skyline, traffic, modern life",
                       ["city", "urban", "skyline", "traffic", "timelapse", "time-lapse", "building",
                        "buildings", "metropolis", "neon", "downtown", "night lights", "busy", "hustle"]),
    "human_write":    ("hands writing in a notebook, journaling, planning goals",
                       ["write", "writing", "notebook", "pen", "pencil", "journal", "journaling",
                        "diary", "letter", "notes", "plan", "planning", "goals", "list"]),
    "mood_calm":      ("meditation, yoga, calm, peace, spirituality",
                       ["meditation", "meditate", "meditating", "yoga", "calm", "peace", "peaceful",
                        "breath", "breathing", "mindful", "mindfulness", "spiritual", "inner",
                        "stillness", "serene", "monk", "soul", "silence", "zen"]),
    "india_crowd":    ("Indian crowds, markets, festivals, everyday India",
                       ["india", "indian", "market", "bazaar", "crowd", "crowds", "festival",
                        "vendor", "temple", "varanasi", "delhi", "mumbai", "kolkata", "ganga",
                        "people", "culture", "youth"]),
}

EMOTION_FALLBACK = {
    "sad": "mood_rain", "sadness": "mood_rain", "despair": "mood_rain", "loneliness": "mood_rain",
    "frustration": "mood_rain", "struggle": "mood_rain", "fear": "mood_rain",
    "hope": "nature_sunrise", "inspiration": "nature_sunrise", "triumph": "nature_sunrise",
    "joy": "nature_sunrise", "awe": "nature_water", "wonder": "nature_water",
    "calm": "mood_calm", "peace": "mood_calm", "serenity": "mood_calm", "reflection": "mood_calm",
    "determination": "human_study", "focus": "human_study", "resolve": "human_write",
    "curiosity": "human_walk", "intrigue": "urban_city", "energy": "urban_city",
    "passion": "nature_fire", "warmth": "nature_fire",
}

ROTATION = ["nature_sunrise", "urban_city", "nature_water", "mood_calm", "human_walk"]


def footage_prompt_hint():
    """One line per category, for the LLM system prompt."""
    return "\n".join(f'  - "{name}": {desc}' for name, (desc, _) in FOOTAGE_CATEGORIES.items())


@lru_cache(maxsize=None)
def _probe(path, mtime):
    """(width, height, duration) of a video via `ffmpeg -i`; cached per file version."""
    res = subprocess.run([get_ffmpeg_executable(), "-hide_banner", "-i", path],
                         capture_output=True, text=True, errors="ignore")
    dur = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    size = re.search(r"Video:.*?(\d{3,5})x(\d{3,5})", res.stderr)
    duration = (int(dur[1]) * 3600 + int(dur[2]) * 60 + float(dur[3])) if dur else 0.0
    w, h = (int(size[1]), int(size[2])) if size else (0, 0)
    return w, h, duration


def load_library():
    """{category: [clip dict, ...]} for every mp4 in reel_clips/."""
    cache_path = os.path.join(CLIPS_DIR, "clip_cache.json")
    all_files = sorted(glob.glob(os.path.join(CLIPS_DIR, "*.mp4")))
    if not all_files:
        return {}

    # Check disk cache
    if os.path.exists(cache_path):
        try:
            import json
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data and isinstance(data, dict):
                return data
        except Exception:
            pass

    library = {}
    for path in all_files:
        m = re.match(r"(.+?)_?(\d+)\.mp4$", os.path.basename(path))
        if not m:
            continue
        w, h, duration = _probe(path, os.path.getmtime(path))
        if duration <= 0:
            continue
        library.setdefault(m[1], []).append(
            {"path": path, "name": os.path.basename(path), "width": w, "height": h,
             "duration": duration, "category": m[1]})

    if library:
        try:
            import json
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(library, f)
        except Exception:
            pass

    return library


def has_clips():
    return bool(glob.glob(os.path.join(CLIPS_DIR, "*.mp4")))


def _keyword_scores(scene, categories):
    fields = [(scene.get("visual_prompt") or "", 2),
              (scene.get("narration") or "", 1),
              (scene.get("subtitle_text") or "", 1),
              (scene.get("emotion") or "", 1)]
    scores = {}
    for cat in categories:
        keywords = FOOTAGE_CATEGORIES.get(cat, ("", [cat.replace("_", " ")]))[1]
        score = 0
        for text, weight in fields:
            text = text.lower()
            score += weight * sum(1 for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", text))
        if score:
            scores[cat] = score
    return scores


MAX_SHOT_SECONDS = 4.0   # no single clip stays on screen longer than this


def load_figures():
    """{figure name: [photo dict, ...]} from assets/figures/<name>/ (photos sorted by name)."""
    figures = {}
    if not os.path.isdir(FIGURES_DIR):
        return figures
    for name in sorted(os.listdir(FIGURES_DIR)):
        folder = os.path.join(FIGURES_DIR, name)
        if not os.path.isdir(folder):
            continue
        photos = sorted(f for f in os.listdir(folder) if f.lower().endswith(IMAGE_EXTS))
        if photos:
            figures[name.lower()] = [
                {"path": os.path.join(folder, f), "name": f, "kind": "image",
                 "category": name.lower(), "duration": float("inf")} for f in photos]
    return figures


def detect_figure(scene, figures):
    """Name of a person the scene talks about (or tags in FOOTAGE) who has photos, else None."""
    text = " ".join(str(scene.get(k) or "") for k in
                    ("narration", "subtitle_text", "visual_prompt", "footage", "text_overlay")).lower()
    for name in figures:
        for alias in FIGURE_ALIASES.get(name, [name.replace("_", " ")]):
            if re.search(r"\b" + re.escape(alias), text):
                return name
    return None


def pick_photos(figure, photos, count, used, scene_idx=0):
    """`count` photos of a figure: unused first, never the same photo twice in a row."""
    picks, last = [], None
    for _ in range(count):
        fresh = [p for p in photos if p["path"] not in used]
        pool = fresh or [p for p in photos if p["path"] != last] or photos
        photo = pool[0]
        used.add(photo["path"])
        last = photo["path"]
        picks.append(dict(photo, reason=f"mentions {figure}"))
    logger.info(f"🖼️  Scene {scene_idx + 1}: {count} photo shot(s) of {figure}: "
                f"{', '.join(p['name'] for p in picks)}")
    return picks


def footage_tags(scene, library):
    """Valid categories from the scene's FOOTAGE field (comma-separated, in order)."""
    raw = str(scene.get("footage") or "")
    tags = [t.strip().lower().rstrip("_") for t in raw.split(",")]
    return [t for t in dict.fromkeys(tags) if t in library]


def choose_category(scene, library, scene_idx=0):
    tags = footage_tags(scene, library)
    if tags:
        return tags[0], "footage tag"

    scores = _keyword_scores(scene, library.keys())
    if scores:
        best = max(scores.values())
        # ties broken alphabetically so picks are reproducible
        return sorted(c for c, s in scores.items() if s == best)[0], f"keywords ({best})"

    emotion = str(scene.get("emotion") or "").lower()
    for word, cat in EMOTION_FALLBACK.items():
        if word in emotion and cat in library:
            return cat, "emotion"

    available = [c for c in ROTATION if c in library] or sorted(library)
    return available[scene_idx % len(available)], "rotation"


def shot_plan(duration, max_shot=MAX_SHOT_SECONDS):
    """Split a scene into equal shots of at most max_shot seconds: (count, seconds each)."""
    import math
    count = max(1, math.ceil(duration / max_shot - 1e-9))
    return count, duration / count


def pick_clips(scene, count, shot_seconds, aspect_ratio="9:16", used=None, scene_idx=0,
               library=None, figures=None):
    """
    Return `count` clip dicts for one scene, one per shot (or [] if the library is empty).
    Shots cycle through the scene's FOOTAGE categories (or its best-matching category),
    prefer clips not yet used in this reel, and never repeat the previous shot's clip.
    If the scene mentions a person with photos in assets/figures/ (e.g. Vivekananda),
    the shots are that person's photos instead.
    `used` (a set of paths shared across the reel) is updated with the picks.
    """
    used = used if used is not None else set()
    figures = figures if figures is not None else load_figures()
    figure = detect_figure(scene, figures)
    if figure:
        return pick_photos(figure, figures[figure], count, used, scene_idx)

    library = library if library is not None else load_library()
    if not library:
        return []
    want_portrait = aspect_ratio == "9:16"

    tags = footage_tags(scene, library)
    primary, reason = choose_category(scene, library, scene_idx)
    preferred = tags or [primary]

    # fallback order when the preferred categories run out of fresh clips
    scores = _keyword_scores(scene, library.keys())
    fallback = sorted(scores, key=lambda c: (-scores[c], c)) + ROTATION + sorted(library)
    order = [c for c in dict.fromkeys(preferred + fallback) if c in library]

    def rank(clip):
        portrait = clip["height"] > clip["width"]
        return (portrait != want_portrait,          # matching orientation
                clip["duration"] < shot_seconds,    # long enough to avoid looping
                clip["name"])

    picks, last = [], None
    for i in range(count):
        want = preferred[i % len(preferred)]
        search = [want] + [c for c in order if c != want]
        clip = None
        for cat in search:                           # fresh clip, nearest category first
            fresh = [c for c in library[cat] if c["path"] not in used]
            if fresh:
                clip = min(fresh, key=rank)
                break
        if clip is None:                             # everything used: allow reuse, not back-to-back
            pool = [c for c in library[want] if c["path"] != last] or library[want]
            clip = min(pool, key=rank)
        used.add(clip["path"])
        last = clip["path"]
        picks.append(dict(clip, reason=reason if clip["category"] in preferred
                          else f"{reason}, borrowed {clip['category']}"))

    logger.info(f"🎞️  Scene {scene_idx + 1}: {count} x {shot_seconds:.1f}s shots: "
                f"{', '.join(p['name'] for p in picks)} [{reason}]")
    return picks

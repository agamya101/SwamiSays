"""
llm_service.py — Improved script generation for ReelForge
Prioritizes Gemini models with better storytelling prompts.
"""

import json
import re
import logging
import requests

from clip_library import footage_prompt_hint
from script_templates import write_script
from prompt_format import script_from_prompt, wants_ai_writer

logger = logging.getLogger(__name__)

# Gemini models to try in order (newest first)
GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

STYLES = {
    "cinematic": "photorealistic cinematic film still, dramatic lighting, shallow depth of field, anamorphic lens flare, golden hour",
    "anime": "anime illustration, Studio Ghibli style, soft watercolor tones, expressive characters, lush detailed backgrounds",
    "cyberpunk": "neon-lit cyberpunk cityscape, rain-slicked streets, holographic displays, dark atmospheric mood",
    "documentary": "documentary photography, natural lighting, raw authentic emotion, photojournalistic style",
    "fantasy": "epic fantasy concept art, magical atmosphere, volumetric god rays, painterly style, ethereal glow",
    "minimalist": "clean minimalist design, flat geometric shapes, soft pastel gradient background, modern typography feel",
    "vintage": "vintage film photography, warm sepia tones, slight grain, nostalgic aesthetic, kodachrome colour grading",
    "viveka": "warm saffron and deep navy palette, ancient Indian motifs, soft candlelight, cinematic grain, sacred geometry patterns, inspirational poster aesthetic",
}


def build_system_prompt():
    return f"""You are an elite short-form video director and scriptwriter specialising in emotionally resonant 30-60 second reels for mobile audiences.

Your job is to generate a scene-by-scene video script as structured JSON.

RULES:
- Every scene must have a clear emotional purpose (hook, build, peak, resolution)
- Narration must be conversational, punchy — no more than 20 words per scene
- Narration is ONLY the words the narrator speaks: never camera directions, never visual descriptions
- Never copy the user's topic sentence into the narration; turn it into a story with a real person, a concrete moment and stakes
- Talk to the viewer as "you"; use specific, sensory details (a time, a place, a feeling) instead of vague inspiration
- subtitle_text is a 2-6 word caption in CAPS, not a copy of the narration
- Visual prompts must be hyper-specific: describe lighting, camera angle, subject, mood, colour
- Each scene must flow naturally into the next (visual and emotional continuity)
- The hook (Scene 1) must grab attention within 2 seconds
- Each scene gets a "footage" tag: the ONE stock-footage category below that best fits its visuals

FOOTAGE CATEGORIES:
{footage_prompt_hint()}

OUTPUT FORMAT (strict JSON, no markdown):
{{
  "title": "short catchy reel title",
  "hook": "one sentence that makes someone stop scrolling",
  "scenes": [
    {{
      "scene_id": 1,
      "duration_hint": 6,
      "narration": "Short punchy narration text for voiceover",
      "subtitle_text": "SUBTITLE TEXT (caps for impact words)",
      "visual_prompt": "Hyper-specific image generation prompt with lighting, angle, mood, colours",
      "footage": "one category name from FOOTAGE CATEGORIES, e.g. mood_rain",
      "text_overlay": "optional bold text shown on screen (or null)",
      "emotion": "the feeling this scene should evoke"
    }}
  ],
  "call_to_action": "final message or action for the viewer"
}}"""


def build_user_prompt(topic, scene_count, style):
    style_desc = STYLES.get(style, STYLES["cinematic"])
    return f"""Create a {scene_count}-scene vertical reel (9:16) script about: "{topic}"

Visual style for ALL images: {style_desc}

Requirements:
- Scene 1: Powerful hook — show the PROBLEM or a striking visual that stops the scroll
- Middle scenes: Build the story, reveal, or journey
- Final scene: Emotional resolution + clear message
- Total reel duration: 25-45 seconds
- Tone: Authentic, inspiring, cinematic — not corporate

Generate exactly {scene_count} scenes. Output only valid JSON."""


def parse_json_response(text):
    """Extract JSON from LLM response, handle markdown code blocks."""
    text = text.strip()
    # Remove markdown code fences if present
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON object
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise


def ensure_exact_scene_count(script_data, required_count):
    """Pad or trim scenes to match required count."""
    scenes = script_data.get("scenes", [])

    # Trim if too many
    if len(scenes) > required_count:
        script_data["scenes"] = scenes[:required_count]
        return script_data

    # Pad if too few
    while len(script_data["scenes"]) < required_count:
        idx = len(script_data["scenes"]) + 1
        script_data["scenes"].append({
            "scene_id": idx,
            "duration_hint": 6,
            "narration": "Every great journey begins with a single step forward.",
            "subtitle_text": "TAKE THE STEP",
            "visual_prompt": "Wide cinematic landscape at golden hour, silhouette of person standing at crossroads, warm orange sky",
            "text_overlay": None,
            "emotion": "hope"
        })

    return script_data


def generate_with_gemini(prompt_system, prompt_user, api_key):
    """Try each Gemini model until one works."""
    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt_user}]}],
            "systemInstruction": {"parts": [{"text": prompt_system}]},
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 3000,
                "responseMimeType": "application/json"
            }
        }
        try:
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                logger.info(f"✅ Gemini model {model} succeeded")
                return text
            else:
                logger.warning(f"⚠️ Gemini {model} returned {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"⚠️ Gemini {model} error: {e}")
    return None


def generate_with_pollinations(prompt_user, api_key=None):
    """Use Pollinations free text API."""
    try:
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "messages": [
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": prompt_user}
            ],
            "model": "openai",
            "jsonMode": True,
            "seed": 42
        }
        resp = requests.post(
            "https://text.pollinations.ai/",
            json=payload,
            headers=headers,
            timeout=45
        )
        if resp.status_code == 200:
            logger.info("✅ Pollinations text API succeeded")
            return resp.text
        logger.warning(f"⚠️ Pollinations POST returned {resp.status_code}, trying GET")

        resp = requests.get(
            "https://text.pollinations.ai/" + requests.utils.quote(prompt_user, safe=""),
            params={"system": build_system_prompt(), "json": "true", "model": "openai"},
            timeout=60
        )
        if resp.status_code == 200 and "scenes" in resp.text:
            logger.info("✅ Pollinations GET succeeded")
            return resp.text
        logger.warning(f"⚠️ Pollinations GET returned {resp.status_code}")
    except Exception as e:
        logger.warning(f"⚠️ Pollinations error: {e}")
    return None


def generate_fallback_script(topic, scene_count, style):
    """Offline script writer (theme-aware story arc) when no LLM is reachable."""
    return write_script(topic, scene_count)


def generate_script(prompt=None, topic=None, scene_count=5, style="cinematic",
                    gemini_api_key=None, pollinations_api_key=None, api_key=None):
    """
    Main entry point. Returns a dict with title, hook, scenes[], call_to_action.

    The prompt is used word for word (see prompt_format.py for the SCENE:/CAPTION:/
    FOOTAGE: format). Only a prompt starting with "WRITE:" is handed to a writer:
    gemini-2.0-flash → gemini-1.5-flash → Pollinations → offline writer.

    Aliases: prompt= for topic=, api_key= for gemini_api_key=.
    """
    topic = topic or prompt or "Inspiring story"
    use_writer, topic = wants_ai_writer(topic)
    if not use_writer:
        script = script_from_prompt(topic, scene_count)
        if script["scenes"]:
            logger.info(f"📝 Using prompt verbatim ({script['source']}, {len(script['scenes'])} scenes)")
            return script

    gemini_api_key = gemini_api_key or api_key
    scene_count = max(2, min(8, int(scene_count)))
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(topic, scene_count, style)

    raw_text = None

    # 1. Try Gemini first (best quality)
    if gemini_api_key:
        logger.info("🔄 Trying Gemini API...")
        raw_text = generate_with_gemini(system_prompt, user_prompt, gemini_api_key)

    # 2. Try Pollinations
    if not raw_text:
        logger.info("🔄 Trying Pollinations API...")
        raw_text = generate_with_pollinations(user_prompt, pollinations_api_key)

    # 3. Parse JSON
    if raw_text:
        try:
            script_data = parse_json_response(raw_text)
            # Normalise structure
            if "scenes" not in script_data:
                # Maybe the model returned a list directly
                if isinstance(script_data, list):
                    script_data = {"scenes": script_data}
                else:
                    raise ValueError("No scenes key in response")
            script_data.setdefault("title", topic[:50])
            script_data.setdefault("hook", "")
            script_data.setdefault("call_to_action", "")
            return ensure_exact_scene_count(script_data, scene_count)
        except Exception as e:
            logger.error(f"❌ JSON parse failed: {e}\nRaw: {raw_text[:300]}")

    # 4. Fallback
    logger.info("⚠️ No LLM reachable — using offline script writer")
    return generate_fallback_script(topic, scene_count, style)

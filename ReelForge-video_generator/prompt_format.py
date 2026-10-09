"""
prompt_format.py — Turn the user's prompt into a script, word for word.

The narration is never rewritten: what the prompt says is what the voiceover says.

STRUCTURED FORMAT (recommended)
-------------------------------
    TITLE: Arise. Awake.

    SCENE: Third attempt. Failed. Arjun stared at the rejection letter.
    CAPTION: 3rd attempt. Failed.
    FOOTAGE: mood_rain

    SCENE: He opened his phone and typed: I want to give up.
    FOOTAGE: urban_city, human_walk

    SCENE: Arise, awake, and stop not till the goal is reached.
    CAPTION: Arise. Awake. Stop not.
    VISUAL: sunrise over the mountains

Keys (case-insensitive, one per line):
    TITLE    optional  reel title (defaults to the first scene's opening words)
    SCENE    required  narration, spoken exactly as written; starts a new scene.
                       "SCENE 2:" style numbering is also accepted.
    CAPTION  optional  on-screen subtitle text (defaults to the SCENE text)
    FOOTAGE  optional  stock-clip categories, comma-separated, used in order:
                       nature_sunrise, nature_fire, nature_water, mood_rain, human_study,
                       human_walk, urban_city, human_write, mood_calm, india_crowd
                       (omit it and clips are matched from the scene's words)
                       Use FOOTAGE: vivekananda to show his photographs; any scene that
                       mentions Vivekananda / Swamiji shows them automatically.
    VISUAL   optional  extra words for clip matching / the AI-image fallback
A line without a key continues the previous field (handy for long narration).

PLAIN TEXT
----------
Anything without SCENE: lines is used verbatim too: it is split into sentences
and the sentences are spread across the requested number of scenes.

AI WRITER
---------
Start the prompt with "WRITE:" to have the script written for you instead
(Gemini / Pollinations / offline writer), e.g.  WRITE: why youth should read Vivekananda
"""

import re

KEYS = ("TITLE", "SCENE", "CAPTION", "FOOTAGE", "VISUAL")
LINE_RE = re.compile(r"^\s*(TITLE|SCENE|CAPTION|FOOTAGE|VISUAL)(?:\s*\d+)?\s*[:\-]\s*(.*)$", re.IGNORECASE)
WRITE_RE = re.compile(r"^\s*WRITE\s*:\s*", re.IGNORECASE)


def wants_ai_writer(prompt):
    """(True, topic) when the prompt starts with WRITE:, else (False, prompt)."""
    if WRITE_RE.match(prompt or ""):
        return True, WRITE_RE.sub("", prompt, count=1).strip()
    return False, prompt


def is_structured(prompt):
    return any(LINE_RE.match(l) and LINE_RE.match(l)[1].upper() == "SCENE"
               for l in (prompt or "").splitlines())


def _title_from(text, limit=40):
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "..."


def _scene(idx, narration, caption=None, footage=None, visual=None):
    narration = " ".join(narration.split())
    return {
        "scene_id": idx,
        "narration": narration,
        "subtitle_text": " ".join((caption or narration).split()),
        "visual_prompt": " ".join((visual or narration).split()),
        "footage": footage or None,
        "text_overlay": None,
        "emotion": None,
    }


def parse_structured(prompt):
    title, scenes, cur, last_key = None, [], None, None
    for raw in prompt.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = LINE_RE.match(line)
        if m:
            key, value = m[1].upper(), m[2].strip()
            if key == "SCENE":
                cur = {"SCENE": value}
                scenes.append(cur)
            elif key == "TITLE":
                title = value
            elif cur is not None:
                cur[key] = value
            last_key = key
        elif last_key == "TITLE":
            title = f"{title} {line}"
        elif cur is not None and last_key:
            cur[last_key] = f"{cur.get(last_key, '')} {line}".strip()

    scenes = [s for s in scenes if s.get("SCENE")]
    out = [_scene(i + 1, s["SCENE"], s.get("CAPTION"), s.get("FOOTAGE"), s.get("VISUAL"))
           for i, s in enumerate(scenes)]
    if not title:
        title = _title_from(out[0]["narration"]) if out else ""
    return {
        "title": title,
        "hook": out[0]["narration"] if out else "",
        "scenes": out,
        "call_to_action": "",
        "source": "prompt:structured",
    }


def split_plain(prompt, scene_count):
    """Verbatim plain text → scenes: sentences spread evenly over scene_count scenes."""
    text = " ".join((prompt or "").split())
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()] or [text]
    n = max(1, min(int(scene_count or 1), len(sentences)))
    # contiguous groups, as even as possible
    base, extra = divmod(len(sentences), n)
    groups, i = [], 0
    for g in range(n):
        size = base + (1 if g < extra else 0)
        groups.append(" ".join(sentences[i:i + size]))
        i += size
    scenes = [_scene(k + 1, g) for k, g in enumerate(groups)]
    return {
        "title": _title_from(sentences[0].rstrip(".!?")),
        "hook": scenes[0]["narration"],
        "scenes": scenes,
        "call_to_action": "",
        "source": "prompt:plain",
    }


def script_from_prompt(prompt, scene_count=4):
    """Verbatim script for a structured or plain prompt."""
    if is_structured(prompt):
        return parse_structured(prompt)
    return split_plain(prompt, scene_count)


TEMPLATE = """TITLE: Your reel title

SCENE: First line the narrator says, exactly as written.
CAPTION: Short on-screen text
FOOTAGE: mood_rain

SCENE: Second line of narration.
FOOTAGE: human_study, human_write

SCENE: Final line, your message or call to action.
CAPTION: Your closing caption
FOOTAGE: nature_sunrise"""

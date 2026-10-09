"""
script_templates.py — Offline reel script writer for ReelForge.

Used when no LLM is reachable (no Gemini key, Pollinations down). Instead of
pasting the prompt into a fixed template, it detects the prompt's theme and
assembles a story arc — hook, struggle, turning point, resolution, call to
action — from hand-written beats, so the narration reads like a real reel.

Every beat carries a stock-footage tag (see clip_library.FOOTAGE_CATEGORIES)
so the matching clip is picked deterministically.
"""

import random
import re

# ── QUOTES (public domain / scripture) ────────────────────────────────────────

QUOTES = {
    "vivekananda": [
        ("Arise, awake, and stop not till the goal is reached.", "Swami Vivekananda"),
        ("Take up one idea. Make that one idea your life.", "Swami Vivekananda"),
        ("Strength is life. Weakness is death.", "Swami Vivekananda"),
        ("All the powers in the universe are already ours.", "Swami Vivekananda"),
        ("We are what our thoughts have made us.", "Swami Vivekananda"),
        ("You cannot believe in God until you believe in yourself.", "Swami Vivekananda"),
    ],
    "gita": [
        ("You have a right to your actions, but never to the fruits of your actions.", "Bhagavad Gita"),
        ("Better your own path, done imperfectly, than another's done perfectly.", "Bhagavad Gita"),
        ("The mind is restless, but it is restrained by practice.", "Bhagavad Gita"),
    ],
    "buddha": [
        ("What you think, you become.", "The Buddha"),
        ("No one saves us but ourselves. We ourselves must walk the path.", "The Buddha"),
    ],
    "nature": [
        ("Adopt the pace of nature. Her secret is patience.", "Ralph Waldo Emerson"),
        ("In every walk with nature, one receives far more than he seeks.", "John Muir"),
    ],
    "general": [
        ("The best time to plant a tree was twenty years ago. The second best time is now.", "Proverb"),
        ("Fall seven times, stand up eight.", "Japanese proverb"),
        ("A journey of a thousand miles begins with a single step.", "Lao Tzu"),
        ("It does not matter how slowly you go, as long as you do not stop.", "Proverb"),
    ],
}

QUOTE_SOURCES = {
    "vivekananda": ["vivekananda", "swami", "ramakrishna"],
    "gita": ["gita", "krishna", "arjuna", "karma", "dharma"],
    "buddha": ["buddha", "buddhism", "zen"],
}

# ── THEMES ────────────────────────────────────────────────────────────────────
# Each beat: (narration, subtitle, visual_prompt, footage, emotion)
# "{quote}" / "{author}" are filled from the theme's quote pool.

THEMES = {
    "spiritual": {
        "keywords": ["vivekananda", "swami", "spiritual", "gita", "krishna", "buddha", "monk",
                     "meditation", "karma", "dharma", "soul", "wisdom", "god", "faith", "yoga",
                     "inner peace", "sanatan", "upanishad", "ramakrishna"],
        "titles": ["The Wisdom We Forgot", "Arise. Awake.", "Ancient Words, Modern Battles"],
        "hook": [
            ("Long before your phone existed, someone already wrote the answer to your anxiety.", "THE ANSWER IS OLD",
             "monk silhouette at sunrise", "nature_sunrise", "intrigue"),
            ("You scroll for peace. You were never going to find it here.", "PEACE ISN'T ON THIS SCREEN",
             "rain on a window at night", "mood_rain", "restlessness"),
        ],
        "build": [
            ("We have more information than any generation before us, and less clarity.", "MORE NOISE. LESS CLARITY.",
             "city night timelapse", "urban_city", "overwhelm"),
            ("Every notification pulls you outward. Nothing teaches you to look within.", "LOOK WITHIN",
             "lonely person walking a city street", "human_walk", "loneliness"),
        ],
        "turn": [
            ("Then you hear it. {quote}", "{quote_short}", "candle flame in a dark room", "nature_fire", "awe"),
        ],
        "resolution": [
            ("Strength was never outside you. Sit still for five minutes, and you will feel it.", "STRENGTH IS WITHIN",
             "person meditating calmly", "mood_calm", "peace"),
            ("The wisdom is ancient. The fight is yours. And you are ready.", "YOU ARE READY",
             "golden sunrise over the horizon", "nature_sunrise", "hope"),
        ],
    },
    "study": {
        "keywords": ["study", "student", "exam", "exams", "jee", "neet", "upsc", "board", "college",
                     "school", "marks", "result", "topper", "learning", "padhai", "rank"],
        "titles": ["One More Chapter", "The Night Before Results", "Study Like It Matters"],
        "hook": [
            ("Two a.m. Same page. Fourth time. And it still isn't going in.", "SAME PAGE. 4TH TIME.",
             "student at a desk late at night", "human_study", "frustration"),
            ("Everyone around you looks ahead. You feel a hundred chapters behind.", "100 CHAPTERS BEHIND",
             "rain on a window at night", "mood_rain", "anxiety"),
        ],
        "build": [
            ("The syllabus is endless, the comparison is louder, and your phone keeps winning.", "YOUR PHONE KEEPS WINNING",
             "busy city at night", "urban_city", "overwhelm"),
            ("You don't need more motivation videos. You need one honest hour.", "ONE HONEST HOUR",
             "hands writing in a notebook", "human_write", "resolve"),
        ],
        "turn": [
            ("Toppers aren't different. They just started again on the days they wanted to quit.", "THEY STARTED AGAIN",
             "student focused at a desk", "human_study", "determination"),
            ("Remember this. {quote}", "{quote_short}", "candle flame glowing", "nature_fire", "inspiration"),
        ],
        "resolution": [
            ("Close the tabs. Open the book. One page, done properly, beats ten skimmed.", "ONE PAGE. DONE PROPERLY.",
             "hands writing notes in a notebook", "human_write", "focus"),
            ("The result is months away. The habit starts tonight.", "THE HABIT STARTS TONIGHT",
             "sunrise over the horizon", "nature_sunrise", "hope"),
        ],
    },
    "failure": {
        "keywords": ["fail", "failed", "failure", "rejection", "rejected", "give up", "giving up",
                     "setback", "comeback", "lost", "broke", "broken", "depression", "sad", "struggle"],
        "titles": ["Not The End", "The Comeback Starts Here", "After The Fall"],
        "hook": [
            ("Third attempt. Rejected again. And everyone is pretending not to notice.", "REJECTED. AGAIN.",
             "rain on a window at night", "mood_rain", "despair"),
            ("Nobody posts the night they almost gave up. So let's talk about it.", "THE NIGHT I ALMOST QUIT",
             "candle in a dark room", "nature_fire", "vulnerability"),
        ],
        "build": [
            ("You replay every mistake. You wonder if you were ever good enough.", "WAS I EVER ENOUGH?",
             "lonely person walking a street", "human_walk", "doubt"),
            ("Failure feels permanent at night. In the morning it's just information.", "FAILURE IS INFORMATION",
             "dark city lights at night", "urban_city", "reflection"),
        ],
        "turn": [
            ("{quote}", "{quote_short}", "sunrise breaking through clouds", "nature_sunrise", "hope"),
            ("Every person you admire has a version of tonight. They just didn't stop there.", "THEY DIDN'T STOP THERE",
             "person walking forward on a street", "human_walk", "resolve"),
        ],
        "resolution": [
            ("So write down what went wrong. Then write down what you'll do tomorrow.", "WRITE TOMORROW'S PLAN",
             "hands writing in a notebook", "human_write", "determination"),
            ("This isn't your ending. It's the part of the story where you turn around.", "THIS IS WHERE YOU TURN",
             "golden sunrise", "nature_sunrise", "triumph"),
        ],
    },
    "discipline": {
        "keywords": ["discipline", "habit", "habits", "routine", "morning", "consistency", "consistent",
                     "procrastination", "lazy", "focus", "productivity", "self improvement", "dopamine",
                     "gym", "fitness", "workout", "health"],
        "titles": ["Discipline Over Mood", "The 5 A.M. Truth", "Small Steps, Every Day"],
        "hook": [
            ("Motivation got you started. It will not get you through Tuesday.", "MOTIVATION FADES",
             "city timelapse", "urban_city", "intrigue"),
            ("You don't need a new plan. You need to stop breaking the old one.", "STOP BREAKING THE PLAN",
             "hands writing a plan in a notebook", "human_write", "challenge"),
        ],
        "build": [
            ("Every skipped day feels small. Together they quietly become your life.", "SMALL SKIPS ADD UP",
             "person walking alone on a street", "human_walk", "reflection"),
            ("Your phone is designed to win. Your future needs you to win first.", "WIN THE MORNING FIRST",
             "sunrise sky", "nature_sunrise", "resolve"),
        ],
        "turn": [
            ("{quote}", "{quote_short}", "ocean waves", "nature_water", "inspiration"),
        ],
        "resolution": [
            ("Pick one habit. Do it badly, daily. In ninety days you won't recognise yourself.", "ONE HABIT. 90 DAYS.",
             "person studying with focus", "human_study", "determination"),
            ("Discipline isn't punishment. It's the promise you finally keep to yourself.", "KEEP YOUR PROMISE",
             "golden sunrise", "nature_sunrise", "pride"),
        ],
    },
    "india": {
        "keywords": ["india", "indian", "bharat", "youth", "desh", "nation", "independence", "culture",
                     "festival", "diwali", "holi", "village", "mumbai", "delhi", "varanasi"],
        "titles": ["Young India, Wake Up", "The Billion-Dream Nation", "Bharat's Next Chapter"],
        "hook": [
            ("Six hundred million young Indians. Imagine if all of them woke up at once.", "600 MILLION. ONE WAKE-UP.",
             "busy Indian street market crowd", "india_crowd", "awe"),
            ("The world's youngest nation is also its most distracted. That can change.", "YOUNGEST. MOST DISTRACTED.",
             "city at night timelapse", "urban_city", "challenge"),
        ],
        "build": [
            ("Our grandparents built this country with less than we waste every day.", "THEY BUILT WITH LESS",
             "crowded Indian market", "india_crowd", "reflection"),
            ("Talent was never the problem. Belief in ourselves was.", "BELIEVE IN YOURSELF",
             "person walking a street", "human_walk", "resolve"),
        ],
        "turn": [
            ("{quote}", "{quote_short}", "diya flame glowing", "nature_fire", "inspiration"),
        ],
        "resolution": [
            ("Build something. Learn something. Serve someone. That is how a nation rises.", "BUILD. LEARN. SERVE.",
             "student studying with focus", "human_study", "determination"),
            ("India's next chapter isn't written by leaders. It's written by you.", "WRITTEN BY YOU",
             "sunrise over the horizon", "nature_sunrise", "pride"),
        ],
    },
    "nature": {
        "keywords": ["ocean", "sea", "nature", "mountain", "mountains", "forest", "river", "rain",
                     "sunrise", "sunset", "travel", "earth", "sky", "beach", "wild"],
        "titles": ["What Nature Already Knows", "Slow Down", "The Ocean Doesn't Hurry"],
        "hook": [
            ("The ocean has been doing the same thing for four billion years. It never looks bored.", "4 BILLION YEARS. NEVER BORED.",
             "ocean waves rolling in", "nature_water", "awe"),
            ("When did you last watch a sunrise without taking a photo of it?", "WHEN DID YOU LAST JUST LOOK?",
             "sunrise sky", "nature_sunrise", "wonder"),
        ],
        "build": [
            ("We live in boxes, between screens, and wonder why we feel so small.", "WE LIVE IN BOXES",
             "city night timelapse", "urban_city", "reflection"),
            ("Rain doesn't apologise for slowing you down. Maybe it's trying to tell you something.", "SLOW DOWN",
             "rain on a window", "mood_rain", "calm"),
        ],
        "turn": [
            ("{quote}", "{quote_short}", "calm ocean waves", "nature_water", "peace"),
        ],
        "resolution": [
            ("Go outside today. No phone. Ten minutes. Let the world remind you how big it is.", "TEN MINUTES. NO PHONE.",
             "person walking outdoors", "human_walk", "peace"),
            ("Nature never rushes, yet everything gets done. You're allowed to move like that too.", "NATURE NEVER RUSHES",
             "person meditating calmly", "mood_calm", "serenity"),
        ],
    },
    "general": {
        "keywords": [],
        "titles": ["Start Before You're Ready", "The Turning Point", "Your Move"],
        "hook": [
            ("Stop scrolling for a second. This might be the sign you were waiting for.", "THIS IS YOUR SIGN",
             "sunrise sky", "nature_sunrise", "intrigue"),
            ("Everyone wants the result. Almost nobody wants the quiet, boring middle.", "NOBODY WANTS THE MIDDLE",
             "city timelapse at night", "urban_city", "challenge"),
        ],
        "build": [
            ("The doubt gets loud right before things start to change.", "DOUBT GETS LOUD",
             "rain on a window", "mood_rain", "tension"),
            ("You don't need to see the whole staircase. Just the next step.", "JUST THE NEXT STEP",
             "person walking forward", "human_walk", "resolve"),
        ],
        "turn": [
            ("{quote}", "{quote_short}", "ocean waves at dawn", "nature_water", "inspiration"),
        ],
        "resolution": [
            ("Start small. Start messy. But start today, while it still scares you.", "START TODAY",
             "hands writing in a notebook", "human_write", "determination"),
            ("A year from now, you'll wish you had started today. So start.", "SO START.",
             "golden sunrise", "nature_sunrise", "hope"),
        ],
    },
}

CTA = [
    ("Save this for the day you need it. And send it to someone who does today.", "SAVE THIS. SHARE IT.",
     "sunrise over the horizon", "nature_sunrise", "warmth"),
    ("Follow for a daily reminder that you're stronger than your worst day.", "FOLLOW FOR DAILY STRENGTH",
     "person meditating calmly", "mood_calm", "warmth"),
]


# ── HELPERS ───────────────────────────────────────────────────────────────────

def detect_theme(topic):
    t = topic.lower()
    # a named figure (Vivekananda, Gita, Buddha) outweighs generic words like "india"
    figures = {kw for kws in QUOTE_SOURCES.values() for kw in kws}
    scores = {name: sum(3 if kw in figures else 1
                        for kw in th["keywords"] if re.search(r"\b" + re.escape(kw), t))
              for name, th in THEMES.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "general"


def pick_quote(topic, theme, rng):
    t = topic.lower()
    for source, kws in QUOTE_SOURCES.items():
        if any(kw in t for kw in kws):
            return rng.choice(QUOTES[source])
    if theme in ("spiritual", "india"):
        return rng.choice(QUOTES["vivekananda"])
    if theme == "nature":
        return rng.choice(QUOTES["nature"])
    return rng.choice(QUOTES["general"])


def short_caption(quote, limit=34):
    """Uppercase caption from a quote: its first sentence, or a word-boundary cut with '...'."""
    first = re.split(r"(?<=[.!?])\s", quote.strip())[0].rstrip(".")
    if len(first) <= limit:
        return first.upper()
    out = ""
    for w in first.split():
        if len(out) + len(w) + 1 > limit - 3:
            break
        out = f"{out} {w}".strip()
    return out.rstrip(",;").upper() + "..."


def title_from(topic, theme, rng):
    topic = " ".join(topic.split())
    if 3 <= len(topic) <= 40:
        return topic[0].upper() + topic[1:]
    return rng.choice(THEMES[theme]["titles"])


# ── MAIN ──────────────────────────────────────────────────────────────────────

def write_script(topic, scene_count=4, seed=None):
    """Return a script dict in the same shape the LLM path produces."""
    rng = random.Random(seed)
    scene_count = max(2, min(8, int(scene_count)))
    theme = detect_theme(topic)
    th = THEMES[theme]
    quote, author = pick_quote(topic, theme, rng)

    # arc: hook → builds → turn → resolution → (cta when there's room)
    hook = rng.choice(th["hook"])
    turn = rng.choice(th["turn"])
    resolution = rng.choice(th["resolution"])
    builds = rng.sample(th["build"], len(th["build"]))
    extra = [b for name, t in THEMES.items() if name != theme for b in t["build"]]
    rng.shuffle(extra)

    if scene_count == 2:
        beats = [hook, resolution]
    elif scene_count == 3:
        beats = [hook, turn, resolution]
    else:
        middle = (builds + extra)[:max(0, scene_count - 4)]
        beats = [hook] + middle + [turn, resolution, rng.choice(CTA)]

    scenes = []
    for i, (narr, sub, visual, footage, emotion) in enumerate(beats):
        fill = {"quote": quote, "author": author, "quote_short": short_caption(quote)}
        narr = narr.format(**fill)
        if "{quote}" in beats[i][0] and author not in narr:
            narr = f"{narr} — {author}."
        scenes.append({
            "scene_id": i + 1,
            "duration_hint": 6,
            "narration": narr,
            "subtitle_text": sub.format(**fill),
            "visual_prompt": visual,
            "footage": footage,
            "text_overlay": author if "{quote}" in beats[i][0] else None,
            "emotion": emotion,
        })

    return {
        "title": title_from(topic, theme, rng),
        "hook": scenes[0]["narration"],
        "scenes": scenes,
        "call_to_action": CTA[0][0],
        "source": f"offline:{theme}",
    }

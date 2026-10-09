"""
Generates high-resolution 720x1280 cinematic visual canvases for scenes.
Provides distinctive palettes and visual motifs for each of the 8 journeys.
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

WIDTH = 720
HEIGHT = 1280

# 8 Distinct Journey Palettes matching the frontend Kesari/Clay/Indigo aesthetic
JOURNEY_THEMES = {
    1: {"name": "Fearlessness", "top": (30, 20, 25), "bot": (60, 25, 30), "accent": (244, 63, 94)},    # Rose / Crimson courage
    2: {"name": "Self-Faith", "top": (15, 23, 42), "bot": (30, 41, 59), "accent": (234, 179, 8)},     # Indigo / Gold self-belief
    3: {"name": "Focus", "top": (8, 28, 36), "bot": (14, 50, 60), "accent": (34, 211, 238)},          # Deep Cyan / Laser focus
    4: {"name": "Purpose", "top": (28, 25, 45), "bot": (50, 35, 75), "accent": (168, 85, 247)},        # Purple / North star
    5: {"name": "Persistence", "top": (40, 20, 10), "bot": (75, 35, 15), "accent": (249, 115, 22)},   # Amber / Fire
    6: {"name": "Strength", "top": (20, 30, 25), "bot": (35, 55, 40), "accent": (52, 211, 153)},      # Emerald / Vitality
    7: {"name": "Self-Mastery", "top": (25, 25, 35), "bot": (45, 40, 60), "accent": (129, 140, 248)}, # Slate / Sovereign mind
    8: {"name": "Service", "top": (35, 25, 15), "bot": (65, 45, 25), "accent": (251, 191, 36)}        # Warm Kesari / Sun
}


def _get_font(size: int, bold: bool = False):
    font_paths = [
        "C:\\Windows\\Fonts\\NirmalaB.ttf" if bold else "C:\\Windows\\Fonts\\Nirmala.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def render_scene_canvas(
    lesson_id: int,
    scene_type: str,
    prompt_hint: str,
    output_path: str,
    scene_idx: int = 0
) -> str:
    """Renders a 720x1280 themed visual canvas."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    theme = JOURNEY_THEMES.get(lesson_id, JOURNEY_THEMES[3])
    img = Image.new("RGB", (WIDTH, HEIGHT), theme["top"])
    draw = ImageDraw.Draw(img)

    r1, g1, b1 = theme["top"]
    r2, g2, b2 = theme["bot"]
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(r1 + ratio * (r2 - r1))
        g = int(g1 + ratio * (g2 - g1))
        b = int(b1 + ratio * (b2 - b1))
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Center mandala / concentric sacred geometry
    cx, cy = WIDTH // 2, HEIGHT // 2 - 80
    accent = theme["accent"]
    soft_accent = (accent[0] // 3, accent[1] // 3, accent[2] // 3)

    # Concentric rings
    for radius in [260, 200, 140, 80]:
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=soft_accent, width=1)

    # 8-petal mandala rays
    for i in range(8):
        angle = i * (math.pi / 4)
        x1 = cx + int(60 * math.cos(angle))
        y1 = cy + int(60 * math.sin(angle))
        x2 = cx + int(240 * math.cos(angle))
        y2 = cy + int(240 * math.sin(angle))
        draw.line([(x1, y1), (x2, y2)], fill=soft_accent, width=1)

    # Subtle vignette overlay at top and bottom
    for y in range(120):
        alpha = int((1 - (y / 120)) * 140)
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0))
    for y in range(HEIGHT - 220, HEIGHT):
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0))

    # Top scene label pill
    pill_y = 64
    font_cat = _get_font(16, bold=True)
    pill_text = f"JOURNEY {lesson_id} • {theme['name'].upper()} • {scene_type.upper()}"
    draw.rounded_rectangle([WIDTH // 2 - 180, pill_y - 14, WIDTH // 2 + 180, pill_y + 16], radius=15, outline=soft_accent, fill=(0, 0, 0))
    draw.text((WIDTH // 2, pill_y), pill_text, fill=accent, font=font_cat, anchor="mm")

    # Center motif icon/label
    font_scene = _get_font(24, bold=True)
    clean_label = {
        "hook": "THE CATALYST",
        "situation": "THE MODERN STRUGGLE",
        "meaning": "THE TIMELESS INSIGHT",
        "action": "YOUR 2-MINUTE SHIFT",
        "outro": "THE PATH FORWARD"
    }.get(scene_type, scene_type.upper())
    draw.text((WIDTH // 2, cy), clean_label, fill=(240, 240, 245), font=font_scene, anchor="mm")

    img.save(output_path, quality=92)
    return output_path

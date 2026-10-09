"""
Renders a gold-framed 9:16 quote card image for Swami Vivekananda's verbatim quotes.
Used in video rendering to distinguish the authentic Complete Works text
from the AI-generated story/illustration scenes.
"""
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
from pathlib import Path

WIDTH = 720
HEIGHT = 1280

BG_GRADIENT_TOP = (15, 23, 42)
BG_GRADIENT_BOT = (30, 41, 59)
GOLD_PRIMARY = (234, 179, 8)
GOLD_SOFT = (202, 138, 4)
WHITE_INK = (248, 250, 252)
MUTED_INK = (148, 163, 184)


def _get_font(size: int, bold: bool = False):
    font_paths = [
        "C:\\Windows\\Fonts\\NirmalaB.ttf" if bold else "C:\\Windows\\Fonts\\Nirmala.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def render_quote_card_image(
    quote_text: str,
    source_citation: str,
    output_path: str,
    lang: str = "en"
) -> str:
    """Renders a 720x1280 portrait quote card image."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), BG_GRADIENT_TOP)
    draw = ImageDraw.Draw(img)

    r1, g1, b1 = BG_GRADIENT_TOP
    r2, g2, b2 = BG_GRADIENT_BOT
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(r1 + ratio * (r2 - r1))
        g = int(g1 + ratio * (g2 - g1))
        b = int(b1 + ratio * (b2 - b1))
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    margin = 36
    draw.rounded_rectangle(
        [margin, margin, WIDTH - margin, HEIGHT - margin],
        radius=24,
        outline=GOLD_SOFT,
        width=2
    )
    inner_m = margin + 12
    draw.rounded_rectangle(
        [inner_m, inner_m, WIDTH - inner_m, HEIGHT - inner_m],
        radius=16,
        outline=(51, 65, 85),
        width=1
    )

    badge_y = margin + 48
    font_badge = _get_font(18, bold=True)
    badge_text = "प्रमाणित उपदेश • COMPLETE WORKS" if lang == "hi" else "VERIFIED TEACHING • COMPLETE WORKS"
    draw.text((WIDTH // 2, badge_y), badge_text, fill=GOLD_PRIMARY, font=font_badge, anchor="mm")

    author_y = badge_y + 44
    font_author = _get_font(28, bold=True)
    draw.text((WIDTH // 2, author_y), "SWAMI VIVEKANANDA", fill=WHITE_INK, font=font_author, anchor="mm")

    line_y = author_y + 24
    draw.line([(WIDTH // 2 - 60, line_y), (WIDTH // 2 + 60, line_y)], fill=GOLD_PRIMARY, width=2)

    font_ornament = _get_font(96, bold=True)
    draw.text((WIDTH // 2, HEIGHT // 2 - 200), "\u201c", fill=GOLD_PRIMARY, font=font_ornament, anchor="mm")

    clean_quote = quote_text.strip().strip('"').strip("'")
    words = clean_quote.split()
    if len(words) > 30:
        font_size = 24
        wrap_width = 30
    elif len(words) > 15:
        font_size = 28
        wrap_width = 26
    else:
        font_size = 34
        wrap_width = 22

    font_quote = _get_font(font_size, bold=True)
    lines = textwrap.wrap(clean_quote, width=wrap_width)

    line_spacing = font_size + 14
    total_text_h = len(lines) * line_spacing
    start_y = (HEIGHT // 2) - (total_text_h // 2) + 20

    for i, line in enumerate(lines):
        y = start_y + i * line_spacing
        draw.text((WIDTH // 2, y), line, fill=WHITE_INK, font=font_quote, anchor="mm")

    # Split citation across multiple lines with smaller font (12pt) for 9:16 portrait visibility
    cite_lines = []
    for chunk in source_citation.split("\n"):
        if chunk.strip():
            cite_lines.extend(textwrap.wrap(chunk.strip(), width=48))

    line_h = 18
    font_cite = _get_font(12, bold=False)
    font_cite_label = _get_font(13, bold=True)

    block_h = len(cite_lines) * line_h + 36
    cite_y = HEIGHT - margin - 36 - block_h

    draw.line([(WIDTH // 2 - 80, cite_y - 14), (WIDTH // 2 + 80, cite_y - 14)], fill=(71, 85, 105), width=1)
    draw.text((WIDTH // 2, cite_y), "ORIGINAL SOURCE:", fill=GOLD_PRIMARY, font=font_cite_label, anchor="mm")

    for i, cline in enumerate(cite_lines):
        draw.text((WIDTH // 2, cite_y + 18 + i * line_h), cline, fill=MUTED_INK, font=font_cite, anchor="mm")

    seal_y = HEIGHT - margin - 22
    font_seal = _get_font(12, bold=True)
    draw.text((WIDTH // 2, seal_y), "\u2713 VERBATIM AUTHENTIC TEXT", fill=GOLD_PRIMARY, font=font_seal, anchor="mm")

    img.save(output_path, quality=95)
    return output_path

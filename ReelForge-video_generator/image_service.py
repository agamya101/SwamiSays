"""
image_service.py — Improved image generation for ReelForge
Priority: Gemini Imagen 3 → Pollinations (with token) → Wikimedia → PIL gradient fallback
"""

import time
import base64
import logging
import requests
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFilter
from io import BytesIO

logger = logging.getLogger(__name__)

# Aspect ratio → pixel dimensions
DIMENSIONS = {
    "16:9": (1280, 720),
    "9:16": (720, 1280),
}

# Style suffix appended to every image prompt for consistency
STYLE_SUFFIXES = {
    "cinematic": "photorealistic, cinematic film still, 8K, dramatic lighting, anamorphic",
    "anime": "anime art, Studio Ghibli style, vibrant colors, detailed",
    "cyberpunk": "cyberpunk, neon lights, rain, dark atmosphere, ultra detailed",
    "documentary": "documentary photo, natural light, candid, raw emotion",
    "fantasy": "epic fantasy art, concept art, magical, ethereal lighting",
    "minimalist": "minimalist, clean, flat design, soft gradient, modern",
    "vintage": "vintage photography, film grain, sepia tones, nostalgic",
    "viveka": "warm saffron palette, deep navy, Indian aesthetic, cinematic grain, sacred geometry, inspirational, high contrast",
}


def get_dimensions(aspect_ratio):
    return DIMENSIONS.get(aspect_ratio, (720, 1280))


def enhance_prompt(visual_prompt, style):
    """Add style suffix and quality boosters to image prompt."""
    suffix = STYLE_SUFFIXES.get(style, "")
    quality_boost = "masterpiece, best quality, highly detailed, professional photography"
    return f"{visual_prompt}, {suffix}, {quality_boost}"


def fetch_imagen3(visual_prompt, style, aspect_ratio, api_key):
    """Google Imagen 3 — best quality, requires Gemini API key."""
    try:
        ar_map = {"16:9": "16:9", "9:16": "9:16"}
        ar = ar_map.get(aspect_ratio, "9:16")

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/imagen-3.0-generate-002:predict?key={api_key}"
        )
        enhanced = enhance_prompt(visual_prompt, style)
        payload = {
            "instances": [{"prompt": enhanced[:480]}],  # Imagen 3 prompt limit
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": ar,
                "safetyFilterLevel": "BLOCK_ONLY_HIGH",
                "personGeneration": "ALLOW_ADULT",
            }
        }
        resp = requests.post(url, json=payload, timeout=45)
        if resp.status_code == 200:
            data = resp.json()
            b64 = data["predictions"][0]["bytesBase64Encoded"]
            img_bytes = base64.b64decode(b64)
            img = Image.open(BytesIO(img_bytes)).convert("RGB")
            logger.info("✅ Imagen 3 succeeded")
            return img
        else:
            logger.warning(f"⚠️ Imagen 3 {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logger.warning(f"⚠️ Imagen 3 error: {e}")
    return None


def fetch_pollinations(visual_prompt, style, aspect_ratio, api_key=None):
    """Pollinations AI — free with optional bearer token for priority queue."""
    try:
        w, h = get_dimensions(aspect_ratio)
        enhanced = enhance_prompt(visual_prompt, style)
        # Pollinations has a URL length limit — keep prompt concise
        clean = enhanced[:300]
        encoded = quote(clean)

        url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&nologo=true&seed={int(time.time()) % 9999}"

        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        resp = requests.get(url, headers=headers, timeout=40, stream=True)
        if resp.status_code == 200 and len(resp.content) > 5000:
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            logger.info("✅ Pollinations succeeded")
            return img
        else:
            logger.warning(f"⚠️ Pollinations {resp.status_code}, size={len(resp.content)}")
    except Exception as e:
        logger.warning(f"⚠️ Pollinations error: {e}")
    return None


def fetch_wikimedia(visual_prompt):
    """Wikimedia Commons — factual/documentary images only."""
    try:
        # Extract key terms
        stop = {"a","an","the","of","in","on","at","to","for","with","and","or","is","are","was"}
        terms = [w for w in visual_prompt.lower().split() if len(w) > 3 and w not in stop][:4]
        if not terms:
            return None
        query = " ".join(terms)

        params = {
            "action": "query", "generator": "search",
            "gsrsearch": f"filetype:bitmap {query}",
            "gsrnamespace": 6, "gsrlimit": 8,
            "prop": "imageinfo", "iiprop": "url|size",
            "format": "json"
        }
        resp = requests.get("https://commons.wikimedia.org/w/api.php", params=params, timeout=15)
        if resp.status_code != 200:
            return None

        pages = resp.json().get("query", {}).get("pages", {})
        for page in list(pages.values())[:5]:
            info = page.get("imageinfo", [{}])[0]
            img_url = info.get("url", "")
            if not img_url or not any(img_url.lower().endswith(e) for e in [".jpg",".jpeg",".png",".webp"]):
                continue
            ir = requests.get(img_url, timeout=20)
            if ir.status_code == 200 and len(ir.content) > 8000:
                img = Image.open(BytesIO(ir.content)).convert("RGB")
                logger.info("✅ Wikimedia succeeded")
                return img
    except Exception as e:
        logger.warning(f"⚠️ Wikimedia error: {e}")
    return None


def create_gradient_fallback(visual_prompt, style, aspect_ratio):
    """Stylised gradient canvas with text — last resort."""
    w, h = get_dimensions(aspect_ratio)

    # Color palettes per style
    palettes = {
        "viveka":    [(255, 153, 51), (25, 25, 112)],   # Saffron → Navy
        "cinematic": [(20, 20, 40),   (80, 40, 10)],
        "anime":     [(255, 182, 193), (135, 206, 250)],
        "cyberpunk": [(10, 10, 30),   (0, 255, 180)],
        "fantasy":   [(75, 0, 130),   (255, 215, 0)],
        "minimalist":[(240, 240, 245),(200, 210, 230)],
        "vintage":   [(180, 140, 90), (80, 50, 20)],
        "documentary":[(40, 40, 40),  (120, 100, 80)],
    }
    c1, c2 = palettes.get(style, [(30, 30, 60), (80, 60, 20)])

    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)

    for y in range(h):
        t = y / h
        r = int(c1[0] * (1 - t) + c2[0] * t)
        g = int(c1[1] * (1 - t) + c2[1] * t)
        b = int(c1[2] * (1 - t) + c2[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Overlay circles for depth
    import random
    random.seed(42)
    for _ in range(6):
        cx = random.randint(0, w)
        cy = random.randint(0, h)
        cr = random.randint(w // 6, w // 2)
        alpha_img = Image.new("RGBA", (w, h), (0,0,0,0))
        adraw = ImageDraw.Draw(alpha_img)
        adraw.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], fill=(*c1, 25))
        img = Image.alpha_composite(img.convert("RGBA"), alpha_img).convert("RGB")

    # Add subtle text
    draw = ImageDraw.Draw(img)
    words = visual_prompt.split()[:8]
    short = " ".join(words)
    draw.text((w//2, h//2), short, fill=(255,255,255,180), anchor="mm")

    logger.info("⚠️ Using gradient fallback image")
    return img


def resize_and_crop(img, aspect_ratio):
    """Resize image to exact target dimensions with centre crop."""
    w, h = get_dimensions(aspect_ratio)
    img_ratio = img.width / img.height
    target_ratio = w / h

    if img_ratio > target_ratio:
        # Image is wider — scale by height then crop width
        new_h = h
        new_w = int(img.width * h / img.height)
    else:
        # Image is taller — scale by width then crop height
        new_w = w
        new_h = int(img.height * w / img.width)

    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - w) // 2
    top = (new_h - h) // 2
    return img.crop((left, top, left + w, top + h))


def generate_scene_image(visual_prompt=None, style="cinematic", aspect_ratio="9:16", output_path=None,
                          gemini_api_key=None, pollinations_api_key=None,
                          prompt=None, api_key=None, image_api_key=None, seed=None):
    """
    Main entry point. Returns the path to the saved image.
    Priority: Imagen 3 → Pollinations → Wikimedia → Gradient fallback

    Aliases: prompt= for visual_prompt=, api_key= for gemini_api_key=,
    image_api_key= for pollinations_api_key=. seed is accepted for API compatibility.
    """
    visual_prompt = visual_prompt or prompt or "cinematic landscape"
    gemini_api_key = gemini_api_key or api_key
    pollinations_api_key = pollinations_api_key or image_api_key
    if not output_path:
        raise ValueError("output_path is required")
    img = None

    # 1. Imagen 3 (best quality — needs Gemini key)
    if gemini_api_key and not img:
        img = fetch_imagen3(visual_prompt, style, aspect_ratio, gemini_api_key)

    # 2. Pollinations (free, decent quality)
    if not img:
        img = fetch_pollinations(visual_prompt, style, aspect_ratio, pollinations_api_key)

    # 3. Wikimedia (for factual/documentary contexts)
    if not img:
        img = fetch_wikimedia(visual_prompt)

    # 4. Gradient fallback
    if not img:
        img = create_gradient_fallback(visual_prompt, style, aspect_ratio)

    # Resize to exact target dimensions
    img = resize_and_crop(img, aspect_ratio)

    # Mild sharpening for crispness
    img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))

    img.save(output_path, "JPEG", quality=95)
    return output_path


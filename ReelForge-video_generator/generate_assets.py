"""
generate_assets.py — Run ONCE from inside your ReelForge folder.
Creates assets/user_images/ and downloads 5 Viveka scene images.

Run: python generate_assets.py
"""

import os
import time
import requests
from urllib.parse import quote

W, H = 720, 1280
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "user_images")
os.makedirs(OUT_DIR, exist_ok=True)

# Short prompts — free Pollinations model works best under 200 chars
SCENES = [
    (
        "scene_01_arjun_dark_room",
        "young Indian man studying alone at night, UPSC books on desk, rejection letter, exhausted face, "
        "single candle flame, dark room, cinematic portrait, warm amber shadows, photorealistic, vertical"
    ),
    (
        "scene_02_phone_saffron",
        "Indian man holding glowing smartphone, warm saffron orange screen light in darkness, "
        "emotional moment, dark background, cinematic bokeh, vertical format, photorealistic"
    ),
    (
        "scene_03_vivekananda_quote",
        "Swami Vivekananda in saffron robes, divine light rays, sacred mandala background, "
        "deep navy and orange palette, inspirational poster, cinematic, vertical format"
    ),
    (
        "scene_04_arjun_rises",
        "young Indian man sitting upright at desk, determined clear eyes, candle lighting face, "
        "open books, renewed strength, cinematic warm glow, vertical portrait, photorealistic"
    ),
    (
        "scene_05_viveka_app",
        "smartphone screen showing spiritual wellness app, lotus flower UI design, saffron and navy colors, "
        "VIVEKA app, dark background, product shot, cinematic vertical, inspirational"
    ),
]


def download_image(filename, prompt, attempt=1):
    out_path = os.path.join(OUT_DIR, f"{filename}.jpg")

    if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
        print(f"   ⏭️  Already exists — skipping")
        return True

    encoded = quote(prompt[:350])
    seed = (int(time.time()) + attempt * 100) % 9999
    # No model param = uses free default model
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={W}&height={H}&nologo=true&seed={seed}"

    try:
        resp = requests.get(url, timeout=90, stream=True)
        if resp.status_code == 200 and len(resp.content) > 5000:
            with open(out_path, "wb") as f:
                f.write(resp.content)
            print(f"   ✅ Saved ({len(resp.content)//1024} KB)")
            return True
        else:
            print(f"   ⚠️  Status {resp.status_code} (attempt {attempt})")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


print(f"Saving to: {OUT_DIR}\n")

for filename, prompt in SCENES:
    print(f"⬇️  {filename} ...")
    success = False
    for attempt in range(1, 4):  # up to 3 tries
        success = download_image(filename, prompt, attempt)
        if success:
            break
        print(f"   Retrying in 5s...")
        time.sleep(5)

    if not success:
        print(f"   ⚠️  Skipped after 3 tries — add image manually\n")

    time.sleep(4)  # pause between scenes

print("\n" + "=" * 50)
files = [f for f in os.listdir(OUT_DIR) if f.endswith(".jpg")]
print(f"Done! {len(files)}/5 images saved in assets/user_images/")
print("Generate your reel at http://127.0.0.1:8080")
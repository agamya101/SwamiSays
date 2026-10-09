"""
download_reel_clips.py — Build a reusable library of free Pexels stock clips.

Clips are saved as reel_clips/{prefix}{index:02d}.mp4 so the reel generator
can pick them by filename keyword (nature_, mood_, human_, urban_, india_ ...).

No API key needed: the clip URLs come from reel_clips_manifest.json, which was
built by searching pexels.com/videos in the browser. Format:
  { "nature_sunrise_": [ {"id": "29119700", "files": ["<best mp4 url>", "<smaller fallback>", ...]}, ... ], ... }

Run:  python download_reel_clips.py
Requirements: pip install requests
"""

import os, sys, json, time
import requests

# ── CONFIG ────────────────────────────────────────────────────────────────────

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
MANIFEST      = os.path.join(BASE_DIR, "reel_clips_manifest.json")
OUT_DIR       = os.path.join(BASE_DIR, "reel_clips")
CLIPS_PER_CAT = 5
MAX_BYTES     = 30 * 1024 * 1024   # skip any file over 30 MB
DELAY_SECONDS = 1.0
USER_AGENT    = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                 "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")

# category order + search terms (for the summary)
CATEGORIES = [
    ("sunrise nature sky",     "nature_sunrise_"),
    ("candle flame fire",      "nature_fire_"),
    ("ocean waves water",      "nature_water_"),
    ("rain window city",       "mood_rain_"),
    ("person studying desk",   "human_study_"),
    ("person walking street",  "human_walk_"),
    ("city timelapse night",   "urban_city_"),
    ("hands writing notebook", "human_write_"),
    ("meditation yoga calm",   "mood_calm_"),
    ("crowd market india",     "india_crowd_"),
]


# ── HELPERS ───────────────────────────────────────────────────────────────────

def download(session, url, out_path):
    """Stream to a .part file; abort if it exceeds MAX_BYTES. Returns bytes or None."""
    tmp = out_path + ".part"
    try:
        with session.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            if int(r.headers.get("Content-Length") or 0) > MAX_BYTES:
                return None
            written = 0
            with open(tmp, "wb") as fh:
                for chunk in r.iter_content(chunk_size=1 << 16):
                    written += len(chunk)
                    if written > MAX_BYTES:
                        break
                    fh.write(chunk)
        if written > MAX_BYTES or written == 0:
            os.remove(tmp)
            return None
        os.replace(tmp, out_path)
        return written
    except requests.RequestException as e:
        print(f"      download error: {e}")
        if os.path.exists(tmp):
            os.remove(tmp)
        return None


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(MANIFEST):
        sys.exit(f"Manifest not found: {MANIFEST}")
    with open(MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)
    os.makedirs(OUT_DIR, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Referer": "https://www.pexels.com/"})

    summary = []
    for query, prefix in CATEGORIES:
        print(f"\n[{prefix}] \"{query}\"")
        existing = new = 0
        index = 1
        while index <= CLIPS_PER_CAT and os.path.exists(os.path.join(OUT_DIR, f"{prefix}{index:02d}.mp4")):
            existing += 1
            index += 1
        if index > CLIPS_PER_CAT:
            print(f"   all {CLIPS_PER_CAT} already downloaded, skipping")
            summary.append((prefix, existing, 0))
            continue

        # ids already saved are tracked in a sidecar so re-runs don't duplicate clips
        ids_file = os.path.join(OUT_DIR, f".{prefix}ids")
        seen = set(open(ids_file).read().split()) if os.path.exists(ids_file) else set()

        for clip in manifest.get(prefix, []):
            if index > CLIPS_PER_CAT:
                break
            if clip["id"] in seen:
                continue
            out_path = os.path.join(OUT_DIR, f"{prefix}{index:02d}.mp4")
            for url in clip["files"]:          # best rendition first, smaller fallbacks after
                got = download(session, url, out_path)
                time.sleep(DELAY_SECONDS)
                if got:
                    print(f"   {os.path.basename(out_path)}  {url.rsplit('/', 1)[-1]}  "
                          f"{got / 1048576:.1f} MB  (pexels #{clip['id']})")
                    with open(ids_file, "a") as fh:
                        fh.write(clip["id"] + "\n")
                    seen.add(clip["id"])
                    new += 1
                    index += 1
                    break
            else:
                print(f"   skipped pexels #{clip['id']} (no rendition under 30 MB downloaded)")

        if index <= CLIPS_PER_CAT:
            print(f"   ⚠️  only got {existing + new}/{CLIPS_PER_CAT} for this category")
        summary.append((prefix, existing, new))

    print("\n" + "=" * 52)
    print(f"{'category':<16}{'already had':>12}{'downloaded':>12}{'total':>8}")
    print("-" * 52)
    for prefix, had, new in summary:
        print(f"{prefix:<16}{had:>12}{new:>12}{had + new:>8}")
    print("-" * 52)
    tot_had = sum(s[1] for s in summary)
    tot_new = sum(s[2] for s in summary)
    print(f"{'TOTAL':<16}{tot_had:>12}{tot_new:>12}{tot_had + tot_new:>8}")
    print(f"\nClips folder: {OUT_DIR}")


if __name__ == "__main__":
    main()

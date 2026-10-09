"""
make_viveka_reel.py — Standalone Viveka reel generator.
No server. No API. Just images + FFmpeg.

HOW TO USE:
1. Put your 5 images in:  assets\\user_images\\
   (any .jpg / .png files, named alphabetically in scene order)
2. Run:  python make_viveka_reel.py
3. Get:  viveka_reel.mp4  in this folder

Requirements: pip install gTTS
FFmpeg must be installed (already is if ReelForge works).
"""

import os, sys, re, shutil, subprocess, tempfile, glob, time

# ── CONFIG — edit these if needed ─────────────────────────────────────────────

IMAGES_DIR   = os.path.join(os.path.dirname(__file__), "assets", "user_images")
OUTPUT_FILE  = os.path.join(os.path.dirname(__file__), "viveka_reel.mp4")
ASPECT_RATIO = "9:16"          # "9:16" for Reels / "16:9" for YouTube
FFMPEG       = "ffmpeg"        # change to full path if needed
FONT_FILE    = "C:/Windows/Fonts/arialbd.ttf"  # Windows FFmpeg has no fontconfig, so drawtext needs a font file

# drawtext needs ':' escaped inside the path (C\:/Windows/...)
FONT_ARG = "fontfile='" + FONT_FILE.replace("\\", "/").replace(":", "\\:") + "':"

# ── SCENES — edit narration text for each scene ───────────────────────────────

SCENES = [
    {
        "narration": "Third attempt. Failed. Arjun stared at the rejection letter.",
        "subtitle":  "3rd Attempt. Failed.",
    },
    {
        "narration": "He opened his phone and typed: I want to give up.",
        "subtitle":  "I want to give up...",
    },
    {
        "narration": "Arise. Awake. And stop not till the goal is reached. — Swami Vivekananda.",
        "subtitle":  "Arise. Awake. Stop Not.",
    },
    {
        "narration": "Arjun sat up straight. Eyes clear. He opened the book again.",
        "subtitle":  "Eyes clear. Back to work.",
    },
    {
        "narration": "Viveka. Ancient wisdom for today's youth.",
        "subtitle":  "Ancient Wisdom. Today's Youth.",
    },
]

# ── DIMENSIONS ────────────────────────────────────────────────────────────────

DIMS = {"9:16": (720, 1280), "16:9": (1280, 720)}
W, H = DIMS.get(ASPECT_RATIO, (720, 1280))

# Ken Burns motion patterns (one per scene, cycles)
MOTIONS = [
    "zoompan=z='min(zoom+0.0008,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    "zoompan=z='if(eq(on,1),1.3,max(zoom-0.0008,1.0))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    "zoompan=z='min(zoom+0.0005,1.2)':x='iw/2-(iw/zoom/2)+on*0.4':y='ih/2-(ih/zoom/2)'",
    "zoompan=z='min(zoom+0.0005,1.2)':x='iw/2-(iw/zoom/2)-on*0.4':y='ih/2-(ih/zoom/2)'",
    "zoompan=z='min(zoom+0.0007,1.25)':x='iw/2-(iw/zoom/2)+on*0.3':y='ih/2-(ih/zoom/2)+on*0.2'",
]


# ── HELPERS ───────────────────────────────────────────────────────────────────

def get_images():
    exts = ["*.jpg","*.jpeg","*.png","*.webp","*.JPG","*.PNG"]
    files = []
    for e in exts:
        files.extend(glob.glob(os.path.join(IMAGES_DIR, e)))
    files = sorted(set(files))
    if not files:
        sys.exit(f"❌ No images found in {IMAGES_DIR}\n   Add .jpg/.png files there and retry.")
    return files


def generate_tts(text, out_path):
    """gTTS → mp3. Falls back to FFmpeg silence if gTTS fails."""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(out_path)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 500:
            return True
    except Exception as e:
        print(f"   gTTS failed ({e}), using silence")
    # silence fallback
    words = len(text.split())
    dur = max(3.0, words * 0.45)
    cmd = [FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
           "-t", str(dur), "-c:a", "aac", out_path]
    subprocess.run(cmd, capture_output=True)
    return True


def get_duration(path):
    res = subprocess.run([FFMPEG, "-i", path], stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE, text=True, errors="ignore")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if m:
        return int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3))
    return 4.0


def render_clip(image_path, audio_path, subtitle, scene_idx, out_path):
    duration = get_duration(audio_path) + 0.3
    duration = max(3.0, min(15.0, duration))
    frames   = int(duration * 25)

    motion = MOTIONS[scene_idx % len(MOTIONS)]
    motion_f = f"{motion}:d={frames}:s={W}x{H}:fps=25"

    sub = subtitle[:60].replace("'","").replace('"',"").replace("\\","").replace(":"," ")
    font_size = 38 if ASPECT_RATIO == "9:16" else 28
    margin_b  = 110 if ASPECT_RATIO == "9:16" else 60
    fade_dur  = 0.35

    vf = ",".join([
        # fill the frame without stretching: scale up to cover, then center-crop
        f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},setsar=1",
        motion_f,
        f"fade=t=in:d={fade_dur},fade=t=out:d={fade_dur}:st={max(0,duration-fade_dur)}",
        f"drawtext={FONT_ARG}text='{sub}':fontsize={font_size}:fontcolor=white:"
        f"bordercolor=black:borderw=3:x=(w-text_w)/2:y=h-{margin_b}:"
        f"box=1:boxcolor=black@0.5:boxborderw=12",
    ])

    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-i", image_path,
        "-i",  audio_path,
        "-vf", vf,
        "-t",  str(duration),
        "-c:v","libx264","-preset","fast","-crf","20",
        "-c:a","aac","-b:a","128k",
        "-pix_fmt","yuv420p","-movflags","+faststart","-r","25",
        out_path
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    if r.returncode == 0 and os.path.exists(out_path):
        return out_path

    # static fallback (no zoompan)
    print(f"   ⚠️  Animation failed, using static render")
    vf_static = (
        f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,"
        f"drawtext={FONT_ARG}text='{sub}':fontsize={font_size}:fontcolor=white:"
        f"bordercolor=black:borderw=3:x=(w-text_w)/2:y=h-{margin_b}:"
        f"box=1:boxcolor=black@0.5:boxborderw=12"
    )
    cmd2 = [
        FFMPEG, "-y",
        "-loop","1","-i", image_path,
        "-i",  audio_path,
        "-vf", vf_static,
        "-t",  str(duration),
        "-c:v","libx264","-preset","fast","-crf","23",
        "-c:a","aac","-b:a","128k",
        "-pix_fmt","yuv420p","-movflags","+faststart",
        out_path
    ]
    subprocess.run(cmd2, capture_output=True)
    return out_path if os.path.exists(out_path) else None


def assemble(clip_paths, out_path):
    if len(clip_paths) == 1:
        shutil.copy2(clip_paths[0], out_path)
        return

    lst = tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                      delete=False, encoding="utf-8")
    for p in clip_paths:
        lst.write(f"file '{p}'\n")
    lst.close()

    cmd = [
        FFMPEG, "-y",
        "-f","concat","-safe","0","-i", lst.name,
        "-c:v","libx264","-preset","fast","-crf","20",
        "-c:a","aac","-b:a","128k",
        "-pix_fmt","yuv420p","-movflags","+faststart",
        out_path
    ]
    subprocess.run(cmd, capture_output=True)
    os.unlink(lst.name)


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    images = get_images()
    n = len(SCENES)
    print(f"Found {len(images)} image(s) for {n} scenes\n")

    tmpdir = tempfile.mkdtemp()
    clips  = []

    try:
        for i, scene in enumerate(SCENES):
            img = images[i % len(images)]
            print(f"Scene {i+1}/{n}: {os.path.basename(img)}")

            # 1. TTS
            audio = os.path.join(tmpdir, f"audio_{i}.mp3")
            print(f"   Generating voiceover...")
            generate_tts(scene["narration"], audio)

            # 2. Render clip
            clip = os.path.join(tmpdir, f"clip_{i}.mp4")
            print(f"   Rendering clip...")
            result = render_clip(img, audio, scene["subtitle"], i, clip)
            if result:
                clips.append(result)
                print(f"   ✅ Done\n")
            else:
                print(f"   ❌ Clip failed, skipping\n")

        if not clips:
            sys.exit("❌ No clips rendered — check FFmpeg is installed")

        print(f"Assembling {len(clips)} clips → {OUTPUT_FILE}")
        assemble(clips, OUTPUT_FILE)

        if os.path.exists(OUTPUT_FILE):
            size_mb = os.path.getsize(OUTPUT_FILE) / (1024*1024)
            print(f"\n✅ Done! viveka_reel.mp4 ({size_mb:.1f} MB)")
            print(f"   Location: {OUTPUT_FILE}")
        else:
            print("❌ Assembly failed")

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()

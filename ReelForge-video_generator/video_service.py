"""
video_service.py — Reliable animated video rendering for ReelForge
Uses simple proven zoompan expressions that work on all FFmpeg versions.
"""

import os
import subprocess
import tempfile
import shutil
import logging
from config import get_ffmpeg_executable

logger = logging.getLogger(__name__)
ffmpeg = get_ffmpeg_executable()

SUBTITLE_COLOURS = {
    "white":   "white",
    "yellow":  "yellow",
    "cyan":    "cyan",
    "gold":    "gold",
    "saffron": "orange",
}

DIMENSIONS = {
    "16:9": (1280, 720),
    "9:16": (720, 1280),
}

# Simple zoompan motion patterns — proven to work across FFmpeg versions
# Each is a (zoom_filter_string) applied after scaling to 2x target size
MOTIONS = [
    # Push in — slow zoom toward centre
    "zoompan=z='min(zoom+0.0008,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d}:s={w}x{h}:fps=25",
    # Pull out — start zoomed, slowly pull back
    "zoompan=z='if(eq(on,1),1.3,max(zoom-0.0008,1.0))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d}:s={w}x{h}:fps=25",
    # Pan left to right while slight push
    "zoompan=z='min(zoom+0.0005,1.2)':x='iw/2-(iw/zoom/2)+on*0.4':y='ih/2-(ih/zoom/2)':d={d}:s={w}x{h}:fps=25",
    # Pan right to left
    "zoompan=z='min(zoom+0.0005,1.2)':x='iw/2-(iw/zoom/2)-on*0.4':y='ih/2-(ih/zoom/2)':d={d}:s={w}x{h}:fps=25",
    # Tilt up (pan upward)
    "zoompan=z='min(zoom+0.0006,1.2)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)+on*0.3':d={d}:s={w}x{h}:fps=25",
    # Diagonal drift
    "zoompan=z='min(zoom+0.0007,1.25)':x='iw/2-(iw/zoom/2)+on*0.3':y='ih/2-(ih/zoom/2)+on*0.2':d={d}:s={w}x{h}:fps=25",
]


def find_font_file():
    """Locate a bold TTF font; drawtext fails on Windows builds without a fontconfig default."""
    candidates = [
        os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", name)
        for name in ("arialbd.ttf", "arial.ttf", "segoeuib.ttf", "segoeui.ttf")
    ] + [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            # FFmpeg filter syntax: forward slashes and an escaped drive colon
            return "fontfile='" + path.replace("\\", "/").replace(":", "\\:") + "':"
    return ""


FONT_OPT = find_font_file()


def get_dimensions(aspect_ratio):
    return DIMENSIONS.get(aspect_ratio, (720, 1280))


def get_audio_duration(audio_path):
    """Get duration of audio file in seconds."""
    try:
        cmd = [ffmpeg, "-i", audio_path]
        res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                             text=True, errors="ignore")
        import re
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if match:
            h, m, s = int(match.group(1)), int(match.group(2)), float(match.group(3))
            return h * 3600 + m * 60 + s
    except Exception:
        pass
    return 5.0


MUSIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "music")
MUSIC_EXTS = (".mp3", ".m4a", ".aac", ".wav", ".ogg")


def list_music_tracks():
    """Background tracks in assets/music, as file names (sorted)."""
    if not os.path.isdir(MUSIC_DIR):
        return []
    return sorted(f for f in os.listdir(MUSIC_DIR) if f.lower().endswith(MUSIC_EXTS))


def resolve_music_track(music_track=None):
    """Path of the requested track; None/'random' picks one at random. None if there are no tracks."""
    import random
    tracks = list_music_tracks()
    if not tracks:
        return None
    if music_track and music_track != "random":
        name = os.path.basename(music_track)
        return os.path.join(MUSIC_DIR, name) if name in tracks else None
    return os.path.join(MUSIC_DIR, random.choice(tracks))


def mix_music_track(video_path, music_path, output_path, duration, music_volume=0.35):
    """
    Lay a music track under the narration: loop/trim it to the video, fade it in
    and out, and duck it (sidechain compression) whenever the voice is speaking.
    """
    fade_out = min(2.5, duration * 0.15)
    graph = (
        f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,"
        f"volume={music_volume},afade=t=in:d=1.0,"
        f"afade=t=out:d={fade_out:.2f}:st={max(0, duration - fade_out):.2f}[music];"
        f"[0:a]aformat=sample_rates=44100:channel_layouts=stereo,asplit=2[voice][key];"
        f"[music][key]sidechaincompress=threshold=0.03:ratio=6:attack=30:release=500[ducked];"
        f"[voice][ducked]amix=inputs=2:duration=first:normalize=0[aout]"
    )
    cmd = [
        ffmpeg, "-y",
        "-i", video_path,
        "-stream_loop", "-1", "-i", music_path,
        "-filter_complex", graph,
        "-map", "0:v", "-map", "[aout]",
        "-t", f"{duration:.3f}",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    if result.returncode != 0:
        logger.warning(f"⚠️ Music track mix failed: {result.stderr[-300:]}")
    return result.returncode == 0 and os.path.exists(output_path)


def generate_ambient_music(duration, output_path):
    """Layered ambient music via FFmpeg sine waves."""
    fade = min(2.0, duration * 0.1)
    fade_out_start = max(0, duration - fade)
    filter_str = (
        "sine=frequency=110:duration={d},"
        "volume=0.04,"
        "afade=t=in:d={fi},"
        "afade=t=out:d={fo}:st={fs}"
    ).format(d=duration, fi=fade, fo=fade, fs=fade_out_start)

    cmd = [
        ffmpeg, "-y",
        "-f", "lavfi", "-i", filter_str,
        "-ar", "44100", "-ac", "2",
        output_path
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path
    except Exception as e:
        logger.warning(f"Music gen failed: {e}")
        return None


def clean_text(text):
    """Strip characters that break FFmpeg filtergraph / drawtext parsing."""
    text = str(text or "").replace("'", "’")
    for ch in "\"\\;[]{}":
        text = text.replace(ch, "")
    text = text.replace(":", " ").replace("%", " percent")
    return " ".join(text.split())


def parse_srt(srt_path):
    """Return a list of (start, end, text) tuples from an SRT file."""
    def to_sec(ts):
        hh, mm, rest = ts.strip().split(":")
        ss, ms = rest.split(",")
        return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000

    entries = []
    try:
        with open(srt_path, encoding="utf-8") as f:
            blocks = f.read().strip().split("\n\n")
        for block in blocks:
            lines = [l for l in block.strip().splitlines() if l.strip()]
            if len(lines) >= 3 and "-->" in lines[1]:
                start, end = lines[1].split("-->")
                entries.append((to_sec(start), to_sec(end), " ".join(lines[2:])))
    except Exception as e:
        logger.warning(f"Could not parse SRT {srt_path}: {e}")
    return entries


def subtitle_filters(entries, colour, font_size, margin_b):
    """One drawtext filter per timed (start, end, text) subtitle chunk."""
    filters = []
    for start, end, text in entries:
        text = clean_text(text)
        if not text:
            continue
        filters.append(
            f"drawtext={FONT_OPT}"
            f"text='{text}':"
            f"fontsize={font_size}:"
            f"fontcolor={colour}:"
            f"bordercolor=black:borderw=3:"
            f"x=(w-text_w)/2:"
            f"y=h-{margin_b}:"
            f"box=1:boxcolor=black@0.45:boxborderw=12:"
            f"enable='between(t,{start:.3f},{end:.3f})'"
        )
    return filters


def overlay_filter(overlay, font_size):
    """Bold yellow text pinned to the top of the frame (e.g. quote attribution)."""
    return (
        f"drawtext={FONT_OPT}"
        f"text='{overlay}':"
        f"fontsize={font_size - 8}:"
        f"fontcolor=yellow:"
        f"bordercolor=black:borderw=2:"
        f"x=(w-text_w)/2:y=50:"
        f"box=1:boxcolor=black@0.4:boxborderw=8"
    )


def render_scene_video_clip(clips, audio_path, output_path, scene_data=None,
                            aspect_ratio="9:16", srt_path=None, duration=None,
                            scene_idx=0, subtitle_color="white", add_text_overlay=True):
    """
    Render one scene from stock video clips and/or photos instead of one still image.
    `clips` is a list of {"path", "duration"[, "kind": "image"]} dicts, one per shot
    (photos get a blurred backdrop and a slow push-in): the scene is cut
    into len(clips) equal shots, each clip scaled to cover the frame and center-
    cropped (so landscape footage fills a 9:16 reel) and looped if shorter than its
    shot. The clips' own audio is replaced by the narration.
    Returns output_path, or None if FFmpeg fails.
    """
    scene_data = scene_data or {}
    w, h = get_dimensions(aspect_ratio)
    duration = (float(duration) if duration else get_audio_duration(audio_path)) + 0.3
    duration = max(3.0, duration)
    shot = duration / len(clips)

    entries = parse_srt(srt_path) if srt_path and os.path.exists(srt_path) else []
    if not entries:
        text = scene_data.get("subtitle_text") or scene_data.get("narration") or ""
        entries = [(0.0, duration, text[:40])] if text else []

    colour = SUBTITLE_COLOURS.get(subtitle_color, "white")
    font_size = 48 if aspect_ratio == "9:16" else 40
    margin_b = 220 if aspect_ratio == "9:16" else 90
    fade_dur = 0.35

    inputs, chains = [], []
    frames = int(round(shot * 25)) + 2
    for i, clip in enumerate(clips):
        if clip.get("kind") == "image":
            # photo: whole picture on a blurred, darkened copy of itself + slow push-in
            inputs += ["-i", clip["path"]]
            chains.append(
                f"[{i}:v]split[bg{i}][fg{i}];"
                f"[bg{i}]scale={w*2}:{h*2}:force_original_aspect_ratio=increase,crop={w*2}:{h*2},"
                f"boxblur=30:2,eq=brightness=-0.18[bgb{i}];"
                f"[fg{i}]scale={w*2}:{h*2}:force_original_aspect_ratio=decrease[fgs{i}];"
                f"[bgb{i}][fgs{i}]overlay=(W-w)/2:(H-h)/2,"
                f"zoompan=z='min(zoom+0.0012,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                f":d={frames}:s={w}x{h}:fps=25,"
                f"setsar=1,format=yuv420p,trim=duration={shot:.3f},setpts=PTS-STARTPTS[v{i}]"
            )
            continue
        # skip the first second of long clips (stock footage often opens on a static frame)
        start = 1.0 if clip.get("duration", 0) > shot + 1.0 else 0.0
        inputs += ["-stream_loop", "-1", "-ss", f"{start:.2f}", "-t", f"{shot + 0.1:.3f}",
                   "-i", clip["path"]]
        chains.append(
            f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
            f"setsar=1,fps=25,format=yuv420p,trim=duration={shot:.3f},setpts=PTS-STARTPTS[v{i}]"
        )
    audio_idx = len(clips)

    post = [f"fade=t=in:d={fade_dur},fade=t=out:d={fade_dur}:st={max(0, duration - fade_dur)}"]
    post += subtitle_filters(entries, colour, font_size, margin_b)
    overlay = clean_text(str(scene_data.get("text_overlay") or "")[:50])
    if overlay and add_text_overlay:
        post.append(overlay_filter(overlay, font_size))

    joined = "".join(f"[v{i}]" for i in range(len(clips)))
    graph = ";".join(chains) + f";{joined}concat=n={len(clips)}:v=1:a=0,{','.join(post)}[vout]"

    cmd = [
        ffmpeg, "-y", *inputs,
        "-i", audio_path,
        "-filter_complex", graph,
        "-map", "[vout]", "-map", f"{audio_idx}:a:0",
        "-af", "apad",
        "-t", f"{duration:.3f}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-r", "25",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    if result.returncode == 0 and os.path.exists(output_path):
        logger.info(f"✅ Scene {scene_idx + 1} stock render OK ({duration:.1f}s, "
                    f"{len(clips)} shots of {shot:.1f}s)")
        return output_path

    logger.warning(f"⚠️ Stock-clip render failed for scene {scene_idx + 1}: {result.stderr[-400:]}")
    return None


def extract_thumbnail(video_path, output_path, at=1.0):
    """Save one frame of a video as a JPEG (used for the scene breakdown in the UI)."""
    cmd = [ffmpeg, "-y", "-ss", str(at), "-i", video_path, "-frames:v", "1",
           "-q:v", "3", output_path]
    subprocess.run(cmd, capture_output=True)
    return output_path if os.path.exists(output_path) else None


def render_scene_clip(image_path, audio_path, scene_data=None, scene_index=None,
                       output_path=None, aspect_ratio="9:16",
                       subtitle_colour=None, add_text_overlay=True,
                       srt_path=None, duration=None, scene_idx=0, subtitle_color="white"):
    """
    Render one scene with Ken Burns animation + subtitles.
    Falls back gracefully if animation filter fails.

    Aliases: scene_idx= for scene_index=, subtitle_color= for subtitle_colour=.
    When srt_path is given, subtitles are shown as timed chunks from the SRT.
    """
    if scene_index is None:
        scene_index = scene_idx
    scene_data = scene_data or {}
    if not output_path:
        raise ValueError("output_path is required")

    w, h = get_dimensions(aspect_ratio)
    duration = (float(duration) if duration else get_audio_duration(audio_path)) + 0.3
    duration = max(3.0, duration)
    frames = int(duration * 25)

    # Pick motion pattern (cycle through them)
    motion_template = MOTIONS[scene_index % len(MOTIONS)]
    motion_filter = motion_template.format(d=frames, w=w, h=h)

    # Subtitle chunks — timed from the SRT, else one short line for the whole scene
    entries = parse_srt(srt_path) if srt_path and os.path.exists(srt_path) else []
    if not entries:
        text = scene_data.get("subtitle_text") or scene_data.get("narration") or ""
        entries = [(0.0, duration, text[:40])] if text else []
    subtitle = clean_text(entries[0][2]) if entries else ""

    colour = SUBTITLE_COLOURS.get(subtitle_colour or subtitle_color, "white")
    font_size = 48 if aspect_ratio == "9:16" else 40
    margin_b = 220 if aspect_ratio == "9:16" else 90

    # Text overlay (e.g. quote attribution)
    overlay = clean_text(str(scene_data.get("text_overlay") or "")[:50])

    # Build filter chain
    # Step 1: scale image to 2× target (zoompan needs room to move)
    scale_filter = f"scale={w*2}:{h*2},setsar=1"

    # Step 2: Ken Burns zoompan
    anim_filter = motion_filter

    # Step 3: Fade in/out
    fade_dur = 0.35
    fade_filter = (
        f"fade=t=in:d={fade_dur},"
        f"fade=t=out:d={fade_dur}:st={max(0, duration - fade_dur)}"
    )

    # Step 4: Subtitles via drawtext, one per timed chunk (+ optional top overlay)
    vf_parts = [scale_filter, anim_filter, fade_filter]
    vf_parts += subtitle_filters(entries, colour, font_size, margin_b)
    if overlay and add_text_overlay:
        vf_parts.append(overlay_filter(overlay, font_size))

    vf = ",".join(vf_parts)

    cmd = [
        ffmpeg, "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-vf", vf,
        "-af", "apad",
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-r", "25",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")

    if result.returncode == 0 and os.path.exists(output_path):
        logger.info(f"✅ Scene {scene_index + 1} animated render OK ({duration:.1f}s)")
        return output_path

    # If animation failed, log the error and try WITHOUT zoompan
    logger.warning(f"⚠️ Animated render failed for scene {scene_index + 1}. Trying static render.")
    logger.warning(f"FFmpeg error: {result.stderr[-400:]}")

    return render_scene_static(image_path, audio_path, duration, output_path,
                                w, h, subtitle, colour, font_size, margin_b)


def render_scene_static(image_path, audio_path, duration, output_path,
                         w, h, subtitle="", colour="white", font_size=36, margin_b=100):
    """Static render with subtitles — fallback if animation fails."""
    subtitle = clean_text(subtitle)

    sub_filter = (
        f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
        f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
        f"drawtext={FONT_OPT}"
        f"text='{subtitle}':"
        f"fontsize={font_size}:"
        f"fontcolor={colour}:"
        f"bordercolor=black:borderw=3:"
        f"x=(w-text_w)/2:y=h-{margin_b}:"
        f"box=1:boxcolor=black@0.45:boxborderw=12"
    )

    cmd = [
        ffmpeg, "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-vf", sub_filter,
        "-af", "apad",
        "-t", str(duration),
        "-r", "25",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    if result.returncode == 0:
        logger.info("✅ Static fallback render OK")
        return output_path

    logger.error(f"❌ Static render also failed:\n{result.stderr[-300:]}")
    return None


def assemble_full_video(clip_paths=None, output_path=None, add_music=True, music_volume=0.12,
                         scene_clips=None, output_video_path=None, total_duration=None,
                         job_dir=None, music_track=None):
    """
    Concatenate all scene clips and optionally mix in background music.
    music_track: a file name in assets/music, or None/'random' for a random track;
    falls back to a generated ambient tone when no tracks are available.

    Aliases: scene_clips= for clip_paths=, output_video_path= for output_path=.
    total_duration and job_dir are accepted for API compatibility.
    """
    clip_paths = [p for p in (clip_paths or scene_clips or []) if p and os.path.exists(p)]
    output_path = output_path or output_video_path
    if not clip_paths:
        raise RuntimeError("No scene clips were rendered — check the FFmpeg errors in the server log")

    if len(clip_paths) == 1:
        shutil.copy2(clip_paths[0], output_path)
        return output_path

    # Write concat list
    concat_list = tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                               delete=False, encoding="utf-8")
    for p in clip_paths:
        concat_list.write(f"file '{os.path.abspath(p).replace(os.sep, '/')}'\n")
    concat_list.close()

    concat_output = output_path.replace(".mp4", "_raw.mp4")

    concat_cmd = [
        ffmpeg, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list.name,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        concat_output
    ]

    result = subprocess.run(concat_cmd, capture_output=True, text=True, errors="ignore")
    os.unlink(concat_list.name)

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg concat failed: {result.stderr[-400:]}")

    logger.info("✅ Clips concatenated")

    if not add_music:
        shutil.move(concat_output, output_path)
        return output_path

    # Get total duration for music
    try:
        probe_cmd = [
            ffmpeg, "-i", concat_output,
            "-f", "null", "-"
        ]
        probe = subprocess.run(probe_cmd, capture_output=True, text=True, errors="ignore")
        import re
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", probe.stderr)
        total_duration = 30.0
        if match:
            total_duration = (int(match.group(1)) * 3600 +
                              int(match.group(2)) * 60 +
                              float(match.group(3)))
    except Exception:
        total_duration = 30.0

    track = resolve_music_track(music_track)
    if track:
        if mix_music_track(concat_output, track, output_path, total_duration):
            logger.info(f"✅ Music track mixed: {os.path.basename(track)}")
            os.unlink(concat_output)
            return output_path
        logger.warning("⚠️ Falling back to generated ambient music")

    music_path = tempfile.NamedTemporaryFile(suffix=".aac", delete=False).name
    music_ok = generate_ambient_music(total_duration, music_path)

    if music_ok and os.path.exists(music_path) and os.path.getsize(music_path) > 100:
        mix_cmd = [
            ffmpeg, "-y",
            "-i", concat_output,
            "-i", music_path,
            "-filter_complex",
            f"[1:a]volume={music_volume}[bg];[0:a][bg]amix=inputs=2:duration=first[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            output_path
        ]
        mix_result = subprocess.run(mix_cmd, capture_output=True, text=True, errors="ignore")
        if mix_result.returncode == 0:
            logger.info("✅ Music mixed into final video")
            os.unlink(concat_output)
            try:
                os.unlink(music_path)
            except Exception:
                pass
            return output_path
        logger.warning("⚠️ Music mix failed — using video without music")

    shutil.move(concat_output, output_path)
    return output_path
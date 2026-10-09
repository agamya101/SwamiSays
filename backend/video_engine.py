"""
Enhanced Video Rendering Service for SwamiSays / Vivekananda Studio:
1. Native 9:16 portrait format (720x1280).
2. Quote scene renders dedicated gold-framed card via quote_card_renderer.
3. Subtitle rendering uses Windows system font 'Nirmala UI' supporting English + Hindi/Devanagari.
4. Smooth camera pan/zoom motion per scene.
5. Soft ambient music ducking underneath narration.
"""
import os
import re
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import imageio_ffmpeg
from quote_card_renderer import render_quote_card_image

logger = logging.getLogger(__name__)

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
WIDTH = 720
HEIGHT = 1280


def generate_ambient_track(duration: float, output_path: str):
    """Generates soothing warm ambient drone using ffmpeg filters."""
    dur_str = f"{max(3.0, duration):.1f}"
    filter_complex = (
        f"anoisesrc=d={dur_str}:c=pink:r=44100:a=0.012,lowpass=f=280[noise];"
        f"sine=f=110:d={dur_str}[n1];"
        f"sine=f=164.81:d={dur_str}[n2];"
        f"[n1][n2]amix=inputs=2:dropout_transition=2[syn];"
        f"[syn]volume=0.04[synv];"
        f"[noise][synv]amix=inputs=2:dropout_transition=2,afade=t=in:ss=0:d=1.0,afade=t=out:st={duration-1.0:.1f}:d=1.0[out]"
    )
    cmd = [
        FFMPEG_PATH, "-y",
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-t", dur_str,
        output_path
    ]
    subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, errors="ignore")


def format_srt_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def create_srt_file(text: str, duration: float, srt_path: str, chunk_words: int = 4):
    words = text.strip().split()
    if not words:
        words = ["..."]

    chunks = []
    for i in range(0, len(words), chunk_words):
        chunks.append(" ".join(words[i:i + chunk_words]))

    chunk_duration = duration / len(chunks)
    entries = []
    for idx, c in enumerate(chunks):
        st = idx * chunk_duration
        et = min(duration, (idx + 1) * chunk_duration)
        entries.append(f"{idx + 1}\n{format_srt_time(st)} --> {format_srt_time(et)}\n{c}\n")

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(entries) + "\n")


def render_scene(
    image_path: str,
    audio_path: str,
    text: str,
    output_clip_path: str,
    duration: float,
    scene_idx: int = 0,
    is_quote_scene: bool = False
) -> bool:
    """Renders a single scene clip with motion, audio, and burned subtitles."""
    work_dir = os.path.dirname(os.path.abspath(output_clip_path))
    os.makedirs(work_dir, exist_ok=True)

    srt_path = os.path.join(work_dir, f"sub_{scene_idx}.srt")
    create_srt_file(text, duration, srt_path)

    # Motion type:
    # Quote scene gets extremely subtle breath zoom to maintain readability.
    # Other scenes get dynamic zoom/pan.
    if is_quote_scene:
        motion = f"zoompan=z='min(zoom+0.0006,1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={WIDTH}x{HEIGHT}:fps=25"
    else:
        motion_idx = scene_idx % 3
        if motion_idx == 0:
            motion = f"zoompan=z='min(zoom+0.0024,1.20)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={WIDTH}x{HEIGHT}:fps=25"
        elif motion_idx == 1:
            motion = f"zoompan=z='if(lte(on,1),1.20,max(1.0,zoom-0.0024))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={WIDTH}x{HEIGHT}:fps=25"
        else:
            motion = f"zoompan=z=1.15:x='min(on*1.5,iw-iw/zoom)':y='ih/2-(ih/zoom/2)':d=1:s={WIDTH}x{HEIGHT}:fps=25"

    rel_img = os.path.basename(image_path)
    rel_audio = os.path.basename(audio_path)
    rel_srt = os.path.basename(srt_path)
    rel_out = os.path.basename(output_clip_path)

    # Subtitle styling with Nirmala UI (renders Devanagari + Latin cleanly)
    # Quote scene doesn't burn redundant subtitles since text is already on the card!
    if is_quote_scene:
        vf = motion
    else:
        sub_style = (
            "FontName=Nirmala UI,FontSize=24,Bold=1,"
            "PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,"
            "BorderStyle=3,Outline=2.5,Shadow=1.5,Alignment=2,MarginV=140"
        )
        vf = f"{motion},subtitles={rel_srt}:force_style='{sub_style}'"

    cmd = [
        FFMPEG_PATH, "-y",
        "-loop", "1", "-i", rel_img,
        "-i", rel_audio,
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-t", f"{duration:.3f}",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        rel_out
    ]

    res = subprocess.run(cmd, cwd=work_dir, capture_output=True, text=True, errors="ignore")
    if res.returncode != 0:
        logger.warning(f"Scene render error with subtitles, falling back without srt: {res.stderr[-200:]}")
        fb_cmd = [
            FFMPEG_PATH, "-y",
            "-loop", "1", "-i", rel_img,
            "-i", rel_audio,
            "-vf", motion,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-t", f"{duration:.3f}",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            rel_out
        ]
        fb_res = subprocess.run(fb_cmd, cwd=work_dir, capture_output=True, text=True, errors="ignore")
        return fb_res.returncode == 0
    return True


def assemble_reel(
    clip_paths: List[str],
    output_video_path: str,
    total_duration: float,
    add_music: bool = True
) -> str:
    """Concatenates scene clips, mixes soft ambient background music, and outputs optimized MP4."""
    if not clip_paths:
        raise ValueError("No clip paths provided")

    work_dir = os.path.dirname(os.path.abspath(output_video_path))
    os.makedirs(work_dir, exist_ok=True)

    concat_file = os.path.join(work_dir, "concat.txt")
    with open(concat_file, "w", encoding="utf-8") as f:
        for c in clip_paths:
            f.write(f"file '{os.path.abspath(c).replace(os.sep, '/')}'\n")

    joined_tmp = os.path.join(work_dir, "joined_tmp.mp4")
    concat_cmd = [
        FFMPEG_PATH, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        joined_tmp
    ]
    subprocess.run(concat_cmd, cwd=work_dir, capture_output=True, errors="ignore")

    if add_music and total_duration > 2.0:
        bgm_path = os.path.join(work_dir, "ambient.mp3")
        generate_ambient_track(total_duration, bgm_path)
        if os.path.exists(bgm_path):
            mix_cmd = [
                FFMPEG_PATH, "-y",
                "-i", joined_tmp,
                "-i", bgm_path,
                "-filter_complex", "[1:a]volume=0.06[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-movflags", "+faststart",
                output_video_path
            ]
            res = subprocess.run(mix_cmd, cwd=work_dir, capture_output=True, errors="ignore")
            if res.returncode == 0 and os.path.exists(output_video_path):
                return output_video_path

    # Fallback without music
    final_cmd = [
        FFMPEG_PATH, "-y",
        "-i", joined_tmp,
        "-c", "copy",
        "-movflags", "+faststart",
        output_video_path
    ]
    subprocess.run(final_cmd, capture_output=True, errors="ignore")
    return output_video_path

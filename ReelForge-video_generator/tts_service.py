import os
import re
import asyncio
import subprocess
from config import FFMPEG_PATH

# ---------------------------------------------------------------------------
# TTS backend selection
# Edge-TTS requires speech.platform.bing.com:443 — blocked on some networks.
# gTTS uses Google TTS (api.soundoftext.com / translate.google.com) — more
# reliable on restricted WiFi.  Install with: pip install gTTS
# We try gTTS first; fall back to edge_tts if gTTS is unavailable.
# ---------------------------------------------------------------------------

def _try_import_gtts():
    try:
        from gtts import gTTS
        return gTTS
    except ImportError:
        return None

def _try_import_edge():
    try:
        import edge_tts
        return edge_tts
    except ImportError:
        return None


def get_audio_duration(audio_path: str) -> float:
    """Extracts exact duration in seconds from an audio file using FFmpeg."""
    cmd = [FFMPEG_PATH, "-i", audio_path]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                         text=True, errors="ignore")
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if match:
        hours   = int(match.group(1))
        minutes = int(match.group(2))
        seconds = float(match.group(3))
        return hours * 3600 + minutes * 60 + seconds
    return 4.0  # safe default fallback


# ── gTTS backend ────────────────────────────────────────────────────────────

# Edge voice locale → (gTTS lang, Google TLD for the accent)
GTTS_LOCALES = {
    "en-US": ("en", "com"),
    "en-GB": ("en", "co.uk"),
    "en-IN": ("en", "co.in"),
    "en-AU": ("en", "com.au"),
    "es-ES": ("es", "es"),
    "fr-FR": ("fr", "fr"),
    "de-DE": ("de", "de"),
    "ja-JP": ("ja", "co.jp"),
}


def _gtts_locale(voice_id: str):
    locale = "-".join((voice_id or "en-US").split("-")[:2])
    return GTTS_LOCALES.get(locale, ("en", "com"))


def _generate_with_gtts(text: str, output_path: str, voice_id: str = None) -> bool:
    """Generate speech using Google TTS. Returns True on success."""
    gTTS = _try_import_gtts()
    if gTTS is None:
        return False
    try:
        lang, tld = _gtts_locale(voice_id)
        tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
        tts.save(output_path)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 500
    except Exception as e:
        print(f"[tts] gTTS failed: {e}")
        return False


# ── Edge-TTS backend ─────────────────────────────────────────────────────────

async def _generate_speech_async(text: str, voice_id: str, output_path: str,
                                  rate: str = "+0%", pitch: str = "+0Hz"):
    """Asynchronously generates speech using Microsoft Edge-TTS."""
    edge_tts = _try_import_edge()
    if edge_tts is None:
        raise RuntimeError("edge_tts not installed")
    communicate = edge_tts.Communicate(text, voice_id, rate=rate, pitch=pitch)
    await communicate.save(output_path)


def _generate_with_edge(text: str, voice_id: str, output_path: str) -> bool:
    """Generate speech using Edge-TTS. Returns True on success."""
    if _try_import_edge() is None:
        return False
    try:
        asyncio.run(_generate_speech_async(text, voice_id, output_path))
        return os.path.exists(output_path) and os.path.getsize(output_path) > 500
    except Exception as e:
        print(f"[tts] Edge-TTS failed: {e}")
        return False


# ── Silent fallback ──────────────────────────────────────────────────────────

def _generate_silence(duration: float, output_path: str) -> bool:
    """Generate a silent audio file via FFmpeg as absolute last resort."""
    try:
        cmd = [
            FFMPEG_PATH, "-y",
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-t", str(duration),
            "-c:a", "libmp3lame", "-b:a", "64k",
            output_path
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except Exception as e:
        print(f"[tts] Silence fallback failed: {e}")
        return False


# ── Public API ───────────────────────────────────────────────────────────────

def generate_scene_audio(text: str = None, voice_id: str = "en-US-ChristopherNeural",
                         output_path: str = None, narration: str = None, voice: str = None,
                         output_file: str = None, audio_path: str = None) -> float:
    """
    Synchronous wrapper to generate scene audio and return exact duration.
    Priority: gTTS → Edge-TTS → silence fallback.

    Aliases: narration= for text=, voice= for voice_id=, output_file=/audio_path= for output_path=.
    """
    text = text or narration or ""
    voice_id = voice or voice_id
    output_path = output_path or output_file or audio_path
    if not output_path:
        raise ValueError("output_path is required")

    # Clean text of markdown / special symbols
    clean_text = re.sub(r"[*_~`#\[\]]", "", text).strip()
    if not clean_text:
        clean_text = "Arise, awake, and stop not till the goal is reached."

    # 1. Try gTTS (works on restricted networks)
    if _generate_with_gtts(clean_text, output_path, voice_id):
        print("[tts] [OK] gTTS succeeded")
        return get_audio_duration(output_path)

    # 2. Try Edge-TTS
    if _generate_with_edge(clean_text, voice_id, output_path):
        print("[tts] [OK] Edge-TTS succeeded")
        return get_audio_duration(output_path)

    # 3. Silent fallback (video still renders, just no voiceover)
    print("[tts] [WARN] All TTS failed — generating silence")
    estimated = max(4.0, len(clean_text.split()) * 0.45)
    _generate_silence(estimated, output_path)
    return estimated


# ── Subtitle generation (unchanged) ─────────────────────────────────────────

def format_srt_time(seconds: float) -> str:
    """Format seconds into HH:MM:SS,mmm string for SRT format."""
    hrs    = int(seconds // 3600)
    mins   = int((seconds % 3600) // 60)
    secs   = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def generate_scene_srt(text: str, duration: float, output_srt_path: str,
                        max_chars_per_chunk: int = 40):
    """
    Splits scene text into timed subtitle chunks for high readability.
    Breaks into 3-word phrases timed across the scene duration.
    """
    words = text.strip().split()
    if not words:
        words = ["..."]

    chunk_size = 3
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))

    chunk_duration = duration / len(chunks)

    srt_entries = []
    for idx, chunk in enumerate(chunks):
        start_t = idx * chunk_duration
        end_t   = min(duration, (idx + 1) * chunk_duration)
        srt_entries.append(
            f"{idx + 1}\n{format_srt_time(start_t)} --> {format_srt_time(end_t)}\n{chunk}\n"
        )

    with open(output_srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries) + "\n")
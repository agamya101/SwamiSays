"""
SQLite Database for SOS Reel History:
Persists past prompts, user profile (name, age, profession), verified teachings,
full transcripts, and generated MP4 reel videos isolated by client device_id.
"""
import sqlite3
import json
import uuid
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

DB_PATH = Path(__file__).resolve().parent / "data" / "history.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reel_history (
        id TEXT PRIMARY KEY,
        device_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        prompt TEXT NOT NULL,
        name TEXT,
        age INTEGER,
        profession TEXT,
        lang TEXT NOT NULL DEFAULT 'en',
        journey TEXT NOT NULL,
        lesson_id INTEGER NOT NULL,
        quote_id TEXT NOT NULL,
        quote_text TEXT NOT NULL,
        quote_source TEXT NOT NULL,
        transcript TEXT NOT NULL,
        scenes_json TEXT NOT NULL,
        job_id TEXT,
        video_url TEXT,
        status TEXT NOT NULL DEFAULT 'pending'
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_device_id ON reel_history (device_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_id ON reel_history (job_id);")
    
    # Graceful column migrations
    try:
        cursor.execute("ALTER TABLE reel_history ADD COLUMN api_model TEXT DEFAULT 'gemini-2.5-flash';")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE reel_history ADD COLUMN api_verified INTEGER DEFAULT 1;")
    except Exception:
        pass

    conn.commit()
    conn.close()


init_db()


def add_history_entry(
    device_id: str,
    prompt: str,
    name: str = "",
    age: Optional[int] = None,
    profession: str = "",
    lang: str = "en",
    journey: str = "Focus",
    lesson_id: int = 3,
    quote_id: str = "q1",
    quote_text: str = "",
    quote_source: str = "",
    transcript: str = "",
    scenes: List[Dict[str, Any]] = None,
    job_id: Optional[str] = None,
    video_url: Optional[str] = None,
    status: str = "pending",
    api_model: str = "gemini-2.5-flash",
    api_verified: bool = True
) -> Dict[str, Any]:
    entry_id = str(uuid.uuid4())
    created_at = datetime.datetime.utcnow().isoformat() + "Z"
    scenes_json = json.dumps(scenes or [], ensure_ascii=False)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reel_history (
            id, device_id, created_at, prompt, name, age, profession,
            lang, journey, lesson_id, quote_id, quote_text, quote_source,
            transcript, scenes_json, job_id, video_url, status, api_model, api_verified
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entry_id, device_id, created_at, prompt, name or "", age, profession or "",
        lang, journey, lesson_id, quote_id, quote_text, quote_source,
        transcript, scenes_json, job_id, video_url, status,
        api_model, 1 if api_verified else 0
    ))
    conn.commit()
    conn.close()

    return {
        "id": entry_id,
        "device_id": device_id,
        "created_at": created_at,
        "prompt": prompt,
        "name": name,
        "age": age,
        "profession": profession,
        "lang": lang,
        "journey": journey,
        "lesson_id": lesson_id,
        "quote_id": quote_id,
        "quote_text": quote_text,
        "quote_source": quote_source,
        "transcript": transcript,
        "scenes": scenes or [],
        "job_id": job_id,
        "video_url": video_url,
        "status": status,
        "api_model": api_model,
        "api_verified": api_verified
    }


def update_history_video(job_id: str, video_url: str, status: str = "completed"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reel_history
        SET video_url = ?, status = ?
        WHERE job_id = ?
    """, (video_url, status, job_id))
    conn.commit()
    conn.close()


def get_history(device_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM reel_history
        WHERE device_id = ?
        ORDER BY created_at DESC
    """, (device_id,))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        item = dict(r)
        try:
            item["scenes"] = json.loads(item["scenes_json"])
        except Exception:
            item["scenes"] = []
        del item["scenes_json"]
        results.append(item)
    return results


def get_history_entry(entry_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reel_history WHERE id = ?", (entry_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None
    item = dict(row)
    try:
        item["scenes"] = json.loads(item["scenes_json"])
    except Exception:
        item["scenes"] = []
    del item["scenes_json"]
    return item


def delete_history_entry(entry_id: str, device_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reel_history WHERE id = ? AND device_id = ?", (entry_id, device_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def clear_history(device_id: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reel_history WHERE device_id = ?", (device_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected

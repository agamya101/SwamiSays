"""
Quote verification and registry.
Every quote MUST be a verbatim substring of a chunk in vivekananda_rag_ready.jsonl.
"""
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

CORPUS_PATH = Path(__file__).resolve().parent.parent / "data" / "vivekananda_rag_ready.jsonl"

_CORPUS_INDEX: Optional[Dict[str, Dict[str, Any]]] = None


def normalize_text(text: str) -> str:
    """Case-fold, collapse whitespace, strip punctuation for fuzzy-free exact comparison."""
    text = text.lower()
    text = re.sub(r"[’‘'`]", "'", text)
    text = re.sub(r'[""“”]', '"', text)
    text = re.sub(r"[—–]", " - ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def load_corpus() -> Dict[str, Dict[str, Any]]:
    global _CORPUS_INDEX
    if _CORPUS_INDEX is not None:
        return _CORPUS_INDEX
    idx = {}
    if CORPUS_PATH.exists():
        with open(CORPUS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                idx[row["chunk_id"]] = row
    _CORPUS_INDEX = idx
    return idx


def verify_quote(quote_text: str, chunk_id: str) -> bool:
    """Returns True if normalized quote_text appears verbatim in normalized chunk text."""
    corpus = load_corpus()
    chunk = corpus.get(chunk_id)
    if not chunk:
        return False
    return normalize_text(quote_text) in normalize_text(chunk.get("text", ""))


# Canonical quote bank covering the 8 journeys.
# Every entry is an EXACT verbatim substring of the given chunk_id.
VERIFIED_QUOTES: List[Dict[str, Any]] = [
    # Journey 1: Fearlessness
    {
        "id": "q1",
        "lessonId": 1,
        "text": "If there is one word that you find coming out like a bomb from the Upanishads, bursting like a bomb-shell upon masses of ignorance, it is the word fearlessness.",
        "chunk_id": "cwsv_0001276",
        "topics": ["fear", "anxiety", "judged", "courage", "overthinking", "fearlessness"]
    },
    {
        "id": "q2",
        "lessonId": 1,
        "text": "A man must go about his duties without taking notice of the sneers and the ridicule of the world.",
        "chunk_id": "cwsv_0000047",
        "topics": ["fear", "hesitation", "judgment", "boldness", "ridicule", "opinion"]
    },

    # Journey 2: Self-Faith
    {
        "id": "q3",
        "lessonId": 2,
        "text": "All power is within you; you can do anything and everything.",
        "chunk_id": "cwsv_0001415",
        "topics": ["confidence", "self-doubt", "imposter", "power", "self-faith"]
    },
    {
        "id": "q4",
        "lessonId": 2,
        "text": "You cannot believe in God until you believe in yourself.",
        "chunk_id": "cwsv_0002620",
        "topics": ["faith", "self-belief", "identity", "insecurity", "trust"]
    },

    # Journey 3: Focus
    {
        "id": "q5",
        "lessonId": 3,
        "text": "To me the very essence of education is concentration of mind, not the collecting of facts.",
        "chunk_id": "cwsv_0002782",
        "topics": ["focus", "concentration", "attention", "learning", "distraction"]
    },
    {
        "id": "q6",
        "lessonId": 3,
        "text": "How has all the knowledge in the world been gained but by the concentration of the powers of the mind?",
        "chunk_id": "cwsv_0000134",
        "topics": ["focus", "overthinking", "powers of mind", "deep work", "mental clarity"]
    },

    # Journey 4: Purpose / One Idea
    {
        "id": "q7",
        "lessonId": 4,
        "text": "Make that one idea your life — think of it, dream of it, live on that idea.",
        "chunk_id": "cwsv_0000190",
        "topics": ["purpose", "direction", "career", "confusion", "one idea", "dedication"]
    },
    {
        "id": "q8",
        "lessonId": 4,
        "text": "Awake, arise, and stop not till the goal is reached!",
        "chunk_id": "cwsv_0000477",
        "topics": ["purpose", "goal", "persistence", "action", "destiny"]
    },

    # Journey 5: Persistence
    {
        "id": "q9",
        "lessonId": 5,
        "text": "Never mind failures; they are quite natural, they are the beauty of life, these failures.",
        "chunk_id": "cwsv_0000691",
        "topics": ["failure", "setbacks", "quitting", "rejection", "persistence", "mistakes"]
    },
    {
        "id": "q9b",
        "lessonId": 5,
        "text": "Purity, patience, and perseverance are the three essentials to success and, above all, love.",
        "chunk_id": "cwsv_0003029",
        "topics": ["patience", "perseverance", "effort", "slow progress", "consistency"]
    },

    # Journey 6: Strength
    {
        "id": "q10",
        "lessonId": 6,
        "text": "Strength is life, weakness is death.",
        "chunk_id": "cwsv_0002548",
        "topics": ["strength", "burnout", "weakness", "resilience", "energy"]
    },
    {
        "id": "q11",
        "lessonId": 6,
        "text": "Anything that makes you weak physically, intellectually, and spiritually, reject as poison; there is no life in it, it cannot be true.",
        "chunk_id": "cwsv_0001350",
        "topics": ["toxic habits", "burnout", "mental health", "boundaries", "poison"]
    },

    # Journey 7: Self-Mastery
    {
        "id": "q12",
        "lessonId": 7,
        "text": "Therefore it is necessary that Kriya-yoga should be constantly practised, in order to gain control of the mind, and bring it into subjection.",
        "chunk_id": "cwsv_0000251",
        "topics": ["self-control", "mind", "habits", "discipline", "impulses"]
    },
    {
        "id": "q13",
        "lessonId": 7,
        "text": "Take the whole responsibility on your own shoulders, and know that you are the creator of your own destiny.",
        "chunk_id": "cwsv_0000776",
        "topics": ["responsibility", "ownership", "comparison", "jealousy", "destiny"]
    },

    # Journey 8: Service
    {
        "id": "q14",
        "lessonId": 8,
        "text": "They alone live who live for others, the rest are more dead than alive.",
        "chunk_id": "cwsv_0002056",
        "topics": ["service", "meaning", "emptiness", "compassion", "contribution"]
    },
    {
        "id": "q15",
        "lessonId": 8,
        "text": "Where should you go to seek for God — are not all the poor, the miserable, the weak, Gods? Why not worship them first?",
        "chunk_id": "cwsv_0002252",
        "topics": ["service", "god in others", "kindness", "ego", "purpose"]
    }
]


def get_quote_by_id(quote_id: str) -> Optional[Dict[str, Any]]:
    for q in VERIFIED_QUOTES:
        if q["id"] == quote_id:
            return enrich_quote(q)
    return None


def get_quotes_for_lesson(lesson_id: int) -> List[Dict[str, Any]]:
    return [enrich_quote(q) for q in VERIFIED_QUOTES if q.get("lessonId") == lesson_id]


def format_multiline_source(source_info: Dict[str, Any], raw_citation: str = "") -> str:
    """Formats quote source into multiple clean lines, perfectly fitted for 9:16 vertical ratio."""
    toc = source_info.get("toc_path") or []
    pub = source_info.get("publisher") or "Advaita Ashrama"
    lines = ["Swami Vivekananda, Complete Works"]
    if len(toc) >= 3:
        lines.append(f"{toc[0]}")
        lines.append(f"{toc[1]}")
        lines.append(f"→ {toc[2]}")
    elif len(toc) == 2:
        lines.append(f"{toc[0]}")
        lines.append(f"→ {toc[1]}")
    elif source_info.get("volume") and source_info.get("section"):
        lines.append(f"{source_info.get('volume')}")
        lines.append(f"→ {source_info.get('section')}")
    elif raw_citation:
        parts = [p.strip() for p in raw_citation.split(" → ")]
        if len(parts) > 1:
            clean_part0 = parts[0].replace("Swami Vivekananda, ", "").replace("The Complete Works of Swami Vivekananda, ", "")
            lines.append(clean_part0)
            clean_part1 = parts[1].replace(", Advaita Ashrama.", "").replace(", Advaita Ashrama", "")
            lines.append(f"→ {clean_part1}")
        else:
            lines.append(raw_citation)

    if pub not in lines[-1]:
        lines.append(pub)

    return "\n".join(lines)


def enrich_quote(q: Dict[str, Any]) -> Dict[str, Any]:
    """Attaches real metadata from the corpus: citation, volume, section, locator, verified boolean."""
    corpus = load_corpus()
    chunk = corpus.get(q["chunk_id"], {})
    source_info = chunk.get("source", {})
    verified = verify_quote(q["text"], q["chunk_id"])

    multiline_citation = format_multiline_source(source_info, source_info.get("citation", ""))
    single_citation = source_info.get("citation") or " ".join(multiline_citation.splitlines())

    return {
        "id": q["id"],
        "text": q["text"],
        "source": multiline_citation,
        "source_single": single_citation,
        "sourceUrl": "https://www.ramakrishnavivekananda.info/vivekananda/complete_works.htm",
        "verified": verified,
        "topics": q.get("topics", []),
        "chunk_id": q["chunk_id"],
        "volume": source_info.get("volume", ""),
        "section": source_info.get("section", ""),
        "epub_locator": source_info.get("epub_locator", ""),
        "lessonId": q.get("lessonId", 1)
    }


def get_all_enriched_quotes() -> List[Dict[str, Any]]:
    return [enrich_quote(q) for q in VERIFIED_QUOTES]

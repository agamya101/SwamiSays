"""
Hybrid 8-Journey Classifier:
1. Crisis gate: checks safety first.
2. Embedding cosine similarity against curated seeds (English + Hindi + Hinglish).
3. Keyword boost for unambiguous terms.
4. Confidence check: flags 'clarify=True' if top-1 and top-2 are close.
"""
import json
import re
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np

SEEDS_PATH = Path(__file__).resolve().parent / "data" / "journey_seeds.json"

_SEEDS_DATA: Optional[Dict[str, Any]] = None
_MODEL = None
_SEED_EMBEDDINGS: Optional[Dict[int, np.ndarray]] = None

CRISIS_PATTERNS = [
    re.compile(r"\bsuicid(e|al)\b", re.I),
    re.compile(r"\bkill\s+(my\s*self|me)\b", re.I),
    re.compile(r"\bend\s+(my\s*life|it\s*all)\b", re.I),
    re.compile(r"\bself[\s-]*harm\b", re.I),
    re.compile(r"\bwant\s+to\s+die\b", re.I),
    re.compile(r"\bno\s+reason\s+to\s+live\b", re.I),
    re.compile(r"\bhurt(ing)?\s+myself\b", re.I),
    re.compile(r"\bcut(ting)?\s+my\s*wrists?\b", re.I),
    re.compile(r"\bmar\s+jaana\s+chahta\b", re.I),
    re.compile(r"\bjaan\s+de\s+du\b", re.I)
]


def check_crisis(text: str) -> bool:
    if not text:
        return False
    return any(p.search(text) for p in CRISIS_PATTERNS)


def load_seeds() -> Dict[str, Any]:
    global _SEEDS_DATA
    if _SEEDS_DATA is None:
        with open(SEEDS_PATH, "r", encoding="utf-8") as f:
            _SEEDS_DATA = json.load(f)["journeys"]
    return _SEEDS_DATA


def get_model():
    """Lazy-load sentence-transformers model. Falls back gracefully if unavailable."""
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    try:
        from sentence_transformers import SentenceTransformer
        # Fast, robust, multilingual-friendly
        model_name = os.environ.get("EMBED_MODEL", "all-MiniLM-L6-v2")
        _MODEL = SentenceTransformer(model_name)
        return _MODEL
    except Exception as e:
        # Graceful fallback: return None, classifier will use keyword scoring
        return None


def get_seed_embeddings() -> Optional[Dict[int, np.ndarray]]:
    global _SEED_EMBEDDINGS
    if _SEED_EMBEDDINGS is not None:
        return _SEED_EMBEDDINGS
    model = get_model()
    if model is None:
        return None
    seeds = load_seeds()
    out = {}
    for j_id_str, j_data in seeds.items():
        j_id = int(j_id_str)
        seed_texts = j_data["seeds"]
        embs = model.encode(seed_texts, normalize_embeddings=True)
        out[j_id] = embs
    _SEED_EMBEDDINGS = out
    return _SEED_EMBEDDINGS


def keyword_score(text: str) -> Dict[int, float]:
    clean = " " + re.sub(r"[^a-z0-9\s]", " ", text.lower()) + " "
    seeds = load_seeds()
    scores = {int(k): 0.0 for k in seeds.keys()}
    for j_id_str, j_data in seeds.items():
        j_id = int(j_id_str)
        for kw in j_data["keywords"]:
            pattern = r"\b" + re.escape(kw.lower()) + r"\b"
            if re.search(pattern, clean):
                # Multi-word keywords get higher weight
                scores[j_id] += 1.5 if " " in kw else 1.0
    return scores


def classify_dilemma(text: str) -> Dict[str, Any]:
    """
    Classifies a user dilemma into 1 of the 8 journeys.
    Returns:
        {
          "lessonId": 3,
          "journey": "Focus",
          "confidence": 0.88,
          "clarify": False,
          "alternatives": [{"lessonId": 4, "journey": "Purpose", "score": 0.45}],
          "isCrisis": False
        }
    """
    if check_crisis(text):
        return {
            "lessonId": 6,
            "journey": "Strength",
            "confidence": 1.0,
            "clarify": False,
            "alternatives": [],
            "isCrisis": True
        }

    seeds = load_seeds()
    kw_scores = keyword_score(text)

    # Embedding similarity
    model = get_model()
    seed_embs = get_seed_embeddings()

    emb_scores = {int(k): 0.0 for k in seeds.keys()}
    if model is not None and seed_embs is not None:
        try:
            q_emb = model.encode([text], normalize_embeddings=True)[0]
            for j_id, embs in seed_embs.items():
                sims = np.dot(embs, q_emb)
                # Max-sim + mean of top-3 sims
                top3 = np.sort(sims)[-3:]
                emb_scores[j_id] = float(0.6 * top3[-1] + 0.4 * np.mean(top3))
        except Exception:
            pass

    # Combine: normalize both to [0, 1] then blend
    max_kw = max(kw_scores.values()) if kw_scores else 0.0
    combined = {}
    for j_id in seeds.keys():
        j_id = int(j_id)
        norm_kw = (kw_scores[j_id] / max_kw) if max_kw > 0 else 0.0
        # If model available: 60% embedding, 40% keyword; else 100% keyword
        if model is not None:
            c = 0.65 * emb_scores[j_id] + 0.35 * norm_kw
        else:
            c = norm_kw
        combined[j_id] = c

    # Rank
    ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)
    best_id, best_score = ranked[0]
    second_id, second_score = ranked[1] if len(ranked) > 1 else (best_id, 0.0)

    # If keyword had zero hits and score is very low, fall back to Focus
    if best_score < 0.15 and max_kw == 0.0:
        best_id = 3

    # Need clarification if top-2 are very close and reasonably high
    clarify = (best_score > 0.3) and ((best_score - second_score) < 0.08)

    best_journey = seeds[str(best_id)]["name"]
    second_journey = seeds[str(second_id)]["name"]

    alts = [
        {"lessonId": r[0], "journey": seeds[str(r[0])]["name"], "score": round(float(r[1]), 3)}
        for r in ranked[1:3]
    ]

    return {
        "lessonId": best_id,
        "journey": best_journey,
        "confidence": round(float(best_score), 3),
        "clarify": clarify,
        "alternatives": alts,
        "isCrisis": False
    }

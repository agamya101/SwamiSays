import pytest
from quotes import VERIFIED_QUOTES, verify_quote, get_all_enriched_quotes, get_quote_by_id

def test_all_quotes_verify_verbatim():
    """CRITICAL: Every single quote MUST pass verbatim check against vivekananda_rag_ready.jsonl."""
    quotes = get_all_enriched_quotes()
    assert len(quotes) >= 15, "Expected at least 15 quotes in bank"
    failed = []
    for q in quotes:
        if not q["verified"]:
            failed.append(f"{q['id']}: '{q['text'][:50]}...' in {q['chunk_id']}")
    assert not failed, f"The following quotes failed verbatim verification: {failed}"

def test_all_eight_lessons_covered():
    quotes = get_all_enriched_quotes()
    covered_lessons = {q["lessonId"] for q in quotes}
    for lesson_id in range(1, 9):
        assert lesson_id in covered_lessons, f"Lesson {lesson_id} has no verified quotes"

def test_verify_rejects_hallucinations():
    fake = "Fear is the mother of all modern AI illusions."
    assert not verify_quote(fake, "cwsv_0001276")

def test_enrichment_has_real_citation():
    q = get_quote_by_id("q1")
    assert q is not None
    assert "Complete Works" in q["source"]
    assert q["chunk_id"] == "cwsv_0001276"
    assert q["verified"] is True

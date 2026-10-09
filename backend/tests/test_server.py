import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["journeys"] == 8

def test_get_lessons():
    res = client.get("/api/lessons")
    assert res.status_code == 200
    lessons = res.json()
    assert len(lessons) == 8
    slugs = [l["slug"] for l in lessons]
    assert "fearlessness" in slugs
    assert "focus" in slugs
    assert "service" in slugs

def test_get_episodes():
    res = client.get("/api/episodes?lessonId=3")
    assert res.status_code == 200
    eps = res.json()
    assert len(eps) == 6
    for e in eps:
        assert e["lessonId"] == 3

def test_daily_quote():
    res = client.get("/api/quote/daily")
    assert res.status_code == 200
    q = res.json()
    assert q["verified"] is True
    assert "Complete Works" in q["source"]

def test_generate_reel_focus_spec():
    """Test user's exact example: 'I keep checking Instagram while studying and can't concentrate'"""
    payload = {
        "prompt": "I keep checking Instagram while studying and can't concentrate.",
        "name": "Arjun",
        "age": 19,
        "profession": "Student",
        "lang": "en",
        "render_video": False
    }
    res = client.post("/api/reel", json=payload)
    assert res.status_code == 200
    data = res.json()

    # Must classify into Focus (Lesson 3)
    assert data["lessonId"] == 3
    assert data["journey"] == "Focus"

    # Must inject a verified quote
    assert data["quote"]["verified"] is True
    assert data["quoteId"] in ["q5", "q6"]

    # Must have all required scenes
    scene_types = [s["type"] for s in data["scenes"]]
    assert "hook" in scene_types
    assert "situation" in scene_types
    assert "quote" in scene_types
    assert "meaning" in scene_types
    assert "action" in scene_types
    assert "outro" in scene_types

    # Quote scene text must contain the verified quote text
    quote_scene = next(s for s in data["scenes"] if s["type"] == "quote")
    assert data["quote"]["text"] in quote_scene["text"]

    # Disclaimer must clearly distinguish AI from authentic quote
    assert "AI-generated" in data["disclaimer"]
    assert "authentic and verified" in data["disclaimer"]

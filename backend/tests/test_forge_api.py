import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_forge_status():
    res = client.get("/api/forge/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert "voices" in data
    assert "stock_categories" in data
    assert data["total_clips"] >= 50
    assert "music_tracks" in data
    assert "figures" in data
    assert "vivekananda" in data["figures"]

def test_forge_templates():
    res = client.get("/api/forge/templates")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 4
    ids = [t["id"] for t in data]
    assert "vivekananda" in ids
    assert "focus" in ids

def test_forge_showcase():
    res = client.get("/api/forge/showcase")
    assert res.status_code == 200
    data = res.json()
    assert "title" in data
    assert data["videoUrl"] is not None

def test_forge_job_not_found():
    res = client.get("/api/forge/job/nonexistent_12345")
    assert res.status_code == 200
    data = res.json()
    assert data["completed"] is False

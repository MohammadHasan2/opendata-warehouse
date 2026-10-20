import sys
from pathlib import Path

from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["database"] == "connected"


def test_overview():
    response = client.get("/api/overview")

    assert response.status_code == 200

    data = response.json()
    assert "repository_count" in data
    assert "total_stars" in data
    assert "total_forks" in data
    assert "total_open_issues" in data


def test_languages():
    response = client.get("/api/languages")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_repository_pagination():
    response = client.get(
        "/api/repositories",
        params={"page": 1, "page_size": 5},
    )

    assert response.status_code == 200

    result = response.json()
    assert len(result["data"]) <= 5
    assert result["pagination"]["page"] == 1
    assert result["pagination"]["page_size"] == 5
    assert result["pagination"]["total"] >= len(result["data"])


def test_repository_language_filter():
    response = client.get(
        "/api/repositories",
        params={"language": "Python", "page_size": 100},
    )

    assert response.status_code == 200

    result = response.json()

    for repository in result["data"]:
        assert repository["language"].lower() == "python"


def test_invalid_page_is_rejected():
    response = client.get(
        "/api/repositories",
        params={"page": 0},
    )

    assert response.status_code == 422


def test_invalid_page_size_is_rejected():
    response = client.get(
        "/api/repositories",
        params={"page_size": 101},
    )

    assert response.status_code == 422

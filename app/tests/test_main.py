"""Tests for the URL Shortener API."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_redis():
    """Create a mock Redis client and patch it into the app module."""
    with patch("app.main.redis_client") as mock_client:
        mock_client.ping.return_value = True
        mock_client.exists.return_value = False
        yield mock_client


@pytest.fixture
def client(mock_redis):
    """Create a test client with mocked Redis."""
    from app.main import app

    return TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_ok(self, client, mock_redis):
        """Health endpoint returns ok status with Redis connected."""
        mock_redis.ping.return_value = True
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["redis"] == "connected"


class TestShortenEndpoint:
    """Tests for POST /shorten."""

    def test_shorten_returns_6_char_code(self, client, mock_redis):
        """Shorten endpoint returns a 6-character alphanumeric code."""
        mock_redis.exists.return_value = False
        mock_redis.set.return_value = True

        response = client.post("/shorten", json={"url": "https://example.com"})
        assert response.status_code == 201
        data = response.json()
        assert "short_code" in data
        assert len(data["short_code"]) == 6
        assert data["short_code"].isalnum()
        assert "short_url" in data
        assert data["short_code"] in data["short_url"]
        assert data["url"] == "https://example.com/"

    def test_shorten_invalid_url(self, client, mock_redis):
        """Shorten endpoint rejects invalid URLs."""
        response = client.post("/shorten", json={"url": "not-a-url"})
        assert response.status_code == 422


class TestRedirectEndpoint:
    """Tests for GET /r/{code}."""

    def test_redirect_not_found(self, client, mock_redis):
        """Redirect returns 404 for unknown codes."""
        mock_redis.get.return_value = None
        response = client.get("/r/abcdef", follow_redirects=False)
        assert response.status_code == 404

    def test_redirect_307(self, client, mock_redis):
        """Redirect returns 307 with correct Location header."""
        mock_redis.get.return_value = "https://example.com"
        response = client.get("/r/abcdef", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "https://example.com"


class TestStatsEndpoint:
    """Tests for GET /stats/{code}."""

    def test_stats_success(self, client, mock_redis):
        """Stats endpoint returns original URL for a valid code."""
        mock_redis.get.return_value = "https://example.com"
        response = client.get("/stats/abcdef")
        assert response.status_code == 200
        data = response.json()
        assert data["short_code"] == "abcdef"
        assert data["original_url"] == "https://example.com"

    def test_stats_not_found(self, client, mock_redis):
        """Stats endpoint returns 404 for unknown codes."""
        mock_redis.get.return_value = None
        response = client.get("/stats/abcdef")
        assert response.status_code == 404

"""URL Shortener API built with FastAPI and Redis."""

import os
import string
import random

import redis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

app = FastAPI(title="URL Shortener", version="1.0.0")

# ── Configuration ────────────────────────────────────────────────
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000").rstrip("/")

# CORS — read allowed origins from env var (comma-separated)
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

CODE_LENGTH = 6
CODE_CHARS = string.ascii_letters + string.digits


class ShortenRequest(BaseModel):
    """Request body for the shorten endpoint."""

    url: HttpUrl


class ShortenResponse(BaseModel):
    """Response body for the shorten endpoint."""

    short_code: str
    short_url: str
    url: str


class StatsResponse(BaseModel):
    """Response body for the stats endpoint."""

    short_code: str
    original_url: str


class HealthResponse(BaseModel):
    """Response body for the health endpoint."""

    status: str
    redis: str


def generate_code(length: int = CODE_LENGTH) -> str:
    """Generate a random alphanumeric code."""
    return "".join(random.choices(CODE_CHARS, k=length))


@app.post("/shorten", response_model=ShortenResponse, status_code=201)
def shorten_url(request: ShortenRequest):
    """Accept a URL and return a shortened code."""
    code = generate_code()
    # Ensure uniqueness
    while redis_client.exists(code):
        code = generate_code()
    redis_client.set(code, str(request.url))
    short_url = f"{BASE_URL}/r/{code}"
    return ShortenResponse(short_code=code, short_url=short_url, url=str(request.url))


@app.get("/r/{code}")
def redirect_to_url(code: str):
    """Redirect to the original URL for the given short code."""
    url = redis_client.get(code)
    if url is None:
        raise HTTPException(status_code=404, detail="Short code not found")
    return RedirectResponse(url=url, status_code=307)


@app.get("/stats/{code}", response_model=StatsResponse)
def get_stats(code: str):
    """Return the original URL for the given short code."""
    url = redis_client.get(code)
    if url is None:
        raise HTTPException(status_code=404, detail="Short code not found")
    return StatsResponse(short_code=code, original_url=url)


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return application and Redis health status."""
    try:
        redis_client.ping()
        redis_status = "connected"
    except redis.ConnectionError:
        redis_status = "disconnected"
    return HealthResponse(status="ok", redis=redis_status)

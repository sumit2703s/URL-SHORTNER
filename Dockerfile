# ── Stage 1: Builder ──────────────────────────────────────────────
# Purpose: Install Python dependencies into an isolated prefix so we
# can copy ONLY the installed packages into the final image, keeping
# the runtime layer small and free of build tools / caches.
FROM python:3.12-slim AS builder

WORKDIR /build

COPY app/requirements.txt .

# Install into a separate prefix so we can cherry-pick just the
# packages in the next stage without dragging along pip cache.
RUN pip install --no-cache-dir --prefix=/install/packages -r requirements.txt

# ── Stage 2: Runtime ─────────────────────────────────────────────
# Purpose: Minimal production image — contains only the Python
# runtime, installed dependencies, and application code.  Runs as
# a non-root user for security.
FROM python:3.12-slim AS runtime

# Copy installed packages from builder stage
COPY --from=builder /install/packages /usr/local

# Create a non-root user so the app never runs as root
RUN useradd --create-home appuser

WORKDIR /home/appuser

# Copy application source code (API only — frontend lives on Vercel)
COPY app/ ./app/

USER appuser

EXPOSE 8000

# Start uvicorn bound to all interfaces on port 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

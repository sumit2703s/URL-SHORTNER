# shortly — URL Shortener

A full-stack URL shortener with a **FastAPI** backend (deployed on **Render**) and a static frontend (deployed on **Vercel**). Fully automated CI/CD via GitHub Actions.

```
Backend:  FastAPI + Redis   → Render
Frontend: Vanilla HTML/JS   → Vercel
CI/CD:    GitHub Actions     → 5-job pipeline
```

---

## Project Structure

```
├── app/
│   ├── main.py              # FastAPI API (JSON only, no static files)
│   ├── requirements.txt     # Python dependencies
│   └── tests/
│       └── test_main.py     # pytest tests (mocked Redis)
├── frontend/
│   ├── index.html           # Standalone SPA (no build tool)
│   └── vercel.json          # Vercel deployment config
├── Dockerfile               # Multi-stage build (builder → runtime)
├── docker-compose.yml       # Local development (Redis + API)
├── render.yaml              # Render Blueprint (API + Redis)
├── .github/workflows/
│   ├── ci.yml               # 5-job CI/CD pipeline
│   └── README.md            # Required secrets documentation
└── README.md
```

---

## Local Development

### 1. Start the backend (API + Redis)

```bash
docker compose up -d
```

This starts Redis and the FastAPI backend at `http://localhost:8000`.

Verify it's running:

```bash
curl http://localhost:8000/health
# {"status":"ok","redis":"connected"}
```

### 2. Open the frontend

Simply open `frontend/index.html` in your browser. It automatically falls back to `http://localhost:8000` when the `__API_URL__` placeholder hasn't been replaced.

```bash
# Or use a simple HTTP server if you prefer:
cd frontend && python3 -m http.server 3000
# Then open http://localhost:3000
```

### 3. Stop everything

```bash
docker compose down -v
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/shorten` | Accept a URL, return a 6-char short code + full short URL |
| `GET` | `/r/{code}` | Redirect (307) to the original URL |
| `GET` | `/stats/{code}` | Return original URL for a short code |
| `GET` | `/health` | Health check with Redis connection status |

---

## One-Time Deployment Setup

### Backend → Render

1. Push this repo to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint**.
3. Connect your GitHub repo — Render will read `render.yaml` and create:
   - A **web service** (FastAPI backend)
   - A **Redis instance**
4. After creation, go to the web service → **Environment** and set:
   - `BASE_URL` = your Render service URL (e.g. `https://url-shortener-api.onrender.com`)
   - `ALLOWED_ORIGINS` = your Vercel frontend URL (e.g. `https://shortly.vercel.app`)
5. Create a **Deploy Hook** under Settings → copy the URL for GitHub Secrets.

### Frontend → Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Link the frontend:
   ```bash
   cd frontend
   vercel link
   ```
3. In the Vercel dashboard, go to your project → **Settings** → **Environment Variables**:
   - Add `VITE_API_URL` = your Render backend URL (e.g. `https://url-shortener-api.onrender.com`)
4. Copy `orgId` and `projectId` from `.vercel/project.json` for GitHub Secrets.

### GitHub Secrets

Add these 5 secrets to your repo (Settings → Secrets → Actions):

| Secret | Where to find it |
|--------|-----------------|
| `RENDER_DEPLOY_HOOK_URL` | Render → Service → Settings → Deploy Hook |
| `RENDER_APP_URL` | Render service URL (e.g. `https://xyz.onrender.com`) |
| `VERCEL_TOKEN` | vercel.com → Account → Settings → Tokens |
| `VERCEL_ORG_ID` | `.vercel/project.json` after `vercel link` |
| `VERCEL_PROJECT_ID` | `.vercel/project.json` after `vercel link` |

See [`.github/workflows/README.md`](.github/workflows/README.md) for detailed instructions.

---

## Auto-Deploy Flow

Once setup is complete, just push to `main`:

```bash
git add . && git commit -m "feat: new feature" && git push origin main
```

GitHub Actions will automatically:

1. ✅ Run unit tests
2. ✅ Build Docker image
3. ✅ Run integration tests
4. 🚀 Deploy backend to Render
5. 🚀 Deploy frontend to Vercel

PRs and pushes to `develop` run only steps 1–3 (no deploy).

---

## Running Tests

```bash
# With venv
python3 -m venv .venv && source .venv/bin/activate
pip install -r app/requirements.txt
pytest app/tests/ -v

# Or with Docker (integration)
docker compose up -d --build
curl http://localhost:8000/health
docker compose down -v
```

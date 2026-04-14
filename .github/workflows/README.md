# CI/CD Secrets Setup

This workflow requires **5 GitHub Secrets** to enable automated deployment. PRs and pushes to `develop` run only the first 3 jobs (test → docker-build → integration). Pushes to `main` run all 5 jobs including deployment.

---

## Required Secrets

### 1. `RENDER_DEPLOY_HOOK_URL`

The webhook URL that triggers a new deployment on Render.

**Where to find it:**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your web service → **Settings**
3. Scroll to **Deploy Hook**
4. Click **Create Deploy Hook**, give it a name (e.g. `github-actions`)
5. Copy the generated URL

**Example:** `https://api.render.com/deploy/srv-xxxxxxxxxxxxx?key=yyyyyyyyyyyy`

---

### 2. `RENDER_APP_URL`

The public URL of your deployed Render web service. Used to poll `/health` after deploy.

**Where to find it:**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your web service
3. Copy the URL shown at the top (e.g. `https://url-shortener-api.onrender.com`)

**Example:** `https://url-shortener-api.onrender.com`

---

### 3. `VERCEL_TOKEN`

A personal access token for the Vercel CLI to deploy without interactive login.

**Where to find it:**
1. Go to [vercel.com](https://vercel.com) → click your avatar → **Settings**
2. Navigate to **Tokens**
3. Click **Create Token**, give it a name (e.g. `github-actions`)
4. Copy the generated token

---

### 4. `VERCEL_ORG_ID`

Your Vercel organization (or personal account) ID.

**Where to find it:**
1. In your terminal, `cd frontend/` and run `vercel link`
2. Follow the prompts to link to your Vercel project
3. Open the generated `.vercel/project.json`
4. Copy the `"orgId"` value

**Example:** `team_xxxxxxxxxxxxxxxxxxxx`

---

### 5. `VERCEL_PROJECT_ID`

The Vercel project ID for the frontend deployment.

**Where to find it:**
1. Same file as above: `.vercel/project.json` (created by `vercel link`)
2. Copy the `"projectId"` value

**Example:** `prj_xxxxxxxxxxxxxxxxxxxx`

---

## How to add secrets to GitHub

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add each of the 5 secrets above with the exact names listed

---

## Pipeline Flow

```
Push to main:     test → docker-build → integration → deploy-backend → deploy-frontend
Push to develop:  test → docker-build → integration
Pull Request:     test → docker-build → integration
```

# Deployment Guide

## Frontend — Vercel

1. Push the repo to GitHub.
2. Import the project in [Vercel](https://vercel.com).
3. Set **Root Directory** to `apps/web`.
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://your-api.onrender.com`
5. Deploy. Vercel auto-detects Next.js.

### Build settings

| Setting | Value |
|---------|--------|
| Framework | Next.js |
| Build command | `npm run build` |
| Output | `.next` (default) |

---

## Backend — Render

1. Create a **Web Service** on [Render](https://render.com).
2. Connect your GitHub repo.
3. Use `render.yaml` or configure manually:

| Setting | Value |
|---------|--------|
| Root directory | `backend` |
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

4. Environment variables:

```
GROQ_API_KEY=...
CORS_ORIGINS=https://your-app.vercel.app
GITHUB_TOKEN=...          # optional
CORS_ALLOW_ALL=false
```

5. After deploy, update Vercel's `NEXT_PUBLIC_API_URL` to the Render URL.

---

## Docker (optional)

```bash
docker compose up --build
```

- API: http://localhost:8000
- Web: http://localhost:3000

---

## Production checklist

- [ ] `GROQ_API_KEY` set on Render
- [ ] `CORS_ORIGINS` matches Vercel domain (no trailing slash)
- [ ] `CORS_ALLOW_ALL=false` in production
- [ ] `NEXT_PUBLIC_API_URL` points to Render API
- [ ] Health check: `GET https://api.example.com/`

---

## Railway (alternative)

Same as Render:

- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Root: `backend`
- Python 3.11 recommended

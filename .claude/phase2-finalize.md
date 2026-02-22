# Phase 2 Finalization Instructions

Load this file in a new Claude Code session at the end of Phase 2 (feature/stt-parakeet).
Run these tasks **in order**. Do not ask for confirmation unless a step says to.

---

## Context

Project: Memories assistant (FastAPI backend + SvelteKit frontend)
Branch: feature/stt-parakeet
Working directory: /home/ralph/memories

---

## Step 1 — Add backend .gitignore

Create the file `backend/.gitignore` with the following content:

```
__pycache__/
*.py[cod]
*.pyo
.pytest_cache/
.mypy_cache/
*.egg-info/
dist/
build/
venv/
env/
.env
*.log
.cache/
```

---

## Step 2 — Commit all Phase 2 work

Check `git status` first. Then stage and commit everything that belongs to Phase 2
using conventional commit messages (English, imperative).

Suggested commit grouping (adjust if files differ):

```
git add backend/ docker-compose.yml
git commit -m "feat: add Parakeet STT backend with FastAPI and Docker"

git add frontend/Dockerfile frontend/package.json frontend/package-lock.json \
        frontend/svelte.config.js frontend/vite.config.ts \
        frontend/src/app.html frontend/src/routes/+layout.svelte \
        frontend/src/routes/+page.svelte frontend/static/
git commit -m "feat: connect frontend microphone to /api/stt endpoint"

git add .env.example
git commit -m "chore: add .env.example with Tailscale origin"

git add .claude/
git commit -m "docs: add Claude rules for git conventions and phases"

git add backend/.gitignore
git commit -m "chore: add backend .gitignore"
```

Verify with `git log --oneline` that all commits look correct before continuing.

---

## Step 3 — Fix: non-root user in backend Dockerfile

File: `backend/Dockerfile`

Find the last `RUN` instruction before the `CMD` line and add after it:

```dockerfile
RUN useradd -m -u 1000 app
USER app
```

---

## Step 4 — Fix: file size limit on /api/stt

File: `backend/app/routers/stt.py`

In the `speech_to_text` function, immediately after `audio_bytes = await audio.read()`,
add:

```python
MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB
if len(audio_bytes) > MAX_UPLOAD_BYTES:
    raise HTTPException(status_code=413, detail="Audiobestand te groot (max 50 MB)")
```

---

## Step 5 — Fix: restrict CORS origins

File: `backend/app/main.py`

Replace the `allow_origins=["*"]` line with:

```python
allow_origins=[
    "https://pc-003.taild4fcd.ts.net",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
],
```

Also narrow the methods and headers:

```python
allow_methods=["GET", "POST"],
allow_headers=["Content-Type"],
```

---

## Step 6 — Fix: sanitize error messages in /api/stt

File: `backend/app/routers/stt.py`

Find any `raise HTTPException(status_code=500, detail=str(exc))` and replace with:

```python
raise HTTPException(status_code=500, detail="Transcriptie mislukt")
```

Keep the original exception as the `from exc` cause for logging:

```python
raise HTTPException(status_code=500, detail="Transcriptie mislukt") from exc
```

---

## Step 7 — Commit security fixes

```
git add backend/Dockerfile backend/app/routers/stt.py backend/app/main.py
git commit -m "fix: harden backend — non-root user, upload size limit, CORS, error messages"
```

---

## Step 8 — Verify and test

1. Run `docker compose build && docker compose up` — verify all containers start cleanly
2. Test the STT endpoint manually or via the frontend
3. Run `git log --oneline` — confirm all commits are present with correct messages

---

## Step 9 — Prepare for squash merge into main

When Phase 2 is fully verified:

```
git checkout main
git merge --squash feature/stt-parakeet
git commit -m "feat: Phase 2 — STT Parakeet endpoint with Docker GPU support"
git push
```

Confirm with the user before pushing.

---

## Step 10 — Architecture refactor: shared AI services

Na de squash merge naar main, voer de architecture refactor uit.
Het volledige plan staat in `.claude/architecture-refactor.md`.

Samenvatting:
- Maak `/home/ralph/services/` aan als aparte git-repo
- Verplaats STT (Parakeet) naar `services/stt/` op poort 8001
- TTS en N8N krijgen eigen folders in `services/` (Phase 3/4)
- `memories/backend/` wordt een dunne proxy die `http://stt:8001` aanroept
- Docker-netwerk `ai-net` verbindt services met memories

Voer dit pas uit als Phase 2 volledig gemerged en getest is.
Lees `.claude/architecture-refactor.md` voor de volledige stappen.

---

## Note for Phase 3 — Parkiet TTS VRAM warning

**Parkiet** (https://github.com/pevers/parkiet) is a 1.6B Dutch TTS model.
It is a separate project from NVIDIA Parakeet (STT) — only the names are similar.

VRAM requirements per the Parkiet README:
- PyTorch float32 → ≥ 15 GB VRAM
- PyTorch bfloat16 → ≥ 10 GB VRAM

The RTX 3060 Ti has 8 GB VRAM — this falls short even with bfloat16.

Implications for Phase 3:
- CUDA SysMem Fallback (unified memory) must be enabled to use system RAM as overflow
- Latency will be significantly higher than native GPU inference
- Piper nl_BE fallback will likely be the daily reality for real-time use
- Evaluate whether Parkiet is viable at all on this hardware before investing build time;
  consider starting with Piper nl_BE as primary and Parkiet as optional/offline

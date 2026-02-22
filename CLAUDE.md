# Memories — Claude Code Instructions

## CONSTRAINTS (non-negotiable)
0. Keep README.md in sync — update architecture diagram, API table, stack table, and roadmap checkboxes when making structural changes
1. Dutch UI text, English code/comments
2. All AI models run LOCAL (no cloud APIs for STT/TTS/LLM)
3. Docker containers for all services
4. FastAPI backend, SvelteKit frontend
5. Target: RTX 3060 Ti (8GB VRAM) + CUDA SysMem Fallback
6. WSL2 on Windows 11 — NEVER install nvidia-drivers in WSL2
7. Tailscale Funnel for HTTPS access (no port forwarding, no paid plan needed)
8. Pre-render news audio via cron (04:30), not on-demand
9. Piper nl_BE fallback if Parkiet unavailable
10. n8n for orchestration workflows
11. All secrets in .env (never hardcode)
12. Git branch per phase: feature/<phase-name>

## Architecture
- Frontend: SvelteKit PWA → iPhone via Tailscale Funnel (HTTPS)
- Backend: FastAPI (Python 3.11)
- STT: NVIDIA Parakeet-TDT-0.6B
- TTS: Parkiet 1.6B (primary) + Piper nl_BE (fallback)
- LLM: Ollama (model TBD)
- Orchestration: n8n
- All services in Docker, GPU passthrough via nvidia-container-toolkit

## Key Commands
- `docker compose up` — start all services
- `cd frontend && npm run dev -- --host` — frontend dev
- `cd backend && uvicorn app.main:app --reload` — backend dev

## Current Phase
Phase 2: STT Parakeet (branch: feature/stt-parakeet)

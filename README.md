# Herinneringen

Personal AI assistant PWA for audio recording, transcription, news briefings, and calendar integration — running entirely on local hardware.

## Architecture

```
iPhone (Safari PWA)
    │
    ▼ HTTPS (Tailscale Funnel)
┌─────────────────────────────────────┐
│  SvelteKit Frontend (port 3000)     │
│  PWA + Service Worker + IndexedDB   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  FastAPI Backend (port 8000)        │
│  Proxy + orchestration              │
└──────────────┬──────────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│  STT   │ │  TTS   │ │ Ollama │
│ :8001  │ │ :8002  │ │ :11434 │
│Parakeet│ │Parkiet │ │  LLM   │
└────────┘ └────────┘ └────────┘
```

## Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Frontend | SvelteKit 2 + Svelte 5 | PWA with offline support |
| Backend | FastAPI (Python 3.11) | Proxy + API orchestration |
| STT | NVIDIA Parakeet-TDT-0.6B | Local GPU inference |
| TTS | Parkiet 1.6B / Piper nl_BE | Dutch speech synthesis |
| LLM | Ollama | Local model inference |
| Orchestration | n8n | Workflow automation |
| Runtime | Docker + NVIDIA Container Toolkit | GPU passthrough |
| Target HW | RTX 3060 Ti (8GB VRAM) | WSL2 on Windows 11 |
| Access | Tailscale Funnel | HTTPS without port forwarding |

## API Endpoints

| Method | Path | Service | Description |
|--------|------|---------|-------------|
| POST | `/api/stt` | STT | Audio transcription (WebM/MP4/WAV) |
| POST | `/api/tts/synthesize` | TTS | Text-to-speech synthesis |
| GET | `/api/tts/engines` | TTS | List available TTS engines |
| GET | `/api/news/today` | Backend | Today's news items |
| POST | `/api/news/refresh` | Backend | Refresh news feed |
| GET/PUT | `/api/news/preferences` | Backend | News preferences |
| GET | `/api/news/:id/audio` | Backend | Pre-rendered news audio |
| POST | `/api/chat` | LLM | Chat completion |
| POST | `/api/summarize` | LLM | Text summarization |
| GET | `/api/health` | Backend | Deep health check (all services) |
| GET | `/health` | Backend | Quick liveness probe |

## Quick Start

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env with your values

# 2. Start all services
docker compose up -d            # memories (frontend + backend)
cd ../services && docker compose up -d  # stt, tts, ollama, n8n

# 3. Access
open https://pc-003.taild4fcd.ts.net   # via Tailscale Funnel
```

## Development

```bash
# Frontend dev (hot reload)
cd frontend && npm run dev -- --host

# Backend dev (hot reload)
cd backend && uvicorn app.main:app --reload

# Type check
cd frontend && npm run check

# Build frontend
cd frontend && npm run build
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ORIGIN` | `http://localhost:3000` | SvelteKit CSRF origin |
| `BODY_SIZE_LIMIT` | `52428800` | Max upload size (50MB) — adapter-node default is 512KB |
| `BACKEND_URL` | `http://backend:8000` | Backend URL for frontend proxy |
| `HF_TOKEN` | — | HuggingFace token for Parakeet model download |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama API URL |

## Testing

See [Test.MD](Test.MD) for testing patterns, known iOS Safari issues, and CI/CD setup.

```bash
# Generate test audio (1-5 min WAV files)
python3 scripts/generate_test_wav.py

# Test STT pipeline
curl -X POST -F "audio=@scripts/test-audio/test-1min.wav" http://localhost:8000/api/stt
```

## Roadmap

- [x] Phase 1: PWA Frontend (SvelteKit + Service Worker + IndexedDB)
- [x] Phase 2: STT Parakeet (audio transcription)
- [x] Phase 2.5: Dictafoon stability (body size, timer, error handling)
- [x] Phase 3: TTS Parkiet (Dutch text-to-speech)
- [x] Phase 4: LLM Ollama (local chat)
- [x] Phase 5: News Briefing (pre-rendered audio via cron)
- [ ] Phase 6: Calendar Outlook
- [ ] Phase 7: Hardening

## Licentie

Dit project is gelicenseerd onder de [MIT License](LICENSE) — Ralph Wagter / [Athide.nl](https://athide.nl)

### Gebruikte open-source componenten en licenties

| Component | Licentie |
|-----------|----------|
| [SvelteKit](https://github.com/sveltejs/kit) | MIT |
| [FastAPI](https://github.com/fastapi/fastapi) | MIT |
| [NVIDIA Parakeet-TDT-0.6B](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) | CC-BY-4.0 |
| [Parkiet TTS](https://huggingface.co/pevers/parkiet) | RAIL-M |
| [Piper TTS](https://github.com/rhasspy/piper) | MIT |
| [Silero VAD](https://github.com/snakers4/silero-vad) | MIT |
| [Ollama](https://github.com/ollama/ollama) | MIT |
| [n8n](https://github.com/n8n-io/n8n) | Sustainable Use License (fair-code) |
| [Docker](https://www.docker.com/) | Apache 2.0 |
| [Tailscale](https://tailscale.com/) | BSD-3-Clause |

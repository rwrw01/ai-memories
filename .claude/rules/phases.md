# Development Phases

## Phase 2: STT Parakeet (current)
- Branch: feature/stt-parakeet
- FastAPI backend with POST /api/stt endpoint
- NVIDIA Parakeet-TDT-0.6B model in Docker container
- Accept WAV/WebM audio, return transcribed text
- GPU passthrough via nvidia-container-toolkit
- Use bfloat16 to reduce VRAM usage
- Dockerfile with CUDA support for RTX 3060 Ti
- docker-compose.yml in project root
- Connect frontend microphone to /api/stt endpoint

## Phase 3: TTS Parkiet (upcoming)
- Parkiet 1.6B primary, Piper nl_BE fallback
- POST /api/tts endpoint

## Phase 4: LLM Ollama
## Phase 5: News Briefing
## Phase 6: Calendar Outlook
## Phase 7: Hardening

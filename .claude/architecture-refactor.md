# Architecture Refactor Plan — Shared AI Services

## Doel

AI-services (STT, TTS, N8N) losmaken van het memories-project zodat ze
herbruikbaar zijn voor toekomstige projecten. De memories-app krijgt een
dunne backend die de services aanroept via een intern Docker-netwerk.

---

## Doelstructuur

```
/home/ralph/
│
├── services/                      ← NIEUW — eigen git-repo
│   ├── stt/                       ← Parakeet STT (verplaatst vanuit memories/backend)
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app/
│   │       ├── __init__.py
│   │       ├── main.py            ← standalone FastAPI, port 8001
│   │       └── routers/
│   │           └── stt.py
│   ├── tts/                       ← Phase 3 (placeholder)
│   │   └── .gitkeep
│   ├── n8n/                       ← Phase 4 (placeholder)
│   │   └── .gitkeep
│   └── docker-compose.yml         ← beheert alle services + ai-net netwerk
│
└── memories/                      ← bestaande git-repo (ongewijzigd van buiten)
    ├── frontend/                  ← ongewijzigd
    ├── backend/                   ← DUN: alleen memories-specifieke routes
    │   └── app/
    │       ├── main.py            ← proxyt naar services via ai-net
    │       └── routers/
    │           └── stt.py         ← stuurt door naar http://stt:8001/api/stt
    └── docker-compose.yml         ← frontend + backend, joinen ai-net
```

---

## Docker-netwerk

```
                    ┌─────────────────────────────────┐
                    │  docker network: ai-net          │
                    │                                  │
  services/         │  stt:8001   tts:8002   n8n:5678 │
  docker-compose ───┤                                  │
                    └────────────┬────────────────────┘
                                 │ external network
  memories/                      │
  docker-compose ────► backend:8000  frontend:3000
```

- `services/docker-compose.yml` maakt het netwerk `ai-net` aan
- `memories/docker-compose.yml` **joinet** `ai-net` als external network
- `memories/backend` roept intern `http://stt:8001` aan — nooit exposed naar buiten
- Alleen poorten 3000 (frontend) en 8000 (backend) zijn zichtbaar via Tailscale

---

## Poorttoewijzing

| Service           | Interne host | Poort |
|-------------------|--------------|-------|
| STT (Parakeet)    | stt          | 8001  |
| TTS (Parkiet)     | tts          | 8002  |
| N8N               | n8n          | 5678  |
| memories/backend  | backend      | 8000  |
| memories/frontend | frontend     | 3000  |

---

## Refactor-stappen (uitvoeren NA Phase 2 merge)

### Stap 1 — Maak de services-repo aan

```bash
mkdir -p /home/ralph/services/stt /home/ralph/services/tts /home/ralph/services/n8n
cd /home/ralph/services
git init
git checkout -b main
```

### Stap 2 — Verplaats STT service

```bash
cp -r /home/ralph/memories/backend/app      /home/ralph/services/stt/app
cp    /home/ralph/memories/backend/Dockerfile     /home/ralph/services/stt/Dockerfile
cp    /home/ralph/memories/backend/requirements.txt /home/ralph/services/stt/requirements.txt
touch /home/ralph/services/tts/.gitkeep
touch /home/ralph/services/n8n/.gitkeep
```

Pas in `services/stt/app/main.py` de poort aan naar 8001:
- `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]`

### Stap 3 — Maak services/docker-compose.yml

```yaml
networks:
  ai-net:
    name: ai-net

services:
  stt:
    build: ./stt
    ports:
      - "8001:8001"
    volumes:
      - stt-cache:/app/.cache
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    networks:
      - ai-net

  # tts:          ← toevoegen in Phase 3
  #   build: ./tts
  #   ports: ["8002:8002"]
  #   networks: [ai-net]

  # n8n:          ← toevoegen in Phase 4
  #   image: n8nio/n8n
  #   ports: ["5678:5678"]
  #   networks: [ai-net]

volumes:
  stt-cache:
```

### Stap 4 — Vervang memories/backend door een dunne proxy

Maak `memories/backend/app/routers/stt.py` een proxy:

```python
import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()
STT_URL = "http://stt:8001/api/stt"

@router.post("/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            resp = await client.post(
                STT_URL,
                files={"audio": (audio.filename, await audio.read(), audio.content_type)},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="STT-service niet beschikbaar")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
```

Voeg `httpx` toe aan `memories/backend/requirements.txt`.

### Stap 5 — Update memories/docker-compose.yml

```yaml
networks:
  ai-net:
    external: true      # ← joinet het netwerk van services/

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - ORIGIN=${ORIGIN:-http://localhost:3000}
    env_file:
      - path: .env
        required: false
    restart: unless-stopped
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - path: .env
        required: false
    restart: unless-stopped
    networks:
      - default
      - ai-net           # ← zodat backend stt:8001 kan bereiken
```

### Stap 6 — .gitignore voor services-repo

Maak `/home/ralph/services/.gitignore`:
```
__pycache__/
*.py[cod]
.env
*.log
.cache/
tts/models/
stt/models/
```

### Stap 7 — Eerste commit services-repo

```bash
cd /home/ralph/services
git add .
git commit -m "feat: initial shared AI services structure with STT (Parakeet)"
```

### Stap 8 — Verwijder nu overtollig uit memories/backend

Na het testen:
```bash
# Verwijder de NeMo/model code uit memories/backend — die zit nu in services/stt
# Alleen de proxy-router en FastAPI shell blijven over
```

### Stap 9 — Opstarten volgorde

```bash
# Altijd eerst services starten (maakt ai-net aan)
cd /home/ralph/services && docker compose up -d

# Dan memories starten (joint ai-net)
cd /home/ralph/memories && docker compose up -d
```

---

## Wat ongewijzigd blijft in memories/

- `frontend/` — volledig ongewijzigd
- `.claude/` — project-specifieke Claude-regels
- `CLAUDE.md` — project-instructies
- Git-history van memories-repo

---

## Opmerking: opstartafhankelijkheid

`memories/docker-compose.yml` vereist dat `services/docker-compose.yml`
al draait (anders bestaat `ai-net` niet). Overweeg een startscript:

```bash
#!/bin/bash
# /home/ralph/start-all.sh
cd /home/ralph/services && docker compose up -d
cd /home/ralph/memories && docker compose up -d
```

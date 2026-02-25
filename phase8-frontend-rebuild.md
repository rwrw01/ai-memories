# Phase 8: Frontend V2 — shadcn rebuild + Smart Recording Flows

> Opgeslagen: 2026-02-24. Volgende sessie: `claude` → "voer phase8-frontend-rebuild.md uit, begin bij fase A"

## Context

De bestaande frontend werkt maar heeft custom inline styles zonder UI framework. Phase 8:
1. **Volledige rebuild** in shadcn-svelte (vervangt uiteindelijk de oude frontend)
2. **Smart Recording** — opnames worden via STT getranscribeerd, door een LLM geclassificeerd, en automatisch gerouteerd naar de juiste n8n workflow
3. **Nieuwe frontend naast de bestaande** (`frontend-v2/`) zodat de huidige app blijft werken

**Phase 6 (Calendar Outlook) is geparkeerd** — DLP-beleid blokkeert data-export uit enterprise Outlook. Kan later opgepakt worden als IT een App Registration maakt.

## Smart Recording Flow

```
Gebruiker spreekt in
    ↓
Opname → STT (Parakeet) → transcriptie
    ↓
LLM (Ollama) → intent classificatie
    ↓
Router: welk triggerwoord?
    ├─ "whatsapp [naam] [bericht]"  → n8n: WhatsApp versturen
    ├─ "aantekening [tekst]"        → UI: toon in scrollbaar venster
    ├─ "vergadering [tekst]"        → n8n: LLM samenvatting + acties
    ├─ "e-mail [naam] [onderwerp]"  → n8n: e-mail via SMTP
    ├─ "herinnering [tijd] [tekst]" → n8n: schedule notificatie
    └─ (geen match)                 → UI: toon als ruwe aantekening
```

## Architectuur

```
frontend-v2/ (SvelteKit + shadcn-svelte + Tailwind)
    │
    ▼  POST /api/stt → transcriptie
    ▼  POST /api/classify → LLM intent detectie
    │
    ▼  POST /api/flow/execute → backend routeert naar n8n
    │
backend:8000
    ├─→ n8n:5678/webhook/flow-whatsapp   → whatsapp-web service
    ├─→ n8n:5678/webhook/flow-vergadering → ollama → samenvatting
    ├─→ n8n:5678/webhook/flow-email       → SMTP
    ├─→ n8n:5678/webhook/flow-herinnering → scheduler
    └─→ (aantekening: direct opslaan, geen n8n nodig)

whatsapp-web:3001 (Docker, whatsapp-web.js)
    └─→ QR code scan → sessie → berichten versturen
```

## 5 Sub-fases

### Fase 8A: Frontend V2 scaffolding + shadcn setup

**Nieuw project naast bestaand:**
```
~/memories/
├── frontend/        ← bestaand (blijft draaien op :3000)
├── frontend-v2/     ← nieuw (draait op :3002)
├── backend/         ← gedeeld
└── docker-compose.yml ← uitbreiden met frontend-v2 service
```

**Setup:**
1. SvelteKit project initialiseren (`bun create svelte@latest frontend-v2`)
2. Tailwind CSS installeren + configureren
3. shadcn-svelte installeren (`bunx shadcn-svelte@latest init`)
4. Dark theme configureren (bestaande kleuren overnemen)
5. PWA configuratie overnemen
6. Basis layout: sidebar navigatie (mobiel: bottom nav)

**shadcn componenten:**
- Button, Card, Input, Label, Tabs, ScrollArea
- Sheet (mobile drawer), Dialog, Badge, Separator
- Slider, Switch, Select, Textarea
- Sonner (toasts/notificaties)

**Pagina's (initieel leeg):**
- `/` — Dashboard
- `/opname` — Smart Recording
- `/nieuws` — Nieuws briefing
- `/instellingen` — Instellingen

### Fase 8B: Bestaande features migreren

**Dictafoon → Opname pagina:**
- Hergebruik `recorder.ts`, `store.svelte.ts`, `wake-lock.ts`
- Rebuild UI met shadcn componenten

**Nieuws → Nieuws pagina:**
- Rebuild NewsPlayer, NewsList, NewsControls met shadcn
- Tabs, Card, Slider componenten

**Instellingen pagina:**
- shadcn Form componenten

### Fase 8C: Intent classificatie + flow routing

**Backend nieuw:**
- `backend/app/routers/classify.py` — POST /api/classify (Ollama intent detectie)
- `backend/app/routers/flow.py` — POST /api/flow/execute (routeert naar n8n)
- `backend/app/models/flow.py` — FlowExecution model (SQLite)
- `backend/app/schemas/flow.py` — Pydantic schemas
- `backend/app/services/classify_service.py` — LLM prompt voor classificatie
- `backend/app/services/flow_service.py` — n8n webhook routing

**Frontend:**
- Na transcriptie → automatisch classificeren → gebruiker bevestigt → execute flow

### Fase 8D: Individuele n8n flows

- **D1: Aantekening** — direct opslaan, tonen in UI (geen n8n)
- **D2: Vergadering** — n8n → Ollama samenvatting + actiepunten
- **D3: WhatsApp** — n8n → whatsapp-web:3001/send
- **D4: E-mail** — n8n → SMTP
- **D5: Herinnering** — n8n → Schedule node → notificatie

### Fase 8E: WhatsApp Docker service

**Nieuwe service:** `services/whatsapp-web/` (whatsapp-web.js + Express)
- GET /status, GET /qr, POST /send, GET /contacts
- Docker met volume mount voor sessie-opslag
- QR code authenticatie via frontend UI

## Beslissingen

- **WhatsApp:** whatsapp-web.js (gratis, onofficieel)
- **UI Framework:** shadcn-svelte + Tailwind CSS
- **Frontend:** Naast bestaande (frontend-v2/)
- **Scope:** Alles overnemen + uitbreiden
- **Flows:** whatsapp, aantekening, vergadering, e-mail, herinnering + uitbreidbaar

## Git

- Branch: `feature/frontend-v2`
- Commits per sub-fase

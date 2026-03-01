import json
import logging
import os

import httpx
from fastapi import HTTPException

from app.services.http_client import service_retry

logger = logging.getLogger(__name__)
OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
MODEL = "qwen3:8b"

CLASSIFY_SYSTEM = """Je bent een intent-classificatie engine. Analyseer de Nederlandse transcriptie en bepaal de intentie.

Mogelijke intenties:
- "whatsapp": Gebruiker wil een WhatsApp-bericht sturen. Extraheer "contact" (naam) en "bericht" (inhoud).
- "artikel": Gebruiker wil een artikel of tekst laten schrijven/herschrijven. Extraheer "onderwerp" (kort) en "brontekst" (de originele tekst).
- "aantekening": Alles wat niet in bovenstaande categorieën valt, of als je twijfelt.

Antwoord ALLEEN met valide JSON in dit formaat:
{"intent": "whatsapp|artikel|aantekening", "params": {...}, "confidence": 0.0-1.0}

Voorbeelden:

Invoer: "stuur een whatsapp aan Peter dat ik wat later kom"
Uitvoer: {"intent": "whatsapp", "params": {"contact": "Peter", "bericht": "ik kom wat later"}, "confidence": 0.95}

Invoer: "stuur een berichtje naar Maria ik sta in de file"
Uitvoer: {"intent": "whatsapp", "params": {"contact": "Maria", "bericht": "ik sta in de file"}, "confidence": 0.9}

Invoer: "maak een artikel van deze tekst over duurzame energie in Nederland"
Uitvoer: {"intent": "artikel", "params": {"onderwerp": "duurzame energie in Nederland", "brontekst": "deze tekst over duurzame energie in Nederland"}, "confidence": 0.9}

Invoer: "vergeet niet melk te kopen"
Uitvoer: {"intent": "aantekening", "params": {"tekst": "vergeet niet melk te kopen"}, "confidence": 0.85}

Invoer: "schrijf op dat de vergadering verplaatst is naar dinsdag"
Uitvoer: {"intent": "aantekening", "params": {"tekst": "de vergadering is verplaatst naar dinsdag"}, "confidence": 0.85}"""

CONFIDENCE_THRESHOLD = 0.7


@service_retry
async def _call_ollama(payload: dict) -> dict:
    """Call Ollama chat API with retry on transient errors."""
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(f"{OLLAMA_BASE}/api/chat", json=payload)
        resp.raise_for_status()
        return resp.json()


async def classify(transcription: str) -> dict:
    """Classify a Dutch transcription into an intent with parameters."""
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": CLASSIFY_SYSTEM},
            {"role": "user", "content": transcription},
        ],
        "stream": False,
        "format": "json",
    }
    try:
        data = await _call_ollama(payload)
        raw = data["message"]["content"]
        result = json.loads(raw)

        # Validate required fields
        if "intent" not in result or "confidence" not in result:
            return _fallback(transcription)

        # Ensure valid intent
        if result["intent"] not in ("whatsapp", "artikel", "aantekening"):
            return _fallback(transcription)

        # Below threshold -> fallback
        if result["confidence"] < CONFIDENCE_THRESHOLD:
            return _fallback(transcription, confidence=result["confidence"])

        # Ensure params exists
        if "params" not in result:
            result["params"] = {"tekst": transcription}

        return result
    except (json.JSONDecodeError, KeyError):
        logger.warning("LLM returned invalid JSON, falling back to aantekening")
        return _fallback(transcription)
    except httpx.RequestError:
        logger.error("Ollama unreachable for classification")
        raise HTTPException(status_code=503, detail="LLM-service niet beschikbaar")
    except httpx.HTTPStatusError as e:
        logger.error("Ollama returned %d: %s", e.response.status_code, e.response.text)
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


def _fallback(transcription: str, confidence: float = 1.0) -> dict:
    """Safe fallback to aantekening intent."""
    return {"intent": "aantekening", "params": {"tekst": transcription}, "confidence": confidence}

import logging

import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.http_client import service_retry

logger = logging.getLogger(__name__)
router = APIRouter()
STT_URL = "http://stt:8001/api/stt"


@service_retry
async def _call_stt(audio_bytes: bytes, filename: str, content_type: str) -> dict:
    """Call STT service with retry on transient errors."""
    async with httpx.AsyncClient(timeout=600) as client:
        resp = await client.post(
            STT_URL,
            files={"audio": (filename, audio_bytes, content_type)},
        )
        resp.raise_for_status()
        return resp.json()


@router.post("/api/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """Proxy audio upload to the STT service and return its transcription."""
    audio_bytes = await audio.read()
    try:
        return await _call_stt(audio_bytes, audio.filename, audio.content_type)
    except httpx.RequestError:
        logger.error("STT service unreachable after retries")
        raise HTTPException(status_code=503, detail="STT-service niet beschikbaar")
    except httpx.HTTPStatusError as e:
        logger.error("STT service returned %d: %s", e.response.status_code, e.response.text)
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

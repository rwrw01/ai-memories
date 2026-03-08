import logging
import os

import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.http_client import service_retry

logger = logging.getLogger(__name__)
router = APIRouter()
STT_URL = "http://stt:8001/api/stt"
_INTERNAL_KEY = os.getenv("INTERNAL_KEY", "")


@service_retry
async def _call_stt(audio_bytes: bytes, filename: str, content_type: str) -> dict:
    """Call STT service with retry on transient errors."""
    headers = {"X-Internal-Key": _INTERNAL_KEY} if _INTERNAL_KEY else {}
    async with httpx.AsyncClient(timeout=600) as client:
        resp = await client.post(
            STT_URL,
            files={"audio": (filename, audio_bytes, content_type)},
            headers=headers,
        )
        resp.raise_for_status()
        return resp.json()


MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB


@router.post("/api/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """Proxy audio to the STT service and return the transcription.

    Classification and flow execution are handled by the frontend
    via separate /api/classify and /api/flow/execute calls.
    """
    audio_bytes = await audio.read()
    if len(audio_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Bestand te groot (max 50 MB)")
    try:
        result = await _call_stt(audio_bytes, audio.filename, audio.content_type)
    except httpx.RequestError:
        logger.error("STT service unreachable after retries")
        raise HTTPException(status_code=503, detail="STT-service niet beschikbaar")
    except httpx.HTTPStatusError as e:
        logger.error("STT service returned %d: %s", e.response.status_code, e.response.text)
        raise HTTPException(status_code=502, detail="Upstream service fout")

    return result

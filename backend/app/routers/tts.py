import logging

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from app.services.http_client import service_retry

logger = logging.getLogger(__name__)
router = APIRouter()
TTS_BASE = "http://tts:8002/api/tts"


class SynthesizeRequest(BaseModel):
    text: str
    engine: str = "auto"
    voice: str = "default"


@service_retry
async def _call_synthesize(payload: dict) -> httpx.Response:
    """Call TTS synthesize with retry on transient errors."""
    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(f"{TTS_BASE}/synthesize", json=payload)
        resp.raise_for_status()
        return resp


@service_retry
async def _call_engines() -> dict:
    """Call TTS engines endpoint with retry."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{TTS_BASE}/engines")
        resp.raise_for_status()
        return resp.json()


@router.post("/api/tts/synthesize")
async def synthesize(req: SynthesizeRequest) -> Response:
    """Proxy text to the TTS service and return WAV audio."""
    try:
        resp = await _call_synthesize(req.model_dump())
        return Response(
            content=resp.content,
            media_type="audio/wav",
            headers={
                k: v for k, v in resp.headers.items()
                if k.lower().startswith("x-")
            },
        )
    except httpx.RequestError:
        logger.error("TTS service unreachable after retries")
        raise HTTPException(status_code=503, detail="TTS-service niet beschikbaar")
    except httpx.HTTPStatusError as e:
        logger.error("TTS service returned %d: %s", e.response.status_code, e.response.text)
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.get("/api/tts/engines")
async def engines():
    """Proxy engine list from TTS service."""
    try:
        return await _call_engines()
    except httpx.RequestError:
        logger.error("TTS engines endpoint unreachable after retries")
        raise HTTPException(status_code=503, detail="TTS-service niet beschikbaar")
    except httpx.HTTPStatusError as e:
        logger.error("TTS engines returned %d: %s", e.response.status_code, e.response.text)
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

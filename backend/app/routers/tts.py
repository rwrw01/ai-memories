import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

router = APIRouter()
TTS_BASE = "http://tts:8002/api/tts"


class SynthesizeRequest(BaseModel):
    text: str
    engine: str = "auto"
    voice: str = "default"


@router.post("/api/tts/synthesize")
async def synthesize(req: SynthesizeRequest) -> Response:
    """Proxy text to the TTS service and return WAV audio."""
    async with httpx.AsyncClient(timeout=300) as client:
        try:
            resp = await client.post(
                f"{TTS_BASE}/synthesize",
                json=req.model_dump(),
            )
            resp.raise_for_status()
            return Response(
                content=resp.content,
                media_type="audio/wav",
                headers={
                    k: v for k, v in resp.headers.items()
                    if k.lower().startswith("x-")
                },
            )
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="TTS-service niet beschikbaar")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.get("/api/tts/engines")
async def engines():
    """Proxy engine list from TTS service."""
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(f"{TTS_BASE}/engines")
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="TTS-service niet beschikbaar")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

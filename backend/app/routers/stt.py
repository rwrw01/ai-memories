import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter()
STT_URL = "http://stt:8001/api/stt"


@router.post("/api/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """Proxy audio upload to the STT service and return its transcription."""
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

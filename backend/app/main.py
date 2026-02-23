import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.stt import router as stt_router
from app.routers.tts import router as tts_router

logging.basicConfig(level=logging.INFO)

_origin = os.getenv("ORIGIN", "http://localhost:3000")
ALLOWED_ORIGINS = list({_origin, "http://localhost:3000", "http://127.0.0.1:3000"})

app = FastAPI(title="Memories Backend", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(stt_router)
app.include_router(tts_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "memories-backend"}

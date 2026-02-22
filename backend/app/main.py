import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.stt import load_model, router as stt_router

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the Parakeet model in a thread so the event loop stays free
    await asyncio.to_thread(load_model)
    yield


app = FastAPI(title="Memories Backend", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stt_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "memories-backend"}

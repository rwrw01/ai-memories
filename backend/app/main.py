import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers.health import check_all as health_check_all
from app.routers.llm import router as llm_router
from app.routers.news import router as news_router
from app.routers.news_ingest import router as news_ingest_router
from app.routers.stt import router as stt_router
from app.routers.tts import router as tts_router
from app.services.cleanup_service import daily_cleanup_loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_origin = os.getenv("ORIGIN", "http://localhost:3000")
ALLOWED_ORIGINS = list({_origin, "http://localhost:3000", "http://127.0.0.1:3000"})


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database ready")
    cleanup_task = asyncio.create_task(daily_cleanup_loop())
    yield
    cleanup_task.cancel()


app = FastAPI(title="Memories Backend", version="0.5.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH"],
    allow_headers=["Content-Type"],
)

app.include_router(stt_router)
app.include_router(tts_router)
app.include_router(llm_router)
app.include_router(news_router)
app.include_router(news_ingest_router)


@app.get("/health")
async def health_simple() -> dict:
    """Quick liveness probe for Docker / load balancers."""
    return {"status": "ok", "service": "memories-backend"}


@app.get("/api/health")
async def health_detailed() -> dict:
    """Deep health check — probes all downstream services in parallel."""
    return await health_check_all()

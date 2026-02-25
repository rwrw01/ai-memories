import asyncio
import logging
import os
from datetime import datetime, timezone

import httpx
from sqlalchemy import text

from app.database import async_session

logger = logging.getLogger(__name__)

STT_URL = os.getenv("STT_HEALTH_URL", "http://stt:8001/health")
TTS_URL = os.getenv("TTS_HEALTH_URL", "http://tts:8002/health")
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
N8N_URL = os.getenv("N8N_HEALTH_URL", "http://n8n:5678/healthz")

# Thresholds in seconds
TIMEOUT = 5
SLOW_THRESHOLD = 3


async def _check_database() -> dict:
    """Check database connectivity with a simple query."""
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        logger.error("Health check failed: database — %s", e)
        return {"status": "down"}


async def _check_http(name: str, url: str) -> dict:
    """Check an HTTP service. Returns ok/slow/down."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            elapsed = resp.elapsed.total_seconds()
            if elapsed > SLOW_THRESHOLD:
                logger.warning("Health check slow: %s (%.1fs)", name, elapsed)
                return {"status": "slow"}
            return {"status": "ok"}
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logger.error("Health check failed: %s — %s", name, e)
        return {"status": "down"}


async def check_all() -> dict:
    """Run all health checks in parallel and aggregate results."""
    db, stt, tts, ollama, n8n = await asyncio.gather(
        _check_database(),
        _check_http("stt", STT_URL),
        _check_http("tts", TTS_URL),
        _check_http("ollama", f"{OLLAMA_URL}/api/tags"),
        _check_http("n8n", N8N_URL),
    )

    services = {
        "database": db,
        "stt": stt,
        "tts": tts,
        "ollama": ollama,
        "n8n": n8n,
    }

    all_ok = all(s["status"] == "ok" for s in services.values())
    overall = "ok" if all_ok else "degraded"

    return {
        "status": overall,
        "services": services,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }

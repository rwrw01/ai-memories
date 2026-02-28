import logging
import os

import httpx
from fastapi import APIRouter

from app.services.http_client import service_retry

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/whatsapp")

WHATSAPP_BASE = os.getenv("WHATSAPP_BASE_URL", "http://whatsapp-web:3001")


@service_retry
async def _whatsapp_get(path: str) -> dict:
    """GET request to WhatsApp service with retry."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{WHATSAPP_BASE}{path}")
        resp.raise_for_status()
        return resp.json()


@router.get("/status")
async def whatsapp_status() -> dict:
    """WhatsApp connection status."""
    try:
        return await _whatsapp_get("/status")
    except Exception as e:
        logger.warning("WhatsApp status check failed: %s", e)
        return {"ready": False, "hasQr": False, "error": "Service niet beschikbaar"}


@router.get("/qr")
async def whatsapp_qr() -> dict:
    """Get QR code for WhatsApp authentication."""
    try:
        return await _whatsapp_get("/qr")
    except Exception as e:
        logger.warning("WhatsApp QR fetch failed: %s", e)
        return {"ready": False, "qr": None, "error": "Service niet beschikbaar"}


@router.post("/pair")
async def whatsapp_pair(body: dict) -> dict:
    """Request pairing code for phone number linking."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{WHATSAPP_BASE}/pair",
                json=body,
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.warning("WhatsApp pair request failed: %s", e)
        return {"error": "Koppeling mislukt, probeer opnieuw"}


@router.get("/contacts")
async def whatsapp_contacts() -> list | dict:
    """List WhatsApp contacts."""
    try:
        return await _whatsapp_get("/contacts")
    except Exception as e:
        logger.warning("WhatsApp contacts fetch failed: %s", e)
        return {"error": "Service niet beschikbaar"}

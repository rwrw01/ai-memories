import os
import secrets

from fastapi import HTTPException, Request

API_KEY = os.getenv("API_KEY", "")
INTERNAL_KEY = os.getenv("INTERNAL_KEY", "")

PUBLIC_PATHS = frozenset({"/health"})


async def verify_request(request: Request):
    """Verify API key for non-public endpoints."""
    if request.url.path in PUBLIC_PATHS:
        return

    key = request.headers.get("X-API-Key") or request.headers.get("X-Internal-Key")
    if not key:
        raise HTTPException(401, "API key vereist")

    valid = (API_KEY and secrets.compare_digest(key, API_KEY)) or (
        INTERNAL_KEY and secrets.compare_digest(key, INTERNAL_KEY)
    )
    if not valid:
        raise HTTPException(403, "Ongeldige API key")

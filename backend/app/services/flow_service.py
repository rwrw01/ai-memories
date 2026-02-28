import json
import logging
import os

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.flow import FlowExecution
from app.services.http_client import service_retry

logger = logging.getLogger(__name__)
N8N_BASE = os.getenv("N8N_WEBHOOK_URL", "http://n8n:5678")

# Intent -> n8n webhook path mapping
FLOW_WEBHOOKS: dict[str, str] = {
    "whatsapp": "/webhook/flow-whatsapp",
    "artikel": "/webhook/flow-artikel",
}


async def create_execution(
    session: AsyncSession, intent: str, params: dict, source_text: str
) -> FlowExecution:
    """Create a new flow execution record."""
    execution = FlowExecution(
        intent=intent,
        params_json=json.dumps(params, ensure_ascii=False),
        source_text=source_text,
        status="pending",
    )
    session.add(execution)
    await session.commit()
    await session.refresh(execution)
    return execution


async def execute_flow(session: AsyncSession, execution_id: str) -> FlowExecution:
    """Execute a flow by calling the appropriate n8n webhook."""
    stmt = select(FlowExecution).where(FlowExecution.id == execution_id)
    result = await session.execute(stmt)
    execution = result.scalar_one_or_none()
    if not execution:
        raise ValueError(f"Execution {execution_id} not found")

    # "aantekening" is stored directly, no n8n call needed
    if execution.intent == "aantekening":
        execution.status = "success"
        execution.result_json = json.dumps({"saved": True})
        await session.commit()
        return execution

    webhook_path = FLOW_WEBHOOKS.get(execution.intent)
    if not webhook_path:
        execution.status = "error"
        execution.error = f"Onbekend intent: {execution.intent}"
        await session.commit()
        return execution

    execution.status = "running"
    await session.commit()

    try:
        payload = {
            "execution_id": execution.id,
            "intent": execution.intent,
            "params": json.loads(execution.params_json),
            "source_text": execution.source_text,
        }
        resp = await _call_n8n(f"{N8N_BASE}{webhook_path}", payload)
        execution.status = "success"
        execution.result_json = json.dumps(resp, ensure_ascii=False)
    except Exception as e:
        logger.error("Flow execution failed for %s: %s", execution.id, e)
        execution.status = "error"
        execution.error = str(e)

    await session.commit()
    await session.refresh(execution)
    return execution


async def get_execution(session: AsyncSession, execution_id: str) -> FlowExecution | None:
    """Get a flow execution by ID."""
    stmt = select(FlowExecution).where(FlowExecution.id == execution_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


@service_retry
async def _call_n8n(url: str, payload: dict) -> dict:
    """Call an n8n webhook with retry on transient errors."""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()

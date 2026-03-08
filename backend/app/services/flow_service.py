import json
import logging
import os

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.flow import FlowExecution
from app.models.uren import TimeEntry, TimeSheet
from app.services.http_client import service_retry

logger = logging.getLogger(__name__)
N8N_BASE = os.getenv("N8N_WEBHOOK_URL", "http://n8n:5678")
NER_BASE = os.getenv("NER_SERVICE_URL", "http://ner:8004")
INTERNAL_KEY = os.getenv("INTERNAL_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

# Intent -> n8n webhook path mapping
FLOW_WEBHOOKS: dict[str, str] = {
    "whatsapp": "/webhook/flow-whatsapp",
    "artikel": "/webhook/flow-artikel",
    "aantekening": "/webhook/flow-aantekening",
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

    # Intents handled directly (no n8n webhook needed)
    DIRECT_INTENTS = {"artikel", "uren"}

    if execution.intent not in DIRECT_INTENTS:
        webhook_path = FLOW_WEBHOOKS.get(execution.intent)
        if not webhook_path:
            execution.status = "error"
            execution.error = f"Onbekend intent: {execution.intent}"
            await session.commit()
            return execution

    execution.status = "running"
    await session.commit()

    try:
        params = json.loads(execution.params_json)

        if execution.intent == "artikel":
            resp = await _generate_article(params, execution.source_text)
        elif execution.intent == "uren":
            resp = await _parse_uren(execution.source_text)
        else:
            webhook_path = FLOW_WEBHOOKS[execution.intent]
            payload = {
                "execution_id": execution.id,
                "intent": execution.intent,
                "params": params,
                "source_text": execution.source_text,
            }
            resp = await _call_n8n(f"{N8N_BASE}{webhook_path}", payload)

        execution.status = "success"
        execution.result_json = json.dumps(resp, ensure_ascii=False)

        if execution.intent == "artikel":
            await _save_article(session, execution, resp)
        elif execution.intent == "uren":
            await _save_timesheet(session, execution, resp)
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


async def _save_article(
    session: AsyncSession, execution: FlowExecution, resp: dict,
) -> None:
    """Extract article text from flow response and save to articles table."""
    article_text = resp.get("article_text", "")
    if not article_text:
        return
    lines = article_text.strip().split("\n", 1)
    title = lines[0].strip().lstrip("#").strip()
    content = lines[1].strip() if len(lines) > 1 else title
    article = Article(
        title=title,
        content=content,
        source_text=execution.source_text,
        flow_execution_id=execution.id,
    )
    session.add(article)


async def _generate_article(params: dict, source_text: str) -> dict:
    """Call Anthropic API directly to generate an article."""
    onderwerp = params.get("onderwerp", source_text)
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            ANTHROPIC_URL,
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-5-20250929",
                "max_tokens": 4096,
                "system": (
                    "Je bent een Nederlandse artikelschrijver. Schrijf een goed leesbaar, "
                    "informatief artikel over het gegeven onderwerp. Gebruik eenvoudig "
                    "Nederlands (B1-B2 niveau). Begin met een pakkende titel, dan een "
                    "lege regel, dan de volledige artikeltekst. Gebruik paragrafen en "
                    "tussenkopjes waar nodig."
                ),
                "messages": [
                    {"role": "user", "content": f"Onderwerp: {onderwerp}\n\nBrontekst: {source_text}"}
                ],
            },
        )
        resp.raise_for_status()
        data = resp.json()
    article_text = data["content"][0]["text"]
    return {"article_text": article_text, "status": "success"}


async def _parse_uren(source_text: str) -> dict:
    """Call local NER service to extract structured time entries from Dutch text."""
    headers = {"X-Internal-Key": INTERNAL_KEY} if INTERNAL_KEY else {}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{NER_BASE}/extract",
            json={"domain": "uren", "text": source_text},
            headers=headers,
        )
        resp.raise_for_status()
        return resp.json()


async def _save_timesheet(
    session: AsyncSession, execution: FlowExecution, resp: dict,
) -> None:
    """Save parsed time entries to the time_sheets and time_entries tables."""
    entries = resp.get("entries", [])
    if not entries:
        return
    sheet = TimeSheet(
        source_text=execution.source_text,
        flow_execution_id=execution.id,
    )
    session.add(sheet)
    await session.flush()  # get sheet.id for FK

    for e in entries:
        entry = TimeEntry(
            time_sheet_id=sheet.id,
            start_tijd=e.get("start", ""),
            eind_tijd=e.get("eind", ""),
            omschrijving=e.get("omschrijving", ""),
            duur_minuten=e.get("duur_minuten", 0),
        )
        session.add(entry)


@service_retry
async def _call_n8n(url: str, payload: dict) -> dict:
    """Call an n8n webhook with retry on transient errors."""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()

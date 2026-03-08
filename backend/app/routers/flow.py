import json

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.database import async_session
from app.models.flow import FlowExecution
from app.schemas.flow import FlowExecuteRequest, FlowExecuteResponse, FlowStatusResponse
from app.services.flow_service import create_execution, execute_flow, get_execution

router = APIRouter(prefix="/api/flow")


@router.post("/execute", response_model=FlowExecuteResponse)
async def execute_endpoint(req: FlowExecuteRequest) -> FlowExecuteResponse:
    """Create and execute a flow. Returns execution ID for status polling."""
    async with async_session() as session:
        execution = await create_execution(session, req.intent, req.params, req.source_text)
        execution = await execute_flow(session, execution.id)
        return FlowExecuteResponse(
            execution_id=execution.id,
            status=execution.status,
            message=_status_message(execution),
        )


@router.get("/status/{execution_id}", response_model=FlowStatusResponse)
async def status_endpoint(execution_id: str) -> FlowStatusResponse:
    """Poll the status of a flow execution."""
    async with async_session() as session:
        execution = await get_execution(session, execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Uitvoering niet gevonden")
        return FlowStatusResponse(
            execution_id=execution.id,
            status=execution.status,
            result=json.loads(execution.result_json) if execution.result_json else None,
            error=execution.error,
        )


@router.get("/recent")
async def recent_executions():
    """Return the 20 most recent flow executions (for pipeline monitor)."""
    async with async_session() as session:
        stmt = (
            select(FlowExecution)
            .order_by(FlowExecution.created_at.desc())
            .limit(20)
        )
        result = await session.execute(stmt)
        executions = result.scalars().all()
        return [
            {
                "id": ex.id,
                "intent": ex.intent,
                "status": ex.status,
                "error": ex.error,
                "source_text": ex.source_text[:100] if ex.source_text else "",
                "created_at": ex.created_at.isoformat() if ex.created_at else None,
            }
            for ex in executions
        ]


def _status_message(execution) -> str:
    """Generate a human-readable status message."""
    if execution.status == "success":
        return "Flow uitgevoerd"
    if execution.status == "error":
        return execution.error or "Uitvoering mislukt"
    return "Bezig..."

from typing import Literal

from pydantic import BaseModel, Field


# --- Classification ---


class ClassifyRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10_000)


class ClassifyResponse(BaseModel):
    intent: str
    params: dict
    confidence: float


# --- Flow execution ---


class FlowExecuteRequest(BaseModel):
    intent: Literal["whatsapp", "artikel", "aantekening", "uren"]
    params: dict = Field(default_factory=dict)
    source_text: str = Field(..., min_length=1, max_length=10_000)


class FlowExecuteResponse(BaseModel):
    execution_id: str
    status: str  # "pending" | "running" | "success" | "error"
    message: str


class FlowStatusResponse(BaseModel):
    execution_id: str
    status: str
    result: dict | None = None
    error: str | None = None

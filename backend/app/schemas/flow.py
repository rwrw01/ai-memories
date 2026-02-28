from pydantic import BaseModel


# --- Classification ---


class ClassifyRequest(BaseModel):
    text: str


class ClassifyResponse(BaseModel):
    intent: str  # "whatsapp" | "artikel" | "aantekening"
    params: dict
    confidence: float


# --- Flow execution ---


class FlowExecuteRequest(BaseModel):
    intent: str
    params: dict
    source_text: str


class FlowExecuteResponse(BaseModel):
    execution_id: str
    status: str  # "pending" | "running" | "success" | "error"
    message: str


class FlowStatusResponse(BaseModel):
    execution_id: str
    status: str
    result: dict | None = None
    error: str | None = None

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.llm_service import chat, summarize

router = APIRouter()


class SummarizeRequest(BaseModel):
    text: str


class SummarizeResponse(BaseModel):
    summary: str


class Message(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class ChatResponse(BaseModel):
    reply: str


@router.post("/api/summarize", response_model=SummarizeResponse)
async def summarize_endpoint(req: SummarizeRequest) -> SummarizeResponse:
    """Summarize a Dutch news article in 4 sentences."""
    summary = await summarize(req.text)
    return SummarizeResponse(summary=summary)


@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest) -> ChatResponse:
    """Chat with the LLM using a conversation history."""
    reply = await chat([m.model_dump() for m in req.messages])
    return ChatResponse(reply=reply)

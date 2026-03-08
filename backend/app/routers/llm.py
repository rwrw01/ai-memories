from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.llm_service import chat, summarize

router = APIRouter()


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=100_000)


class SummarizeResponse(BaseModel):
    summary: str


class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., max_length=50_000)


class ChatRequest(BaseModel):
    messages: list[Message] = Field(..., min_length=1, max_length=50)


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

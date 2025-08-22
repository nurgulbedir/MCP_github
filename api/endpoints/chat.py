from fastapi import APIRouter
from pydantic import BaseModel
from llm.orchestrator import run_orchestration
from typing import List, Dict, Any
from fastapi.responses import StreamingResponse

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    chat_history: List[Dict[str, Any]] = []  # Opsiyonel chat_history alanı

class ChatResponse(BaseModel):
    reply: str
@router.post("/query", response_model=ChatResponse)
async def handle_stream_chat(request: ChatRequest):
    return StreamingResponse(
        run_orchestration(
            user_message=request.message,
            chat_history=request.chat_history
        ),
        media_type="text/event-stream"
    )
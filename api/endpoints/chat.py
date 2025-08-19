from fastapi import APIRouter
from pydantic import BaseModel
from llm.orchestrator import run_orchestration

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("/query", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    """
    Kullanıcıdan gelen sorguyu alır, orkestratöre gönderir ve cevabı döndürür.
    """
    final_reply = run_orchestration(request.message)
    return ChatResponse(reply=final_reply)
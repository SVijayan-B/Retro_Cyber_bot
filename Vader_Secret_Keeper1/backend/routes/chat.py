# backend/routes/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.core.emotiongendect import ENGINE

from backend.core.memory_manager import MEMORY

router = APIRouter(tags=["chat"])

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Client session id")
    message: str = Field("", description="User message")

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    question: str = ""
    chapter: int = 0
    unlocked: bool = False

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    sid = (req.session_id or "").strip()
    msg = (req.message or "").strip()
    if not sid:
        raise HTTPException(status_code=400, detail="session_id required")

    # new session or explicit begin -> story
    state = MEMORY.get(sid, {"chapter": 0})
    if state.get("chapter", 0) == 0 or msg.lower() in ("begin", "start", "story"):
        resp = ENGINE.step(sid, msg)
        return ChatResponse(
            session_id=resp.get("session_id"),
            reply=resp.get("reply",""),
            question=resp.get("question",""),
            chapter=resp.get("chapter",0),
            unlocked=bool(resp.get("unlocked", False))
        )

    # otherwise treat as answer to current question
    resp = ENGINE.answer(sid, msg)
    return ChatResponse(
        session_id=resp.get("session_id"),
        reply=resp.get("reply",""),
        question=resp.get("question",""),
        chapter=resp.get("chapter",0),
        unlocked=bool(resp.get("unlocked", False))
    )


from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import APP_NAME, ALLOWED_ORIGINS
from backend.routes.chat import router as chat_router

app = FastAPI(
    title=f"{APP_NAME} API",
    version="0.1.0",
    description="Retro-cyber Sith trial chatbot (Phase 1–3 skeleton)."
)

# CORS (frontend will run on a different port later)
allow = ["*"] if ALLOWED_ORIGINS == ["*"] else ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "service": APP_NAME}

app.include_router(chat_router, prefix="/api")

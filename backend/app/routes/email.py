"""Email generation API routes."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.config import AVAILABLE_MODELS, GROQ_API_KEY
from app.schemas import EmailRequest, EmailResponse
from app.services.auth import get_current_user
from app.services.email_generation import (
    generate_email,
    generate_stream_text,
    get_history,
    resolve_provider,
)

router = APIRouter()


@router.get("/")
def root():
    return {
        "status": "ok",
        "message": "AI Email Generator API is running",
        "provider": resolve_provider(),
    }


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "groq_configured": GROQ_API_KEY is not None,
        "provider": resolve_provider(),
    }


@router.get("/models")
def list_models():
    return {"models": AVAILABLE_MODELS}


@router.post("/generate", response_model=EmailResponse)
def generate_email_route(request: EmailRequest, username: str = Depends(get_current_user)):
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    return generate_email(request, username)


@router.post("/generate/stream")
def generate_email_stream(request: EmailRequest, username: str = Depends(get_current_user)):
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    return StreamingResponse(generate_stream_text(request), media_type="text/plain")


@router.get("/history")
def get_history_route(username: str = Depends(get_current_user)):
    return {"history": get_history(username)}

"""Pydantic request and response models."""

from pydantic import BaseModel, Field
from typing import Optional


class EmailRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    tone: str = "Professional"
    model: Optional[str] = None  # Optional — uses default if not provided


class EmailResponse(BaseModel):
    subject: str
    body: str
    provider: str
    model: str


class HistoryItem(BaseModel):
    prompt: str
    tone: str
    subject: str
    provider: str
    model: str
    created_at: str


# --- Authentication schemas ---

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    message: str
    username: str
    token: str


class UserInfo(BaseModel):
    username: str

"""Application configuration and environment loading."""

import os

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq").strip().lower()
AI_MODEL = os.getenv("AI_MODEL", "llama-3.1-8b-instant").strip()

# Available Groq models for multi-model support
AVAILABLE_MODELS = [
    {"id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B Instant", "description": "Fast, lightweight — priority model"},
    {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B Versatile", "description": "Larger model — higher quality output"},
]

AVAILABLE_MODEL_IDS = [m["id"] for m in AVAILABLE_MODELS]

# JWT Authentication config
JWT_SECRET = os.getenv("JWT_SECRET", "ai-email-gen-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
try:
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
except ValueError:
    JWT_EXPIRE_MINUTES = 60 * 24  # default to 24 hours

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017").strip()
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "ai_email_generator").strip()

# CORS allowed origins
cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:3000")
CORS_ORIGINS = [origin.strip() for origin in cors_raw.split(",") if origin.strip()]

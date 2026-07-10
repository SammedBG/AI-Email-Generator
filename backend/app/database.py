"""MongoDB connection setup and collections initialization."""

import logging
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGODB_URL, MONGODB_DB_NAME

logger = logging.getLogger("uvicorn")

try:
    client = AsyncIOMotorClient(
        MONGODB_URL,
        serverSelectionTimeoutMS=2000,
        tlsCAFile=certifi.where()
    )
except Exception as e:
    logger.warning(f"Could not load certifi certs, initializing default MotorClient: {e}")
    client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=2000)

db = client[MONGODB_DB_NAME]

users_collection = db["users"]
history_collection = db["history"]

_connected = False
_checked = False


async def is_mongodb_available() -> bool:
    """Check if MongoDB is available. Caches the result to avoid ping overhead."""
    global _connected, _checked
    if _checked:
        return _connected

    try:
        await client.admin.command("ping")
        _connected = True
        logger.info(f"Successfully connected to MongoDB at {MONGODB_URL}")
    except Exception as e:
        _connected = False
        logger.warning(f"MongoDB not available: {e}. Falling back to in-memory storage.")

    _checked = True
    return _connected

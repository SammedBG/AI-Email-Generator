import bcrypt
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from fastapi import Cookie, Header, HTTPException, status

from app.config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET
from app.database import users_collection, is_mongodb_available

# In-memory user store fallback: {username: str (hashed_password)}
users_db: dict[str, str] = {}


def hash_password(password: str) -> str:
    # bcrypt expects bytes for both password and salt
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_bytes.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> str | None:
    """Decode JWT and return the username, or None if invalid."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


async def register_user(username: str, password: str) -> str:
    """Register a new user. Returns the JWT token."""
    username_lower = username.lower()
    hashed = hash_password(password)

    if await is_mongodb_available():
        existing = await users_collection.find_one({"_id": username_lower})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )
        await users_collection.insert_one({"_id": username_lower, "password": hashed})
    else:
        if username_lower in users_db:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )
        users_db[username_lower] = hashed

    return create_token(username_lower)


async def login_user(username: str, password: str) -> str:
    """Authenticate user. Returns the JWT token."""
    username_lower = username.lower()
    stored_hash = None

    if await is_mongodb_available():
        user_doc = await users_collection.find_one({"_id": username_lower})
        if user_doc:
            stored_hash = user_doc.get("password")
    else:
        stored_hash = users_db.get(username_lower)

    if not stored_hash or not verify_password(password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return create_token(username_lower)


def get_current_user(
    access_token: str | None = Cookie(default=None),
    authorization: str | None = Header(default=None),
) -> str:
    """FastAPI dependency — extracts username from Bearer header or httpOnly cookie."""
    token = None

    # 1. Try Authorization header first (works cross-origin on all browsers)
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()

    # 2. Fall back to httpOnly cookie
    if not token and access_token:
        token = access_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated — please log in",
        )

    username = decode_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired — please log in again",
        )

    return username


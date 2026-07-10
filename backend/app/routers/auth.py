"""Authentication API routes."""

from fastapi import APIRouter, Depends, Response

from app.config import COOKIE_SECURE
from app.schemas import LoginRequest, RegisterRequest, TokenResponse, UserInfo
from app.services.auth import create_token, get_current_user, login_user, register_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _set_token_cookie(response: Response, token: str) -> None:
    """Set the JWT as an httpOnly cookie."""
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
        max_age=60 * 60 * 24,  # 24 hours
        path="/",
    )


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, response: Response):
    token = await register_user(request.username, request.password)
    _set_token_cookie(response, token)
    return TokenResponse(message="Account created successfully", username=request.username.lower())


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, response: Response):
    token = await login_user(request.username, request.password)
    _set_token_cookie(response, token)
    return TokenResponse(message="Logged in successfully", username=request.username.lower())


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserInfo)
def me(username: str = Depends(get_current_user)):
    return UserInfo(username=username)

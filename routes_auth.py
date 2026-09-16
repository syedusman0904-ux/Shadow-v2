from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from .config import settings
from .database import get_db
from .deps import get_current_user
from .models import User, UserSession
from .schemas import AuthResponse, LoginRequest, RegisterRequest, UserOut
from .security import (
    create_access_token,
    hash_password,
    hash_refresh_token,
    new_refresh_token,
    verify_password,
)


router = APIRouter(prefix="/auth", tags=["authentication"])
COOKIE_NAME = "shadow_refresh"


def set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=settings.refresh_token_days * 86400,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/auth",
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/auth")


async def create_session(db: AsyncSession, user: User) -> tuple[str, UserSession]:
    token = new_refresh_token()
    session = UserSession(
        user_id=user.id,
        refresh_token_hash=hash_refresh_token(token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_days),
    )
    db.add(session)
    await db.flush()
    return token, session


def auth_response(user: User) -> AuthResponse:
    return AuthResponse(access_token=create_access_token(str(user.id)), user=UserOut.model_validate(user))


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(User).where(User.username == data.username))
    if existing:
        raise HTTPException(status_code=409, detail="Username is already in use")

    user = User(
        username=data.username,
        display_name=data.display_name.strip(),
        password_hash=hash_password(data.password),
    )
    db.add(user)
    await db.flush()

    refresh_token, _ = await create_session(db, user)
    await db.commit()
    await db.refresh(user)

    set_refresh_cookie(response, refresh_token)
    return auth_response(user)


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.username == data.username))

    # Keep login errors generic so account existence is not unnecessarily exposed.
    if not user or not user.is_active or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    refresh_token, _ = await create_session(db, user)
    await db.commit()

    set_refresh_cookie(response, refresh_token)
    return auth_response(user)


@router.post("/refresh", response_model=AuthResponse)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Refresh session missing")

    session = await db.scalar(
        select(UserSession).where(UserSession.refresh_token_hash == hash_refresh_token(token))
    )
    now = datetime.now(timezone.utc)

    if not session or session.revoked or session.expires_at <= now:
        clear_refresh_cookie(response)
        raise HTTPException(status_code=401, detail="Refresh session expired")

    user = await db.scalar(select(User).where(User.id == session.user_id, User.is_active.is_(True)))
    if not user:
        clear_refresh_cookie(response)
        raise HTTPException(status_code=401, detail="Invalid session")

    # Rotate refresh token to reduce replay risk.
    session.revoked = True
    new_token, _ = await create_session(db, user)
    await db.commit()

    set_refresh_cookie(response, new_token)
    return auth_response(user)


@router.post("/logout", status_code=204)
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        session = await db.scalar(
            select(UserSession).where(UserSession.refresh_token_hash == hash_refresh_token(token))
        )
        if session:
            session.revoked = True
            await db.commit()
    clear_refresh_cookie(response)
    return Response(status_code=204)


@router.post("/logout-all", status_code=204)
async def logout_all(
    response: Response,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        update(UserSession)
        .where(UserSession.user_id == user.id, UserSession.revoked.is_(False))
        .values(revoked=True)
    )
    await db.commit()
    clear_refresh_cookie(response)
    return Response(status_code=204)

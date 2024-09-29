"""Routes that deal with user sessions."""

import logging
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.responses import PlainTextResponse
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from anime_rest_api.api.common_query import requesting_user_header
from anime_rest_api.api.common_query import security
from anime_rest_api.api.dependencies import DbDependency
from anime_rest_api.api.models import LoginRequest
from anime_rest_api.api.models import LoginResponse
from anime_rest_api.api.models import RefreshRequest
from anime_rest_api.api.models import RefreshResponse
from anime_rest_api.api.models.sessions import JWTError
from anime_rest_api.api.models.sessions import JwtUser
from anime_rest_api.api.models.sessions import build_access_token
from anime_rest_api.api.models.sessions import build_refresh_token
from anime_rest_api.api.models.sessions import decode_access_token
from anime_rest_api.api.models.sessions import decode_refresh_token
from anime_rest_api.api.models.sessions import epoch_now
from anime_rest_api.db.crud.errors import EntryNotFoundError
from anime_rest_api.db.crud.user_operations import get_user
from anime_rest_api.db.crud.user_operations import get_user_login
from anime_rest_api.db.crud.user_operations import increment_user_session_version

ROUTER = APIRouter()
LOG = logging.getLogger(f"anime-api.{__name__}")


@ROUTER.post("/login", response_model=LoginResponse)
async def login_route(
    login: LoginRequest,
    session: Annotated[AsyncSession, DbDependency],
):
    """Login a user."""
    try:
        user = await get_user_login(session, login.username, login.password)
    except EntryNotFoundError as e:
        LOG.exception("Invalid login attempt for user %s", login.username)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password",
        ) from e
    access_token = build_access_token(user)
    refresh_token = build_refresh_token(user, access_token=access_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@ROUTER.post("/refresh", response_model=RefreshResponse)
async def refresh_route(
    tokens: RefreshRequest,
    session: Annotated[AsyncSession, DbDependency],
    user_credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    """Refresh a user session."""
    try:
        decoded = decode_refresh_token(
            tokens.refresh_token,
            user_credentials.credentials,
        )
    except JWTError as e:
        LOG.exception("Invalid refresh token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token",
        ) from e
    if decoded.expires_at < epoch_now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token",
        )
    requesting_user = decode_access_token(
        user_credentials.credentials,
        verify_exp=False,
    )
    user = await get_user(session, int(requesting_user.user_id))
    # make sure that this refresh token is valid for current login session
    if user.session_version != decoded.session_version:
        LOG.error(
            "Session version id mismatch between refresh token (%d) and user (%d)",
            decoded.session_version,
            user.session_version,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token",
        )
    access_token = build_access_token(user)
    refresh_token = build_refresh_token(user, access_token=access_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@ROUTER.post("/logout", response_model=None)
async def logout_route(
    session: Annotated[AsyncSession, DbDependency],
    user_credentials: Annotated[JwtUser, Depends(requesting_user_header)],
):
    """Logout a user.

    Doesn't need any body data, as the necessary info comes in JWT bearer.
    """
    # TODO(@rhyn0): need to add a 'session_version' flag on User table.
    # This way, we can invalidate all sessions by incrementing this flag.
    try:
        await increment_user_session_version(session, user_credentials.user_id)
    except EntryNotFoundError as e:
        LOG.exception("Invalid logout attempt for user %s", user_credentials.username)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid logout target",
        ) from e
    return PlainTextResponse("Success")

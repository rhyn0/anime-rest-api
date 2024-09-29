from datetime import UTC
from datetime import datetime
from datetime import timedelta
import logging
import os
from typing import Annotated
from typing import Literal

from jose import jwt
from jose.exceptions import JWTError
from pydantic import Field

from anime_rest_api.db.models.auth.user import UserRead

from .base import Base

LOG = logging.getLogger(f"anime-api.{__name__}")
LOG.setLevel(logging.DEBUG)

# raises KeyError if not set, is required
_SECRET = os.environ["ANIME_API_SECRET"]
_ACCESS_TOKEN_LIFETIME = timedelta(minutes=15)
_REFRESH_TOKEN_LIFETIME = timedelta(days=14)
_JWT_ISS = "anime_api"
_JWT_AUD = "anime_api"  # want this to be the API URL

__all__ = [
    "LoginRequest",
    "LoginResponse",
    "RefreshRequest",
    "RefreshResponse",
    "build_access_token",
    "build_refresh_token",
    "epoch_now",
    "decode_access_token",
    "JWTError",
]


class LoginRequest(Base):
    """Request to login a user."""

    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginResponse(Base):
    """Response to a login request."""

    access_token: Annotated[
        str,
        Field(..., min_length=32, description="JWT access token."),
    ]
    """JWT access token."""
    refresh_token: Annotated[
        str,
        Field(..., min_length=32, description="JWT refresh token."),
    ]
    """JWT refresh token."""
    expires_at: Annotated[
        int,
        Field(..., description="Access token expiration time."),
    ]
    """Access token expiration time."""
    refresh_expires_at: Annotated[
        int,
        Field(..., description="Refresh token expiration time."),
    ]
    """Refresh token expiration time."""
    version: Annotated[
        int,
        Field(..., description="User session version."),
    ]
    """User session version."""


class RefreshRequest(Base):
    """Request to refresh a JWT access token."""

    refresh_token: Annotated[
        str,
        Field(..., min_length=32, description="JWT refresh token."),
    ]
    """JWT refresh token."""


class RefreshResponse(LoginResponse):
    """Response to refresh a user session.

    Same fields as a login response.
    """


def epoch_now() -> int:
    """Return the current epoch time in seconds."""
    return int(datetime.now(UTC).timestamp())


def access_token_claims_from_user(user: UserRead) -> "ApiAccessJwt":
    """Build the model for an access token from a user."""
    now = epoch_now()
    return ApiAccessJwt(
        user=JwtUserDetails(
            username=user.username,
            email=user.email,
        ),
        user_id=str(user.user_id),
        issued_at=now,
        expires_at=now + int(_ACCESS_TOKEN_LIFETIME.total_seconds()),
        scope="access",
        aud=_JWT_AUD,
        iss=_JWT_ISS,
        role="admin" if user.is_admin else "user",
    )


def refresh_token_claims_from_user(user: UserRead) -> "ApiRefreshJwt":
    """Build the model for an access token from a user."""
    now = epoch_now()
    LOG.debug("Building refresh token for user %s. Issue at %d", user.user_id, now)
    return ApiRefreshJwt(
        user_id=str(user.user_id),
        issued_at=now,
        expires_at=now + int(_REFRESH_TOKEN_LIFETIME.total_seconds()),
        scope="refresh",
        aud=_JWT_AUD,
        iss=_JWT_ISS,
        session_version=user.session_version,
    )


def build_access_token(claims: dict) -> str:
    """Build a JWT access token for the user."""
    return jwt.encode(
        claims,
        _SECRET,
        algorithm="HS256",
    )


def build_refresh_token(claims: dict, access_token: str) -> str:
    """Build a refresh token for the user."""
    LOG.debug("Building refresh token with claims %s", claims)
    return jwt.encode(
        claims,
        _SECRET,
        algorithm="HS256",
        access_token=access_token,
    )


def decode_access_token(tok: str, *, verify_exp: bool = True) -> "ApiAccessJwt":
    """Parse a JWT access token for the user.

    If the token does not match our specifications, it will raise an error.

    Args:
        tok (str): JWT token to decode
        verify_exp (bool): Verify the expiration time of the token.

    Raises:
        jwt.exceptions.ExpiredSignatureError: If the token is expired.
        jwt.exceptions.InvalidSignatureError: If the token signature is invalid.
        jwt.exceptions.DecodeError: If the token is invalid.

    Returns:
        ApiAccessJwt: Decoded token
    """
    return ApiAccessJwt.model_validate(
        jwt.decode(
            tok,
            _SECRET,
            algorithms=["HS256"],
            audience=_JWT_AUD,
            issuer=_JWT_ISS,
            options={
                "require_aud": True,
                "require_iat": True,
                "require_exp": verify_exp,
                "require_sub": True,
                "require_iss": True,
            },
        ),
    )


def decode_refresh_token(refresh_tok: str) -> "ApiRefreshJwt":
    """Parse a JWT refresh token for the user.

    If the token does not match our specifications, it will raise an error.

    Args:
        refresh_tok (str): JWT token to decode
        access_tok (str): JWT access token to use for verification

    Raises:
        jwt.exceptions.ExpiredSignatureError: If the token is expired.
        jwt.exceptions.InvalidSignatureError: If the token signature is invalid.
        jwt.exceptions.DecodeError: If the token is invalid.

    Returns:
        ApiRefreshJwt: Decoded token
    """
    return ApiRefreshJwt.model_validate(
        jwt.decode(
            refresh_tok,
            _SECRET,
            algorithms=["HS256"],
            audience=_JWT_AUD,
            issuer=_JWT_ISS,
            options={
                "require_aud": True,
                "require_iat": True,
                "require_exp": True,
                "require_sub": True,
                "require_iss": True,
                "require_at_hash": True,
            },
        ),
    )


class JwtUserDetails(Base):
    """User details to store inside a JWT."""

    username: str
    email: str


class ApiJwtBase(Base):
    """Simple JWT claims that are common to all tokens."""

    user_id: Annotated[str, Field(..., description="User ID.", alias="sub")]
    """User id - alias `sub`."""
    issued_at: Annotated[
        int,
        Field(..., description="Issued at epoch seconds.", alias="iat", gt=0),
    ]
    """Issued at epoch seconds - alias `iat`."""
    expires_at: Annotated[
        int,
        Field(..., description="Expires at epoch seconds.", alias="exp", gt=0),
    ]
    """Expires at epoch seconds - alias `exp`."""
    scope: Annotated[
        Literal["access", "refresh"],
        Field(..., description="Token scope."),
    ]
    """Which type of token."""
    aud: Annotated[str, Field(..., description="Audience.", alias="aud")]
    """Audience - alias `aud`."""
    iss: Annotated[str, Field(..., description="Issuer.", alias="iss")]
    """Issuer - alias `iss`."""


class ApiRefreshJwt(ApiJwtBase):
    """JWT claims for a refresh token."""

    scope: Annotated[
        Literal["refresh"],
        Field("refresh", description="Token scope."),
    ]
    """Which type of token. Always `refresh`."""
    session_version: Annotated[
        int,
        Field(..., description="Session version."),
    ]
    """User session version."""


class ApiAccessJwt(ApiJwtBase):
    """JWT claims for tokens issued from here."""

    user: JwtUserDetails
    scope: Annotated[Literal["access"], Field("access", description="Token scope.")]
    """Which type of token. Always `access`."""

    role: Annotated[Literal["admin", "user"], Field(..., description="User role.")]
    """User role. Either `admin` or `user`."""


class JwtUser(Base):
    """User details from a JWT."""

    user_id: int
    username: str
    email: str
    role: Literal["admin", "user"]
    iat: int
    exp: int

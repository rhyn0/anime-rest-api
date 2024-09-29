from typing import Annotated

from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
import jose

from anime_rest_api.api.models.sessions import JwtUser
from anime_rest_api.api.models.sessions import decode_access_token

security = HTTPBearer()


def limit_and_offset_query(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> tuple[int, int]:
    """Limit and offset query."""
    return limit, offset


async def requesting_user_header(
    user_credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> JwtUser:
    """Requesting user header."""
    if user_credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authentication schema",
        )

    try:
        contents = decode_access_token(user_credentials.credentials)
    except jose.JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        ) from e
    return JwtUser(
        user_id=int(contents.user_id),
        username=contents.user.username,
        email=contents.user.email,
        role=contents.role,
        iat=contents.issued_at,
        exp=contents.expires_at,
    )

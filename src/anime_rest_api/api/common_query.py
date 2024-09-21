import os
from typing import Annotated

from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from anime_rest_api.db.models.auth import UserRead
from anime_rest_api.db.models.auth.user import User

from .dependencies import DbDependency

security = HTTPBearer()


def limit_and_offset_query(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> tuple[int, int]:
    """Limit and offset query."""
    return limit, offset


async def requesting_user_header(
    user_credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[AsyncSession, DbDependency],
) -> UserRead:
    """Requesting user header."""
    if user_credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authentication schema",
        )

    contents = jwt.decode(
        user_credentials.credentials,
        os.environ["ANIME_API_SECRET"],
        algorithms=["HS256"],
    )
    result = await session.get(User, contents["user"]["id"])
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    return result  # type: ignore[return-value]

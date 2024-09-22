from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from anime_rest_api.api.common_query import limit_and_offset_query
from anime_rest_api.api.common_query import requesting_user_header
from anime_rest_api.api.dependencies import DbDependency
from anime_rest_api.api.models import UserResponseList
from anime_rest_api.api.models.sessions import JwtUser
from anime_rest_api.db.crud.user_operations import list_users

ROUTER = APIRouter(prefix="/users", tags=["users", "auth"])


@ROUTER.get("", response_model=UserResponseList)
async def list_users_route(
    *,
    limit_and_offset: tuple[int, int] = Depends(limit_and_offset_query),
    session: Annotated[AsyncSession, DbDependency],
    requesting_user: Annotated[JwtUser, Depends(requesting_user_header)],
):
    """List users in a paginated way."""
    limit, offset = limit_and_offset
    users = list(
        await list_users(
            session,
            offset,
            limit + 1,
            requesting_user.model_dump(by_alias=False),
        ),
    )
    has_more = len(users) > limit
    return UserResponseList(users=users[:limit], has_more=has_more)

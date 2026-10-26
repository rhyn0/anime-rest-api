from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from anime_rest_api.api.common_query import limit_and_offset_query
from anime_rest_api.api.common_query import requesting_user_header
from anime_rest_api.api.dependencies import DbDependency
from anime_rest_api.api.models.content_responses import UserShowStatusResponseList
from anime_rest_api.api.models.sessions import JwtUser
from anime_rest_api.db.crud.user_show_operations import create_user_show
from anime_rest_api.db.crud.user_show_operations import delete_user_show
from anime_rest_api.db.crud.user_show_operations import get_user_show
from anime_rest_api.db.crud.user_show_operations import list_user_shows
from anime_rest_api.db.crud.user_show_operations import update_user_show
from anime_rest_api.db.models.content.user_shows import UserShowStatusCreate
from anime_rest_api.db.models.content.user_shows import UserShowStatusRead
from anime_rest_api.db.models.content.user_shows import UserShowStatusUpdate

ROUTER = APIRouter(prefix="/user_shows", tags=["user_shows"])


@ROUTER.get("", response_model=UserShowStatusResponseList)
async def read_user_shows_route(
    *,
    limit_and_offset: tuple[int, int] = Depends(limit_and_offset_query),
    session: Annotated[AsyncSession, DbDependency],
    user_id: int | None = None,
) -> UserShowStatusResponseList:
    """Get all user show statuses."""
    limit, offset = limit_and_offset
    user_shows = list(await list_user_shows(session, offset, limit + 1, user_id))
    has_more = len(user_shows) > limit
    return UserShowStatusResponseList(user_shows=user_shows[:limit], has_more=has_more)


@ROUTER.post("", response_model=UserShowStatusRead)
async def create_user_show_route(
    user_show_body: UserShowStatusCreate,
    session: Annotated[AsyncSession, DbDependency],
) -> UserShowStatusRead:
    """Create a new user show status."""
    return await create_user_show(session, user_show_body)


@ROUTER.get("/{user_id}/{show_id}", response_model=UserShowStatusRead)
async def read_user_show_route(
    user_id: int,
    show_id: int,
    session: Annotated[AsyncSession, DbDependency],
    current_user: Annotated[JwtUser, Depends(requesting_user_header)],
) -> UserShowStatusRead:
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    """Get a user show status by user ID and show ID."""
    user_show = await get_user_show(session, user_id, show_id)
    if user_show is None:
        raise HTTPException(status_code=404, detail="UserShowStatus not found")
    return user_show


@ROUTER.patch("/{user_id}/{show_id}", response_model=UserShowStatusRead)
async def update_user_show_route(
    user_id: int,
    show_id: int,
    user_show_body: UserShowStatusUpdate,
    session: Annotated[AsyncSession, DbDependency],
    current_user: Annotated[JwtUser, Depends(requesting_user_header)],
) -> UserShowStatusRead:
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    """Update a user show status."""
    return await update_user_show(session, user_id, show_id, user_show_body)


@ROUTER.delete("/{user_id}/{show_id}", response_model=UserShowStatusRead)
async def delete_user_show_route(
    user_id: int,
    show_id: int,
    session: Annotated[AsyncSession, DbDependency],
    current_user: Annotated[JwtUser, Depends(requesting_user_header)],
) -> UserShowStatusRead:
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    """Delete a user show status."""
    return await delete_user_show(session, user_id, show_id)

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from anime_rest_api.api.common_query import limit_and_offset_query
from anime_rest_api.api.common_query import requesting_user_header
from anime_rest_api.api.dependencies import DbDependency
from anime_rest_api.api.models.content_responses import UserEpisodeRatingResponseList
from anime_rest_api.api.models.sessions import JwtUser
from anime_rest_api.db.crud.user_episode_operations import create_user_episode
from anime_rest_api.db.crud.user_episode_operations import delete_user_episode
from anime_rest_api.db.crud.user_episode_operations import get_user_episode
from anime_rest_api.db.crud.user_episode_operations import list_user_episodes
from anime_rest_api.db.crud.user_episode_operations import update_user_episode
from anime_rest_api.db.models.content.user_episodes import UserEpisodeRatingCreate
from anime_rest_api.db.models.content.user_episodes import UserEpisodeRatingRead
from anime_rest_api.db.models.content.user_episodes import UserEpisodeRatingUpdate

ROUTER = APIRouter(prefix="/user_episodes", tags=["user_episodes"])


@ROUTER.get("", response_model=UserEpisodeRatingResponseList)
async def read_user_episodes_route(
    *,
    limit_and_offset: tuple[int, int] = Depends(limit_and_offset_query),
    session: Annotated[AsyncSession, DbDependency],
    user_id: int | None = None,
) -> UserEpisodeRatingResponseList:
    """Get all user episode ratings."""
    limit, offset = limit_and_offset
    user_episodes = list(await list_user_episodes(session, offset, limit + 1, user_id))
    has_more = len(user_episodes) > limit
    return UserEpisodeRatingResponseList(
        user_episodes=user_episodes[:limit], has_more=has_more,  # type: ignore[arg-type]
    )


@ROUTER.post("", response_model=UserEpisodeRatingRead)
async def create_user_episode_route(
    user_episode_body: UserEpisodeRatingCreate,
    session: Annotated[AsyncSession, DbDependency],
) -> UserEpisodeRatingRead:
    """Create a new user episode rating."""
    return await create_user_episode(session, user_episode_body)  # type: ignore[return-value]


@ROUTER.get("/{user_id}/{episode_id}", response_model=UserEpisodeRatingRead)
async def read_user_episode_route(
    user_id: int,
    episode_id: int,
    session: Annotated[AsyncSession, DbDependency],
    current_user: Annotated[JwtUser, Depends(requesting_user_header)],
) -> UserEpisodeRatingRead:
    """Route operation."""
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    """Get a user episode rating by user ID and episode ID."""
    user_episode = await get_user_episode(session, user_id, episode_id)
    if user_episode is None:
        raise HTTPException(status_code=404, detail="UserEpisodeRating not found")
    return user_episode  # type: ignore[return-value]


@ROUTER.patch("/{user_id}/{episode_id}", response_model=UserEpisodeRatingRead)
async def update_user_episode_route(
    user_id: int,
    episode_id: int,
    user_episode_body: UserEpisodeRatingUpdate,
    session: Annotated[AsyncSession, DbDependency],
    current_user: Annotated[JwtUser, Depends(requesting_user_header)],
) -> UserEpisodeRatingRead:
    """Route operation."""
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    """Update a user episode rating."""
    return await update_user_episode(session, user_id, episode_id, user_episode_body)  # type: ignore[return-value]


@ROUTER.delete("/{user_id}/{episode_id}", response_model=UserEpisodeRatingRead)
async def delete_user_episode_route(
    user_id: int,
    episode_id: int,
    session: Annotated[AsyncSession, DbDependency],
    current_user: Annotated[JwtUser, Depends(requesting_user_header)],
) -> UserEpisodeRatingRead:
    """Route operation."""
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    """Delete a user episode rating."""
    return await delete_user_episode(session, user_id, episode_id)  # type: ignore[return-value]

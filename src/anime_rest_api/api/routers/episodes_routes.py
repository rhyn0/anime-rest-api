from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from anime_rest_api.api.common_query import limit_and_offset_query
from anime_rest_api.api.dependencies import DbDependency
from anime_rest_api.api.models.content_responses import EpisodeResponseList
from anime_rest_api.db.crud.episode_operations import create_episode
from anime_rest_api.db.crud.episode_operations import delete_episode
from anime_rest_api.db.crud.episode_operations import get_episode
from anime_rest_api.db.crud.episode_operations import list_episodes
from anime_rest_api.db.crud.episode_operations import update_episode
from anime_rest_api.db.models.content.episodes import EpisodeCreate
from anime_rest_api.db.models.content.episodes import EpisodeRead
from anime_rest_api.db.models.content.episodes import EpisodeUpdate

ROUTER = APIRouter(prefix="/episodes", tags=["episodes"])


@ROUTER.get("", response_model=EpisodeResponseList)
async def read_episodes_route(
    *,
    limit_and_offset: tuple[int, int] = Depends(limit_and_offset_query),
    session: Annotated[AsyncSession, DbDependency],
    show_id: int | None = None,
) -> EpisodeResponseList:
    """Get all episodes."""
    limit, offset = limit_and_offset
    episodes = list(await list_episodes(session, offset, limit + 1, show_id))
    has_more = len(episodes) > limit
    return EpisodeResponseList(episodes=episodes[:limit], has_more=has_more)


@ROUTER.post("", response_model=EpisodeRead)
async def create_episode_route(
    episode_body: EpisodeCreate,
    session: Annotated[AsyncSession, DbDependency],
) -> EpisodeRead:
    """Create a new episode."""
    return await create_episode(session, episode_body)


@ROUTER.get("/{episode_id}", response_model=EpisodeRead)
async def read_episode_route(
    episode_id: int,
    session: Annotated[AsyncSession, DbDependency],
) -> EpisodeRead:
    """Get an episode by its ID."""
    episode = await get_episode(session, episode_id)
    if episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode


@ROUTER.patch("/{episode_id}", response_model=EpisodeRead)
async def update_episode_route(
    episode_id: int,
    episode_body: EpisodeUpdate,
    session: Annotated[AsyncSession, DbDependency],
) -> EpisodeRead:
    """Update an episode by its ID."""
    return await update_episode(session, episode_id, episode_body)


@ROUTER.delete("/{episode_id}", response_model=EpisodeRead)
async def delete_episode_route(
    episode_id: int,
    session: Annotated[AsyncSession, DbDependency],
) -> EpisodeRead:
    """Delete an episode by its ID."""
    return await delete_episode(session, episode_id)

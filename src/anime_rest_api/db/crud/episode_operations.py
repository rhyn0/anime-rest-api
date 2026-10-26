from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from anime_rest_api.db.models.content.episodes import Episode
from anime_rest_api.db.models.content.episodes import EpisodeCreate
from anime_rest_api.db.models.content.episodes import EpisodeUpdate

from .errors import EntryNotFoundError


async def list_episodes(session: AsyncSession, offset: int, limit: int, show_id: int | None = None) -> Sequence[Episode]:
    """List episodes."""
    statement = select(Episode)
    if show_id is not None:
        statement = statement.where(Episode.show_id == show_id)
    statement = statement.order_by(Episode.episode_id).offset(offset).limit(limit)
    result = await session.execute(statement)
    return result.scalars().all()


async def get_episode(session: AsyncSession, episode_id: int) -> Episode | None:
    """Get an episode by its ID."""
    statement = select(Episode).where(Episode.episode_id == episode_id)
    result = await session.execute(statement)
    return result.scalars().first()


async def create_episode(session: AsyncSession, episode: EpisodeCreate) -> Episode:
    """Create an episode."""
    db_episode = Episode.model_validate(episode)
    session.add(db_episode)
    await session.commit()
    await session.refresh(db_episode)
    return db_episode


async def update_episode(session: AsyncSession, episode_id: int, episode: EpisodeUpdate) -> Episode:
    """Update an episode."""
    db_episode = await get_episode(session, episode_id)
    if db_episode is None:
        raise EntryNotFoundError(Episode.__tablename__, episode_id)
    db_episode.sqlmodel_update(episode.model_dump(exclude_unset=True))
    session.add(db_episode)
    await session.commit()
    await session.refresh(db_episode)
    return db_episode


async def delete_episode(session: AsyncSession, episode_id: int) -> Episode:
    """Delete an episode."""
    episode = await get_episode(session, episode_id)
    if episode is None:
        raise EntryNotFoundError(Episode.__tablename__, episode_id)
    await session.delete(episode)
    await session.commit()
    return episode

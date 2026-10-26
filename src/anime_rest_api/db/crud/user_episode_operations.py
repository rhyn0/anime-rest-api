from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from anime_rest_api.db.models.content.user_episodes import UserEpisodeRating
from anime_rest_api.db.models.content.user_episodes import UserEpisodeRatingCreate
from anime_rest_api.db.models.content.user_episodes import UserEpisodeRatingUpdate

from .errors import EntryNotFoundError


async def list_user_episodes(
    session: AsyncSession, offset: int, limit: int, user_id: int | None = None,
) -> Sequence[UserEpisodeRating]:
    """List user episode ratings."""
    statement = select(UserEpisodeRating)
    if user_id is not None:
        statement = statement.where(UserEpisodeRating.user_id == user_id)
    statement = statement.offset(offset).limit(limit)
    result = await session.execute(statement)
    return result.scalars().all()


async def get_user_episode(
    session: AsyncSession, user_id: int, episode_id: int,
) -> UserEpisodeRating | None:
    """Get a user episode rating by user ID and episode ID."""
    statement = select(UserEpisodeRating).where(
        UserEpisodeRating.user_id == user_id,
        UserEpisodeRating.episode_id == episode_id,
    )
    result = await session.execute(statement)
    return result.scalars().first()


async def create_user_episode(
    session: AsyncSession, user_episode: UserEpisodeRatingCreate,
) -> UserEpisodeRating:
    """Create a user episode rating."""
    db_user_episode = UserEpisodeRating.model_validate(user_episode)
    session.add(db_user_episode)
    await session.commit()
    await session.refresh(db_user_episode)
    return db_user_episode


async def update_user_episode(
    session: AsyncSession,
    user_id: int,
    episode_id: int,
    user_episode: UserEpisodeRatingUpdate,
) -> UserEpisodeRating:
    """Update a user episode rating."""
    db_user_episode = await get_user_episode(session, user_id, episode_id)
    if db_user_episode is None:
        raise EntryNotFoundError(
            UserEpisodeRating.__tablename__,
            f"user_id={user_id}, episode_id={episode_id}",
        )
    db_user_episode.sqlmodel_update(user_episode.model_dump(exclude_unset=True))
    session.add(db_user_episode)
    await session.commit()
    await session.refresh(db_user_episode)
    return db_user_episode


async def delete_user_episode(
    session: AsyncSession, user_id: int, episode_id: int,
) -> UserEpisodeRating:
    """Delete a user episode rating."""
    user_episode = await get_user_episode(session, user_id, episode_id)
    if user_episode is None:
        raise EntryNotFoundError(
            UserEpisodeRating.__tablename__,
            f"user_id={user_id}, episode_id={episode_id}",
        )
    await session.delete(user_episode)
    await session.commit()
    return user_episode

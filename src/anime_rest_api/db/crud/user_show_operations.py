from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from anime_rest_api.db.models.content.user_shows import UserShowStatus
from anime_rest_api.db.models.content.user_shows import UserShowStatusCreate
from anime_rest_api.db.models.content.user_shows import UserShowStatusUpdate

from .errors import EntryNotFoundError


async def list_user_shows(
    session: AsyncSession, offset: int, limit: int, user_id: int | None = None,
) -> Sequence[UserShowStatus]:
    """List user show statuses."""
    statement = select(UserShowStatus)
    if user_id is not None:
        statement = statement.where(UserShowStatus.user_id == user_id)
    statement = statement.offset(offset).limit(limit)
    result = await session.execute(statement)
    return result.scalars().all()


async def get_user_show(
    session: AsyncSession, user_id: int, show_id: int,
) -> UserShowStatus | None:
    """Get a user show status by user ID and show ID."""
    statement = select(UserShowStatus).where(
        UserShowStatus.user_id == user_id,
        UserShowStatus.show_id == show_id,
    )
    result = await session.execute(statement)
    return result.scalars().first()


async def create_user_show(
    session: AsyncSession, user_show: UserShowStatusCreate,
) -> UserShowStatus:
    """Create a user show status."""
    db_user_show = UserShowStatus.model_validate(user_show)
    session.add(db_user_show)
    await session.commit()
    await session.refresh(db_user_show)
    return db_user_show


async def update_user_show(
    session: AsyncSession, user_id: int, show_id: int, user_show: UserShowStatusUpdate,
) -> UserShowStatus:
    """Update a user show status."""
    db_user_show = await get_user_show(session, user_id, show_id)
    if db_user_show is None:
        raise EntryNotFoundError(
            UserShowStatus.__tablename__, f"user_id={user_id}, show_id={show_id}",
        )
    db_user_show.sqlmodel_update(user_show.model_dump(exclude_unset=True))
    session.add(db_user_show)
    await session.commit()
    await session.refresh(db_user_show)
    return db_user_show


async def delete_user_show(
    session: AsyncSession, user_id: int, show_id: int,
) -> UserShowStatus:
    """Delete a user show status."""
    user_show = await get_user_show(session, user_id, show_id)
    if user_show is None:
        raise EntryNotFoundError(
            UserShowStatus.__tablename__, f"user_id={user_id}, show_id={show_id}",
        )
    await session.delete(user_show)
    await session.commit()
    return user_show

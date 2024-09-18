from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from anime_rest_api.db.models.shows import Show
from anime_rest_api.db.models.shows import ShowCreate
from anime_rest_api.db.models.shows import ShowUpdate

from .errors import EntryNotFoundError


async def list_shows(session: AsyncSession, offset: int, limit: int) -> Sequence[Show]:
    """List shows."""
    # issue here where mypy detects that the column is int | None
    # but the database version is int
    statement = select(Show).order_by(Show.show_id).offset(offset).limit(limit)  # type: ignore[arg-type]
    result = await session.execute(statement)
    return result.scalars().all()


async def get_show(session: AsyncSession, show_id: int) -> Show | None:
    """Get a show by its ID."""
    statement = select(Show).where(Show.show_id == show_id)
    result = await session.execute(statement)
    return result.scalars().first()


async def create_show(session: AsyncSession, show: ShowCreate) -> Show:
    """Create a show."""
    session.add(show)
    await session.commit()
    await session.refresh(show)
    return show  # type: ignore[return-value]


async def update_show(session: AsyncSession, show_id: int, show: ShowUpdate) -> Show:
    """Update a show with only the fields that are set.

    Args:
        session (AsyncSession): Database session
        show_id (int): Show ID to update
        show (ShowUpdate): Wrapper of fields to set for the Show

    Raises:
        EntryNotFoundError: If show_id does not exist in table.

    Returns:
        Show: Updated model
    """
    db_show = await get_show(session, show_id)
    if db_show is None:
        raise EntryNotFoundError(Show.__tablename__, show_id)
    db_show.sqlmodel_update(show.model_dump(exclude_unset=True))
    session.add(db_show)
    await session.commit()
    await session.refresh(db_show)
    return db_show


async def delete_show(session: AsyncSession, show_id: int) -> Show:
    """Delete a show.

    Args:
        session (AsyncSession): Database session.
        show_id (int): ID of the show to delete.

    Raises:
        EntryNotFoundError: If show with ID does not exist.

    Returns:
        Show: Show that was deleted
    """
    show = await get_show(session, show_id)
    if show is None:
        raise EntryNotFoundError(Show.__tablename__, show_id)
    await session.delete(show)
    await session.commit()
    return show

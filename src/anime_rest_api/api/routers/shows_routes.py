from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from anime_rest_api.api.common_query import limit_and_offset_query
from anime_rest_api.api.dependencies import DbDependency
from anime_rest_api.api.models import ShowResponseList
from anime_rest_api.db.crud.show_operations import create_show
from anime_rest_api.db.crud.show_operations import delete_show
from anime_rest_api.db.crud.show_operations import get_show
from anime_rest_api.db.crud.show_operations import list_shows
from anime_rest_api.db.crud.show_operations import update_show
from anime_rest_api.db.models.content import ShowCreate
from anime_rest_api.db.models.content import ShowRead
from anime_rest_api.db.models.content import ShowUpdate

ROUTER = APIRouter(prefix="/shows", tags=["shows"])


@ROUTER.get("", response_model=ShowResponseList)
async def read_shows_route(
    *,
    limit_and_offset: tuple[int, int] = Depends(limit_and_offset_query),
    session: Annotated[AsyncSession, DbDependency],
) -> ShowResponseList:
    """Get all shows."""
    limit, offset = limit_and_offset
    shows = list(await list_shows(session, offset, limit + 1))
    has_more = len(shows) > limit
    return ShowResponseList(shows=shows[:limit], has_more=has_more)  # type: ignore[arg-type]


@ROUTER.post("", response_model=ShowRead)
async def create_show_route(
    show_body: ShowCreate,
    session: Annotated[AsyncSession, DbDependency],
) -> ShowRead:
    """Create a new show."""
    return await create_show(session, show_body)  # type: ignore[return-value]


@ROUTER.get("/{show_id}", response_model=ShowRead)
async def read_show_route(
    show_id: int,
    session: Annotated[AsyncSession, DbDependency],
) -> ShowRead:
    """Get a show by its ID."""
    # TODO(Ryan): this can raise an error if the show is not found
    # need to add a exception handler to app
    return await get_show(session, show_id)  # type: ignore[return-value]


@ROUTER.patch("/{show_id}", response_model=ShowRead)
async def update_show_route(
    show_id: int,
    show_body: ShowUpdate,
    session: Annotated[AsyncSession, DbDependency],
) -> ShowRead:
    """Update a show by its ID."""
    # TODO(Ryan): this can raise an error if the show is not found
    # need to add a exception handler to app
    return await update_show(session, show_id, show_body)  # type: ignore[return-value]


@ROUTER.delete("/{show_id}", response_model=ShowRead)
async def delete_show_route(
    show_id: int,
    session: Annotated[AsyncSession, DbDependency],
) -> ShowRead:
    """Delete a show by its ID."""
    # TODO(Ryan): this can raise an error if the show is not found
    # need to add a exception handler to app
    return await delete_show(session, show_id)  # type: ignore[return-value]

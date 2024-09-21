from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.schema import CreateSchema

from .connection import DatabaseConnection
from .errors import InvalidDbConnectionStateError
from .models.auth import AUTH_METADATA
from .models.content import CONTENT_METADATA

__all__ = [
    "DatabaseConnection",
    "InvalidDbConnectionStateError",
    "setup_db",
    "CONTENT_METADATA",
    "AUTH_METADATA",
]


async def setup_db(conn: AsyncConnection) -> None:
    """Setup the database."""
    for meta in [CONTENT_METADATA, AUTH_METADATA]:
        await conn.execute(CreateSchema(meta.schema, if_not_exists=True))
        await conn.run_sync(meta.create_all)

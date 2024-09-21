from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.schema import CreateSchema
from sqlalchemy.schema import DropSchema

from .connection import DatabaseConnection
from .errors import InvalidDbConnectionStateError
from .models.auth import AUTH_METADATA
from .models.content import CONTENT_METADATA

__all__ = [
    "DatabaseConnection",
    "InvalidDbConnectionStateError",
    "setup_db",
    "clean_db",
    "CONTENT_METADATA",
    "AUTH_METADATA",
]


async def setup_db(conn: AsyncConnection) -> None:
    """Setup the database."""
    # enable crytpography extension, for passwords
    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
    for meta in [CONTENT_METADATA, AUTH_METADATA]:
        await conn.execute(CreateSchema(meta.schema, if_not_exists=True))
        await conn.run_sync(meta.create_all)


async def clean_db(conn: AsyncConnection) -> None:
    """Drop all tables and schemas."""
    for meta in [CONTENT_METADATA, AUTH_METADATA]:
        await conn.run_sync(meta.drop_all)
        await conn.execute(DropSchema(meta.schema, cascade=True))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.schema import CreateSchema
from sqlalchemy.schema import DropSchema

from .connection import DatabaseConnection
from .errors import InvalidDbConnectionStateError
from .models import DB_METADATA
from .models import Show
from .models import ShowBase
from .models import ShowCreate
from .models import ShowRead
from .models import ShowUpdate

__all__ = [
    "DatabaseConnection",
    "Show",
    "ShowBase",
    "ShowCreate",
    "ShowRead",
    "ShowUpdate",
    "DB_METADATA",
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

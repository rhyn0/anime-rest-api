from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.schema import CreateSchema

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
]


async def setup_db(conn: AsyncConnection) -> None:
    """Setup the database."""
    await conn.execute(CreateSchema(DB_METADATA.schema, if_not_exists=True))
    await conn.run_sync(DB_METADATA.create_all)

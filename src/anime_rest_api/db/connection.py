from collections.abc import AsyncGenerator
import os
from typing import Self

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from .errors import InvalidDbConnectionStateError


class DatabaseConnection:
    """Wrapper object to hold database connection information."""

    _instance: Self

    def __new__(cls, *_args: tuple, **_kwargs: dict) -> Self:
        """Instantiate object in Singelton pattern.

        Raises error if instance already exists.
        """
        if hasattr(cls, "_instance"):
            msg = f"{cls.__name__}.__new__"
            raise InvalidDbConnectionStateError(msg)
        cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_url: str | URL | None, *, echo: bool = False) -> None:
        """Initialize DatabaseConnection object with database url.

        Args:
            db_url (str | URL | None): Source to build engine connection from.
                If not set, uses environment variables. Defaults to None.
            echo (bool, optional): Whether to echo SQL statements to stderr.
                Default False.
        """
        if db_url is None:
            return
        self.echo = echo
        self._engine = create_async_engine(db_url, echo=echo)
        self._session = async_sessionmaker(self._engine)

    def __repr__(self) -> str:
        """Debug representation of the object."""
        return f"{self.__class__.__name__}(url={self._engine.url.host!r}, echo={self.echo})"  # noqa: E501

    @classmethod
    def instance(cls) -> Self:
        """Return the instance of this class."""
        if not hasattr(cls, "_instance"):
            msg = f"{cls.__name__}.instance"
            raise InvalidDbConnectionStateError(msg)
        return cls._instance

    @property
    def engine(self) -> AsyncEngine:
        """Public getter for the engine."""
        return self._engine

    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Public getter for the session."""
        async with self._session() as session:
            yield session


Db = DatabaseConnection(os.getenv("ANIME_API_DATABASE_URL"), echo=False)

import os

from sqlalchemy import URL
from sqlalchemy import Engine
from sqlmodel import create_engine

from .errors import MissingDatabaseUrlError

_engine: Engine | None = None


def get_engine(*, url: str | URL | None = None, echo: bool = False) -> Engine:
    """Connect engine to database based on arguments.

    Caches engine to global scope so multiple calls to this function
    don't create more engines.

    Uses environment variable: ANIME_API_DATABASE_URL

    Args:
        url (str | URL | None, optional): Source to build engine connection from.
            If not set, uses environment variables. Defaults to None.
        echo (bool, optional): Whether to echo SQL statements to stderr. Default False.

    Raises:
        MissingDatabaseUrlError - if no connection url is provided.

    Returns:
        Engine: Database connection engine
    """
    global _engine  # noqa: PLW0603
    if _engine is not None:
        return _engine
    if url is None:
        try:
            url = os.environ["ANIME_API_DATABASE_URL"]
        except KeyError:
            raise MissingDatabaseUrlError from None

    _engine = create_engine(url, echo=echo)
    return _engine

import asyncio
from collections.abc import AsyncIterator
from collections.abc import Iterator

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.schema import DropSchema
from testcontainers.postgres import PostgresContainer
import uvloop

from anime_rest_api.api.app import create_app
from anime_rest_api.api.dependencies import Db
from anime_rest_api.db.connection import DatabaseConnection
from anime_rest_api.db.models.auth.base import AUTH_METADATA
from anime_rest_api.db.models.content.base import CONTENT_METADATA


@pytest.fixture(scope="session")
def pg_url() -> Iterator[str]:
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres.get_connection_url(driver="asyncpg")


@pytest.fixture(scope="module")
def monkey_mod() -> Iterator[pytest.MonkeyPatch]:
    """If you need to monkeypatch something that could be 'module' scoped, use this."""
    # External Party
    from _pytest.monkeypatch import MonkeyPatch

    monkey = MonkeyPatch()
    yield monkey
    monkey.undo()


@pytest.fixture(scope="module")
def pg_engine(
    pg_url: str,
    monkey_mod: pytest.MonkeyPatch,
) -> AsyncEngine:
    monkey_mod.setattr("anime_rest_api.api.app.Db", DatabaseConnection(pg_url))
    return create_async_engine(pg_url, echo=True)


@pytest.fixture(scope="module")
def sessions(pg_engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(pg_engine, expire_on_commit=False)


@pytest.fixture(scope="module")
def overriden_app(
    sessions: async_sessionmaker,
) -> TestClient:
    def override_db_session() -> Iterator[AsyncSession]:
        with sessions() as session:
            yield session

    app = create_app()
    app.dependency_overrides[Db] = override_db_session
    return app


@pytest.fixture
def test_client(overriden_app: FastAPI) -> TestClient:
    return TestClient(overriden_app)


@pytest.fixture(scope="module")
def test_client_lifespan(overriden_app: FastAPI) -> Iterator[TestClient]:
    with TestClient(overriden_app, base_url="http://test") as client:
        yield client

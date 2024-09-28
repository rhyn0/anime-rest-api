import asyncio
from collections.abc import AsyncIterator
from collections.abc import Coroutine
from collections.abc import Iterator
import contextlib

import pytest
import pytest_asyncio
from sqlalchemy import CursorResult
from sqlalchemy import Row
from sqlalchemy import delete
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import async_sessionmaker

from anime_rest_api.db import setup_db
from anime_rest_api.db.crud import user_operations
from anime_rest_api.db.models.auth.user import User

pytestmark = pytest.mark.asyncio(loop_scope="module")


@pytest.fixture
def example_password() -> str:
    return "password"


@pytest.fixture
async def setup_test_db(pg_engine: AsyncEngine) -> None:
    async with pg_engine.begin() as conn:
        await setup_db(conn)


@pytest.fixture
async def user_with_example_password(
    pg_engine: AsyncEngine,
    example_password: str,
    setup_test_db: Coroutine,
) -> AsyncIterator[int]:
    await setup_test_db
    async with pg_engine.begin() as conn:
        result: tuple[bool] = (
            await conn.execute(
                insert(
                    User,
                )
                .values(
                    username="test",
                    email="example@example.com",
                    first_name="Test",
                    last_name="User",
                    password_hash=user_operations.password_salt_hash_statement(
                        example_password,
                    ),
                )
                .returning(User.user_id),
            )
        ).scalar_one()
    yield result
    async with pg_engine.begin() as conn:
        await conn.execute(
            delete(User).where(User.user_id == result),
        )


class TestPasswords:
    """Collection of tests for password operations."""

    async def test_password_salt_hash_statement(
        self,
        example_password: str,
        pg_engine: AsyncEngine,
        setup_test_db: Coroutine,
    ) -> None:
        await setup_test_db
        async with pg_engine.connect() as conn:
            result = (
                await conn.execute(
                    user_operations.password_salt_hash_statement(example_password),
                )
            ).first()
        assert result != example_password

    async def test_password_hash_check(
        self,
        user_with_example_password: AsyncIterator[Coroutine[int, None, None]],
        example_password: str,
        pg_engine: AsyncEngine,
    ) -> None:
        async with contextlib.aclosing(user_with_example_password) as setup:
            await anext(setup)
            async with pg_engine.connect() as conn:
                result = (
                    await conn.execute(
                        select(
                            user_operations.password_hash_check(example_password),
                        ),
                    )
                ).scalar_one_or_none()
            assert result is True
            # cleanup to resume generator
            with contextlib.suppress(StopAsyncIteration):
                await setup.asend(None)


class TestUserOps:
    """Collection of tests for user operations."""

    async def test_list_users(
        self,
        sessions: async_sessionmaker,
        user_with_example_password: AsyncIterator[Coroutine[int, None, None]],
    ) -> None:
        async with contextlib.aclosing(user_with_example_password) as setup:
            expected_user_id = await anext(setup)
            async with sessions() as session:
                users = await user_operations.list_users(session, 0, 10)

            assert len(users) == 1
            assert users[0].user_id == expected_user_id
            # cleanup to resume generator
            with contextlib.suppress(StopAsyncIteration):
                await setup.asend(None)

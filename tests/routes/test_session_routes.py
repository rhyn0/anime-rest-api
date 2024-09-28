from collections.abc import AsyncIterator
import contextlib

from fastapi import status
from fastapi.testclient import TestClient
import pytest

from tests.db.crud.test_user_ops import example_password
from tests.db.crud.test_user_ops import setup_test_db
from tests.db.crud.test_user_ops import user_with_example_password


class TestSession:
    """Collection of tests for the session routes."""

    class TestLogin:
        """Tests dealing with login behavior."""

        def test_login_no_users(
            self,
            test_client_lifespan: TestClient,
        ):
            response = test_client_lifespan.post(
                "/login",
                json={
                    "username": "test",
                    "password": "password",
                },
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json() == {"detail": "Invalid username or password"}

        @pytest.mark.asyncio(loop_scope="class")
        class TestAsync:
            """Async tests for login."""

            async def test_login_user_wrong_password(
                self,
                test_client_lifespan: TestClient,
                user_with_example_password: AsyncIterator[int],
            ):
                async with contextlib.aclosing(user_with_example_password) as setup:
                    await anext(setup)
                    response = test_client_lifespan.post(
                        "/login",
                        json={
                            "username": "test",
                            "password": "wrong",
                        },
                    )
                    assert response.status_code == status.HTTP_400_BAD_REQUEST
                    assert response.json() == {"detail": "Invalid username or password"}

                    # cleanup
                    with contextlib.suppress(StopAsyncIteration):
                        await setup.asend(None)

            async def test_login_user(
                self,
                test_client_lifespan: TestClient,
                user_with_example_password: AsyncIterator[int],
                example_password: str,
            ):
                async with contextlib.aclosing(user_with_example_password) as setup:
                    await anext(setup)
                    response = test_client_lifespan.post(
                        "/login",
                        json={
                            "username": "test",
                            "password": example_password,
                        },
                    )
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert all(
                        key in data
                        for key in [
                            "accessToken",
                            "expiresAt",
                            "refreshToken",
                            "refreshExpiresAt",
                            "version",
                        ]
                    )

                    # cleanup
                    with contextlib.suppress(StopAsyncIteration):
                        await setup.asend(None)

import logging

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


@pytest.mark.xfail
class TestStartupEvents:
    """Collection of tests dealing with startup events."""

    class TestLogging:
        """Collection of tests about the logging setup."""

        @pytest.mark.usefixtures("test_client_lifespan")
        def test_logger_exists(self) -> None:
            loggers = logging.root.manager.loggerDict
            assert "anime-api" in loggers


@pytest.mark.xfail
class TestDatabase:
    """Tests regarding startup behavior with database."""

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("test_client_lifespan")
    async def test_database_schema_exists(self, pg_engine: AsyncEngine) -> None:
        async with pg_engine.connect() as conn:
            result = await conn.execute(
                text(
                    """select 1
                    from pg_catalog.pg_namespace
                    where nspname = 'auth';""",
                ),
            )
            # now schema exists, so we should get a result
            assert result.scalar() == 1

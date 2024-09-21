from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI

from anime_rest_api import __version__
from anime_rest_api.api.routers import SHOW_ROUTER
from anime_rest_api.api.routers import USER_ROUTER
from anime_rest_api.db import setup_db
from anime_rest_api.db.connection import Db


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Run on-startup and on-shutdown code."""
    async with Db.engine.begin() as conn:
        await setup_db(conn)
    # check that this is set
    os.environ["ANIME_API_SECRET"]
    yield


def create_app() -> FastAPI:
    """Factory function to build the application."""
    app = FastAPI(
        title="Anime API",
        description="API for tracking comments, reviews, and finding new anime.",
        version=__version__,
        # disable redoc
        redoc_url=None,
        lifespan=lifespan,
    )
    app.include_router(SHOW_ROUTER)
    app.include_router(USER_ROUTER)
    return app

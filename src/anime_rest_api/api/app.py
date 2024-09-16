from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI

from anime_rest_api import __version__
from anime_rest_api.db import DatabaseConnection


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Run on-startup and on-shutdown code."""
    DatabaseConnection(os.environ["ANIME_API_DATABASE_URL"])
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
    # disable RET for here as we will augment later with more calls
    return app  # noqa: RET504

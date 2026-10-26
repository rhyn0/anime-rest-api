from sqlmodel import Field
from sqlmodel import SQLModel

from .base import CONTENT_METADATA


class EpisodeBase(SQLModel):
    """Basic model for all common fields of an Episode."""

    show_id: int = Field(foreign_key="content.shows.show_id")
    episode_number: int
    name: str
    description: str | None = None


class Episode(EpisodeBase, table=True):
    """Database model for an episode."""

    __tablename__ = "episodes"
    metadata = CONTENT_METADATA

    episode_id: int | None = Field(None, primary_key=True)


class EpisodeRead(EpisodeBase):
    """Data model for outbound data of an episode."""

    episode_id: int


class EpisodeCreate(EpisodeBase):
    """Data model to create an episode from."""


class EpisodeUpdate(SQLModel):
    """Data model to update an existing episode with."""

    show_id: int | None = None
    episode_number: int | None = None
    name: str | None = None
    description: str | None = None

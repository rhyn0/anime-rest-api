from sqlmodel import Field
from sqlmodel import SQLModel

from .base import CONTENT_METADATA


class UserEpisodeRatingBase(SQLModel):
    """Basic model for all common fields of a UserEpisodeRating."""

    user_id: int = Field(foreign_key="auth.users.user_id", primary_key=True)
    episode_id: int = Field(foreign_key="content.episodes.episode_id", primary_key=True)
    rating: int | None = None
    comments: str | None = None


class UserEpisodeRating(UserEpisodeRatingBase, table=True):
    """Database model for a user's episode rating."""

    __tablename__ = "user_episode_ratings"
    metadata = CONTENT_METADATA


class UserEpisodeRatingRead(UserEpisodeRatingBase):
    """Data model for outbound data of a user's episode rating."""


class UserEpisodeRatingCreate(UserEpisodeRatingBase):
    """Data model to create a user's episode rating from."""


class UserEpisodeRatingUpdate(SQLModel):
    """Data model to update an existing user's episode rating with."""

    rating: int | None = None
    comments: str | None = None

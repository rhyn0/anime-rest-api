from pydantic import BaseModel

from anime_rest_api.db.models.content.episodes import EpisodeRead
from anime_rest_api.db.models.content.user_episodes import UserEpisodeRatingRead
from anime_rest_api.db.models.content.user_shows import UserShowStatusRead


class EpisodeResponseList(BaseModel):
    """Response model for episode list."""

    episodes: list[EpisodeRead]
    has_more: bool


class UserShowStatusResponseList(BaseModel):
    """Response model for user show list."""

    user_shows: list[UserShowStatusRead]
    has_more: bool


class UserEpisodeRatingResponseList(BaseModel):
    """Response model for user episode list."""

    user_episodes: list[UserEpisodeRatingRead]
    has_more: bool

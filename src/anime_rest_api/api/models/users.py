from pydantic import computed_field

from anime_rest_api.db.models.auth import UserPublic

from .base import Base


class UserResponseList(Base):
    """Response model for a list of shows."""

    users: list[UserPublic]
    has_more: bool

    @computed_field
    def count(self) -> int:
        """Count the number of shows in the list."""
        return len(self.users)

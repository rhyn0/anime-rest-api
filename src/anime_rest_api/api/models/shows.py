from pydantic import computed_field

from anime_rest_api.db.models.content import ShowRead

from .base import Base


class ShowBaseIo(Base):
    """Common fields for shows for requests and responses."""


class ShowResponseBase(Base):
    """Response model for a show."""


class ShowResponseList(Base):
    """Response model for a list of shows."""

    shows: list[ShowRead]
    has_more: bool

    @computed_field
    def count(self) -> int:
        """Count the number of shows in the list."""
        return len(self.shows)

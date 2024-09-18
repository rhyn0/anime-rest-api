import datetime as dt
from typing import Annotated

from sqlmodel import Field
from sqlmodel import SQLModel

from anime_rest_api.db.models.show_details import ShowContentRating
from anime_rest_api.db.models.show_details import ShowStatus
from anime_rest_api.db.models.show_details import ShowType

from .base import DB_METADATA


class ShowBase(SQLModel):
    """Basic model for all common fields of a Show."""

    name: Annotated[str, Field(..., min_length=1)]
    release_date: dt.date
    finish_date: dt.date | None = None
    show_type: ShowType
    status: ShowStatus
    content_rating: ShowContentRating


class Show(ShowBase, table=True):
    """Database model for a show."""

    __tablename__ = "shows"
    metadata = DB_METADATA

    show_id: int | None = Field(None, primary_key=True)


class ShowRead(ShowBase):
    """Data model for outbound data of a show."""

    show_id: int


class ShowCreate(ShowBase):
    """Data model to create a show from."""


class ShowUpdate(SQLModel):
    """Data model to update an existing show with.

    All fields are optional as we only update the ones that are set.
    These fields could change to be a subset of the actual table,
    as maybe those fields don't need to be modified.
    """

    name: str | None = None
    release_date: dt.date | None = None
    finish_date: dt.date | None = None
    show_type: ShowType | None = None
    status: ShowStatus | None = None
    content_rating: ShowContentRating | None = None

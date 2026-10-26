from sqlmodel import Field
from sqlmodel import SQLModel

from .base import CONTENT_METADATA


class UserShowStatusBase(SQLModel):
    """Basic model for all common fields of a UserShowStatus."""

    user_id: int = Field(foreign_key="auth.users.user_id", primary_key=True)
    show_id: int = Field(foreign_key="content.shows.show_id", primary_key=True)
    status: str
    rating: int | None = None
    comments: str | None = None


class UserShowStatus(UserShowStatusBase, table=True):
    """Database model for a user's show status."""

    __tablename__ = "user_show_status"
    metadata = CONTENT_METADATA


class UserShowStatusRead(UserShowStatusBase):
    """Data model for outbound data of a user's show status."""


class UserShowStatusCreate(UserShowStatusBase):
    """Data model to create a user's show status from."""


class UserShowStatusUpdate(SQLModel):
    """Data model to update an existing user's show status with."""

    status: str | None = None
    rating: int | None = None
    comments: str | None = None

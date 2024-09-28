from pydantic import EmailStr
from sqlmodel import Field
from sqlmodel import SQLModel

from .base import AUTH_METADATA


class UserBase(SQLModel):
    """Basic model for all common fields of a User."""

    username: str
    email: EmailStr
    first_name: str
    last_name: str
    password_hash: str
    is_admin: bool = False


class User(UserBase, table=True):
    """Database model for a user."""

    __tablename__ = "users"
    metadata = AUTH_METADATA

    user_id: int | None = Field(None, primary_key=True)
    session_version: int = 1
    """Make this attribute be an internal version of the user's session.

    When a logout happens we bump this value upwards to invalidate refresh tokens from
    this session.
    """


class UserRead(User):
    """Model for reading a user from the database.

    This differs from `UserPublic` because of the session_version field.
    This model should be the return when interacting with the database.
    """

    user_id: int


class UserPublic(UserBase):
    """Model for reading a user from the database.

    This is the model that is returned to the client.
    """

    user_id: int


class UserUpdate(SQLModel):
    """Model for updating a user in the database."""

    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = None
    is_admin: bool | None = None


class UserCreate(SQLModel):
    """Model for creating a user in the database."""

    username: str
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    is_admin: bool

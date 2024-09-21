"""Routes that deal with user sessions."""

from typing import Annotated

from fastapi import APIRouter
from pydantic import Field
from pydantic import TypeAdapter

UserSession: TypeAdapter[str] = TypeAdapter(Annotated[str, Field(..., min_length=32)])

ROUTER = APIRouter()


@ROUTER.post("/login")
def login_route():
    """Login a user."""


@ROUTER.post("/logout")
def logout_route() -> None:
    """Logout a user."""

from collections.abc import Sequence

from sqlalchemy import ColumnElement
from sqlalchemy import Function
from sqlalchemy import Result
from sqlalchemy import func
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import and_
from sqlmodel import select

from anime_rest_api.db.models.auth import User
from anime_rest_api.db.models.auth import UserRead
from anime_rest_api.db.models.auth.user import UserCreate
from anime_rest_api.db.models.auth.user import UserUpdate

from .errors import EntryNotFoundError
from .errors import InvalidPermissionsError
from .errors import UnexpectedDbError


def password_salt_hash_statement(password: str) -> Function:
    """Create a statement to hash a password with a salt.

    Args:
        password (str): Password to hash

    Returns:
        str: SQL statement to hash the password
    """
    return func.crypt(password, func.gen_salt("bf", 10))


def password_hash_check(password: str) -> ColumnElement[bool]:
    """Hash a password with a salt.

    Args:
        password (str): Password to hash

    Returns:
        ColumnElement[bool]: Usable statement for WHERE clause.
    """
    return func.crypt(password, User.password_hash) == User.password_hash


async def list_users(
    session: AsyncSession,
    offset: int,
    limit: int,
) -> Sequence[UserRead]:
    """List users.

    Only usable by admin users.

    Raises:
        InvalidPermissionsError: If requesting user is not an admin.

    Args:
        session (AsyncSession): Database session
        offset (int): Offset for pagination
        limit (int): Limit for pagination

    Returns:
        Sequence[UserRead]: List of users
    """
    # issue here where mypy detects that the column is int | None
    # but the database version is int
    statement = select(User).order_by(User.user_id).offset(offset).limit(limit)  # type: ignore[arg-type]
    result: Result[tuple[UserRead]] = await session.execute(statement)
    # since this is coming from DB, the UserRead model is correct as `user_id` is set
    return result.scalars().all()


async def get_user(
    session: AsyncSession,
    user_id: int,
) -> UserRead:
    """Get a user by its ID.

    Any user can make this call as we want to allow navigating to a user's profile.
    But only by knowing the id, not by listing and finding.

    Raises:
        EntryNotFoundError: If user_id does not exist in table.

    Args:
        session (AsyncSession): Database session
        user_id (int): ID of the user to get

    Returns:
        UserRead: User with the given id
    """
    statement = select(User).where(User.user_id == user_id)
    result = await session.execute(statement)
    user = result.scalars().first()
    if user is None:
        raise EntryNotFoundError(User.__tablename__, user_id)

    return user  # type: ignore[return-value]


async def get_user_login(
    session: AsyncSession,
    username: str,
    password: str,
) -> UserRead:
    """Get a user by its ID.

    Any user can make this call as we want to allow navigating to a user's profile.
    But only by knowing the id, not by listing and finding.

    Raises:
        EntryNotFoundError: If user_id does not exist in table.
        MultipleEntriesFoundError: If multiple users are found with the same ID.

    Args:
        session (AsyncSession): Database session
        username (str): ID of the user to get
        password (str): password to check

    Returns:
        UserRead: User with the given id
    """
    statement = select(User).where(
        and_(
            User.username == username,
            password_hash_check(password),
        ),
    )
    result = await session.execute(statement)
    user = result.scalars().one_or_none()
    if user is None:
        raise EntryNotFoundError(User.__tablename__, username)

    return user  # type: ignore[return-value]


async def create_user(
    session: AsyncSession,
    user: UserCreate,
    requesting_user: UserRead,
) -> UserRead:
    """Create a user in the database.

    Args:
        session (AsyncSession): Database session
        user (UserCreate): Values to create the user with
        requesting_user (UserRead): User making the request

    Raises:
        UnexpectedDbError: If no user is returned after insert

    Returns:
        UserRead: User created with its id
    """
    # normal users cant just make extra admin accounts
    if user.is_admin and not requesting_user.is_admin:
        raise InvalidPermissionsError("auth.users", "CREATE", requesting_user.user_id)

    statement = (
        insert(User)
        .values(
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_admin=user.is_admin,
            password_hash=password_salt_hash_statement(user.password),
        )
        .returning(User)
    )
    result = await session.execute(statement)
    inserted_user = result.scalars().first()
    if inserted_user is None:
        raise UnexpectedDbError(
            User.__tablename__,
            "CREATE",
            "No user returned after insert",
        )
    return inserted_user  # type: ignore[return-value]


async def update_user(
    session: AsyncSession,
    user_id: int,
    user_update: UserUpdate,
    requesting_user: UserRead,
) -> UserRead:
    """Update a show with only the fields that are set.

    Args:
        session (AsyncSession): Database session
        user_id (int): User ID to update
        user_update (UserUpdate): Wrapper of fields to set for the User
        requesting_user (UserRead): User making the request

    Raises:
        EntryNotFoundError: If show_id does not exist in table.

    Returns:
        Show: Updated model
    """
    # normal account users can't update an account to be an admin
    if not requesting_user.is_admin and user_update.is_admin:
        raise InvalidPermissionsError("auth.users", "UPDATE", requesting_user.user_id)
    db_user = await get_user(session, user_id)
    if db_user is None:
        raise EntryNotFoundError(User.__tablename__, user_id)
    updated_fields = user_update.model_dump(exclude_unset=True)
    if "password" in updated_fields:
        updated_fields["password_hash"] = password_salt_hash_statement(
            updated_fields.pop("password"),
        )
    db_user.sqlmodel_update(updated_fields)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def delete_user(session: AsyncSession, user_id: int) -> UserRead:
    """Delete a show.

    Args:
        session (AsyncSession): Database session.
        user_id (int): ID of the user to delete.

    Raises:
        EntryNotFoundError: If user with ID does not exist.

    Returns:
        UserRead: User that was deleted
    """
    db_user = await get_user(session, user_id)
    if db_user is None:
        raise EntryNotFoundError(User.__tablename__, user_id)
    await session.delete(db_user)
    await session.commit()
    return db_user


async def increment_user_session_version(
    session: AsyncSession,
    user_id: int,
) -> UserRead:
    """Increment the session version of a user.

    Args:
        session (AsyncSession): Database session.
        user_id (int): ID of the user to increment the session version.

    Raises:
        EntryNotFoundError: If user with ID does not exist.

    Returns:
        UserRead: User that was updated
    """
    db_user = await get_user(session, user_id)
    if db_user is None:
        raise EntryNotFoundError(User.__tablename__, user_id)
    db_user.session_version += 1
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

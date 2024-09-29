"""Collection of top level errors for CRUD operations."""

from typing import Literal


class DatabaseError(Exception):
    """Simple error for operations involving database."""

    table: str
    operation: str

    def __init__(self, table: str, operation: str, *args: object) -> None:
        """Save the table and operation for the error.

        Args:
            table (str): Tablename where the error occurred.
            operation (str): Create, read, update or delete operation
            args: Extra pass through to Exception super.
        """
        self.table = table
        self.operation = operation
        message = f"Error in {operation} operation on {table}"
        super().__init__(message, *args)


class UnexpectedDbError(DatabaseError):
    """Raised when an unexpected error occurs in the database."""

    def __init__(self, table: str, operation: str, error: str) -> None:
        """Initialize the error with the unexpected error."""
        super().__init__(table, operation)
        self.add_note(f"Unexpected error: {error}")

    def add_note(self, note: str) -> None:
        """Add a note to the error message."""
        self.args = (f"{self.args[0]} - {note}",)


class EntryNotFoundError(DatabaseError):
    """Raised when an entry is not found in the database."""

    entry_id: int | str

    def __init__(self, table: str, entry_id: int | str) -> None:
        """Initialize the error with the missing entry id."""
        super().__init__(table, "READ")
        self.entry_id = entry_id
        self.add_note(f"Entry {entry_id} not found in {table}")


type Operation = Literal["CREATE", "READ", "UPDATE", "DELETE"]


class InvalidPermissionsError(Exception):
    """Raised when an entry is not found in the database."""

    operation: Operation
    table: str
    violating_user_id: int

    def __init__(
        self,
        table: str,
        operation: Operation,
        user_id: int,
        *args: tuple,
    ) -> None:
        """Initialize the error with the missing entry id.

        Args:
            table (str): Table where the error occurred.
            operation (Operation): Operation that was attempted.
            user_id (int): User ID that attempted the operation.
            args: Extra pass through to Exception super.
        """
        super().__init__(
            f"User {user_id} called {operation} on table {table} - PERMISSION DENIED",
            *args,
        )
        self.table = table
        self.operation = operation
        self.violating_user_id = user_id

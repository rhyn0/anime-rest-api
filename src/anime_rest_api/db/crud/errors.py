"""Collection of top level errors for CRUD operations."""


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


class EntryNotFoundError(Exception):
    """Raised when an entry is not found in the database."""

    def __init__(self, table: str, entry_id: int) -> None:
        """Initialize the error with the missing entry id."""
        super().__init__(table, "READ")
        self.entry_id = entry_id
        self.add_note(f"Entry {entry_id} not found in {table}")

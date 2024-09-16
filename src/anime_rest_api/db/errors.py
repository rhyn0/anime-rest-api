"""Collection of errors that we can raise from this module."""


class MissingDatabaseUrlError(Exception):
    """Error to raise when no valid connection string provided."""

    def __init__(self, *args: object) -> None:
        """Return error with default message."""
        super().__init__("No Database URL provided to connect to.", *args)


class InvalidDbConnectionStateError(Exception):
    """Error when using methods on DatabaseConnection in invalid state."""

    def __init__(self, method_name: str, *args: object) -> None:
        """Return error with interpolated message."""
        super().__init__(f"Invalid state for method call {method_name!r}", *args)
        self.method_call = method_name

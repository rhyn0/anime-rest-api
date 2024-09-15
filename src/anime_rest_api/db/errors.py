"""Collection of errors that we can raise from this module."""


class MissingDatabaseUrlError(Exception):
    """Error to raise when no valid connection string provided."""

    def __init__(self, *args: object) -> None:
        """Return error with default message."""
        super().__init__("No Database URL provided to connect to.", *args)

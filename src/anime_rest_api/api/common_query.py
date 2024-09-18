from fastapi import Query


def limit_and_offset_query(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> tuple[int, int]:
    """Limit and offset query."""
    return limit, offset

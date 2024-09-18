from sqlmodel import MetaData

DB_METADATA = MetaData(schema="anime_data")

__all__ = ["DB_METADATA"]

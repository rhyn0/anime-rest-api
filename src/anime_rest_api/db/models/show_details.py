import enum

from sqlmodel import Enum

from anime_rest_api.db.models.base import DB_METADATA

### Python Enums usable in Pydantic models and code


class ShowType(enum.StrEnum):
    """Enum for the type of show."""

    TV = "TV"
    OVA = "OVA"
    Movie = "Movie"
    Special = "Special"


class ShowStatus(enum.StrEnum):
    """Enum for the status of a show."""

    Finished = "Finished"
    Airing = "Airing"
    NotYetAired = "NotYetAired"


class ShowContentRating(enum.StrEnum):
    """Enum for the content rating of a show."""

    G = "G"
    PG = "PG"
    PG13 = "PG13"
    R = "R"
    NC17 = "NC17"


### SqlAlchemy Enum for creating the Enum inside the database

ShowTypeEnum = Enum(ShowType, name="show_type_enum", metadata=DB_METADATA)
ShowStatusEnum = Enum(ShowStatus, name="show_status_enum", metadata=DB_METADATA)
ShowContentRatingEnum = Enum(
    ShowContentRating,
    name="show_content_rating_enum",
    metadata=DB_METADATA,
)

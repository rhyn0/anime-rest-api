from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


class Base(BaseModel):
    """Basic model for inheriting Pydantic Config for all API models."""

    model_config = ConfigDict(alias_generator=to_camel)

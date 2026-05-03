from pydantic import BaseModel, ConfigDict


class UserMe(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str | None
    display_name: str
    is_local_alpha: bool

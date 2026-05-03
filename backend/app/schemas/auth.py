from typing import Literal

from pydantic import BaseModel, ConfigDict


AuthMode = Literal["google_oauth", "local_dev"]


class UserMe(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str | None
    display_name: str
    is_local_alpha: bool


class AuthConfig(BaseModel):
    auth_mode: AuthMode
    local_dev_enabled: bool
    google_oauth_enabled: bool
    google_oauth_message: str | None = None

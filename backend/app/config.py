from pydantic import BaseModel


class AppSettings(BaseModel):
    api_prefix: str = "/api/v1"
    allowed_origins: list[str] = ["*"]


settings = AppSettings()


from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "Fresh Log API"
    database_url: str = "sqlite:///./fridge.db"
    cors_origins: str = "http://localhost:5173"
    secret_key: str = "change-this-secret-key-in-production"
    access_token_expire_minutes: int = 60 * 24 * 7
    algorithm: str = "HS256"

    max_boxes: int = 50
    max_private_boxes_per_user: int = 5
    private_box_expiry_days: int = 7
    private_box_grace_days: int = 3

    class Config:
        env_file = ".env"

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()

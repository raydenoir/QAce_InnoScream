from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application‑wide configuration (reads from .env)."""

    # Telegram / Bot
    bot_token: str = Field(..., env="BOT_TOKEN")
    admins: str | None = Field(None, env="ADMINS")  # comma‑separated

    # Security / Hash salt
    hash_salt: str = Field("dev‑salt", env="HASH_SALT")
    channel_id: int = Field(..., env="CHANNEL_ID")

    # ImgFlip / QuickChart (place‑holders for now)
    imgflip_user: str | None = Field(default=None, env="IMGFLIP_USER")
    imgflip_pass: str | None = Field(default=None, env="IMGFLIP_PASS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    # Convenience -------------------------------------------------
    @property
    def admin_ids(self) -> set[int]:
        if not self.admins:
            return set()
        return {int(x) for x in self.admins.split(",") if x}


@lru_cache()
def get_settings() -> Settings:  # FastAPI dependency‑friendly
    """Getter for the Settings class."""
    return Settings()
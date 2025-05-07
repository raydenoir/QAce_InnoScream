"""InnoScream Bot config module."""

from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application‑wide configuration (reads from .env)."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    # Telegram / Bot
    bot_token: str = Field(..., validation_alias="BOT_TOKEN")
    admins: str | None = Field(None, validation_alias="ADMINS")

    # Security / Hash salt
    hash_salt: str = Field("dev-salt", validation_alias="HASH_SALT")
    channel_id: int = Field(..., validation_alias="CHANNEL_ID")

    # ImgFlip / QuickChart (placeholders for now)
    imgflip_user: str | None = Field(
        default=None,
        validation_alias="IMGFLIP_USER"
    )
    imgflip_pass: str | None = Field(
        default=None,
        validation_alias="IMGFLIP_PASS"
    )

    @property
    def admin_ids(self) -> set[int]:
        """Get list of admin ids."""
        if not self.admins:
            return set()
        return {int(x) for x in self.admins.split(",") if x}


@lru_cache()
def get_settings() -> Settings:
    """Getter for the Settings class."""
    return Settings()

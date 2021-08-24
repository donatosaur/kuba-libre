# Modified:    2021-08-25
# Description: Loads settings from .env file

from pydantic import BaseSettings


__all__ = ["settings"]


class _Settings(BaseSettings):
    APP_NAME: str = "Marble Game API"
    DEBUG_MODE: bool
    HOST: str
    PORT: int
    MONGODB_URI: str
    DB_NAME: str
    PLAYER_COLLECTION_NAME: str
    GAME_COLLECTION_NAME: str

    class Config:
        env_file = ".env"


settings = _Settings()

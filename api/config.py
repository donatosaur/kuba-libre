# Modified:    2022-06-01
# Description: Loads settings from environment

from pydantic import BaseSettings


__all__ = ["settings"]


class _Settings(BaseSettings):
    APP_NAME: str = "KubaLibre API"
    DEBUG: bool = False
    HOST: str
    PORT: int
    MONGODB_URI: str
    DB_NAME: str
    PLAYER_COLLECTION_NAME: str
    GAME_COLLECTION_NAME: str
    STATIC_CONTENT_DIR: str = "/static/"

    class Config:
        env_prefix = "FASTAPI_"


settings = _Settings()

from pydantic import BaseSettings


__all__ = ["settings"]


class _Settings(BaseSettings):
    APP_NAME: str = "Marble Game API"
    DEBUG_MODE: bool
    HOST: str
    PORT: int
    MONGODB_URI: str
    DB_NAME: str

    class Config:
        env_file = ".env"


settings = _Settings()

# Modified:    2021-08-25
# Description: Defines the database for the app
#
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from .config import settings


class _MongoDBClient:
    """Wraps AsyncIOMotorClient so that database connection can be shared among modules"""
    client: AsyncIOMotorClient = None

    async def get_player_collection(self) -> AsyncIOMotorCollection:
        return self.client[settings.DB_NAME][settings.PLAYER_COLLECTION_NAME]

    async def get_game_collection(self) -> AsyncIOMotorCollection:
        return self.client[settings.DB_NAME][settings.GAME_COLLECTION_NAME]


db = _MongoDBClient()

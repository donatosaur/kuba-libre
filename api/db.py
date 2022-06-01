# Modified:    2022-06-01
# Description: Defines the database for the app
#
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from config import settings


class _MongoDBClient:
    """Wraps AsyncIOMotorClient so that database connection can be shared among modules"""
    client: AsyncIOMotorClient = None

    async def get_player_collection(self) -> AsyncIOMotorCollection:
        return self.client[settings.DB_NAME][settings.PLAYER_COLLECTION_NAME]

    async def get_game_collection(self) -> AsyncIOMotorCollection:
        return self.client[settings.DB_NAME][settings.GAME_COLLECTION_NAME]

    async def index(self) -> None:
        """Indexes the database's collections; should be run once on app startup"""
        # index the user collection by id and auth0_id
        player_collection = await self.get_player_collection()
        await player_collection.create_index(
            [("_id", pymongo.ASCENDING), ("auth0_id", pymongo.ASCENDING)],
            unique=True,
        )


db = _MongoDBClient()

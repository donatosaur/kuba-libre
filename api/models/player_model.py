# Modified:    2021-08-26
# Description: Implements a model for player info
#
from pydantic import BaseModel, Field
from pymongo import ReturnDocument
from typing import Optional
from db import db
from .pydantic_object_id import PydanticObjectID
from . import OBJ_ID_FIELD_DESC


class PlayerModel(BaseModel):
    """Defines the base player schema"""
    id: str = Field(default_factory=PydanticObjectID, alias="_id", description=OBJ_ID_FIELD_DESC)
    current_games: list = Field(default_factory=lambda: [], description="A list of Game IDs denoting ongoing games")
    completed_games: list = Field(default_factory=lambda: [], description="A list of Game IDs denoting completed games")

    class Config:
        # allow id to be populated by id or _id
        allow_population_by_field_name = True

        # define JSON metadata for FastAPI's doc generator
        schema_extra = {
            "example": {
                "id": "c838c7eb1f84086bf3b08e60",
                "current_games": ["4dea5825ed8666d1f4114277", "6c3f5ca0bb6b5a79257e2c17"],
                "completed_games": ["cd82357045798bc3d1e844e2"],
            }
        }


class PlayerInput(BaseModel):
    """Defines the player input schema"""
    auth0_id: str = Field(..., description=OBJ_ID_FIELD_DESC)

    class Config:
        # define JSON metadata for FastAPI's doc generator
        schema_extra = {
            "example": {
                "auth0_id": "6140d8eb44672c00694b8627",
            }
        }


# ---- CREATE ----
async def create(player_input: PlayerInput) -> dict:
    """
    Creates a new entry in the player database.

    :param player_input: input containing the player's auth0_id
    :return: an awaitable resolving to the inserted document
    """
    collection = await db.get_player_collection()
    res = await collection.insert_one({
        "auth0_id": player_input.auth0_id,
        "current_games": [],
        "completed_games": [],
    })
    return await find_by_id(res.inserted_id)


# ---- RETRIEVE ----
async def find_by_id(player_id: str) -> Optional[dict]:
    """
    Retrieves the specified player document.

    :param player_id: the object id of the player
    :return: an awaitable resolving to the matching document, or None if one is not found
    """
    collection = await db.get_player_collection()
    return await collection.find_one({"_id": PydanticObjectID(player_id)})


async def find_by_auth0_id(auth0_id: str) -> Optional[dict]:
    """
    Retrieves the specified player document.

    :param auth0_id: the unique auth0_id of the player
    :return: an awaitable resolving to the matching document, or None if one is not found
    """
    collection = await db.get_player_collection()
    return await collection.find_one({"auth0_id": auth0_id})


# ---- UPDATE ----
async def add_current_game(player_id: str, game_id: str) -> Optional[dict]:
    """
    Updates the player's current games by adding a game to it.

    :param player_id: the object id of the player
    :param game_id: the object id of the game
    :return: an awaitable resolving to the updated document, or None if one is not found
    """
    collection = await db.get_player_collection()
    updated_player = await collection.find_one_and_update(
        {"_id": PydanticObjectID(player_id)},
        {"$push": {"current_games": game_id}},
        return_document=ReturnDocument.AFTER,
    )
    return updated_player


async def remove_current_game(player_id: str, game_id: str) -> Optional[dict]:
    """
    Updates the player's current games by removing a game from it.

    :param player_id: the object id of the player
    :param game_id: the object id of the game
    :return: an awaitable resolving to the updated document, or None if one is not found
    """
    collection = await db.get_player_collection()
    updated_player = await collection.find_one_and_update(
        {"_id": PydanticObjectID(player_id)},
        {"$pull": {"current_games": game_id}},
        return_document=ReturnDocument.AFTER,
    )
    return updated_player


async def add_completed_game(player_id: str, game_id: str) -> Optional[dict]:
    """
    Updates the player's completed games by adding a game to it.

    :param player_id: the object id of the player
    :param game_id: the object id of the game
    :return: an awaitable resolving to the updated document, or None if one is not found
    """
    collection = await db.get_player_collection()
    updated_player = await collection.find_one_and_update(
        {"_id": PydanticObjectID(player_id)},
        {"$push": {"completed_games": PydanticObjectID(game_id)}},
        return_document=ReturnDocument.AFTER,
    )
    return updated_player


async def remove_completed_game(player_id: str, game_id: str) -> Optional[dict]:
    """
    Updates the player's current games by removing a game from it.

    :param player_id: the object id of the player
    :param game_id: the object id of the game

    :return: an awaitable resolving to the updated document, or None if one is not found
    """
    collection = await db.get_player_collection()
    updated_player = await collection.find_one_and_update(
        {"_id": PydanticObjectID(player_id)},
        {"$pull": {"completed_games": PydanticObjectID(game_id)}},
        return_document=ReturnDocument.AFTER,
    )
    return updated_player


async def move_current_game_to_completed(player_id: str, game_id: str) -> Optional[dict]:
    """
    Updates the player's current_games ***and*** completed_games by removing the specified game from
    current_games and adding it to completed_games

    :param player_id: the object id of the player
    :param game_id: the object id of the game
    :return: an awaitable resolving to the updated document, or None if one is not found
    """
    collection = await db.get_player_collection()
    updated_player = await collection.find_one_and_update(
        {"_id": PydanticObjectID(player_id)},
        {
            "$pull": {"current_games": PydanticObjectID(game_id)},
            "$push": {"completed_games": PydanticObjectID(game_id)},
        },
        return_document=ReturnDocument.AFTER,
    )
    return updated_player


# ---- DELETE ----
async def delete(player_id: str) -> int:
    """
    Deletes the specified player from the database.

    :param player_id: the object id of the player
    :return: an awaitable resolving to the number of deleted documents
    """
    collection = await db.get_player_collection()
    deleted = await collection.delete_one({"_id": PydanticObjectID(player_id)})
    return deleted.deleted_count

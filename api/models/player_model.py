# Modified:    2021-08-23
# Description: Implements a model for player info
#
from pydantic import BaseModel, Field
from pymongo import ReturnDocument
from . import PydanticObjectID
from ..main import app

# get the player collection
collection = app.db["players"]


class Player(BaseModel):
    """Defines the Player schema"""
    id: str = Field(default_factory=PydanticObjectID, alias="_id", description="24-digit hex string ObjectID")
    username: str
    name: str
    current_games: list = Field(default_factory=lambda: [])
    completed_games: list = Field(default_factory=lambda: [])

    class Config:
        # allow id to be populated by id or _id
        allow_population_by_field_name = True

        # define JSON metadata for FastAPI's doc generator
        schema_extra = {
            "example": {
                "id": "c838c7eb1f84086bf3b08e60",
                "username": "player_username",
                "name": "Player Name",
                "current_games": ["4dea5825ed8666d1f4114277", "6c3f5ca0bb6b5a79257e2c17"],
                "completed_games": ["cd82357045798bc3d1e844e2"],
            }
        }


# ---- CREATE ----
async def create(username: str, name: str) -> Player:
    """
    Creates a new entry in the player database.

    :param username: the player's username
    :param name: the player's name
    :return: an awaitable resolving to the id of the inserted document
    """
    return await collection.insert_one({"username": username, "name": name})


# ---- RETRIEVE ----
async def find(player_id: str) -> Player:
    """
    Retrieves the specified player document.

    :param player_id: the object id of the player
    :return: an awaitable resolving to the matching document, or None if one is not found
    """
    return await collection.find_one({"_id": player_id})


# ---- UPDATE ----
async def update_name(player_id: str, new_name: str) -> Player:
    """
    Updates the specified player's name.

    :param player_id: the object id of the player
    :param new_name: the player's new name
    :return: an awaitable resolving to the updated document, or None if one is not found
    """
    updated_player = await collection.find_one_and_update(
        {"_id": player_id},
        {"$set": {"name": new_name}},
        return_document=ReturnDocument.AFTER,
    )
    return updated_player


async def add_current_game(player_id: str, game_id: str) -> Player:
    """
    Updates the specified player's current games by adding a game to it.

    :param player_id: the object id of the player
    :param game_id: the object id of the game
    :return: an awaitable resolving to the updated document, or None if one is not found
    """
    updated_player = await collection.find_one_and_update(
        {"_id": player_id},
        {"$push": {"current_games": game_id}},
        return_document=ReturnDocument.AFTER,
    )
    return updated_player


async def remove_current_game(player_id: str, game_id: str) -> Player:
    """
    Updates the specified player's current games by removing a game from it.

    :param player_id: the object id of the player
    :param game_id: the object id of the game
    :return: an awaitable resolving to the updated document, or None if one is not found
    """
    updated_player = await collection.find_one_and_update(
        {"_id": player_id},
        {"$pull": {"current_games": game_id}},
        return_document=ReturnDocument.AFTER,
    )
    return updated_player


async def add_completed_game(player_id: str, game_id: str) -> Player:
    """
    Updates the specified player's completed games by adding a game to it.

    :param player_id: the object id of the player
    :param game_id: the object id of the game
    :return: an awaitable resolving to the updated document, or None if one is not found
    """
    updated_player = await collection.find_one_and_update(
        {"_id": player_id},
        {"$push": {"completed_games": game_id}},
        return_document=ReturnDocument.AFTER,
    )
    return updated_player


async def remove_completed_game(player_id: str, game_id: str) -> Player:
    """
    Updates the specified player's current games by removing a game from it.

    :param player_id: the object id of the player
    :param game_id: the object id of the game
    :return: an awaitable resolving to the updated document, or None if one is not found
    """
    updated_player = await collection.find_one_and_update(
        {"_id": player_id},
        {"$pull": {"completed_games": game_id}},
        return_document=ReturnDocument.AFTER,
    )
    return updated_player


async def move_current_game_to_completed(player_id: str, game_id: str) -> Player:
    """
    Updates the specified player's current_games ***and*** completed_games by removing the specified game from
    current_games and adding it to completed_games

    :param player_id: the object id of the player
    :param game_id: the object id of the game
    :return: an awaitable resolving to the updated document, or None if one is not found
    """
    updated_player = await collection.find_one_and_update(
        {"_id": player_id},
        {"$pull": {"current_games": game_id}, "push": {"completed_games": game_id}},
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
    deleted = await collection.delete_one({"_id": player_id})
    return deleted.deleted_count

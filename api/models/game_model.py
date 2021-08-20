# Modified:    2021-08-20
# Description: Implements a model for game info
#
import json
from marble_game import MarbleGame, MarbleGameEncoder, MarbleGameDecoder
from typing import Awaitable
from pydantic import BaseModel, Field
from pymongo import ReturnDocument
from . import PydanticObjectID
from ..main import app

# get the game collection
collection = app.db["games"]


class Game(BaseModel):
    """Defines the Game schema"""
    id: str = Field(default_factory=PydanticObjectID, alias="_id")
    player_ids: tuple[str, str]
    game_state: MarbleGame

    class Config:
        # allow id to be populated by id or _id
        allow_population_by_field_name = True

        # define json encoders & decoders for the schema
        @staticmethod
        def json_dumps(o: Game):
            if not isinstance(o, Game):
                raise TypeError(f"Unsupported type {o.__class__}")
            return json.dumps({
                "id": o.id,
                "player_ids": o.player_ids,
                "game_state": json.dumps(o.game_state, cls=MarbleGameEncoder),
            })

        @staticmethod
        def json_loads(s: str):
            def hook(d: dict):
                return Game(
                    id=d["id"],
                    player_ids=tuple(json.loads(d["player_ids"])),
                    game_state=json.loads(d[""], cls=MarbleGameDecoder),
                )
            return json.loads(s, object_hook=hook)


async def create(player_one_data: tuple[str, str, str], player_two_data: tuple[str, str, str]) -> Awaitable:
    """
    Creates a new entry in the games database.

    :param player_one_data: a tuple containing the first player's id, name and marble color (in that order)
    :param player_two_data: a tuple containing the second player's id, name and marble color (in that order)
    :return: an awaitable resolving to the id of the inserted document
    """
    player_ids = (player_one_data[0], player_two_data[0])
    game_state = MarbleGame(player_one_data, player_two_data)
    game = await collection.insert_one({"player_ids": player_ids, "game_state": game_state})
    return game.inserted_id


async def find(game_id: str) -> Awaitable:
    """
    Retrieves the specified game document.

    :param game_id: the object id of the game
    :return: an awaitable resolving to the matching document, or None if one is not found
    """
    return await collection.find_one({"_id": game_id})


async def update_game_state(game_id: str, new_game_state: MarbleGame) -> Awaitable:
    """
    Updates the specified game's state.

    :param game_id: the object id of the game
    :param new_game_state: the new game state
    :return: an awaitable resolving to the updated document, or None if one is not found
    """
    updated_game = await collection.find_one_and_update(
        {"_id": game_id},
        {"$set": {"game_state": new_game_state}},
        return_document=ReturnDocument.AFTER,
    )
    return updated_game


async def delete(game_id: str) -> Awaitable:
    """
    Deletes the specified game from the database.

    :param game_id: the object id of the game
    :return: an awaitable resolving to the number of deleted documents
    """
    deleted = await collection.delete_one({"_id": game_id})
    return deleted.deleted_count

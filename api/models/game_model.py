# Modified:    2021-08-23
# Description: Implements a model for game info
#
import json
from marble_game import MarbleGame, MarbleGameEncoder, MarbleGameDecoder
from pydantic import BaseModel, Field
from pymongo import ReturnDocument
from .pydantic_object_id import PydanticObjectID
from . import OBJ_ID_FIELD_DESC
from ..main import app

# get the game collection
collection = app.db["games"]


class Game(BaseModel):
    """Defines the Game schema"""
    id: str = Field(default_factory=PydanticObjectID, alias="_id", description=OBJ_ID_FIELD_DESC)
    player_ids: tuple[str, str] = Field(..., description="The players' IDs")
    game_state: MarbleGame = Field(..., description="A representation of the game state")

    class Config:
        # allow id to be populated by id or _id
        allow_population_by_field_name = True

        # define JSON metadata for FastAPI's doc generator
        schema_extra = {
            "example": {
                "id": "b0ab39b98aa9e0db3404c117",
                "player_ids": ["c838c7eb1f84086bf3b08e60", "9967854891700e3f20654a0f"],
                "game_state": {
                    "board": {
                        "grid": " W   BBWW R BBW RRR   RRRRR   RRR  BB R WWBB   WW",
                        "previous_state": "WW   BBWW R BB  RRR   RRRRR   RRR  BB R WWBB   WW",
                    },
                    "players": {
                        "c838c7eb1f84086bf3b08e60": {
                            "color": 'B',
                            "red_marbles_captured": 0,
                            "opponent_marbles_captured": 0,
                        },
                        "9967854891700e3f20654a0f":
                            {
                                "color": 'W',
                                "red_marbles_captured": 0,
                                "opponent_marbles_captured": 0,
                            },
                    },
                    "current_turn": "c838c7eb1f84086bf3b08e60",
                    "winner": None,
                },
            }
        }

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
                    game_state=json.loads(d["game_state"], cls=MarbleGameDecoder),
                )
            return json.loads(s, object_hook=hook)


# ---- CREATE ----
async def create(player_one_data: tuple[str, str], player_two_data: tuple[str, str]) -> Game:
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


# ---- RETRIEVE ----
async def find(game_id: str) -> Game:
    """
    Retrieves the specified game document.

    :param game_id: the object id of the game
    :return: an awaitable resolving to the matching document, or None if one is not found
    """
    return await collection.find_one({"_id": game_id})


# ---- UPDATE ----
async def update_game_state(game_id: str, new_game_state: MarbleGame) -> Game:
    """
    Updates the specified game's state.

    :param game_id: the object id of the game
    :param new_game_state: the new game state
    :return: an awaitable resolving to the updated document, or None if one is not found
    """
    new_game_state = json.dumps(new_game_state, cls=MarbleGameEncoder)
    updated_game = await collection.find_one_and_update(
        {"_id": game_id},
        {"$set": {"game_state": new_game_state}},
        return_document=ReturnDocument.AFTER,
    )
    return updated_game


# ---- DELETE ----
async def delete(game_id: str) -> int:
    """
    Deletes the specified game from the database.

    :param game_id: the object id of the game
    :return: an awaitable resolving to the number of deleted documents
    """
    deleted = await collection.delete_one({"_id": game_id})
    return deleted.deleted_count

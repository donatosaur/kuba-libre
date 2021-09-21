# Modified:    2021-09-21
# Description: Implements a model for game info
#
import json
from typing import Optional
from pydantic import BaseModel, Field
from pymongo import ReturnDocument, CursorType
from marble_game import MarbleGame, MarbleGameEncoder, MarbleGameDecoder
from api.db import db
from .pydantic_object_id import PydanticObjectID
from . import OBJ_ID_FIELD_DESC, COLOR_REGEX, ID_REGEX, PLAYER_ID_DESC, COLOR_FIELD_DESC


class MarbleGameModel(BaseModel):
    """Defines the MarbleGame schema"""
    board: dict = Field(..., description="A representation of the board state")
    players: dict = Field(..., description="A representation of the players' states")
    current_turn: Optional[str] = Field(..., description="The current player's ID, if any")
    winner: Optional[str] = Field(..., description="The winning player's ID, if any")

    class Config:
        # define JSON metadata for FastAPI's doc generator
        schema_extra = {
            "example": {
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
            }
        }


class GameModel(BaseModel):
    """Defines the Game schema"""
    id: str = Field(default_factory=PydanticObjectID, alias="_id", description=OBJ_ID_FIELD_DESC)
    player_ids: list[str, str] = Field(..., description="The players' IDs")
    game_state: MarbleGameModel = Field(..., description="A representation of the game state")
    versus_ai: bool = Field(...,  description="True if the game is one-player (vs AI), False if the game is two-player")
    completed: bool = Field(..., description="True if the game is over (completed), False otherwise")

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
                "versus_ai": False,
                "completed": False
            }
        }


class GameModelArray(BaseModel):
    """Defines the output schema for arrays of GameModels"""
    __root__: list[GameModel] = Field(..., description="Array of game id (key) - game data (value) pairs")


class _BaseGameInput(BaseModel):
    """Defines the base input schema for Game data"""
    player_one_id: str = Field(..., regex=ID_REGEX, description=f"{PLAYER_ID_DESC}: {OBJ_ID_FIELD_DESC}")
    player_one_color: str = Field(..., regex=COLOR_REGEX, description=COLOR_FIELD_DESC)


class OnePlayerGameInput(_BaseGameInput):
    """Defines the input schema for a one-player (player vs. ai) game"""

    class Config:
        # define JSON metadata for FastAPI's doc generator
        schema_extra = {
            "example": {
                "player_one_id": "79d9f0b7b744e7ba8e0dd4b8",
                "player_one_color": 'B',
            }
        }


class TwoPlayerGameInput(_BaseGameInput):
    """Defines the input schema for a two-player (player vs. player) game"""
    player_two_id: str = Field(..., regex=ID_REGEX, description=f"{PLAYER_ID_DESC}: {OBJ_ID_FIELD_DESC}")
    player_two_color: str = Field(..., regex=COLOR_REGEX, description=COLOR_FIELD_DESC)

    class Config:
        # define JSON metadata for FastAPI's doc generator
        schema_extra = {
            "example": {
                "player_one_id": "79d9f0b7b744e7ba8e0dd4b8",
                "player_two_id": "fe804ebe0d4ed7ebd277ca38",
                "player_one_color": 'B',
                "player_two_color": 'W',
            }
        }


# ---- CREATE ----
async def create(player_one_data: tuple[str, str], player_two_data: tuple[str, str], versus_ai: bool) -> dict:
    """
    Creates a new entry in the games database.

    :param player_one_data: a tuple containing the first player's id, name and marble color (in that order)
    :param player_two_data: a tuple containing the second player's id, name and marble color (in that order)
    :param versus_ai: True if the game is one-player (vs AI), False if the game is two-player (vs player)
    :return: an awaitable resolving to the inserted document
    """
    collection = await db.get_game_collection()
    player_ids = [player_one_data[0], player_two_data[0]]
    game_state = json.dumps(
        MarbleGame(player_one_data, player_two_data),
        cls=MarbleGameEncoder,
    )
    res = await collection.insert_one({
        "player_ids": player_ids,
        "game_state": game_state,
        "versus_ai": versus_ai,
        "completed": False,
    })
    return await find(res.inserted_id)


# ---- RETRIEVE ----
async def find(game_id: str) -> Optional[dict]:
    """
    Retrieves the specified game document.

    :param game_id: the object id of the game
    :return: an awaitable resolving to the matching document, or None if one is not found
    """
    collection = await db.get_game_collection()
    return await collection.find_one({"_id": PydanticObjectID(game_id)})


async def find_by_player_id(player_id: str, skip: int = 0, limit: int = 20, additional_filters: dict = None) -> list:
    """
    Retrieves an array of game documents containing the specified player_id.

    :param player_id: the object id of the player
    :param skip: the number of documents to skip (use this for more efficient searches; should be set to
                 limit*num_previous_calls on subsequent calls)
    :param limit: the maximum number of games to return (default = 20)
    :param additional_filters: any additional filters, passed as key-value pairs
    :return: an awaitable resolving to the array of matching document, or an empty array if there are none
    """
    filters = {} if additional_filters is None else additional_filters
    filters.update({"player_ids": player_id})
    collection = await db.get_game_collection()
    cursor = collection.find(
        filter=filters,
        skip=skip,
        limit=limit,
        cursor_type=CursorType.NON_TAILABLE,
    )
    return await cursor.to_list(length=limit)


async def find_and_decode_game_state(game_id: str) -> Optional[tuple[MarbleGame, bool]]:
    """
    Retrieves the specified game document's game state and whether the game is versus_ai.

    :param game_id: the object id of the game
    :return: an awaitable resolving to the matching document's game_state, or None if one is not found
    """
    collection = await db.get_game_collection()
    if (game := await collection.find_one({"_id": PydanticObjectID(game_id)})) is not None:
        return json.loads(game["game_state"], cls=MarbleGameDecoder), game["versus_ai"]


# ---- UPDATE ----
async def update_game_state(game_id: str, new_game_state: MarbleGame) -> Optional[dict]:
    """
    Updates the specified game document as follows:
        * game_state is replaced with the value passed
        * completed is set to True if the game is over (has a winner)

    :param game_id: the object id of the game
    :param new_game_state: the new game state
    :return: an awaitable resolving to the updated document, or None if one is not found
    """
    collection = await db.get_game_collection()
    values_to_set = {
        "game_state": json.dumps(new_game_state, cls=MarbleGameEncoder),
        "completed": new_game_state.winner is not None
    }
    updated_game = await collection.find_one_and_update(
        {"_id": PydanticObjectID(game_id)},
        {"$set": values_to_set},
        return_document=ReturnDocument.AFTER,
    )
    return updated_game


async def force_complete(game_id: str) -> Optional[dict]:
    """
    Updates the specified game document by setting completed to True, regardless of whether there's a winner.

    :param game_id: the object id of the game
    :return: an awaitable resolving to the updated document, or None if one is not found
    """
    collection = await db.get_game_collection()
    updated_game = await collection.find_one_and_update(
        {"_id": PydanticObjectID(game_id)},
        {"$set": {"completed": True}},
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
    collection = await db.get_game_collection()
    deleted = await collection.delete_one({"_id": PydanticObjectID(game_id)})
    return deleted.deleted_count

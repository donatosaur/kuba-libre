# Modified:    2021-08-23
# Description: Implements a controller for /game
#
from pydantic import BaseModel, Field
from httpx import AsyncClient
from fastapi import APIRouter, Path, HTTPException, status
from fastapi.responses import JSONResponse
from ..models import game_model, move_model
from . import ID_REGEX

game_router = APIRouter()

# define constants for descriptions and error messages
INVALID_PARAMS_MESSAGE = "Invalid parameters: player ids must be valid and unique, colors must be 'B' or 'W' and unique"
ID_FIELD_DESC = "24-digit hex string ObjectID"
COLOR_FIELD_DESC = "The player's marble color: 'B' for black or 'W' for white. These must be unique to each player."


class GameInput(BaseModel):
    """Defines the input schema for Game data"""
    player_one_id: str = Field(..., regex=ID_REGEX, description=ID_FIELD_DESC)
    player_two_id: str = Field(..., regex=ID_REGEX, description=ID_FIELD_DESC)
    player_one_color: str = Field(..., regex="[BbWw]", description=COLOR_FIELD_DESC)
    player_two_color: str = Field(..., regex="[BbWw]", description=COLOR_FIELD_DESC)

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


@game_router.post("/", response_description="Create a new game", response_model=game_model.Game)
async def create_game(game_input: GameInput) -> JSONResponse:
    """Handles /game create requests."""
    # ignore case
    p1_id, p2_id = game_input.player_one_id, game_input.player_two_id
    p1_color, p2_color = game_input.player_one_color.upper(), game_input.player_two_color.upper()

    # check whether the player ids are valid and unique
    async with AsyncClient() as client:
        urls = (f"localhost/player/{p1_id}", f"localhost/player/{p2_id}")
        requests = (await client.get(url) for url in urls)
        responses = map(lambda r: r.status_code != 200, requests)
    if p1_id == p2_id or any(responses):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_PARAMS_MESSAGE)

    # check whether the player colors are valid are unique
    colors = {'B', 'W'}
    colors.discard(p1_color)
    colors.discard(p2_color)
    if len(colors) != 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_PARAMS_MESSAGE)

    # create the game
    if (created := game_model.create((p1_id, p1_color), (p2_id, p2_color))) is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created)


@game_router.get("/{game_id}", response_description="Get a game", response_model=game_model.Game)
async def retrieve_player(game_id: str = Path(..., regex=ID_REGEX, description="The game's id")) -> JSONResponse:
    """Handles /game/{game_id} retrieve requests."""
    if (retrieved := game_model.find(game_id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Game with id={game_id} not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content=retrieved)


@game_router.patch("/{game_id}/make-move", response_description="Make a move", response_model=move_model.MoveOutput)
async def make_move(game_id: str, move: move_model.MoveInput) -> JSONResponse:
    """Handles /game/{game_id}/move update requests"""
    # get the game
    if (retrieved := await game_model.find(game_id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Game with id={game_id} not found")

    # validate the player ID
    if move.player_id not in retrieved.player_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Player with id={move.player_id} not found in game with id={game_id}"
        )

    # parse the game, make the move, and check the game state
    game = retrieved.game_state
    move_successful = game.make_move(move.player_id, (move.row_coord, move.col_coord), move.direction.lower())
    game_complete = game.winner is not None

    # update the game and player resources if applicable
    if move_successful:
        await game_model.update_game_state(game_id, game)
    if game_complete:
        async with AsyncClient() as client:
            for player_id in retrieved.player_ids:
                await client.patch(f"localhost/players/{player_id}/current-games/{game_id}/complete")

    res = {
        "move_successful": move_successful,
        "game_complete": game_complete,
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=res)

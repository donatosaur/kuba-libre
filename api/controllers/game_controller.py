# Modified:    2021-08-22
# Description: Implements a controller for game info
#
from httpx import AsyncClient
from fastapi import APIRouter, Path, Body, HTTPException, status
from fastapi.responses import JSONResponse
from ..models import game_model
from . import ID_REGEX

game_router = APIRouter()
INVALID_PARAMS_MESSAGE = "Invalid parameters: player ids must be valid and unique, colors must be 'B' or 'W' and unique"

# define JSON metadata for FastAPI's doc generator
create_example = {
    "player_one_id": "79d9f0b7b744e7ba8e0dd4b8",
    "player_one_color": 'B',
    "player_two_id": "fe804ebe0d4ed7ebd277ca38",
    "player_two_color": 'W'
}


@game_router.post("/", response_description="Create a new game", response_model=game_model.Game)
async def create_game(body: Body(..., example=create_example)) -> JSONResponse:
    """Handles /game create requests."""
    # check whether the required body parameters were passed
    body_params = (
        p1_id := body.get("player_one_id"),
        p2_id := body.get("player_two_id"),
        p1_color := body.get("player_one_color"),
        p2_color := body.get("player_two_color"),
    )
    if any(map(lambda x: x is None, body_params)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required parameter")

    # check whether the player ids are valid and unique
    with AsyncClient() as client:
        requests = (await client.get(url) for url in (f"localhost/player/{p1_id}", f"localhost/player/{p2_id}"))
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
    if (created_game := game_model.create((p1_id, p1_color), (p2_id, p2_color))) is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_game)


@game_router.get("/{game_id}", response_description="Get a game", response_model=game_model.Game)
async def retrieve_player(game_id: str = Path(..., regex=ID_REGEX, description="The game's id")) -> JSONResponse:
    """Handles /game/{game_id} retrieve requests."""
    # retrieve the game
    if (retrieved_game := game_model.find(game_id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Game with id={game_id} not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content=retrieved_game)

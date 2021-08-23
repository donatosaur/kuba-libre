# Modified:    2021-08-23
# Description: Implements a controller for /player
#
from pydantic import Field
from fastapi import APIRouter, Path, Body, HTTPException, status
from fastapi.responses import JSONResponse
from ..models import player_model
from . import ID_REGEX, PLAYER_ID_DESC, GAME_ID_DESC

player_router = APIRouter()


@player_router.post("/", response_description="Create a new player", response_model=player_model.Player)
async def create_player(
        body: Body(..., example={"name": "Player Name", "username": "player_username"}),
) -> JSONResponse:
    """Handles /player create requests."""
    # check whether the required body parameters were passed
    if (username := body.get("username")) is None or (name := body.get("name")) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required parameter")
    # create the player
    if (created := player_model.create(username, name)) is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created)


@player_router.get("/{player_id}", response_description="Get a player", response_model=player_model.Player)
async def retrieve_player(
        player_id: str = Path(..., regex=ID_REGEX, description=PLAYER_ID_DESC),
) -> JSONResponse:
    """Handles /player/{player_id} retrieve requests."""
    if (retrieved := player_model.find(player_id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Player with id={player_id} not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content=retrieved)


@player_router.patch("/{player_id}", response_description="Update a player's name", response_model=player_model.Player)
async def update_player(
        player_id: str = Path(..., regex=ID_REGEX, description=PLAYER_ID_DESC),
        name: str = Body(..., description="A new name for the player"),
) -> JSONResponse:
    """Handles /player/{player_id} update requests."""
    # check whether the required body parameter was passed
    if name is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required parameter")
    # update the player
    if (updated := player_model.update_name(player_id, name)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Player with id={player_id} not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content=updated)


@player_router.patch(
    "/{player_id}/current-games/{game_id}/add",
    response_description="Adds the specified game to the player's current games",
    response_model=player_model.Player,
)
async def update_player(
        player_id: str = Field(..., regex=ID_REGEX, description=PLAYER_ID_DESC),
        game_id: str = Field(..., regex=ID_REGEX, description=GAME_ID_DESC),
) -> JSONResponse:
    """Handles /{player_id}/current-games/{game_id}/add update requests."""
    if (updated := player_model.add_current_game(player_id, game_id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Player with id={player_id} not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content=updated)


@player_router.patch(
    "/{player_id}/current-games/{game_id}/complete",
    response_description="Moves the specified game from the player's current games and adds to their completed games",
    response_model=player_model.Player,
)
async def update_player(
        player_id: str = Field(..., regex=ID_REGEX, description=PLAYER_ID_DESC),
        game_id: str = Field(..., regex=ID_REGEX, description=GAME_ID_DESC),
) -> JSONResponse:
    """Handles /{player_id}/current-games/{game_id}/complete update requests"""
    if (updated := player_model.move_current_game_to_completed(player_id, game_id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Player with id={player_id} not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content=updated)

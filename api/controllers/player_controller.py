# Modified:    2021-08-21
# Description: Implements a controller for game info
#
from fastapi import APIRouter, Path, Body, HTTPException, status
from fastapi.responses import JSONResponse
from ..models import player_model
from . import ID_REGEX

player_router = APIRouter()

# define JSON metadata for FastAPI's doc generator
create_example = {
    "name": "Example Name",
    "username": "example_username"
}


@player_router.post("/", response_description="Create a new player", response_model=player_model.Player)
async def create_player(body: Body(..., example=create_example)) -> JSONResponse:
    """Handles /player create requests."""
    # check whether the required body parameters were passed
    if (username := body.get("username")) is None or (name := body.get("name")) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required parameter")

    # create the player
    if (created_player := player_model.create(username, name)) is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_player)


@player_router.get("/{player_id}", response_description="Get a player", response_model=player_model.Player)
async def retrieve_player(player_id: str = Path(..., regex=ID_REGEX, description="The player's id")) -> JSONResponse:
    """Handles /player/{player_id} retrieve requests."""
    # retrieve the player
    if (retrieved_player := player_model.find(player_id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Player with id={player_id} not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content=retrieved_player)


@player_router.put("/{player_id}", response_description="Update a player", response_model=player_model.Player)
async def update_player(
        player_id: str = Path(..., regex=ID_REGEX, description="The player's id"),
        name: str = Body(..., description="A new name for the player")
) -> JSONResponse:
    """Handles /player/{player_id} update requests."""
    # check whether the required body parameter was passed
    if name is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required parameter")

    # update the player
    if (updated_player := player_model.update_name(player_id, name)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Player with id={player_id} not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content=updated_player)

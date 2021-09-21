# Modified:    2021-08-30
# Description: Implements a controller for /player
#
from fastapi import APIRouter, Path, HTTPException, status, Query
from api.models import player_model, game_model
from .responses import CustomJSONResponse as JSONResponse
from . import ID_REGEX, PLAYER_ID_DESC, SKIP_DESC, LIMIT_DESC

router = APIRouter()


@router.post("/", response_description="Create a new player", response_model=player_model.PlayerModel)
async def create_player(player_input: player_model.PlayerInput) -> JSONResponse:
    """Handles /player create requests."""
    # ensure auth0_id is unique
    if await player_model.find_by_auth0_id(player_input.auth0_id) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with auth0_id={player_input.auth0_id} already exists"
        )
    if (created := await player_model.create(player_input)) is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created)


@router.get("/{player_id}", response_description="Get a player", response_model=player_model.PlayerModel)
async def retrieve_player(
        player_id: str = Path(..., regex=ID_REGEX, description=PLAYER_ID_DESC),
) -> JSONResponse:
    """Handles /player/{player_id} retrieve requests."""
    if (retrieved := await player_model.find_by_id(player_id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id={player_id} not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content=retrieved)


@router.get(
    "/{player_id}/games",
    response_description="Get all of a player's games (both current and completed)",
    response_model=game_model.GameModelArray
)
async def retrieve_player_games(
        player_id: str = Path(..., regex=ID_REGEX, description=PLAYER_ID_DESC),
        skip: int = Query(..., ge=0, description=SKIP_DESC),
        limit: int = Query(..., gt=0, le=100, description=LIMIT_DESC),
) -> JSONResponse:
    """Handles /player/{player_id}/games retrieve requests."""
    # find_by_player_id should always return an array (barring database connection issues); if the array is empty, we
    # need to check whether the player exists so that we can return a specific error (otherwise, the empty array)
    if (retrieved := await game_model.find_by_player_id(player_id, skip, limit)) is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    if not retrieved and await(player_model.find_by_id(player_id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id={player_id} not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content=retrieved)


@router.get(
    "/{player_id}/games/current",
    response_description="Get a player's current games",
    response_model=game_model.GameModelArray
)
async def retrieve_player_games_current(
        player_id: str = Path(..., regex=ID_REGEX, description=PLAYER_ID_DESC),
        skip: int = Query(..., ge=0, description=SKIP_DESC),
        limit: int = Query(..., ge=1, le=100, description=LIMIT_DESC),
) -> JSONResponse:
    """Handles /player/{player_id}/games/current retrieve requests."""
    if (retrieved := await game_model.find_by_player_id(player_id, skip, limit, {"completed": False})) is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    if not retrieved and await(player_model.find_by_id(player_id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id={player_id} not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content=retrieved)


@router.get(
    "/{player_id}/games/completed",
    response_description="Get a player's completed games",
    response_model=game_model.GameModelArray
)
async def retrieve_player_games_completed(
        player_id: str = Path(..., regex=ID_REGEX, description=PLAYER_ID_DESC),
        skip: int = Query(..., ge=0, description=SKIP_DESC),
        limit: int = Query(..., ge=1, le=100, description=LIMIT_DESC),
) -> JSONResponse:
    """Handles /player/{player_id}/games/current retrieve requests."""
    if (retrieved := await game_model.find_by_player_id(player_id, skip, limit, {"completed": True})) is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    if not retrieved and await(player_model.find_by_id(player_id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id={player_id} not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content=retrieved)

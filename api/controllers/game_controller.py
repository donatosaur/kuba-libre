# Modified:    2021-09-21
# Description: Implements a controller for /game
#
from typing import Union
from fastapi import APIRouter, Path, HTTPException, status
from models import game_model, player_model, move_model
from marble_game import make_move_ai
from .responses import CustomJSONResponse as JSONResponse
from . import ID_REGEX, GAME_ID_DESC, AI_PLAYER_ID


router = APIRouter()

# define constants for error messages
INVALID_PARAMS_MESSAGE = "Invalid parameters: player ids must be valid and unique, colors must be 'B' or 'W' and unique"


@router.post("/", response_description="Create a new game", response_model=game_model.GameModel)
async def create_game(
        # more restrictive schema must be first (see https://fastapi.tiangolo.com/tutorial/extra-models/#union-or-anyof)
        game_input: Union[game_model.TwoPlayerGameInput, game_model.OnePlayerGameInput]
) -> JSONResponse:
    """
    Handles /game create requests.

    If the request is valid, also adds the games ids to the players' current games.
    """
    versus_ai = isinstance(game_input, game_model.OnePlayerGameInput)

    # generate default values for AI (if applicable) and ignore case
    p1_id = game_input.player_one_id
    p2_id = game_input.player_two_id if not versus_ai else AI_PLAYER_ID
    p1_color = game_input.player_one_color.upper()
    p2_color = game_input.player_two_color if not versus_ai else ('W' if p1_color == 'B' else 'B')

    # validate input for one player games (vs AI)
    if versus_ai:
        # check whether the player's id and marble color are valid
        if await player_model.find_by_id(p1_id) is None or p1_color not in {'B', 'W'}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_PARAMS_MESSAGE)
    # validate input for two player games (vs player)
    else:
        # check whether the player ids are valid and unique
        if p1_id == p2_id or await player_model.find_by_id(p1_id) is None or await player_model.find_by_id(p2_id) is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_PARAMS_MESSAGE)
        # check whether the players' marble colors are valid and unique
        colors = {'B', 'W'}
        colors.discard(p1_color)
        colors.discard(p2_color)
        if len(colors) != 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_PARAMS_MESSAGE)

    # create the game
    if (created := await game_model.create((p1_id, p1_color), (p2_id, p2_color), versus_ai)) is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    # update the player resources (if applicable)
    await player_model.add_current_game(p1_id, created["_id"])
    if not versus_ai:
        await player_model.add_current_game(p2_id, created["_id"])

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created)


@router.get("/{game_id}", response_description="Get a game", response_model=game_model.GameModel)
async def retrieve_game(game_id: str = Path(..., regex=ID_REGEX, description=GAME_ID_DESC)) -> JSONResponse:
    """Handles /game/{game_id} retrieve requests."""
    if (retrieved := await game_model.find(game_id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Game with id={game_id} not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content=retrieved)


@router.patch("/{game_id}/make-move", response_description="Make a move", response_model=move_model.MoveOutput)
async def make_move(game_id: str, move: move_model.MoveInput) -> JSONResponse:
    """
    Handles /game/{game_id}/move update requests.

    If the request is valid and the move results in a completed game, also moves the game id from the players' current
    games to their completed games.
    """
    # get the game and parse it; we can skip validating the player id because moves made by an invalid player will
    # be unsuccessful and this method doesn't ever expose the game state to the client
    if (game_info := await game_model.find_and_decode_game_state(game_id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Game with id={game_id} not found")
    game, versus_ai = game_info

    # make the player's move; if applicable, also make the AI player's move
    move_successful = game.make_move(move.player_id, (move.row_coord, move.col_coord), move.direction.upper())
    if move_successful and versus_ai and game.winner is None:       # make the AI player's move
        if not make_move_ai(AI_PLAYER_ID, game):                    # this move should always succeed
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error: AI move failed"
            )

    # update game resource
    if await game_model.update_game_state(game_id, game) is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error: game update failed."
        )

    # check if the game is over
    game_complete = game.winner is not None

    # update player resources, if applicable (and only the *first time* there's a winner)
    if move_successful and game_complete:
        if versus_ai:
            await player_model.move_current_game_to_completed(move.player_id, game_id)
        else:
            for player_id in game.player_ids:
                await player_model.move_current_game_to_completed(player_id, game_id)

    res = {
        "move_successful": move_successful,
        "game_complete": game_complete,
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=res)

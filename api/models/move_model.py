# Modified:    2021-08-23
# Description: Implements a model for move info
#
from pydantic import BaseModel, Field
from . import ID_REGEX, PLAYER_ID_DESC, OBJ_ID_FIELD_DESC


class MoveInput(BaseModel):
    """Defines a schema for move input"""
    player_id: str = Field(..., regex=ID_REGEX, description=f"{PLAYER_ID_DESC}: {OBJ_ID_FIELD_DESC}")
    row_coord: int = Field(..., ge=0, le=6)
    col_coord: int = Field(..., ge=0, le=6)
    direction: str = Field(..., regex=r"^[FfBbLlRr]$", description="The direction of the move: F, B, R or L")

    class Config:
        # define JSON metadata for FastAPI's doc generator
        schema_extra = {
            "player_id": "e6a6c4b619378404d636668f",
            "row_coord": 2,
            "col_coord": 5,
            "direction": 'R',
        }


class MoveOutput(BaseModel):
    """Defines a schema for move output"""
    move_successful: bool = Field(..., description="True if the move was successful and the game state has changed")
    game_complete: bool = Field(..., description="True if the game is over as a result of the move")

    class Config:
        # define JSON metadata for FastAPI's doc generator
        schema_extra = {
            "move_successful": True,
            "game_complete": False,
        }

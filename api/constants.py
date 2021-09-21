# Modified:    2021-08-31
# Description: Defines api-wide constants
from typing import Final

# regex
ID_REGEX: Final = r"^[0-9a-f]{24}$"
DIRECTION_REGEX: Final = r"^[FfBbLlRr]$"
COLOR_REGEX: Final = r"^[BbWw]$"

# descriptions for API docs
OBJ_ID_FIELD_DESC: Final = "24-digit hex string ObjectID"
PLAYER_ID_DESC: Final = "The player's ID"
GAME_ID_DESC: Final = "The game's ID"
COLOR_FIELD_DESC: Final = "The player's marble color: 'B' for black or 'W' for white. " \
                          "These must be unique to each player."
SKIP_DESC: Final = "An offset, used to page through the results." \
                   "For example, if a previous call was made with a skip of 0 and a limit of 20, a subsequent call " \
                   "to obtain the next page of results should have a skip of 20"
LIMIT_DESC: Final = "Maximum number of documents to include"

# standard ID representing the AI player
AI_PLAYER_ID: Final = "AI_PLAYER"

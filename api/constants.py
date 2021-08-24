# Modified:    2021-08-24
# Description: Defines api-wide constants
from typing import Final

# regex
ID_REGEX: Final = r"^[0-9a-f]{24}$"
DIRECTION_REGEX: Final = r"^[FfBbLlRr]$"

# descriptions for API docs
OBJ_ID_FIELD_DESC: Final = "24-digit hex string ObjectID"
PLAYER_ID_DESC: Final = "The player's ID"
GAME_ID_DESC: Final = "The game's ID"

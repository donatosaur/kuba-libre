from typing import Optional
from pydantic import BaseModel, Field


# define the schema for each game instance
class Game(BaseModel):
    id: str = Field(alias="_id")
    player_ids: tuple
    player_data: dict
    previous_state: list = []
    current_state: list = []


async def create_game(players: tuple):
    """
    Creates a new game with the specified player info

    :param players:
    :return:
    """
    pass

async def find_all_games():
    pass

async def find_game():
    pass

async def update_game():
    pass

import bson

from pydantic import BaseModel, Field


# define the schema for each player
class Player(BaseModel):
    id: str = Field(alias="_id")
    username: str
    name: str
    games: set = set()
    history: list = []

# Copyright 2021 Donato Quartuccia
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# All trademarks and copyrights are the property of their respective owners.
#
# Modified:    2021-08-20
# Description: Implements a model for game info
#
import json
from pydantic import BaseModel, Field
from marble_game import MarbleGame, MarbleGameEncoder, MarbleGameDecoder
from . import PydanticObjectID


class Game(BaseModel):
    """Defines the Game schema"""
    id: str = Field(default_factory=PydanticObjectID, alias="_id")
    player_ids: tuple[str, str]
    game_state: MarbleGame

    class Config:
        # allow id to be populated by id or _id
        allow_population_by_field_name = True

        # define json encoders & decoders for the schema
        @staticmethod
        def json_dumps(o: Game):
            if not isinstance(o, Game):
                raise TypeError(f"Unsupported type {o.__class__}")
            return json.dumps({
                "id": o.id,
                "player_ids": o.player_ids,
                "game_state": json.dumps(o.game_state, cls=MarbleGameEncoder),
            })

        @staticmethod
        def json_loads(s: str):
            def hook(d: dict):
                return Game(
                    id=d["id"],
                    player_ids=tuple(json.loads(d["player_ids"])),
                    game_state=json.loads(d[""], cls=MarbleGameDecoder),
                )
            return json.loads(s, object_hook=hook)


async def find_all_games():
    pass

async def find_game():
    pass

async def update_game():
    pass


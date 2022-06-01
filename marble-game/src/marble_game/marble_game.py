# Copyright 2021-2022 Donato Quartuccia
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
# Modified:    2021-09-09
# Description: Contains backend logic for the marble game and provides an interface for the game. Responsible for:
#              turn tracking, score tracking, making (valid) moves and determining win conditions.
#
import json
from typing import Optional, Generator
from .game_board import GameBoard, GameBoardEncoder, GameBoardDecoder


class MarbleGame:
    """Represents a game instance, with two players and a board."""

    def __init__(self,
                 player_one_data: tuple[str, str] = None,
                 player_two_data: tuple[str, str] = None,
                 **kwargs):
        """
        Creates a MarbleGame in the state defined by kwargs if present, otherwise in its initial state (with no winner,
        a score of zero for each player, a board with no moves having been made, and any player allowed to go first).

        **Note**:
            - if state is being restored, both board and players must be passed as kwargs, and any values passed as
              other parameters are ignored
            - if the game is being created in its initial state, both player_one_data and player_two_data are required

        :param player_one_data: a tuple containing the first player's id and marble color (in that order)
        :param player_two_data: a tuple containing the second player's id and marble color (in that order)
        :keyword board: the GameBoard to be restored
        :keyword players: player dictionary mapped by player_id -> {name, color, red captured, opponent captured}
        :keyword current_turn: id of player whose turn it is
        :keyword winner: id of player who won
        """
        # get and validate player and board info
        if "players" in kwargs and "board" in kwargs:
            player_ids = tuple(kwargs["players"].keys())
            if len(player_ids) != 2:
                raise ValueError("kwarg players missing 1 or more player id")

            required = {"color", "red_marbles_captured", "opponent_marbles_captured"}
            if not all(required.issubset(kwargs["players"][player_id].keys()) for player_id in player_ids):
                raise ValueError("kwarg players[player_id] missing required keys")

            valid_colors = {'B', 'W'}
            valid_colors.discard(kwargs["players"][player_ids[0]]["color"])
            valid_colors.discard(kwargs["players"][player_ids[1]]["color"])
            if len(valid_colors) != 0:
                raise ValueError("players cannot have the same marble color and only 'B' and 'W' are valid colors")

            captured = 0
            for player_id in player_ids:
                captured += kwargs["players"][player_id]["red_marbles_captured"]
                captured += kwargs["players"][player_id]["opponent_marbles_captured"]
            if 29 - captured != sum(kwargs["board"].marble_count):  # there are 29 marbles originally on the board
                raise ValueError("check board state or captured marble count")

            # at this point, we can be fairly certain the data is valid
            self._players = kwargs["players"]
            self._game_board = kwargs["board"]

        elif player_one_data is not None and player_two_data is not None:
            # unpack the data; this will throw ValueError if there isn't enough data
            p1_id, p1_color = player_one_data
            p2_id, p2_color = player_two_data

            # validate the ids and colors
            if p1_id == p2_id:
                raise ValueError("player ids must be unique")

            valid_colors = {'B', 'W'}
            valid_colors.discard(p1_color)
            valid_colors.discard(p2_color)
            if len(valid_colors) != 0:
                raise ValueError("players cannot have the same marble color and only 'B' and 'W' are valid colors")

            # the data is valid, so create the player dictionary and initialize the board
            self._players = {
                p1_id: {
                    "color": p1_color,
                    "red_marbles_captured": 0,       # if this is >= 7, the player wins
                    "opponent_marbles_captured": 0,  # this doesn't affect the score
                },
                p2_id: {
                    "color": p2_color,
                    "red_marbles_captured": 0,       # if this is >= 7, the player wins
                    "opponent_marbles_captured": 0,  # this doesn't affect the score
                }
            }
            self._game_board = GameBoard()

        else:
            raise TypeError("missing params - either pass required args or required kwargs")

        self._current_turn = kwargs.get("current_turn")  # will hold the current player's id
        self._winner = kwargs.get("winner")              # will hold the winning player's id

    @property
    def current_turn(self) -> Optional[str]:
        """The player whose turn it is, if any"""
        return self._current_turn

    @property
    def player_ids(self) -> set[str]:
        """A set containing the players' ids"""
        return set(self._players.keys())

    @property
    def winner(self) -> Optional[str]:
        """The name of the winning player, if any"""
        return self._winner

    @property
    def marble_count(self) -> tuple[int, int, int]:
        """The number of white, black and red marbles (in that order) present on the game board"""
        return self._game_board.marble_count

    def get_player_color(self, player_id: str) -> Optional[str]:
        """Returns the color of the specified player's marbles, or None if no such player exists"""
        try:
            return self._players[player_id]["color"]
        except KeyError:
            return None

    def get_captured(self, player_id: str) -> Optional[int]:
        """Returns the number of red marbles captured by the specified player, or none if no such player exists"""
        try:
            return self._players[player_id]["red_marbles_captured"]
        except KeyError:
            return None

    def get_opponent_captured(self, player_id: str) -> Optional[int]:
        """Returns the number of opponent marbles captured by the specified player, or None if no such player exists"""
        try:
            return self._players[player_id]["opponent_marbles_captured"]
        except KeyError:
            return None

    def get_marble(self, coordinates: tuple[int, int]) -> Optional[str]:
        """
        Returns the marble ('W', 'B', 'R') in the specified cell, or None if there is no marble in the cell

        :param coordinates: (row, column) coordinates of the cell
        """
        # we can just just call the game board's method for this
        return self._game_board.get_contents_at_position(coordinates)

    def generate_possible_moves(self, player_id: str) -> Generator[tuple[tuple[int, int], str], None, None]:
        """Generates all the possible moves that may be made by the specified player in the board's current state"""
        player_color = self.get_player_color(player_id)
        for coordinate in self._game_board.generate_all_row_and_column_combinations():
            if self._game_board.get_contents_at_position(coordinate) == player_color:
                # unpack the coordinates and check whether the adjacent squares are empty (or represent an edge)
                row_index, column_index = coordinate

                adjacent_squares = (               # adjacent squares, in order: above, below, left, right
                    (row_index - 1, column_index),
                    (row_index + 1, column_index),
                    (row_index, column_index - 1),
                    (row_index, column_index + 1)
                )
                directions = ('B', 'F', 'R', 'L')   # opposite moves, in order: backward, forward, right, left

                for adjacent_coordinate, direction in zip(adjacent_squares, directions):
                    # only valid coordinates are generated; if the square is now invalid, the original was on an edge
                    square_along_edge = -1 in adjacent_coordinate or 7 in adjacent_coordinate
                    if not square_along_edge and not self._game_board.is_empty_position(adjacent_coordinate):
                        continue
                    if self._game_board.simulate_move(coordinate, direction) not in {"previous", player_color}:
                        yield coordinate, direction

    def is_player_out_of_moves(self, player_id: str) -> bool:
        """Returns True if the specified player is out of possible moves, otherwise False."""
        return next(self.generate_possible_moves(player_id), None) is None

    def is_move_valid(self, player_id: str, coordinates: tuple[int, int], direction: str) -> bool:
        """
        Returns True if the move being attempted is valid. Otherwise, returns False.

        A move is invalid if the game is over, the player/direction/coordinates don't exist, it's not the current
        player's turn, the player is trying to make a move with a marble that is not theirs, or the marble can't
        be moved in the specified direction.

        :param player_id: the id of the player making the move
        :param coordinates: (row, column) coordinates of the cell
        :param direction: the direction to move the marble in the specified cell
        """
        # validate game state and input
        prerequisites = (
            self.winner is None,                                # the game must not be over
            player_id in self.player_ids,                       # the player must exist
            direction in {'L', 'R', 'F', 'B'},                  # the direction must be valid
            self._current_turn in {None, player_id},            # the player must be able to make a move
            self._game_board.is_valid_square(coordinates),      # the square must exist
        )
        if not all(prerequisites):
            return False

        # check whether the square opposite the direction of movement is empty or an edge
        row_index, column_index = coordinates
        if direction == 'L':
            column_index += 1  # pushing left => square one column to the right should be empty or an edge
        elif direction == 'R':
            column_index -= 1  # pushing right => square one column to the left should be empty or an edge
        elif direction == 'F':
            row_index += 1     # pushing up => square one row below should be empty or an edge
        else:
            row_index -= 1     # pushing down => square one row above should be empty or an edge
        adjacent_coordinates = row_index, column_index
        # if the original square exists but the previous one doesn't, then the original square must occupy an edge
        square_is_not_along_edge = self._game_board.is_valid_square(adjacent_coordinates)
        if square_is_not_along_edge and self.get_marble(adjacent_coordinates) is not None:
            return False

        # at this point, the game is still ongoing, it's the current player's turn, and the move is physically possible
        # but we still need to check that the player is trying to move their own marble, won't push off one of their
        # own marbles, and that the move won't return the board to its previous state

        # if the player is trying to move a marble that doesn't belong to them, the move is invalid
        player_marble_color = self.get_player_color(player_id)
        if player_marble_color != self.get_marble(coordinates):
            return False

        # if pushing the marble would return the board to its previous state, the move is invalid
        simulated_result = self._game_board.simulate_move(coordinates, direction)
        if simulated_result == "previous":
            return False

        # if the move would cause one of the player's marbles to fall off the edge, the move is invalid
        if simulated_result == player_marble_color:
            return False

        # otherwise, the move is valid
        return True

    def make_move(self, player_id: str, coordinates: tuple[int, int], direction: str) -> bool:
        """
        Attempts to move a marble in the specified cell.

        Directions must be one of the following:
          - 'L' for left
          - 'R' for right
          - 'F' for forward (up)
          - 'B' for backward (down)

        :param player_id: the id of the player making the move
        :param coordinates: (row, column) coordinates of the cell
        :param direction: the direction to move the marble in the specified cell
        """
        # check whether the move is invalid before proceeding
        if not self.is_move_valid(player_id, coordinates, direction):
            return False

        # otherwise, make the move
        marble_pushed_off = self._game_board.move_marble(coordinates, direction)

        # update the marble/score trackers
        if marble_pushed_off is not None:
            if marble_pushed_off == 'R':
                self._players[player_id]["red_marbles_captured"] += 1
            else:
                self._players[player_id]["opponent_marbles_captured"] += 1

        # check for win conditions (player captured 7 marbles, opponent has no marbles left)
        if self.get_captured(player_id) >= 7:
            # the player captured 7 red marbles, so they win
            self._winner = player_id
        else:
            white_marbles, black_marbles, red_marbles = self.marble_count
            if white_marbles == 0 or black_marbles == 0:
                # a player can't push their own marbles off the board, so if either of these is 0 it's guaranteed
                # that the player just pushed their opponent's last marble off the board
                self._winner = player_id

        # get the opponent's id
        ids = self.player_ids
        ids.remove(player_id)
        opponent = ids.pop()  # there should only be one element in the set so we can just use pop()

        # swap the current player
        self._current_turn = opponent

        # check whether the opponent has any available moves (if they don't, then they lose)
        if self.is_player_out_of_moves(opponent):
            self._winner = player_id

        # if we get here, then the move was valid
        return True

    def __str__(self):
        return str(self._game_board)

    def __repr__(self):
        # build a string representation of the MarbleGame
        representation = [
            "MarbleGame(",
            "_players=" + repr(self._players),
            "_current_turn=" + repr(self._current_turn),
            "_winner=" + repr(self._winner),
            "_game_board=" + repr(self._game_board),
        ]
        return '\n'.join(representation)


class MarbleGameEncoder(json.JSONEncoder):
    """Encodes the relevant MarbleGame info to JSON str"""

    def default(self, o: MarbleGame) -> dict:
        if not isinstance(o, MarbleGame):
            raise TypeError(f"Unsupported type {o.__class__}")
        return {
            "board": json.dumps(o._game_board, cls=GameBoardEncoder),
            "players": json.dumps(o._players),
            "current_turn": o.current_turn,
            "winner": o.winner,
        }


class MarbleGameDecoder(json.JSONDecoder):
    """Decodes JSON GameBoard str to a MarbleGame object"""

    def __init__(self):
        # define a hook
        def hook(d: dict):
            return MarbleGame(
                board=json.loads(d["board"], cls=GameBoardDecoder),
                players=json.loads(d["players"]),
                current_turn=d["current_turn"],
                winner=d["winner"],
            )
        # pass it to deserialize JSON dict to MarbleGame
        super().__init__(object_hook=hook)

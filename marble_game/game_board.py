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
# Modified:    2021-08-16
# Description: Contains backend logic for the game board. Responsible for containing & counting marbles, validating
#              coordinates, making & simulating moves, and communicating each grid square's contents.
#
from typing import Any, Final, Generator, Optional
from itertools import chain
from dataclasses import dataclass
import json


class IllegalMoveException(Exception):
    """Raised when an attempted move violates the game rules in an unrecoverable way."""
    pass


@dataclass
class Square:
    """A mutable container for a single-character string (or None). Represents a square on the game board."""
    _contents: Optional[str] = None

    @property
    def contents(self) -> Any:
        """The contents of the Square"""
        return self._contents

    @contents.setter
    def contents(self, value: Optional[str]):
        self._contents = value

    def __eq__(self, other):
        if not isinstance(other, Square):
            return NotImplemented
        return self._contents == other._contents

    def __str__(self):
        return str(self._contents)

    def __repr__(self):
        return f"Square(id={hex(id(self))} _contents= {self._contents})"


class GameBoard:
    """Represents 7 x 7 game board composed of 49 Squares and intended to be indexed by (row, column)."""

    # class variables
    _max_index: Final = 6  # the board is a square
    _direction_to_step: Final = {'F': -1, 'B': 1, 'L': -1, 'R': 1}  # maps directions to a step (for indexing)

    def __init__(self, **kwargs):
        """
        Creates a game board in the state defined by kwargs if present, otherwise in its initial state:
            - 8 'W' marbles in the top-left and bottom-right corner regions
            - 8 'B' marbles in the top-right and bottom-left corner regions
            - 13 'R' marbles in the center region, radiating outward in a plus-pattern
            - 20 empty squares

        :keyword grid: 49-character string denoting square contents, row-by-row ('W', 'B', 'R', ' ')
        :keyword previous_state: 49-character string denoting the previous game state's square contents, as in grid
        """
        # get and validate kwargs
        if "previous_state" in kwargs and "grid" not in kwargs:
            raise TypeError("missing parameter - cannot restore previous_state without restoring grid")

        grid_string = kwargs.get("grid", "WW   BBWW R BB  RRR   RRRRR   RRR  BB R WWBB   WW")
        prev_string = kwargs.get("previous_state")

        if len(grid_string) != 49:
            raise ValueError("grid must contain exactly 49 chars")
        if prev_string is not None and len(prev_string) != 49:
            raise ValueError("prev_string must contain exactly 49 chars")

        # initialize the grid
        self._grid = [[Square() for _ in range(7)] for _ in range(7)]
        for index in range(49):
            if grid_string[index] != ' ':
                # the row is located at index // 7, the column at index % 7
                self._grid[index // 7][index % 7].contents = grid_string[index]

        # initialize previous state
        self._previous_state = [[Square() for _ in range(7)] for _ in range(7)]
        if prev_string is not None:
            for index in range(49):
                if prev_string[index] != ' ':
                    # the row is located at index // 7, the column at index % 7
                    self._previous_state[index // 7][index % 7].contents = prev_string[index]

    @property
    def marble_count(self) -> tuple[int, int, int]:
        """The number of white, black and red marbles (in that order) present on the game board"""
        # initialize marble counters
        white_marble_count, black_marble_count, red_marble_count = 0, 0, 0

        # count the marbles (we can ignore any empty cells)
        for coordinates in self.generate_all_row_and_column_combinations():
            contents = self.get_contents_at_position(coordinates)
            if contents == 'W':
                white_marble_count += 1
            elif contents == 'B':
                black_marble_count += 1
            elif contents == 'R':
                red_marble_count += 1
        return white_marble_count, black_marble_count, red_marble_count

    @property
    def grid_as_str(self) -> str:
        """A 49-char string representation of grid"""
        return ''.join([str(square) for square in chain(*self._grid)]).replace('None', ' ')

    @property
    def previous_grid_as_str(self) -> str:
        """A 49-char string representation of previous_grid"""
        return ''.join([str(square) for square in chain(*self._previous_state)]).replace('None', ' ')

    def generate_all_row_and_column_combinations(self) -> Generator[tuple[int, int], None, None]:
        """Generates all the possible (row, column) combinations for the GameBoard"""
        for row_index in range(self._max_index + 1):
            for column_index in range(self._max_index + 1):
                yield row_index, column_index

    def get_contents_at_position(self, coordinates: tuple[int, int]) -> Optional[str]:
        """
        Returns the contents of the square at the specified coordinates

        :param coordinates: (row, column) of the square
        """
        row_index, column_index = coordinates
        return self._grid[row_index][column_index].contents

    def is_valid_square(self, coordinates: tuple[int, int]) -> bool:
        """
        Returns True if the specified coordinates refer to a square on the GameBoard, otherwise False.

        :param coordinates: (row, column) of the square
        """
        row_index, column_index = coordinates
        # the cell is valid if both of its row and column values are within the game board
        return 0 <= row_index <= self._max_index and 0 <= column_index <= self._max_index

    def is_empty_position(self, coordinates: tuple[int, int]) -> bool:
        """
        Returns True if the specified coordinates refer to an empty square, otherwise False.

        :param coordinates: (row, column) of the square
        """
        return self.get_contents_at_position(coordinates) is None

    def _deepcopy_grid(self) -> list[list]:
        """
        Returns a deepcopy of the GameBoard's grid
        """
        grid_copy = []
        for row in self._grid:
            row_copy = [Square(square.contents) for square in row]
            grid_copy.append(row_copy)
        return grid_copy

    def _validate_move(self, coordinates: tuple[int, int], direction):
        """
        Validates whether the proposed move is possible

        :param coordinates: (row, column) coordinates of the marble being pushed
        :param str direction: the direction to push the marble ('L', 'R', 'F' or 'B')
        :raises IllegalMoveException: if the move is not defined
        """
        # validate the coordinates
        if not self.is_valid_square(coordinates) or self.is_empty_position(coordinates):
            raise IllegalMoveException
        # validate the direction
        if direction not in {'L', 'R', 'F', 'B'}:
            raise IllegalMoveException

    def move_marble(self, coordinates: tuple[int, int], direction: str) -> Optional[str]:
        """
        Moves the marble at the given coordinates in the specified direction. Modifies the state of the game board.
        Assumes the move being made is legal, except as noted.

        :param coordinates: (row, column) of the marble being pushed
        :param direction: the direction to push the marble ('L', 'R', 'F' or 'B')
        :returns: the contents of the Square pushed off the game board as a result of the move
                  ('W', 'B' or 'R if a marble has been pushed off the game board, otherwise None)
        :raises IllegalMoveException: if the direction is undefined, the square doesn't exist, or the square is empty
        """
        self._validate_move(coordinates, direction)
        # save the board state (so we can check for ko rule compliance later)
        self._previous_state = self._deepcopy_grid()

        # push the marble along the appropriate axis
        step = self._direction_to_step[direction]
        if direction in {'F', 'B'}:
            # fix column index, vary row index; the Square's initial index along column is its original row position
            index_along_axis, fixed_index = coordinates
            axis = [self._grid[row_index][fixed_index] for row_index in range(self._max_index + 1)]
        else:
            # fix row index, vary column index; the Square's initial index along row is its original column position
            fixed_index, index_along_axis = coordinates
            axis = [self._grid[fixed_index][column_index] for column_index in range(self._max_index + 1)]

        return self._push_marble(axis, index_along_axis, step)

    def simulate_move(self, coordinates: tuple[int, int], direction: str) -> Optional[str]:
        """
        Simulates a potential move on the game board **without** modifying the game board's state. This should be used
        to determine what marble color (if any) would be knocked off the edge of the game board by the proposed move,
        or if the proposed move would violate the Ko rule.

        (See https://sites.google.com/site/boardandpieces/terminology/ko-rule)
        Assumes the specified coordinates and direction are valid and that the proposed move constitutes a legal move,
        except as noted.

        :param coordinates: (row, column) coordinates of marble being pushed
        :param direction: the direction to push the marble ('L', 'R', 'F' or 'B')
        :returns: "previous" if the proposed move would return the board to its previous state, otherwise the
                  the contents of the Square that would be pushed off the board as a result of the move (or
                  None if nothing would be pushed off)
        :raises IllegalMoveException: if the direction is undefined, the square doesn't exist, or the square is empty
        """
        self._validate_move(coordinates, direction)

        # push the marble along the appropriate axis, but on a deepcopy of the grid since we're just simulating it
        grid_copy = self._deepcopy_grid()
        step = self._direction_to_step[direction]
        if direction in {'F', 'B'}:
            # fix column index, vary row index; the Square's initial index along column is its original row position
            index_along_axis, fixed_index = coordinates
            axis = [grid_copy[row_index][fixed_index] for row_index in range(self._max_index + 1)]
        else:
            # fix row index, vary column index; the Square's initial index along row is its original column position
            fixed_index, index_along_axis = coordinates
            axis = [grid_copy[fixed_index][column_index] for column_index in range(self._max_index + 1)]

        # simulate the move and save the value that is pushed off
        pushed_off = self._push_marble(axis, index_along_axis, step)

        # check whether the proposed move would recreate the previous state
        for row_index, column_index in self.generate_all_row_and_column_combinations():
            # get the contents of the position that would result from the simulated move and its previous contents
            simulated_state = grid_copy[row_index][column_index].contents
            previous_state = self._previous_state[row_index][column_index].contents

            if simulated_state != previous_state:
                # at least one square differs, so the previous state isn't recreated
                return pushed_off

        # if we get here, then the proposed move would recreate the previous state and violates the Ko rule
        return "previous"

    def _push_marble(self, axis: list[Square], current_position: int, step: int, previous: Square = None) -> Optional[str]:
        """
        Helper method for move_marble and simulate_move. Pushes a marble along the specific axis, mutating the
        Squares along it to reflect their post-push contents.

        When first called, current_position should be the index of the Square that contains the marble being pushed,
        and previous_square should be None.

        The move should be checked for legality **before** calling this method. Assumes:
          - the Square at the specified coordinates exists
          - the Square contains a marble
          - moving the marble in the specified direction constitutes a legal move
          - current_position has been set to the index of the Square that contains the marble being pushed
          - previous_square is None

        :param axis: list of Squares
        :param current_position: the index of our current position on the axis
        :param step: -1 to push left (or up) along the axis, or +1 to push right (or down) along the axis
        :param previous: the square being moved
        :returns: the contents of the Square that pushed off the game board as a result of the proposed move
                  (or None if nothing is pushed off)
        """
        if previous is None:
            previous = Square()  # when the first marble is moved, its original space becomes empty

        # base case: we've moved off the edge of the game board
        if current_position < 0 or current_position > len(axis) - 1:
            return previous.contents
        # recursive step: move the contents of the previous square into the current one
        else:
            previous_contents = previous.contents
            current_contents = axis[current_position].contents
            # check whether we're pushing a marble into an empty square
            reached_empty = current_contents is None
            # swap the contents to move the marble into the current square
            axis[current_position].contents = previous_contents
            previous.contents = current_contents

            # if we pushed a marble into an empty square, we're done (and no marble was pushed off)
            return None if reached_empty else self._push_marble(axis, current_position + step, step, previous)

    def __str__(self):
        result = []
        for row in self._grid:
            for square in row:
                if square.contents is None:  # the square is empty
                    result.append("  ")
                else:
                    result.append(str(square) + ' ')
            result.append('\n')
        return ''.join(result)

    def __repr__(self):
        # build a string representation of the grids
        if self._previous_state is None:
            previous_state_representation = "None"
        else:
            previous_state_representation = [repr(row) for row in self._previous_state]
        grid_representation = [repr(row) for row in self._grid]

        # replace "None" with the unicode 'NUL' representation to align output
        null_char = '\u2400'

        # build a string representation of the GameBoard
        representation = [
            "MarbleGame(",
            "_max_index= " + repr(self._max_index),
            "_direction_to_step= " + repr(self._direction_to_step),
            "_previous_state=[\n" + ",\n".join(previous_state_representation).replace("None", null_char) + "]",
            "_grid=[\n" + ",\n".join(grid_representation).replace("None", null_char) + "]",
            ")"
        ]
        return '\n'.join(representation)


class GameBoardEncoder(json.JSONEncoder):
    """Encodes the relevant GameBoard info to JSON str"""

    def default(self, o: GameBoard) -> dict:
        if not isinstance(o, GameBoard):
            raise TypeError(f"Unsupported type {o.__class__}")
        return {"grid": o.grid_as_str, "previous_state": o.previous_grid_as_str}


class GameBoardDecoder(json.JSONDecoder):
    """Decodes JSON GameBoard str to a GameBoard object"""

    def __init__(self):
        # define and pass a hook to deserialize JSON to GameBoard
        super().__init__(object_hook=lambda d: GameBoard(grid=d["grid"], previous_state=d["previous_state"]))

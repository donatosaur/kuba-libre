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
# Modified:    2021-06-11
# Description: Contains backend logic for the game board, win tracking, score and turn tracking, movement rule
#              compliance, and actual movement along the board. The Game class is intended to provide an interface
#              for this backend logic.


class IllegalMoveException(Exception):
    """
    Raised when an attempted move violates the game rules in an unrecoverable way (e.g. the direction is undefined
    or the coordinates are undefined while an actual move is being made)
    """
    pass


class Square:
    """
    A mutable container that may hold any type of object. Represents a square on the game board.
    """

    def __init__(self, contents=None):
        """
        Creates a square with the specified contents (or an empty square if no arguments are passed)

        :param Any contents: the object contained in the Square
        """
        self._contents = contents

    @property
    def contents(self):
        """
        The object contained in the Square.
        """
        return self._contents

    @contents.setter
    def contents(self, value):
        self._contents = value

    def __str__(self):
        return str(self._contents)

    def __repr__(self):
        return f"Square(id={hex(id(self))} _contents= {self._contents})"


class GameBoard:
    """
    A 7 x 7 game board containing marbles.

    A GameBoard is composed of 49 Squares held on a 7 x 7 grid and intended to be indexed using (row, column) notation.
    These Squares are either empty (in which case their contents are None) or contain a marble ('R' for red marble,
    'W' for white marbles, 'B' for black marbles).

    The GameBoard is responsible for: containing and counting marbles; determining whether a given coordinate pair
    exists; moving marbles along a row or column; simulating a proposed move (including whether it would revert
    the board back to its previous state; and communicating the contents of each square on the grid to the caller.
    """

    def __init__(self):
        """
        Creates the game board in its initial state:
          - 8 white marbles in the top-left and bottom-right corner regions ('W' marbles)
          - 8 black marbles in the bottom-left and top-right corner regions ('B' marbles)
          - 13 red marbles in the center-most region, radiating outward in a plus-pattern ('R' marbles)
          - 20 empty squares
        """
        # initialize a game board so that it can be indexed by [row_number][column_number]
        self._grid = [
            [Square('W'), Square('W'), Square(   ), Square(   ), Square(   ), Square('B'), Square('B')],
            [Square('W'), Square('W'), Square(   ), Square('R'), Square(   ), Square('B'), Square('B')],
            [Square(   ), Square(   ), Square('R'), Square('R'), Square('R'), Square(   ), Square(   )],
            [Square(   ), Square('R'), Square('R'), Square('R'), Square('R'), Square('R'), Square(   )],
            [Square(   ), Square(   ), Square('R'), Square('R'), Square('R'), Square(   ), Square(   )],
            [Square('B'), Square('B'), Square(   ), Square('R'), Square(   ), Square('W'), Square('W')],
            [Square('B'), Square('B'), Square(   ), Square(   ), Square(   ), Square('W'), Square('W')],
        ]

        self._previous_state = None  # to hold a copy of the previous grid
        self._max_index = len(self._grid) - 1  # the board is a square
        self._direction_to_step = {'F': -1, 'B': 1, 'L': -1, 'R': 1}  # maps directions to a step (for indexing)

    def generate_all_row_and_column_combinations(self):
        """
        Generates all the possible (row, column) combinations for the GameBoard
        """
        for row_index in range(self._max_index + 1):
            for column_index in range(self._max_index + 1):
                yield row_index, column_index

    def get_contents_at_position(self, coordinates):
        """
        Returns the contents of the square at the specified coordinates

        :param tuple[int, int] coordinates: (row, column) coordinates of the square
        """
        row_index, column_index = coordinates
        return self._grid[row_index][column_index].contents

    def get_marble_count(self):
        """
        Returns a tuple containing the number of white, black and red marbles (in that order) on the game board
        """
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

    def is_valid_square(self, coordinates):
        """
        Returns True if the specified coordinates refer to a square on the GameBoard. Otherwise, returns False.

        :param tuple[int, int] coordinates: (row, column) coordinates to check for
        """
        row_index, column_index = coordinates
        # the cell is valid if both of its row and column values are within the game board
        return 0 <= row_index <= self._max_index and 0 <= column_index <= self._max_index

    def is_empty_position(self, coordinates):
        """
        Returns True if the specified coordinates refer to an empty square. Otherwise, returns False.

        :param tuple[int, int] coordinates: (row, column) coordinates of the square to be checked
        """
        return self.get_contents_at_position(coordinates) is None

    def deepcopy_grid(self):
        """
        Returns a deepcopy of the GameBoard's grid
        """
        grid_copy = []
        for row in self._grid:
            row_copy = [Square(square.contents) for square in row]
            grid_copy.append(row_copy)
        return grid_copy

    def _validate_move(self, coordinates, direction):
        """
        Validates whether the proposed move is possible

        :param tuple[int, int] coordinates: (row, column) coordinates of marble being pushed
        :param str direction: the direction to push the marble ('L', 'R', 'F' or 'B')
        :raises IllegalMoveException: if the move is not defined
        """
        # validate the coordinates
        if not self.is_valid_square(coordinates) or self.is_empty_position(coordinates):
            raise IllegalMoveException
        # validate the direction
        if direction not in {'L', 'R', 'F', 'B'}:
            raise IllegalMoveException

    def move_marble(self, coordinates, direction):
        """
        Moves the marble at the given coordinates in the specified direction. Modifies the state of the game board.
        Assumes the move being made is legal, except as noted.

        :param tuple[int, int] coordinates: (row, column) coordinates of marble being pushed
        :param str direction: the direction to push the marble ('L', 'R', 'F' or 'B')
        :returns: the contents of the Square pushed off the game board as a result of the move
                  ('W', 'B' or 'R if a marble has been pushed off the game board, otherwise None)
        :raises IllegalMoveException: if the direction is undefined, the square doesn't exist, or the square is empty
        """
        # validate the move and save the board state (so we can check for ko rule compliance later)
        self._validate_move(coordinates, direction)
        self._previous_state = self.deepcopy_grid()

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

    def simulate_move(self, coordinates, direction):
        """
        Simulates a potential move on the game board **without** modifying the game board's state. This should be used
        to determine what marble color (if any) would be knocked off the edge of the game board by the proposed move,
        or if the proposed move would violate the Ko rule.

        (See https://sites.google.com/site/boardandpieces/terminology/ko-rule)
        Assumes the specified coordinates and direction are valid and that the proposed move constitutes a legal move,
        except as noted.

        :param tuple[int, int] coordinates: (row, column) coordinates of marble being pushed
        :param str direction: the direction to push the marble ('L', 'R', 'F' or 'B')
        :returns: "previous" if the proposed move would return the board to its previous state, otherwise the
                  the contents of the Square that would be pushed off the board as a result of the move (or
                  None if nothing would be pushed off)
        :raises IllegalMoveException: if the direction is undefined, the square doesn't exist, or the square is empty
        """
        # validate the move
        self._validate_move(coordinates, direction)

        # push the marble along the appropriate axis, but on a deepcopy of the grid since we're just simulating it
        grid_copy = self.deepcopy_grid()
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

        # if this is the first move, we don't need to check the previous state
        if self._previous_state is None:
            return pushed_off
        # otherwise we need to check whether the proposed move would recreated the previous state
        else:
            for row_index, column_index in self.generate_all_row_and_column_combinations():
                # get the contents of the position that would result from the simulated move and its previous contents
                simulated_state = grid_copy[row_index][column_index].contents
                previous_state = self._previous_state[row_index][column_index].contents

                if simulated_state != previous_state:
                    # at least one square differs, so the previous state isn't recreated
                    return pushed_off

        # if we get here, then the proposed move would recreate the previous state and violates the Ko rule
        return "previous"

    def _push_marble(self, axis, current_position, step, previous_square=None):
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

        :param list[Square] axis: list of Squares
        :param int current_position: the index of our current position on the axis
        :param int step: -1 to push left (or up) along the axis, or +1 to push right (or down) along the axis
        :param Square previous_square: the square being moved
        :returns: the contents of the Square that pushed off the game board as a result of the proposed move
                  (or None if nothing is pushed off)
        """
        if previous_square is None:
            previous_square = Square()  # when the first marble is moved, its original space becomes empty

        # base case: we've moved off the edge of the game board
        if current_position < 0 or current_position > len(axis) - 1:
            return previous_square.contents
        # recursive step: move the contents of the previous square into the current one
        else:
            previous_contents = previous_square.contents
            current_contents = axis[current_position].contents
            # check whether we're pushing a marble into an empty square
            reached_empty = current_contents is None
            # swap the contents to move the marble into the current square
            axis[current_position].contents = previous_contents
            previous_square.contents = current_contents

            # if we pushed a marble into an empty square, we're done (and no marble was pushed off)
            return None if reached_empty else self._push_marble(axis, current_position + step, step, previous_square)

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
            "Game(",
            "_max_index= " + repr(self._max_index),
            "_direction_to_step= " + repr(self._direction_to_step),
            "_previous_state=[\n" + ",\n".join(previous_state_representation).replace("None", null_char) + "]",
            "_grid=[\n" + ",\n".join(grid_representation).replace("None", null_char) + "]",
            ")"
        ]
        return '\n'.join(representation)


class Game:
    """
    Represents a game of Kuba with two players and a game board. Composed of a GameBoard.

    The Game is responsible for: tracking player turns; tracking player scores; determining whether a move follow
    the game rules; making (legal) moves; and determining win conditions.
    """

    def __init__(self, player_one_info, player_two_info):
        """
        Creates a Game with the specified players. The players' names and marble colors must be unique.

        Player marbles may only have the following values:
          - 'B' for black
          - 'W' for white

        :param tuple[str, str] player_one_info: first player's name and marble color ('B' or 'W'), in that order
        :param tuple[str, str] player_two_info: second player's name and marble color ('B' or 'W'), in that order
        """
        # validate the player info before proceeding
        player_one_name, player_one_color = player_one_info
        player_two_name, player_two_color = player_two_info
        if player_one_name == player_two_name:
            raise ValueError("The players must have unique names")
        elif player_one_color == player_two_color:
            raise ValueError("The players cannot have the same marble color")
        elif player_one_color not in {'B', 'W'} or player_two_color not in {'B', 'W'}:
            raise ValueError("The marble color must be 'B' for black or 'W' for white")

        self._current_turn = None  # will hold the current player's name
        self._winner = None  # will hold the winning player's name
        self._game_board = GameBoard()

        # build a dictionary to represent the player data
        self._players = dict()
        for player_info in (player_one_info, player_two_info):
            player_name, marble_color = player_info
            self._players[player_name] = {
                "color": marble_color,
                "red_marbles_captured": 0,  # if this is >= 7, the player wins
                "opponent_marbles_captured": 0,  # this doesn't affect the score
            }

    def get_current_turn(self):
        """
        Returns the name of the current player, if any
        """
        return self._current_turn

    def get_player_names(self):
        """
        Returns a set containing the players' names
        """
        return set(self._players.keys())

    def get_winner(self):
        """
        Returns the name of the winning player, if any
        """
        return self._winner

    def get_player_color(self, player_name):
        """
        Returns the color of the specified player's marbles, or None if the player doesn't exist

        :param str player_name: the name of the player
        """
        try:
            return self._players[player_name]["color"]
        except KeyError:
            return None

    def get_captured(self, player_name):
        """
        Returns the number of red marbles captured by the specified player, or None if the player doesn't exist

        :param str player_name: the name of the player
        """
        try:
            return self._players[player_name]["red_marbles_captured"]
        except KeyError:
            return None

    def get_marble(self, coordinates):
        """
        Returns the marble ('W', 'B', 'R') in the specified cell, or 'X' if there is no marble in the cell

        :param tuple[int, int] coordinates: (row, column) coordinates of the cell
        """
        # we can just just call the game board's method for this
        if self._game_board.is_empty_position(coordinates):
            return 'X'
        else:
            return self._game_board.get_contents_at_position(coordinates)

    def get_marble_count(self):
        """
        Returns a tuple containing the number of white, black and red marbles (in that order) on the game board
        """
        return self._game_board.get_marble_count()

    def is_player_out_of_moves(self, player_name):
        """
        Returns True if the specified player is out of possible moves. Otherwise, returns False.

        :param str player_name: the name of the player to be checked
        """
        player_color = self.get_player_color(player_name)
        marble_coordinates = set()  # the coordinates should be unique

        # find the coordinates of all the player's marbles
        for coordinate in self._game_board.generate_all_row_and_column_combinations():
            if self._game_board.get_contents_at_position(coordinate) == player_color:
                marble_coordinates.add(coordinate)

        # if the player is out of marbles, then they have no moves left
        if len(marble_coordinates) == 0:
            return True
        # if each of the player's marbles is boxed in, then they have no moves left
        else:
            # check whether each position adjacent to one of the player's marbles can be moved (occupies the edge of
            # the board on a row or column that isn't full, or is adjacent to an empty square)
            for coordinates in marble_coordinates:
                row_index, column_index = coordinates
                # if the position occupies a column edge (it's on row 0 or 6), check whether the row is full
                if row_index == 0 or row_index == 6:
                    # a marble can be pushed forward or backward
                    return False
                elif column_index == 0 or column_index == 6:
                    # a marble can be pushed left or right
                    return False
                else:
                    adjacent_squares = (
                        (row_index - 1, column_index),
                        (row_index + 1, column_index),
                        (row_index, column_index - 1),
                        (row_index, column_index + 1)
                    )
                    # if any of the adjacent squares are empty, then a marble can be pushed in some direction
                    for adjacent_coordinates in adjacent_squares:
                        if self._game_board.is_empty_position(adjacent_coordinates):
                            return False

        # if we get here, then the player has no more moves remaining
        return True

    def is_move_valid(self, player_name, coordinates, direction):
        """
        Returns True if the move being attempted is valid. Otherwise, returns False.

        A move is invalid if the game is over, the player/direction/coordinates don't exist, it's not the current
        player's turn, the player is trying to make a move with a marble that is not theirs, or the marble can't
        be moved in the specified direction.

        :param str player_name: the name of the player making the move
        :param tuple[int, int] coordinates: (row, column) coordinates of the cell
        :param str direction: the direction to move the marble in the specified cell
        """
        # if the game is over, then the move is invalid
        if self.get_winner() is not None:
            return False

        # if the input is invalid (the player/direction/coordinates don't exist), then the move is invalid
        if player_name not in self._players:
            return False
        if direction not in {'L', 'R', 'F', 'B'}:
            return False
        if not self._game_board.is_valid_square(coordinates):
            return False

        # if it's not the current player's turn, the move is invalid (unless no one's gone yet)
        if self._current_turn is not None and player_name != self._current_turn:
            return False

        # get the coordinates of the square opposite the current one and determine whether it's empty or an edge
        row_index, column_index = coordinates
        if direction == 'L':
            column_index += 1  # pushing left => square one column to the right should be empty or an edge
        elif direction == 'R':
            column_index -= 1  # pushing right => square one column to the left should be empty or an edge
        elif direction == 'F':
            row_index += 1     # pushing up => square one row below should be empty or an edge
        else:
            row_index -= 1     # pushing down => square one row above should be empty or an edge
        new_coordinates = (row_index, column_index)
        # if the original square exists but the previous one doesn't, then the original square must occupy an edge
        square_is_not_along_edge = self._game_board.is_valid_square(new_coordinates)
        if square_is_not_along_edge and self.get_marble(new_coordinates) != 'X':
            return False

        # at this point, the game is still ongoing, it's the current player's turn, and the move is physically possible
        # but we still need to check that the player is trying to move their own marble, won't push off one of their
        # own marbles, and that the move won't return the board to its previous state

        # if the player is trying to move a marble that doesn't belong to them, the move is invalid
        player_marble_color = self.get_player_color(player_name)
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

    def make_move(self, player_name, coordinates, direction):
        """
        Attempts move a marble in the specified cell.

        Directions must be one of the following:
          - 'L' for left
          - 'R' for right
          - 'F' for forward (up)
          - 'B' for backward (down)

        :param str player_name: the name of the player making the move
        :param tuple[int, int] coordinates: (row, column) coordinates of the cell
        :param str direction: the direction to move the marble in the specified cell
        """
        # check whether the move is invalid before proceeding
        if not self.is_move_valid(player_name, coordinates, direction):
            return False

        # otherwise, make the move
        marble_pushed_off = self._game_board.move_marble(coordinates, direction)

        # update the marble/score trackers
        if marble_pushed_off is not None:
            if marble_pushed_off == 'R':
                self._players[player_name]["red_marbles_captured"] += 1
            else:
                self._players[player_name]["opponent_marbles_captured"] += 1

        # check for win conditions (player captured 7 marbles, opponent has no marbles left)
        if self.get_captured(player_name) >= 7:
            # the player captured 7 red marbles, so they win
            self._winner = player_name
        else:
            white_marbles, black_marbles, red_marbles = self.get_marble_count()
            if white_marbles == 0 or black_marbles == 0:
                # a player can't push their own marbles off the board, so if either of these is 0 it's guaranteed
                # that the player just pushed their opponent's last marble off the board
                self._winner = player_name

        # get the opponent's name
        names = self.get_player_names()
        names.remove(player_name)
        # assert len(names) == 1  # debugging
        opponent = names.pop()  # there should only be one element in the set so we can just use pop()

        # swap the current player
        self._current_turn = opponent

        # check whether the opponent has any available moves (if they don't, then they lose)
        if self.is_player_out_of_moves(opponent):
            self._winner = player_name

        # if we get here, then the move was valid
        return True

    def __str__(self):
        return str(self._game_board)

    def __repr__(self):
        # build a string representation of the Game
        representation = [
            "Game(",
            "_players=" + repr(self._players),
            "_current_turn=" + repr(self._current_turn),
            "_winner=" + repr(self._winner),
            "_game_board=" + repr(self._game_board),
            ""
        ]

        return '\n'.join(representation)

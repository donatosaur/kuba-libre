# Author: Donato Quartuccia
# Date: 6/4/2021
# Description: Contains class definitions representing a game of Kuba. This module specifically implements the
#              backend logic for Kuba (including logic for the game board, win tracking, player and score tracking,
#              turn tracking, movement rule compliance, and actual movement along the board).


class IllegalMoveException(Exception):
    """
    Raised when an attempted move violates the game rules in an unrecoverable way (e.g. the direction is undefined
    or the coordinates are undefined while an actual move is being made)
    """
    pass


class Square:
    """
    Represents a square on a game board. Squares are mutable containers that can hold any type of object.
    Useful for mimicking mutable pointer behavior for otherwise immutable objects.

    The Square class is self-contained and only responsible for holding other objects.
    """

    def __init__(self, contents=None):
        """
        Creates a square with the specified contents (or an empty square if no arguments are passed)

        :param any contents: the object contained in the Square
        """
        self._contents = contents

    def get_contents(self):
        """
        Returns the Square's contents
        """
        return self._contents

    def set_contents(self, value):
        """
        Replaces the Square's contents with the specified value

        :param any value: the object that is to be contained in the Square
        """
        self._contents = value

    def is_empty(self):
        """
        Returns True if the Square is empty. Otherwise, returns False.
        """
        return self._contents is None

    def __str__(self):
        """
        Returns the object's contents, formatted as a string
        """
        return str(self.get_contents())

    def __repr__(self):
        """
        Returns a string representation of the Square object for debugging
        """
        return "Square(id=" + str(hex(id(self))) + " _contents=" + str(self.get_contents()) + ")"


class KubaGameBoard:
    """
    Represents a 7 x 7 game board with marbles, composed of Squares.

    Each of the 49 Squares in the KubaGameBoard is held on a 7 x 7 grid and intended to be indexed using (row, column)
    notation. These Squares are used to hold marbles ('R' for red marbles, 'W' for white marbles, 'B' for black
    marbles, None for empty).

    The KubaGameBoard object has the following responsibilities: Containing and counting marbles. Determining whether
    a particular row or column is full and whether a given coordinate pair exists. Moving marbles along a row or column
    (without checking whether the move follows any rules). Simulating a proposed move (including whether it would revert
    the board to its previous state). Communicating the contents of a square.

    The KubaGameBoard requires "communicating with" Squares. This is a result of how the game board logic for moving is
    marbles is implemented. Marbles need to be moved along two axes but are only contained along rows, so they need to
    be copied by reference if moved along a column. This requires copying mutable object references, and strings are
    not mutable.
    """

    def __init__(self):
        """
        Creates a game board for Kuba in its initial state:
          - 8 white marbles in the top-left and bottom-right corner regions ('W' marbles)
          - 8 black marbles in the bottom-left and top-right corner regions ('B' marbles)
          - 13 red marbles in the center-most region, radiating outward in a plus-pattern ('R' marbles)
          - 20 empty spaces
        """
        # initialize a game board with cells that can be indexed using [row_number][column_number]
        self._grid = [
            [Square('W'), Square('W'), Square(   ), Square(   ), Square(   ), Square('B'), Square('B')],
            [Square('W'), Square('W'), Square(   ), Square('R'), Square(   ), Square('B'), Square('B')],
            [Square(   ), Square(   ), Square('R'), Square('R'), Square('R'), Square(   ), Square(   )],
            [Square(   ), Square('R'), Square('R'), Square('R'), Square('R'), Square('R'), Square(   )],
            [Square(   ), Square(   ), Square('R'), Square('R'), Square('R'), Square(   ), Square(   )],
            [Square('B'), Square('B'), Square(   ), Square('R'), Square(   ), Square('W'), Square('W')],
            [Square('B'), Square('B'), Square(   ), Square(   ), Square(   ), Square('W'), Square('W')],
        ]

        self._previous_state = None  # will hold a copy of the previous grid
        self._max_index = len(self._grid) - 1  # the board is a square, so rows and columns have the same length
        self._direction_to_step = {'F': -1, 'B': 1, 'L': -1, 'R': 1}  # maps directions to a step (for indexing)

    def generate_all_row_and_column_combinations(self):
        """
        Generates all the possible (row, column) combinations for the KubaGameBoard
        """
        for row_index in range(self._max_index + 1):
            for column_index in range(self._max_index + 1):
                yield row_index, column_index

    def get_contents_from_position(self, coordinates):
        """
        Returns the contents of the square at the specified coordinates

        :param tuple[int, int] coordinates: (row, column) coordinates of the square
        """
        # get the row and column indices
        row_index, column_index = coordinates

        return self._grid[row_index][column_index].get_contents()

    def get_marble_count(self):
        """
        Returns the number of White, Black and Red marbles (in that order) currently present on the KubaGameBoard
        """
        # initialize marble counters
        white_marble_count = 0
        black_marble_count = 0
        red_marble_count = 0

        # count the marbles (we can ignore any empty cells)
        for coordinates in self.generate_all_row_and_column_combinations():
            # get the cell contents
            cell_contents = self.get_contents_from_position(coordinates)

            # categorize and count the cell contents
            if cell_contents == 'W':
                white_marble_count += 1
            elif cell_contents == 'B':
                black_marble_count += 1
            elif cell_contents == 'R':
                red_marble_count += 1
            else:
                # the only other possibility is that the cell is empty
                continue

        return white_marble_count, black_marble_count, red_marble_count

    def is_valid_square(self, coordinates):
        """
        Returns True if the specified coordinates refer to a square on the KubaGameBoard. Otherwise, returns False.

        :param tuple[int, int] coordinates: (row, column) coordinates to check for
        """
        # get the row and column indices
        row_index, column_index = coordinates

        # the cell is valid if both of its row and column values are within the game board
        return 0 <= row_index <= self._max_index and 0 <= column_index <= self._max_index

    def is_empty_position(self, coordinates):
        """
        Returns True if the specified coordinates refer to an empty square. Otherwise, returns False.

        :param tuple[int, int] coordinates: (row, column) coordinates of the square to be checked
        """
        return self.get_contents_from_position(coordinates) is None

    def deepcopy_grid(self):
        """
        Returns a **deepcopy** of the KubaGameBoard's grid
        """
        grid_copy = []
        for row in self._grid:
            row_copy = [Square(square.get_contents()) for square in row]
            grid_copy.append(row_copy)

        # # these assertions should never end up being triggered, but they're here to catch any bugs early
        # assert row is not row_copy, "The squares were not deep copied correctly"
        # for index in range(len(row_copy)):
        #     assert row[index] is not row_copy[index], "The squares were not deep copied correctly"

        return grid_copy

    def move_marble(self, coordinates, direction):
        """
        Moves the marble at the given coordinates in the specified direction. Modifies the state of the game board.
        Assumes the move being made is legal, except as noted.

        :param tuple[int, int] coordinates: (row, column) coordinates of marble being pushed
        :param str direction: the direction to push the marble ('L', 'R', 'F' or 'B')
        :returns: the contents of the Square pushed off the game board as a result of the move
                  ('W', 'B' or 'R if a marble has been pushed off the game board, otherwise None)
        :raises IllegalMoveException: if the direction is undefined,
                                      if the specified square doesn't exist, or
                                      if the specified square is empty
        """
        # before continuing, make sure we have at least have a marble, a valid square and a defined direction
        if not self.is_valid_square(coordinates) or self.is_empty_position(coordinates):
            raise IllegalMoveException
        if direction not in {'L', 'R', 'F', 'B'}:
            raise IllegalMoveException

        # save the board state (so we can later check whether a proposed move might cause an infinitely long game)
        self._previous_state = self.deepcopy_grid()

        # determine the appropriate step for traversing the axis the marble is being pushed along
        step = self._direction_to_step[direction]

        # push the marble along the appropriate axis
        if direction in {'F', 'B'}:
            # we're pushing along a column, so fix the column index and vary the row index to get the Squares in the
            # column, and set the initial Square's index to be that of its original position in the row
            index_along_axis, fixed_index = coordinates
            axis = [self._grid[row_index][fixed_index] for row_index in range(self._max_index + 1)]
        else:
            # otherwise we're pushing along a row, so fix the row index and get the squares along the row
            # the square's position on the axis is its original position along the column
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
        :raises IllegalMoveException: if the direction is undefined,
                                      if the specified square doesn't exist, or
                                      if the specified square is empty
        """
        # before continuing, make sure we have at least have a marble, a valid square and a defined direction
        if not self.is_valid_square(coordinates) or self.is_empty_position(coordinates):
            raise IllegalMoveException
        if direction not in {'L', 'R', 'F', 'B'}:
            raise IllegalMoveException

        # since we're just simulating the move and not actually making it, make the move on a deepcopy of the grid
        grid_copy = self.deepcopy_grid()

        # determine the appropriate step for traversing the axis the marble is being pushed along
        step = self._direction_to_step[direction]

        # push the marble along the appropriate axis
        if direction in {'F', 'B'}:
            # we're pushing along a column, so fix the column index and vary the row index to get the Squares in the
            # column, and set the initial Square's index to be that of its original position in the row
            index_along_axis, fixed_index = coordinates
            axis = [grid_copy[row_index][fixed_index] for row_index in range(self._max_index + 1)]
        else:
            # otherwise we're pushing along a row, so fix the row index and get the squares along the row
            # the square's position on the axis is its original position along the column
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
                simulated_state = grid_copy[row_index][column_index].get_contents()
                previous_state = self._previous_state[row_index][column_index].get_contents()

                if simulated_state != previous_state:
                    # at least one square differs, so the previous state isn't recreated
                    return pushed_off

        # if we get here, then the proposed move would recreate the previous state and violates the Ko rule
        return "previous"

    def _push_marble(self, axis, current_position, step, previous_square=None):
        """
        Pushes a marble along the specified axis (row or column). Mutates the Squares present along the axis to
        reflect the post-push contents. When first called, current_position should be the index of the Square that
        contains the marble being pushed, and previous_square should be None.

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
        # the first "previous" value will always be empty (when the marble at the first position is moved, nothing will
        # occupy its original space) - this avoids the pitfalls of using a mutable default argument
        if previous_square is None:
            previous_square = Square()

        # base case: we've moved off the edge of the game board
        if current_position < 0 or current_position > len(axis) - 1:
            return previous_square.get_contents()

        # in any other case, the contents of the previous square will be moved into the current one, so get them
        previous_contents = previous_square.get_contents()
        current_contents = axis[current_position].get_contents()

        # base case: we've reached an empty square
        if axis[current_position].is_empty():
            # drop the previous square's contents into the empty square
            axis[current_position].set_contents(previous_contents)
            previous_square.set_contents(current_contents)
            # nothing was pushed off the board
            return None

        # otherwise, at each step of the recursion, we need to move the contents of the previous square into the
        # current one and continue doing so until we reach either an empty square or push something off the board
        axis[current_position].set_contents(previous_contents)
        previous_square.set_contents(current_contents)
        return self._push_marble(axis, current_position + step, step, previous_square)

    def __str__(self):
        """
        Returns the game board in an easy-to-read format for printing or string operations
        """
        result = []
        for row in self._grid:
            for square in row:
                if square.is_empty():
                    result.append("  ")
                else:
                    result.append(square.get_contents() + ' ')
            result.append('\n')
        return ''.join(result)

    def __repr__(self):
        """
        Returns a string representation of the KubaGameBoard object for debugging
        """
        # build a string representation of the grids
        previous_state_representation = [repr(row) for row in self._previous_state]
        grid_representation = [repr(row) for row in self._grid]

        # replace "None" with the unicode 'NUL' representation to align output
        null_char = '\u2400'

        # build a string representation of the KubaGameBoard
        representation = [
            "KubaGame(",
            "_max_index= " + repr(self._max_index),
            "_direction_to_step= " + repr(self._direction_to_step),
            "_previous_state=[\n" + ",\n".join(previous_state_representation).replace("None", null_char) + "]",
            "_grid=[\n" + ",\n".join(grid_representation).replace("None", null_char) + "]",
            ")"
        ]
        return '\n'.join(representation)


class KubaGame:
    """
    Represents a game of Kuba with two players and a game board. Composed of a KubaGameBoard.

    The KubaGame object has the following responsibilities: Tracking player turns. Tracking player scores. Determining
    whether a move does or does not follow the rules. Making (legal) moves. Determining win conditions (including
    whether a player is out of moves).

    The KubaGame requires "communicating with" the KubaGameBoard it contains. This is because the KubaGameBoard is
    responsible for implementing the game board and handling movement logic.
    """

    def __init__(self, player_one_info, player_two_info):
        """
        Creates a KubaGame with the specified players. The players' names and marble colors must be unique.

        Player marbles may only have the following values:
          - 'W' for white
          - 'B' for black

        :param tuple[str, str] player_one_info: first player's name and marble color ('W' or 'B'), in that order
        :param tuple[str, str] player_two_info: second player's name and marble color ('W' or 'B'), in that order
        """
        self._current_turn = None  # will hold the current player's name
        self._winner = None        # will hold the winning player's name

        # build a dictionary to represent the player data with the following format:
        #   ["player name"]["color"] = player's marble color ('W' or 'B')
        #                  ["score"] = player's captured red marbles
        self._players = dict()
        for player_info in (player_one_info, player_two_info):
            player_name, marble_color = player_info
            self._players[player_name] = {"color": marble_color,
                                          "score": 0  # if this is >= 7, the player wins
                                          }

        # Create an empty 7x7 game board
        self._game_board = KubaGameBoard()

    def get_player_names(self):
        """
        Returns a set containing the players' names
        """
        return set(self._players.keys())

    def get_current_turn(self):
        """
        Returns the name of the player whose turn it is, or None if no player has yet to make a move
        """
        return self._current_turn

    def get_winner(self):
        """
        Returns the name of the winning player, or None if no player has yet to win the game
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
            return self._players[player_name]["score"]
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
            return self._game_board.get_contents_from_position(coordinates)

    def get_marble_count(self):
        """
        Returns the number of White, Black and Red marbles (in that order) currently present on the board
        """
        # we can just just call the game board's marble count method for this
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
            if self._game_board.get_contents_from_position(coordinate) == player_color:
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

        # get the coordinates of the square that comes "before" the current one
        row_index, column_index = coordinates
        if direction == 'L':
            # we're pushing left, so the square one column to the right should be empty or an edge
            column_index += 1
        elif direction == 'R':
            # we're pushing right, so the square one column to the left should be empty or an edge
            column_index -= 1
        elif direction == 'F':
            # we're pushing up, so the square one row below should be empty or an edge
            row_index += 1
        else:
            # otherwise, we're pushing down, so the square one row above should be empty or an edge
            row_index -= 1
        new_coordinates = (row_index, column_index)

        # determine whether the "previous" square is an edge or is empty (if the original square exists but the previous
        # one doesn't, then the original square must occupy an edge) - if neither is true, the move is invalid
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

        # update the score
        if marble_pushed_off == 'R':
            # the current player captured a red marble (and they get to go again)
            self._players[player_name]["score"] += 1

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
        # assert len(names) == 1  # this should never go off, here to catch bugs early
        opponent = names.pop()  # there should only be one element in the set so we can just use pop()

        # swap the current player
        self._current_turn = opponent

        # check whether the opponent has any available moves (if they don't, then they lose)
        if self.is_player_out_of_moves(opponent):
            self._winner = player_name

        # if we get here, then the move was valid
        return True

    def __str__(self):
        """
        Returns the game board, formatted as a string (for printing or casting to a string)
        """
        # since we're just printing the game board, we can return the board's string method
        return str(self._game_board)

    def __repr__(self):
        """
        Returns a string representation of the KubaGame for debugging
        """
        # build a string representation of the KubaGame
        representation = [
            "KubaGame(",
            "_players=" + repr(self._players),
            "_current_turn=" + repr(self._current_turn),
            "_winner=" + repr(self._winner),
            "_game_board=" + repr(self._game_board),
            ""
        ]

        return '\n'.join(representation)


# if __name__ == "__main__":
#     # Test code
#     p1, p2 = ("p1", 'B'), ("p2", 'W')
#     game = KubaGame(p1, p2)
#     print(game)
#     assert game.make_move("p2", (6, 5), 'F')
#     print(repr(game))

# Author: Donato Quartuccia
# Date: 6/4/2021
# Description: Contains unit tests for KubaGame.py
import unittest
from KubaGame import Square, KubaGameBoard, KubaGame, IllegalMoveException


class TestGame(KubaGame):
    """
    Extends the KubaGame class so that the board can be directly accessed for debugging
    """

    def __init__(self, player_one_info, player_two_info):
        """
        Creates a TestGame with the specified players

        :param tuple[str, str] player_one_info: first player's name and marble color ('W' or 'B'), in that order)
        :param tuple[str, str] player_two_info: second player's name and marble color ('W' or 'B'), in that order
        """
        super().__init__(player_one_info, player_two_info)

    def force_move_marble(self, coordinates, direction):
        """
        Passes the specified parameters to the KubaGameBoard's make_move method to force a marble move on the board.
        Used to create a specific game state for testing purposes

        :param tuple[int, int] coordinates: (row, column) coordinates of the marble to push
        :param str direction: the direction to push the marble ('L', 'R', 'F' or 'B')
        :returns: the contents of the Square pushed off the game board as a result of the move
        :raises IllegalMoveException: if the direction or coordinates are undefined, or the referenced square is empty
        """
        self._game_board.move_marble(coordinates, direction)

    def set_current_turn(self, player_name):
        """
        Sets current_turn to the specified player, for testing purposes
        :param player_name: the player whose turn it is
        """
        self._current_turn = player_name

    def set_winner(self, player_name):
        """
        Sets the winner to the specified player, forcing the game to end for testing purposes
        :param player_name: the player who "won"
        """
        self._winner = player_name


class SquareTester(unittest.TestCase):
    """
    Contains unittests for the Square class
    """

    def test_create_square(self):
        """
        Tests whether Squares are created as expected
        """
        empty_square = Square()
        square = Square('R')

        # the empty square shouldn't contain anything, but the other should contain 'R'
        self.assertIsNone(empty_square.get_contents())
        self.assertEqual(square.get_contents(), 'R')

    def test_set_square_contents(self):
        """
        Tests whether Squares can have their contents changed as expected
        """
        empty_square = Square()
        square = Square('R')

        # test whether we can set new values for the empty square
        empty_square.set_contents('W')
        self.assertEqual(empty_square.get_contents(), 'W')

        # test whether we can set new values for the non-empty square
        square.set_contents('B')
        self.assertEqual(square.get_contents(), 'B')

    def test_square_is_empty(self):
        """
        Tests whether Square.is_empty works as expected
        """
        # check is_empty for a square that is initially empty and one that isn't
        empty_square = Square()
        square = Square('R')
        self.assertTrue(empty_square.is_empty())
        self.assertFalse(square.is_empty())


class KubaGameBoardTester(unittest.TestCase):
    """
    Contains unit tests for the KubaGame.py module
    """

    def setUp(self):
        """
        Create a KubaGameBoard to be used in tests
        """
        self._board = KubaGameBoard()

    def test_generate_all_row_and_column_combinations(self):
        """
        Tests whether KubaGameBoard.generate_all_row_and_column_combinations correctly generates every
        possible row & column index pair
        """
        # generate all the combinations
        combinations = [combination for combination in self._board.generate_all_row_and_column_combinations()]

        # there should be 49 (7 * 7) total combinations
        self.assertEqual(len(combinations), 49)

        # check for the four corners
        self.assertIn((0, 0), combinations)
        self.assertIn((6, 0), combinations)
        self.assertIn((0, 6), combinations)
        self.assertIn((6, 6), combinations)

        # check for the middle
        self.assertIn((3, 3), combinations)

        # check to make sure there are no out of bounds values
        for combination in combinations:
            self.assertTrue(combination[0] >= 0 or combination[1] >= 0)
            self.assertFalse(combination[0] >= 7 or combination[1] >= 7)

    def test_get_contents_from_position(self):
        """
        Tests whether contents are obtained correctly
        """
        # get some coordinates
        white_marble = (0, 0)
        black_marble = (0, 6)
        red_marble = (3, 3)
        empty = (1, 2)

        self.assertEqual(self._board.get_contents_from_position(white_marble), 'W')
        self.assertEqual(self._board.get_contents_from_position(black_marble), 'B')
        self.assertEqual(self._board.get_contents_from_position(red_marble), 'R')
        self.assertIsNone(self._board.get_contents_from_position(empty))

    def test_get_marble_count(self):
        """
        Tests whether marble counts are obtained correctly
        """
        self.assertTupleEqual(self._board.get_marble_count(), (8, 8, 13))

    def test_is_valid_square(self):
        """
        Tests whether is_valid_square works as expected
        """
        # check a few squares that are not on the board
        self.assertFalse(self._board.is_valid_square((-1, 0)))
        self.assertFalse(self._board.is_valid_square((7, 0)))
        self.assertFalse(self._board.is_valid_square((0, 7)))

        # check for some edges
        self.assertTrue(self._board.is_valid_square((0, 0)))
        self.assertTrue(self._board.is_valid_square((6, 6)))

        # check for something in the middle
        self.assertTrue(self._board.is_valid_square((4, 5)))

    def test_is_empty_position(self):
        """
        Tests whether is_empty_position works correctly
        """
        # check an empty position
        self.assertTrue(self._board.is_empty_position((2, 0)))

        # check a non-empty position
        self.assertFalse(self._board.is_empty_position((3, 2)))

    def test_deepcopy_grid(self):
        """
        Tests whether deepcopy_grid correctly returns a deepcopy and not a shallow copy
        """
        # make two deep copies - if the grids contain identical copies, then the copies were shallow
        grid_1 = self._board.deepcopy_grid()
        grid_2 = self._board.deepcopy_grid()

        self.assertIsNot(grid_1, grid_2)
        for coordinates in self._board.generate_all_row_and_column_combinations():
            # get the squares at the same position in each grid copy
            row_index, column_index = coordinates
            square_1 = grid_1[row_index][column_index]
            square_2 = grid_2[row_index][column_index]
            # contents of the squares should be the same
            self.assertEqual(square_1.get_contents(), square_2.get_contents())
            # but they should be totally different objects
            self.assertIsNot(square_1, square_2)

    def test_illegal_move_exception_raised(self):
        """
        Tests whether move_marble and simulate_move correctly prevent undefined moves from occurring
        """
        # while the board isn't responsible for checking the legality of moves, it should check whether the moves are
        # defined before trying to execute them

        # try a non-existent direction
        self.assertRaises(IllegalMoveException, self._board.move_marble, (0, 0), 'X')
        self.assertRaises(IllegalMoveException, self._board.simulate_move, (0, 0), 'X')

        # try some non-existent coordinates
        self.assertRaises(IllegalMoveException, self._board.move_marble, (7, 0), 'L')
        self.assertRaises(IllegalMoveException, self._board.move_marble, (-1, -5), 'R')
        self.assertRaises(IllegalMoveException, self._board.move_marble, (88, 50), 'F')
        self.assertRaises(IllegalMoveException, self._board.move_marble, (7, -7), 'B')
        self.assertRaises(IllegalMoveException, self._board.simulate_move, (7, 0), 'L')
        self.assertRaises(IllegalMoveException, self._board.simulate_move, (-1, -5), 'R')
        self.assertRaises(IllegalMoveException, self._board.simulate_move, (88, 50), 'F')
        self.assertRaises(IllegalMoveException, self._board.simulate_move, (7, -7), 'B')

        # try to move an empty space
        self.assertRaises(IllegalMoveException, self._board.move_marble, (0, 2), 'R')
        self.assertRaises(IllegalMoveException, self._board.simulate_move, (0, 2), 'R')

    def test_move_marble_left(self):
        """
        Tests whether moving left works as expected
        """
        try:
            # make these calls a little more readable
            direction = 'L'
            get_contents = self._board.get_contents_from_position
            get_marble_count = self._board.get_marble_count
            move = self._board.move_marble

            # move the white marble at 0, 1 left: this should move it one space and knock off the white marble at 0, 0
            self.assertEqual(move((0, 1), direction), 'W')
            # the original space should now be empty...

            self.assertIsNone(get_contents((0, 1)))
            # ...and the marble should've been moved one over to the left
            self.assertEqual(get_contents((0, 0)), 'W')
            # make sure nothing in the adjacent cells not to the left was moved
            self.assertEqual(get_contents((1, 0)), 'W')
            self.assertIsNone(get_contents((0, 2)))
            # there should be one less white marble on the board
            self.assertTupleEqual(get_marble_count(), (7, 8, 13))

            # move the black marble at 1, 5 left: this should move it one space but not knock anything off
            self.assertIsNone(move((1, 5), direction))
            # the original space should now be empty...
            self.assertIsNone(get_contents((1, 5)))
            # ...and the marble should've been moved one over to the left
            self.assertEqual(get_contents((1, 4)), 'B')
            # make sure nothing in the adjacent cells not to the left was moved
            self.assertEqual(get_contents((1, 6)), 'B')
            self.assertEqual(get_contents((0, 5)), 'B')
            self.assertIsNone(get_contents((2, 5)))
            # no additional marbles should've been pushed off
            self.assertTupleEqual(get_marble_count(), (7, 8, 13))

            # move the red marble at 4, 4 left: this should cause a chain where three red marbles move left resulting in
            # the marble at 4, 2 moving one space left, but not knock anything off
            self.assertIsNone(move((4, 4), direction))
            # the original space should now be empty...
            self.assertIsNone(get_contents((4, 4)))
            # ...and the marble should've been moved one over to the left (chained 3x)
            self.assertEqual(get_contents((4, 3)), 'R')
            self.assertEqual(get_contents((4, 2)), 'R')
            self.assertEqual(get_contents((4, 1)), 'R')
            self.assertIsNone(get_contents((4, 0)))  # nothing should've been moved into the 4th space to the left
            # make sure nothing in the adjacent cells not to the left was moved
            self.assertEqual(get_contents((3, 4)), 'R')
            self.assertIsNone(get_contents((4, 5)))
            self.assertIsNone(get_contents((5, 4)))
            # no additional marbles should've been pushed off
            self.assertTupleEqual(get_marble_count(), (7, 8, 13))
        except AssertionError as error:
            # show the board state when the error occurred
            print("State of board at time of error:")
            print(self._board)
            # re-raise to preserve the original behavior of the test on failure
            raise error

    def test_simulate_move_left(self):
        """
        Tests whether simulating a move left gives the expected result without changing the actual state
        of the game board
        """
        # simulate moving the white marble at 1, 1 left, which would push off a white marble
        self.assertEqual(self._board.simulate_move((1, 1), 'L'), 'W')
        # the original state of the board shouldn't change
        self.assertTupleEqual(self._board.get_marble_count(), (8, 8, 13))
        self.assertEqual(self._board.get_contents_from_position((1, 1)), 'W')

    def test_move_marble_right(self):
        """
        Tests whether moving right works as expected
        """
        try:
            # make these calls a little more readable
            direction = 'R'
            get_contents = self._board.get_contents_from_position
            get_marble_count = self._board.get_marble_count
            move = self._board.move_marble

            # move the white marble at 0, 0 right: this should move it one space but not knock anything off
            self.assertIsNone(move((0, 0), direction))
            # the original space should now be empty...
            self.assertIsNone(get_contents((0, 0)))
            # ...and the marble should've been moved one over to the right (causing the next marble to be moved too)
            self.assertEqual(get_contents((0, 1)), 'W')
            self.assertEqual(get_contents((0, 2)), 'W')
            # make sure nothing in the adjacent cells not to the right was moved
            self.assertEqual(get_contents((1, 0)), 'W')
            # no marbles should've been pushed off
            self.assertTupleEqual(get_marble_count(), (8, 8, 13))

            # move the black marble at 1, 5 right: this should move it one space and knock off the black marble at 1, 6
            self.assertEqual(move((1, 5), direction), 'B')
            # the original space should now be empty...
            self.assertIsNone(get_contents((1, 5)))
            # ...and the marble should've been moved one over to the right
            self.assertEqual(get_contents((1, 6)), 'B')
            # make sure nothing in the adjacent cells not to the right was moved
            self.assertEqual(get_contents((1, 6)), 'B')
            self.assertIsNone(get_contents((1, 4)))
            self.assertIsNone(get_contents((2, 5)))
            # there should be one less black marble on the board
            self.assertTupleEqual(get_marble_count(), (8, 7, 13))

            # move the red marble at 4, 2 right: this should cause a chain where three red marbles move right resulting
            # in the marble at 4, 4 moving one space right, but not knock anything off
            self.assertIsNone(move((4, 2), direction))
            # the original space should now be empty...
            self.assertIsNone(get_contents((4, 2)))
            # ...and the marble should've been moved one over to the right (chained 3x)
            self.assertEqual(get_contents((4, 3)), 'R')
            self.assertEqual(get_contents((4, 4)), 'R')
            self.assertEqual(get_contents((4, 5)), 'R')
            self.assertIsNone(get_contents((4, 6)))  # nothing should've been moved into the 4th space to the right
            # make sure nothing in the adjacent cells not to the right was moved
            self.assertEqual(get_contents((3, 2)), 'R')
            self.assertIsNone(get_contents((4, 1)))
            self.assertIsNone(get_contents((5, 2)))
            # no additional marbles should've been pushed off
            self.assertTupleEqual(get_marble_count(), (8, 7, 13))
        except AssertionError as error:
            # show the board state when the error occurred
            print("State of board at time of error:")
            print(self._board)
            # re-raise to preserve the original behavior of the test on failure
            raise error

    def test_simulate_move_right(self):
        """
        Tests whether simulating a move right gives the expected result without changing the actual state
        of the game board
        """
        # simulate moving the black marble at 1, 5 right, which would push off a black marble
        self.assertEqual(self._board.simulate_move((1, 5), 'R'), 'B')
        # the original state of the board shouldn't change
        self.assertTupleEqual(self._board.get_marble_count(), (8, 8, 13))
        self.assertEqual(self._board.get_contents_from_position((1, 5)), 'B')

    def test_move_marble_forward(self):
        """
        Tests whether moving right forward (up) as expected
        """
        try:
            # make these calls a little more readable
            direction = 'F'
            get_contents = self._board.get_contents_from_position
            get_marble_count = self._board.get_marble_count
            move = self._board.move_marble

            # move the white marble at 1, 1 forward: this should move it one space and knock off a white marble
            self.assertEqual(move((1, 1), direction), 'W')
            # the original space should now be empty...
            self.assertIsNone(get_contents((1, 1)))
            # ...and the marble should've been moved one up
            self.assertEqual(get_contents((0, 1)), 'W')
            # make sure nothing in the adjacent cells not above the original was moved
            self.assertEqual(get_contents((1, 0)), 'W')
            self.assertIsNone(get_contents((1, 2)))
            self.assertIsNone(get_contents((2, 1)))
            # there should be one less white marble on the board
            self.assertTupleEqual(get_marble_count(), (7, 8, 13))

            # move the black marble at 6, 0 forward: this should move it one space but not knock anything off
            self.assertIsNone(move((6, 0), direction))
            # the original space should now be empty...
            self.assertIsNone(get_contents((6, 0)))
            # ...and the marble should've been moved one up one (chained 2x)
            self.assertEqual(get_contents((5, 0)), 'B')
            self.assertEqual(get_contents((4, 0)), 'B')
            # make sure nothing in the adjacent cells not above the original was moved
            self.assertEqual(get_contents((6, 1)), 'B')
            # no additional marbles should've been pushed off
            self.assertTupleEqual(get_marble_count(), (7, 8, 13))

            # move the red marble at 5, 3 up: this should cause a chain where four red marbles move up resulting
            # in the marble at 1, 3 moving one space up, but not knock anything off
            self.assertIsNone(move((5, 3), direction))
            # the original space should now be empty...
            self.assertIsNone(get_contents((5, 3)))
            # ...and the marble should've been moved up one (chained 4x)
            self.assertEqual(get_contents((4, 3)), 'R')
            self.assertEqual(get_contents((3, 3)), 'R')
            self.assertEqual(get_contents((2, 3)), 'R')
            self.assertEqual(get_contents((1, 3)), 'R')
            self.assertEqual(get_contents((0, 3)), 'R')
            # make sure nothing in the adjacent cells not above the original was moved
            self.assertIsNone(get_contents((5, 2)))
            self.assertIsNone(get_contents((5, 4)))
            self.assertIsNone(get_contents((6, 3)))
            # no additional marbles should've been pushed off
            self.assertTupleEqual(get_marble_count(), (7, 8, 13))
        except AssertionError as error:
            # show the board state when the error occurred
            print("State of board at time of error:")
            print(self._board)
            # re-raise to preserve the original behavior of the test on failure
            raise error

    def test_simulate_move_forward(self):
        """
        Tests whether simulating a move forward (up) gives the expected result without changing the actual state
        of the game board
        """
        # simulate moving the white marble at 1, 1 forward, which would push off a white marble
        self.assertEqual(self._board.simulate_move((1, 1), 'F'), 'W')
        # the original state of the board shouldn't change
        self.assertTupleEqual(self._board.get_marble_count(), (8, 8, 13))
        self.assertEqual(self._board.get_contents_from_position((1, 1)), 'W')

    def test_move_marble_backward(self):
        """
        Tests whether moving backward (down) works as expected
        """
        try:
            # make these calls a little more readable
            direction = 'B'
            get_contents = self._board.get_contents_from_position
            get_marble_count = self._board.get_marble_count
            move = self._board.move_marble

            # move the white marble at 0, 1 backward: this should move it one space but not knock anything off
            self.assertIsNone(move((0, 1), direction))
            # the original space should now be empty...
            self.assertIsNone(get_contents((0, 1)))
            # ...and the marble should've been moved one down (chained 2x)
            self.assertEqual(get_contents((1, 1)), 'W')
            self.assertEqual(get_contents((2, 1)), 'W')
            # make sure nothing in the adjacent cells not below the original was moved
            self.assertEqual(get_contents((0, 0)), 'W')
            self.assertIsNone(get_contents((0, 2)))
            # no marbles should've been pushed off
            self.assertTupleEqual(get_marble_count(), (8, 8, 13))

            # move the black marble at 5, 1 backward: this should move it one space and knock off a black marble
            self.assertEqual(move((5, 1), direction), 'B')
            # the original space should now be empty...
            self.assertIsNone(get_contents((5, 1)))
            # ...and the marble should've been moved down one
            self.assertEqual(get_contents((6, 1)), 'B')
            # make sure nothing in the adjacent cells not below the original was moved
            self.assertEqual(get_contents((5, 0)), 'B')
            self.assertIsNone(get_contents((4, 1)))
            self.assertIsNone(get_contents((5, 2)))
            # one black marble should have been pushed off the board
            self.assertTupleEqual(get_marble_count(), (8, 7, 13))

            # move the red marble at 1, 3 down: this should cause a chain where four red marbles move down resulting
            # in the marble at 5, 3 moving one space down, but not knock anything off
            self.assertIsNone(move((1, 3), direction))
            # the original space should now be empty...
            self.assertIsNone(get_contents((1, 3)))
            # ...and the marble should've been moved down one (chained 4x)
            self.assertEqual(get_contents((2, 3)), 'R')
            self.assertEqual(get_contents((3, 3)), 'R')
            self.assertEqual(get_contents((4, 3)), 'R')
            self.assertEqual(get_contents((5, 3)), 'R')
            self.assertEqual(get_contents((6, 3)), 'R')
            # make sure nothing in the adjacent cells not below the original was moved
            self.assertIsNone(get_contents((1, 2)))
            self.assertIsNone(get_contents((1, 3)))
            self.assertIsNone(get_contents((1, 4)))
            # no additional marbles should've been pushed off
            self.assertTupleEqual(get_marble_count(), (8, 7, 13))
        except AssertionError as error:
            # show the board state when the error occurred
            print("State of board at time of error:")
            print(self._board)
            # re-raise to preserve the original behavior of the test on failure
            raise error

    def test_simulate_move_backward(self):
        """
        Tests whether simulating a move backward (down) gives the expected result without changing the actual state
        of the game board
        """
        # simulate moving the white marble at 5, 1 forward, which would push off a black marble
        self.assertEqual(self._board.simulate_move((5, 1), 'B'), 'B')
        # the original state of the board shouldn't change
        self.assertTupleEqual(self._board.get_marble_count(), (8, 8, 13))
        self.assertEqual(self._board.get_contents_from_position((5, 1)), 'B')

    def test_simulate_returns_previous(self):
        """
        Test whether simulating a move that would return the state of the board to its previous state returns
        the expected result ("previous")
        """
        # move the white marble from 1, 1 down one square
        self._board.move_marble((1, 1), 'B')  # after this, the marble is at 2, 1

        # now simulate trying to move it back up
        self.assertEqual(self._board.simulate_move((2, 1), 'F'), "previous")


class KubaGameTester(unittest.TestCase):
    """
    Contains unit tests for the KubaGame.py module
    """

    def setUp(self):
        """
        Create a KubaGameBoard and a KubaGame to be used in tests
        """
        self._player_b = "Player B"
        self._player_w = "Player W"

        player_b_info = (self._player_b, 'B')
        player_w_info = (self._player_w, 'W')

        self._test_game = TestGame(player_b_info, player_w_info)

        # moves to create a board state where the player is out of moves, namely:
        #   - Columns 0, 1, 2, 6 are empty
        #   - Column 3 is red, red, red
        #   - Column 5 is white, black, red, red, red, white, white
        #   - Column 5 is white
        # in this scenario, there are no possible moves left for the black marbles, but there are for the white ones
        # make the moves that would lead to this scenario
        self._moves_to_stalemate_b = (
            # knock off four white marbles
            ((0, 0), 'L'), ((1, 0), 'L'), ((5, 6), 'R'), ((6, 6), 'R'),
            # knock off six black marbles
            ((5, 1), 'L'), ((5, 0), 'L'), ((6, 1), 'L'), ((6, 0), 'L'), ((0, 6), 'R'), ((1, 6), 'R'),
            # slide the black marbles in column 5 over to column 4
            ((0, 5), 'L'), ((1, 5), 'L'),
            # slide the white marbles in column 5 up (and knock off the red marble in column 5)
            ((6, 5), 'F'), ((5, 5), 'F'), ((4, 5), 'F'), ((3, 5), 'F'), ((2, 5), 'F'),
            # slide the white marbles in column 1 down and over to column 4 (and knock the red marble in column 1)
            ((0, 1), 'B'), ((1, 1), 'B'), ((2, 1), 'B'), ((3, 1), 'B'), ((4, 1), 'B'), ((5, 1), 'R'), ((6, 1), 'R'),
            ((5, 2), 'R'), ((6, 2), 'R'), ((5, 3), 'R'), ((6, 3), 'R'),
            # slide the red marbles in column up 3 so only 3 remain, and slide the red marbles in column 2 off
            ((4, 3), 'F'), ((3, 3), 'F'), ((4, 2), 'F'), ((3, 2), 'F'), ((2, 2), 'F'), ((1, 2), 'F'), ((0, 2), 'F'),
            # slide the red marble in 5, 5 and the black marble in 0, 4 off the board
            ((5, 5), 'R'), ((5, 6), 'R'), ((0, 4), 'F'),
            # slide the white marble in 0, 5 left, which should result in the described board state
            ((0, 5), 'L'),
        )

    def test_game_is_initialized_correctly(self):
        """
        Tests whether the initial state of the KubaGame is as expected
        """
        # there should initially be no current turn and no winner
        self.assertIsNone(self._test_game.get_winner())
        self.assertIsNone(self._test_game.get_current_turn())
        # the board should have 8 white marbles, 8 black marbles and 13 red marbles
        self.assertTupleEqual(self._test_game.get_marble_count(), (8, 8, 13))
        # player b should be assigned the black marbles and player w the white marbles
        self.assertEqual(self._test_game.get_player_color(self._player_b), 'B')
        self.assertEqual(self._test_game.get_player_color(self._player_w), 'W')

    def test_either_player_can_go_first(self):
        """
        Tests whether any player is allowed to go first
        """
        # create two new games, then have each player try to make a legal move first
        player_b_info = (self._player_b, 'B')
        player_w_info = (self._player_w, 'W')

        game_1 = KubaGame(player_b_info, player_w_info)
        game_2 = KubaGame(player_b_info, player_w_info)

        self.assertTrue(game_2.make_move(self._player_w, (0, 0), 'B'))
        self.assertTrue(game_1.make_move(self._player_b, (0, 5), 'B'))

    def test_get_captured(self):
        """
        Tests whether get_captured correctly returns 0 when no red marbles have been captured
        """
        self.assertEqual(self._test_game.get_captured(self._player_b), 0)
        self.assertEqual(self._test_game.get_captured(self._player_w), 0)

        # check whether get_captured still returns 0 after an opponent's marble is pushed off but no red ones have been
        self._test_game.force_move_marble((0, 0), 'R')
        self._test_game.force_move_marble((0, 1), 'R')
        self._test_game.force_move_marble((0, 2), 'R')
        self._test_game.make_move(self._player_w, (0, 3), 'R')
        self.assertEqual(self._test_game.get_captured(self._player_b), 0)
        self.assertEqual(self._test_game.get_captured(self._player_w), 0)

        # check whether get_captured returns 1 after a player pushes a red marble off the board
        self._test_game.force_move_marble((1, 6), 'L')
        self._test_game.force_move_marble((1, 5), 'L')
        self._test_game.force_move_marble((1, 4), 'L')
        self._test_game.force_move_marble((1, 3), 'L')
        self._test_game.make_move(self._player_b, (1, 2), 'L')
        self.assertEqual(self._test_game.get_captured(self._player_b), 1)
        self.assertEqual(self._test_game.get_captured(self._player_w), 0)

    def test_get_marble_count(self):
        """
        Tests whether marble counts are obtained correctly
        """
        self.assertTupleEqual(self._test_game.get_marble_count(), (8, 8, 13))

    def test_get_marble(self):
        """
        Tests whether board contents are obtained correctly
        """
        self.assertEqual(self._test_game.get_marble((0, 0)), 'W')
        self.assertEqual(self._test_game.get_marble((0, 6)), 'B')
        self.assertEqual(self._test_game.get_marble((3, 2)), 'R')
        self.assertEqual(self._test_game.get_marble((0, 2)), 'X')

    def test_is_player_out_of_moves(self):
        """
        Tests whether is_player_out_of_moves works as expected
        """
        try:
            # create a board state where there are no possible moves left for the black marbles, but there are for the
            # white marbles
            for coordinates, direction in self._moves_to_stalemate_b:
                self._test_game.force_move_marble(coordinates, direction)

            # check whether there are any moves remaining for black marbles (the player should be out of moves)
            self.assertTrue(self._test_game.is_player_out_of_moves(self._player_b))
            # check whether there are any moves remaining for white marbles (the player should not be out of moves)
            self.assertFalse(self._test_game.is_player_out_of_moves(self._player_w))
        except AssertionError as error:
            # show the board state when the error occurred
            print("State of board at time of error:")
            print(self._test_game)
            # re-raise to preserve the original behavior of the test on failure
            raise error

    def test_is_move_valid_on_invalid_input(self):
        """
        Tests whether is_move_valid correctly returns False when passed a player, direction or coordinates
        that don't exist
        """
        # pass a nonexistent player
        self.assertFalse(self._test_game.is_move_valid("doesn't exist", (1, 5), 'B'))

        # pass a nonexistent direction
        self.assertFalse(self._test_game.is_move_valid(self._player_b, (1, 5), 'D'))

        # pass nonexistent coordinates
        self.assertFalse(self._test_game.is_move_valid(self._player_b, (1, 7), 'R'))

    def test_is_move_valid_on_game_over(self):
        """
        Tests whether is_move_valid correctly returns False when it's not the current player's turn
        """
        self._test_game.set_winner(self._player_b)
        self.assertFalse(self._test_game.is_move_valid(self._player_b, (0, 5), 'R'))

    def test_is_move_valid_on_wrong_turn(self):
        """
        Tests whether is_move_valid correctly returns False when it's not the current player's turn
        """
        self._test_game.set_current_turn(self._player_w)
        self.assertFalse(self._test_game.is_move_valid(self._player_b, (0, 5), 'R'))

    def test_is_move_valid_on_empty_square(self):
        """
        Tests whether is_move_valid correctly returns False when a square is empty
        """
        self.assertFalse(self._test_game.is_move_valid(self._player_b, (0, 3), 'R'))

    def test_is_move_valid_on_marble_color(self):
        """
        Tests whether is_move_valid returns the correct value depending on the color of the marble located
        at the specified coordinates
        """
        # try to push a marble of the wrong color - this should return False
        self.assertFalse(self._test_game.is_move_valid(self._player_b, (1, 1), 'L'))

        # try to push a marble of the correct color - this should return True
        self.assertFalse(self._test_game.is_move_valid(self._player_w, (1, 1), 'L'))

        # try to push a neutral (red) marble - this should always return False
        self.assertFalse(self._test_game.is_move_valid(self._player_w, (1, 3), 'L'))
        self.assertFalse(self._test_game.is_move_valid(self._player_b, (1, 3), 'L'))
        self.assertFalse(self._test_game.is_move_valid(self._player_b, (1, 3), 'R'))
        self.assertFalse(self._test_game.is_move_valid(self._player_b, (1, 3), 'F'))
        self.assertFalse(self._test_game.is_move_valid(self._player_b, (1, 3), 'B'))

    def test_is_move_valid_on_adjacent_not_edge_or_empty(self):
        """
        Tests whether is_move_valid correctly returns False when the space "before" the specified coordinates is
        neither an edge nor an empty space
        """
        # try pushing 6, 0 left or backward - these should return False
        self.assertFalse(self._test_game.is_move_valid(self._player_b, (6, 0), 'B'))  # 5, 0 is occupied
        self.assertFalse(self._test_game.is_move_valid(self._player_b, (6, 0), 'L'))  # 6, 1 is occupied

        # try pushing 0, 6 right or forward - these should return False
        self.assertFalse(self._test_game.is_move_valid(self._player_b, (0, 6), 'F'))  # 1, 6 is occupied
        self.assertFalse(self._test_game.is_move_valid(self._player_b, (0, 6), 'R'))  # 0, 5 is occupied

    def test_is_move_valid_pushing_off_marble(self):
        """
        Tests whether is_move_valid correctly returns the correct value depending on what color marble would be
        pushed off the board by a proposed move
        """
        # try to have the player push off one of their marbles
        self.assertFalse(self._test_game.is_move_valid(self._player_w, (1, 1), 'L'))

        # try to have the player push off no marbles
        self.assertTrue(self._test_game.is_move_valid(self._player_w, (1, 0), 'R'))

        # try to have the player push off an opponents' marble
        self._test_game.force_move_marble((1, 0), 'R')
        self._test_game.force_move_marble((1, 1), 'R')
        self.assertTrue(self._test_game.is_move_valid(self._player_w, (1, 2), 'R'))

        # try to have the player push off a neutral (red) marble
        self._test_game.force_move_marble((1, 2), 'R')
        self._test_game.force_move_marble((1, 3), 'R')
        self.assertTrue(self._test_game.is_move_valid(self._player_w, (1, 4), 'R'))

    def test_is_move_valid_on_recreated_board_state(self):
        """
        Tests whether is_move_valid returns the correct value when a move would cause the board to return to
        its previous state
        """
        # move the marbles around so we get them into a state where pushing back and forth is easy
        # get row 1 to a state where it's "Empty, White, White, Red, Black, Black, Empty)
        self._test_game.force_move_marble((1, 0), 'R')
        self._test_game.force_move_marble((1, 6), 'L')

        # now push the row right and try to push it back left - this should be False
        self._test_game.force_move_marble((1, 1), 'R')
        self.assertFalse(self._test_game.is_move_valid(self._player_b, (1, 6), 'L'))

    def test_make_move_win_condition_1(self):
        """
        Tests whether make move correctly alters the state of the board and game when a valid move is made, but does
        not alter either when an invalid one is made. This test ends with Player W winning by capturing 7 red marbles.
        """
        try:
            # move white marbles around to make it easier for player W to push red marbles off the board
            self._test_game.force_move_marble((0, 0), 'R')
            self._test_game.force_move_marble((0, 1), 'R')
            self._test_game.force_move_marble((1, 1), 'R')

            # alternate turns, until player w has pushed off their seventh red marble
            self.assertTrue(self._test_game.make_move(self._player_w, (0, 3), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_b, (5, 0), 'R'))

            # push off red marble 1
            self.assertTrue(self._test_game.make_move(self._player_w, (1, 3), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_b, (6, 0), 'R'))

            # push off red marble 2
            self.assertTrue(self._test_game.make_move(self._player_w, (2, 3), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_b, (6, 1), 'F'))

            # push off red marble 3
            self.assertTrue(self._test_game.make_move(self._player_w, (3, 3), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_b, (0, 6), 'L'))

            # push off red marble 4
            self.assertTrue(self._test_game.make_move(self._player_w, (4, 3), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_b, (1, 6), 'L'))

            # push off red marble 5
            self.assertTrue(self._test_game.make_move(self._player_w, (5, 3), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_b, (6, 2), 'R'))

            # push off red marble 6
            self.assertTrue(self._test_game.make_move(self._player_w, (0, 2), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_b, (0, 5), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_w, (1, 2), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_b, (0, 4), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_w, (2, 2), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_b, (1, 5), 'B'))

            # push off red marble 7 - player w wins
            self.assertTrue(self._test_game.make_move(self._player_w, (3, 2), 'B'))
            self.assertEqual(self._test_game.get_captured(self._player_w), 7)
            self.assertTrue(self._test_game.get_winner(), self._player_w)

        except AssertionError as error:
            # show the board state when the error occurred
            print("State of board at time of error:")
            print("Current turn:", self._test_game.get_current_turn())
            print()
            print(self._test_game)
            # re-raise to preserve the original behavior of the test on failure
            raise error

    def test_make_move_win_condition_2(self):
        """
        Tests whether make move correctly alters the state of the board and game when a valid move is made, but does
        not alter either when an invalid one is made. This test ends with Player W winning by pushing all of Player B's
        marbles pushed off the board.
        """
        try:
            # forcibly remove all but one of the black marbles from the board
            self._test_game.force_move_marble((0, 5), 'R')
            self._test_game.force_move_marble((0, 6), 'R')
            self._test_game.force_move_marble((1, 5), 'R')
            self._test_game.force_move_marble((1, 6), 'R')
            self._test_game.force_move_marble((5, 1), 'L')
            self._test_game.force_move_marble((5, 0), 'L')
            self._test_game.force_move_marble((6, 1), 'L')

            # push the white marbles in row 6 all the way to the left (short of pushing the last black marble off)
            self._test_game.force_move_marble((6, 6), 'L')
            self._test_game.force_move_marble((6, 5), 'L')
            self._test_game.force_move_marble((6, 4), 'L')
            self._test_game.force_move_marble((6, 3), 'L')
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 1, 13))

            # have player w go first and push the only black marble off the board - player w wins
            self.assertTrue(self._test_game.make_move(self._player_w, (6, 2), 'L'))
            self.assertEqual(self._test_game.get_captured(self._player_b), 0)
            self.assertEqual(self._test_game.get_captured(self._player_w), 0)
            self.assertTrue(self._test_game.get_winner(), self._player_w)

        except AssertionError as error:
            # show the board state when the error occurred
            print("State of board at time of error:")
            print()
            print(self._test_game)
            # re-raise to preserve the original behavior of the test on failure
            raise error

    def test_make_move_win_condition_3(self):
        """
        Tests whether make move correctly alters the state of the board and game when a valid move is made, but does
        not alter either when an invalid one is made. This test ends with Player W winning because  Player B has run
        out of moves.
        """
        try:
            # create a board state where there are no possible moves left for the black marbles, but there are for the
            # white marbles
            for coordinates, direction in self._moves_to_stalemate_b:
                self._test_game.force_move_marble(coordinates, direction)

            # push the white marble at 6, 4 right (when player w pushes it back, player b is out of moves)
            self._test_game.force_move_marble((6, 4), 'R')

            # push the red marble at 2, 3 left (otherwise, pushing the white marble back will recreate the last state)
            self._test_game.force_move_marble((2, 3), 'L')

            # have player w push the white marble at 6, 5 back - player b is out of moves and player w wins
            self.assertTrue(self._test_game.make_move(self._player_w, (6, 5), 'L'))
            self.assertTrue(self._test_game.get_winner(), self._player_w)

        except AssertionError as error:
            # show the board state when the error occurred
            print("State of board at time of error:")
            print()
            print(self._test_game)
            # re-raise to preserve the original behavior of the test on failure
            raise error

    def test_make_move(self):
        """
        Tests whether make move correctly alters the state of the board and game when a valid move is made, but does
        not alter either when an invalid one is made. (This test ends with Player B winning by capturing 7 marbles.)

        This is effectively an integration test.
        """
        try:
            # make a few invalid moves first - each should return false and not alter the board state
            # try to have player b move a white marble
            self.assertFalse(self._test_game.make_move(self._player_b, (0, 0), 'R'))
            self.assertIsNone(self._test_game.get_current_turn())
            self.assertIsNone(self._test_game.get_winner())
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 8, 13))

            # try to have player w move a black marble
            self.assertFalse(self._test_game.make_move(self._player_w, (0, 5), 'R'))
            self.assertIsNone(self._test_game.get_current_turn())
            self.assertIsNone(self._test_game.get_winner())
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 8, 13))

            # try to have player b move a red marble
            self.assertFalse(self._test_game.make_move(self._player_b, (1, 3), 'R'))
            self.assertIsNone(self._test_game.get_current_turn())
            self.assertIsNone(self._test_game.get_winner())
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 8, 13))

            # try to have player b move a marble in an empty space
            self.assertFalse(self._test_game.make_move(self._player_b, (0, 3), 'R'))
            self.assertIsNone(self._test_game.get_current_turn())
            self.assertIsNone(self._test_game.get_winner())
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 8, 13))

            # try to have player b move a black marble, but in a disallowed direction
            self.assertFalse(self._test_game.make_move(self._player_b, (0, 5), 'L'))
            self.assertIsNone(self._test_game.get_current_turn())
            self.assertIsNone(self._test_game.get_winner())
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 8, 13))

            # try to have a player move their own marble off the board
            self.assertFalse(self._test_game.make_move(self._player_b, (0, 5), 'R'))
            self.assertIsNone(self._test_game.get_current_turn())
            self.assertIsNone(self._test_game.get_winner())
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 8, 13))

            # now make a mix of valid and invalid moves and check the game state after each
            # make a valid move and make sure the next player's turn is set correctly
            self.assertTrue(self._test_game.make_move(self._player_b, (0, 5), 'B'))
            self.assertEqual(self._test_game.get_current_turn(), self._player_w)
            self.assertIsNone(self._test_game.get_winner())
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 8, 13))
            self.assertEqual(self._test_game.get_marble((0, 5)), 'X')
            self.assertEqual(self._test_game.get_marble((1, 5)), 'B')
            self.assertEqual(self._test_game.get_marble((2, 5)), 'B')
            self.assertEqual(self._test_game.get_marble((3, 5)), 'R')

            # try to have player b go again - nothing should have changed
            self.assertFalse(self._test_game.make_move(self._player_b, (1, 5), 'B'))
            self.assertEqual(self._test_game.get_current_turn(), self._player_w)
            self.assertIsNone(self._test_game.get_winner())
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 8, 13))
            self.assertEqual(self._test_game.get_marble((0, 5)), 'X')
            self.assertEqual(self._test_game.get_marble((1, 5)), 'B')
            self.assertEqual(self._test_game.get_marble((2, 5)), 'B')
            self.assertEqual(self._test_game.get_marble((3, 5)), 'R')

            # make a few valid moves until someone pushes off a marble
            self.assertTrue(self._test_game.make_move(self._player_w, (1, 0), 'R'))
            self.assertTrue(self._test_game.make_move(self._player_b, (1, 6), 'L'))
            self.assertTrue(self._test_game.make_move(self._player_w, (1, 1), 'R'))
            self.assertTrue(self._test_game.make_move(self._player_b, (0, 6), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_w, (1, 2), 'R'))
            # at this point, player w has pushed off one of the black marbles
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 7, 13))
            self.assertEqual(self._test_game.get_captured(self._player_w), 0)  # only red marbles increase the score
            self.assertEqual(self._test_game.get_current_turn(), self._player_b)  # no bonus turns allowed

            # keep making moves until someone pushes off a red marble
            self.assertTrue(self._test_game.make_move(self._player_b, (1, 6), 'L'))
            self.assertFalse(self._test_game.make_move(self._player_w, (1, 2), 'R'))  # would re-create previous state
            self.assertTrue(self._test_game.make_move(self._player_w, (5, 6), 'L'))
            self.assertTrue(self._test_game.make_move(self._player_b, (2, 6), 'L'))
            self.assertTrue(self._test_game.make_move(self._player_w, (6, 6), 'L'))
            self.assertTrue(self._test_game.make_move(self._player_b, (2, 5), 'L'))
            self.assertTrue(self._test_game.make_move(self._player_w, (6, 4), 'F'))
            # the black marble at (1, 4) is boxed in at this point
            self.assertFalse(self._test_game.make_move(self._player_b, (1, 4), 'R'))
            self.assertFalse(self._test_game.make_move(self._player_b, (1, 4), 'L'))
            self.assertFalse(self._test_game.make_move(self._player_b, (1, 4), 'F'))
            self.assertFalse(self._test_game.make_move(self._player_b, (1, 4), 'B'))
            # but the black marble at (1, 5) can still be pushed left
            self.assertTrue(self._test_game.make_move(self._player_b, (1, 5), 'L'))
            self.assertTrue(self._test_game.make_move(self._player_w, (5, 4), 'F'))
            # a red marble was pushed off by player w
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 7, 12))
            self.assertEqual(self._test_game.get_captured(self._player_w), 1)
            self.assertEqual(self._test_game.get_captured(self._player_b), 0)
            self.assertEqual(self._test_game.get_current_turn(), self._player_b)  # no bonus turns allowed

            # make some more moves
            self.assertTrue(self._test_game.make_move(self._player_b, (5, 0), 'R'))
            self.assertTrue(self._test_game.make_move(self._player_w, (4, 4), 'F'))  # pushes off a black marble
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 6, 12))
            self.assertTrue(self._test_game.make_move(self._player_b, (1, 3), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_w, (3, 4), 'F'))  # pushes off a red marble
            self.assertEqual(self._test_game.get_captured(self._player_w), 2)
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 6, 11))
            self.assertTrue(self._test_game.make_move(self._player_b, (3, 3), 'L'))
            self.assertTrue(self._test_game.make_move(self._player_w, (2, 4), 'F'))  # pushes off a red marble
            self.assertEqual(self._test_game.get_captured(self._player_w), 3)
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 6, 10))
            self.assertTrue(self._test_game.make_move(self._player_b, (3, 2), 'L'))
            self.assertEqual(self._test_game.get_captured(self._player_b), 1)
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 6, 9))

            # at this point, the board looks like this:
            #     0 1 2 3 4 5 6            CAPTURED
            #  0  W W _ _ W _ _            W: 3
            #  1  _ W W _ W _ _            B: 1
            #  2  R R R B _ _ _
            #  3  R B _ _ _ R _
            #  4  _ _ R R _ _ _
            #  5  _ B B R _ W _
            #  6  B B _ R _ W _

            # keep making moves
            self.assertFalse(self._test_game.make_move(self._player_w, (1, 4), 'F'))
            self.assertTrue(self._test_game.make_move(self._player_w, (6, 5), 'L'))
            self.assertTrue(self._test_game.make_move(self._player_b, (3, 1), 'L'))  # pushes off a red marble
            self.assertEqual(self._test_game.get_captured(self._player_b), 2)
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 6, 8))
            self.assertTrue(self._test_game.make_move(self._player_w, (0, 4), 'R'))
            self.assertTrue(self._test_game.make_move(self._player_b, (2, 3), 'L'))  # pushes off a red marble
            self.assertEqual(self._test_game.get_captured(self._player_b), 3)
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 6, 7))
            self.assertTrue(self._test_game.make_move(self._player_w, (0, 0), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_b, (2, 2), 'L'))  # pushes off a red marble
            self.assertEqual(self._test_game.get_captured(self._player_b), 4)
            self.assertTupleEqual(self._test_game.get_marble_count(), (8, 6, 6))
            self.assertTrue(self._test_game.make_move(self._player_w, (1, 0), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_b, (2, 1), 'L'))  # pushes off a white marble
            self.assertEqual(self._test_game.get_captured(self._player_b), 4)
            self.assertTupleEqual(self._test_game.get_marble_count(), (7, 6, 6))
            self.assertTrue(self._test_game.make_move(self._player_w, (0, 1), 'R'))
            self.assertTrue(self._test_game.make_move(self._player_b, (4, 0), 'F'))
            self.assertTrue(self._test_game.make_move(self._player_w, (1, 2), 'L'))  # pushes off a black marble
            self.assertEqual(self._test_game.get_captured(self._player_w), 3)
            self.assertTupleEqual(self._test_game.get_marble_count(), (7, 5, 6))
            self.assertTrue(self._test_game.make_move(self._player_b, (6, 0), 'R'))
            self.assertTrue(self._test_game.make_move(self._player_w, (5, 5), 'F'))
            self.assertTrue(self._test_game.make_move(self._player_b, (5, 1), 'R'))
            self.assertTrue(self._test_game.make_move(self._player_w, (0, 2), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_b, (5, 2), 'R'))
            self.assertTrue(self._test_game.make_move(self._player_w, (1, 4), 'L'))
            self.assertTrue(self._test_game.make_move(self._player_b, (5, 3), 'R'))
            self.assertTrue(self._test_game.make_move(self._player_w, (1, 0), 'R'))
            self.assertTrue(self._test_game.make_move(self._player_b, (3, 0), 'F'))

            # at this point, the board looks like this:
            #     0 1 2 3 4 5 6            CAPTURED
            #  0  _ _ _ _ _ W _            W: 3
            #  1  R W W W W _ _            B: 4
            #  2  B _ _ _ _ _ _
            #  3  _ _ _ _ _ R _
            #  4  _ _ R R _ W _
            #  5  _ _ _ _ B B R
            #  6  _ B B R W _ _

            # keep making moves
            self.assertTrue(self._test_game.make_move(self._player_w, (0, 5), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_b, (5, 4), 'R'))  # pushes off a red marble
            self.assertEqual(self._test_game.get_captured(self._player_b), 5)
            self.assertTupleEqual(self._test_game.get_marble_count(), (7, 5, 5))
            self.assertTrue(self._test_game.make_move(self._player_w, (1, 5), 'L'))  # pushes off a red marble
            self.assertEqual(self._test_game.get_captured(self._player_w), 4)
            self.assertTupleEqual(self._test_game.get_marble_count(), (7, 5, 4))
            self.assertTrue(self._test_game.make_move(self._player_b, (6, 1), 'R'))
            self.assertTrue(self._test_game.make_move(self._player_w, (6, 5), 'F'))
            self.assertTrue(self._test_game.make_move(self._player_b, (6, 2), 'R'))
            self.assertTrue(self._test_game.make_move(self._player_w, (5, 5), 'R'))  # pushes off a black marble
            self.assertEqual(self._test_game.get_captured(self._player_w), 4)
            self.assertTupleEqual(self._test_game.get_marble_count(), (7, 4, 4))
            self.assertTrue(self._test_game.make_move(self._player_b, (4, 5), 'F'))
            self.assertTrue(self._test_game.make_move(self._player_w, (1, 0), 'R'))
            self.assertTrue(self._test_game.make_move(self._player_b, (2, 0), 'F'))
            self.assertTrue(self._test_game.make_move(self._player_w, (2, 5), 'R'))
            self.assertTrue(self._test_game.make_move(self._player_b, (1, 0), 'R'))  # pushes off a red marble
            self.assertEqual(self._test_game.get_captured(self._player_b), 6)
            self.assertTupleEqual(self._test_game.get_marble_count(), (7, 4, 3))

            # at this point, the board looks like this:
            #     0 1 2 3 4 5 6            CAPTURED
            #  0  _ _ _ _ _ _ _            W: 4
            #  1  _ B W W W W W            B: 6
            #  2  _ _ _ _ _ _ W
            #  3  _ _ _ _ _ B _
            #  4  _ _ R R _ _ _
            #  5  _ _ _ _ _ _ W
            #  6  _ _ _ B B R _

            # keep making moves
            self.assertTrue(self._test_game.make_move(self._player_w, (5, 6), 'B'))
            self.assertTrue(self._test_game.make_move(self._player_b, (6, 3), 'R'))  # pushes off a white marble
            self.assertEqual(self._test_game.get_captured(self._player_b), 6)
            self.assertTupleEqual(self._test_game.get_marble_count(), (6, 4, 3))
            self.assertTrue(self._test_game.make_move(self._player_w, (1, 6), 'L'))

            # have player b push off their 7th red marble - player b wins
            self.assertTrue(self._test_game.make_move(self._player_b, (6, 4), 'R'))
            self.assertEqual(self._test_game.get_winner(), self._player_b)
            self.assertEqual(self._test_game.get_captured(self._player_b), 7)
            self.assertTupleEqual(self._test_game.get_marble_count(), (6, 4, 2))

            # final board state:
            #     0 1 2 3 4 5 6            CAPTURED
            #  0  _ _ _ _ _ _ _            W: 4
            #  1  B W W W W W _            B: 7
            #  2  _ _ _ _ _ _ W
            #  3  _ _ _ _ _ B _
            #  4  _ _ R R _ _ _
            #  5  _ _ _ _ _ _ _
            #  6  _ _ _ _ _ B B

            # no more moves are allowed at this point
            self.assertFalse(self._test_game.make_move(self._player_w, (2, 6), 'L'))
            self.assertFalse(self._test_game.make_move(self._player_w, (1, 0), 'R'))

        except AssertionError as error:
            # show the board state when the error occurred
            print("State of board at time of error:")
            print("Current turn:", self._test_game.get_current_turn())
            print()
            print(self._test_game)
            # re-raise to preserve the original behavior of the test on failure
            raise error


if __name__ == '__main__':
    unittest.main()


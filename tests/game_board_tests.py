# Modified:    2021-08-16
# Description: Contains unit tests for GameBoard & Square
import unittest
from marble_game.game_board import Square, GameBoard, IllegalMoveException


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
        self.assertIsNone(empty_square.contents)
        self.assertEqual(square.contents, 'R')

    def test_set_square_contents(self):
        """
        Tests whether Squares can have their contents changed as expected
        """
        empty_square = Square()
        square = Square('R')

        # tests whether we can set new values for the empty square
        empty_square.contents = 'W'
        self.assertEqual(empty_square.contents, 'W')

        # tests whether we can set new values for the non-empty square
        square.contents = 'B'
        self.assertEqual(square.contents, 'B')


class GameBoardTester(unittest.TestCase):
    """
    Contains unit tests for the game_board.py module
    """

    def setUp(self):
        """
        Create a GameBoard to be used in tests
        """
        self._board = GameBoard()

    def test_generate_all_row_and_column_combinations(self):
        """
        Tests whether GameBoard.generate_all_row_and_column_combinations correctly generates every
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

        self.assertEqual(self._board.get_contents_at_position(white_marble), 'W')
        self.assertEqual(self._board.get_contents_at_position(black_marble), 'B')
        self.assertEqual(self._board.get_contents_at_position(red_marble), 'R')
        self.assertIsNone(self._board.get_contents_at_position(empty))

    def test_get_marble_count(self):
        """
        Tests whether marble counts are obtained correctly
        """
        self.assertTupleEqual(self._board.marble_count, (8, 8, 13))

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
        Tests whether _deepcopy_grid correctly returns a deepcopy and not a shallow copy
        """
        # make two deep copies - if the grids contain identical copies, then the copies were shallow
        grid_1 = self._board._deepcopy_grid()
        grid_2 = self._board._deepcopy_grid()

        self.assertIsNot(grid_1, grid_2)
        for coordinates in self._board.generate_all_row_and_column_combinations():
            # get the squares at the same position in each grid copy
            row_index, column_index = coordinates
            square_1 = grid_1[row_index][column_index]
            square_2 = grid_2[row_index][column_index]
            # contents of the squares should be the same
            self.assertEqual(square_1.contents, square_2.contents)
            # but they should be totally different objects
            self.assertIsNot(square_1, square_2)

    # noinspection DuplicatedCode
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
            get_contents = self._board.get_contents_at_position
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
            self.assertTupleEqual(self._board.marble_count, (7, 8, 13))

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
            self.assertTupleEqual(self._board.marble_count, (7, 8, 13))

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
            self.assertTupleEqual(self._board.marble_count, (7, 8, 13))
        except AssertionError as error:
            # show the board state when the error occurred
            print("State of board at time of error:")
            print(self._board)
            # re-raise to preserve the original behavior of the tests on failure
            raise error

    def test_simulate_move_left(self):
        """
        Tests whether simulating a move left gives the expected result without changing the actual state
        of the marble_game board
        """
        # simulate moving the white marble at 1, 1 left, which would push off a white marble
        self.assertEqual(self._board.simulate_move((1, 1), 'L'), 'W')
        # the original state of the board shouldn't change
        self.assertTupleEqual(self._board.marble_count, (8, 8, 13))
        self.assertEqual(self._board.get_contents_at_position((1, 1)), 'W')

    def test_move_marble_right(self):
        """
        Tests whether moving right works as expected
        """
        try:
            # make these calls a little more readable
            direction = 'R'
            get_contents = self._board.get_contents_at_position
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
            self.assertTupleEqual(self._board.marble_count, (8, 8, 13))

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
            self.assertTupleEqual(self._board.marble_count, (8, 7, 13))

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
            self.assertTupleEqual(self._board.marble_count, (8, 7, 13))
        except AssertionError as error:
            # show the board state when the error occurred
            print("State of board at time of error:")
            print(self._board)
            # re-raise to preserve the original behavior of the tests on failure
            raise error

    def test_simulate_move_right(self):
        """
        Tests whether simulating a move right gives the expected result without changing the actual state
        of the marble_game board
        """
        # simulate moving the black marble at 1, 5 right, which would push off a black marble
        self.assertEqual(self._board.simulate_move((1, 5), 'R'), 'B')
        # the original state of the board shouldn't change
        self.assertTupleEqual(self._board.marble_count, (8, 8, 13))
        self.assertEqual(self._board.get_contents_at_position((1, 5)), 'B')

    def test_move_marble_forward(self):
        """
        Tests whether moving right forward (up) as expected
        """
        try:
            # make these calls a little more readable
            direction = 'F'
            get_contents = self._board.get_contents_at_position
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
            self.assertTupleEqual(self._board.marble_count, (7, 8, 13))

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
            self.assertTupleEqual(self._board.marble_count, (7, 8, 13))

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
            self.assertTupleEqual(self._board.marble_count, (7, 8, 13))
        except AssertionError as error:
            # show the board state when the error occurred
            print("State of board at time of error:")
            print(self._board)
            # re-raise to preserve the original behavior of the tests on failure
            raise error

    def test_simulate_move_forward(self):
        """
        Tests whether simulating a move forward (up) gives the expected result without changing the actual state
        of the marble_game board
        """
        # simulate moving the white marble at 1, 1 forward, which would push off a white marble
        self.assertEqual(self._board.simulate_move((1, 1), 'F'), 'W')
        # the original state of the board shouldn't change
        self.assertTupleEqual(self._board.marble_count, (8, 8, 13))
        self.assertEqual(self._board.get_contents_at_position((1, 1)), 'W')

    def test_move_marble_backward(self):
        """
        Tests whether moving backward (down) works as expected
        """
        try:
            # make these calls a little more readable
            direction = 'B'
            get_contents = self._board.get_contents_at_position
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
            self.assertTupleEqual(self._board.marble_count, (8, 8, 13))

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
            self.assertTupleEqual(self._board.marble_count, (8, 7, 13))

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
            self.assertTupleEqual(self._board.marble_count, (8, 7, 13))
        except AssertionError as error:
            # show the board state when the error occurred
            print("State of board at time of error:")
            print(self._board)
            # re-raise to preserve the original behavior of the tests on failure
            raise error

    def test_simulate_move_backward(self):
        """
        Tests whether simulating a move backward (down) gives the expected result without changing the actual state
        of the marble_game board
        """
        # simulate moving the white marble at 5, 1 forward, which would push off a black marble
        self.assertEqual(self._board.simulate_move((5, 1), 'B'), 'B')
        # the original state of the board shouldn't change
        self.assertTupleEqual(self._board.marble_count, (8, 8, 13))
        self.assertEqual(self._board.get_contents_at_position((5, 1)), 'B')

    def test_simulate_returns_previous(self):
        """
        Test whether simulating a move that would return the state of the board to its previous state returns
        the expected result ("previous")
        """
        # move the white marble from 1, 1 down one square
        self._board.move_marble((1, 1), 'B')  # after this, the marble is at 2, 1

        # now simulate trying to move it back up
        self.assertEqual(self._board.simulate_move((2, 1), 'F'), "previous")


if __name__ == '__main__':
    unittest.main()

# Author:      Donato Quartuccia
# Modified:    2021-08-18
# Description: Contains unit tests for JSON Encoding & Decoding of package objects
import unittest
import json
from marble_game.marble_game import MarbleGame, MarbleGameEncoder, MarbleGameDecoder
from marble_game.game_board import GameBoard, GameBoardEncoder, GameBoardDecoder


class GameBoardJSONTests(unittest.TestCase):
    """Contains unit tests for GameBoard JSON encoding & decoding"""

    def setUp(self):
        """Create GameBoards and JSON strings to be used in tests"""

        self._initial_board = GameBoard()
        self._board = GameBoard()
        self._board.move_marble((0, 5), 'F')  # the black marble at 0, 5 should be removed from the board
        self._board.move_marble((2, 4), 'F')  # the red marble at 0, 4 should now be at 1, 4
        self.json_string_init = json.dumps(
            {
                "grid":           "WW   BBWW R BB  RRR   RRRRR   RRR  BB R WWBB   WW",
                "previous_state": " "*49,
            },
            sort_keys=True,
        )
        self.json_string_mid = json.dumps(
            {
                "grid":           "WW    BWW RRBB  RR    RRRRR   RRR  BB R WWBB   WW",
                "previous_state": "WW    BWW R BB  RRR   RRRRR   RRR  BB R WWBB   WW",
            },
            sort_keys=True,
        )

    def test_encode(self):
        """Tests whether GameBoard is encoded as expected"""
        # test encoding the board in its initial state
        self.assertEqual(self.json_string_init, json.dumps(self._initial_board, cls=GameBoardEncoder, sort_keys=True))

        # test encoding the board after two moves are made
        self.assertEqual(self.json_string_mid, json.dumps(self._board, cls=GameBoardEncoder, sort_keys=True))

    def test_decode(self):
        """Tests whether GameBoard is decoded as expected"""
        # decode the string
        board = json.loads(self.json_string_mid, cls=GameBoardDecoder)

        # check whether an instance of GameBoard was returned
        self.assertIsInstance(board, GameBoard)

        # check whether the grid and previous states are set as expected
        self.assertEqual("WW    BWW RRBB  RR    RRRRR   RRR  BB R WWBB   WW", board.grid_as_str)
        self.assertEqual("WW    BWW R BB  RRR   RRRRR   RRR  BB R WWBB   WW", board.previous_grid_as_str)

    def test_encode_then_decode(self):
        """Tests whether GameBoard can be encoded then decoded to the same state"""
        encoded_json = json.dumps(self._board, cls=GameBoardEncoder)
        decoded_board = json.loads(encoded_json, cls=GameBoardDecoder)
        for var in vars(self._board):
            self.assertEqual(getattr(self._board, var), getattr(decoded_board, var))


class MarbleGameJSONTests(unittest.TestCase):
    """Contains unit tests for MarbleGame JSON encoding & decoding"""

    def setUp(self):
        """Create a MarbleGame and JSON strings to be used in tests"""
        self._player_b = "Player B ID"
        self._player_w = "Player W ID"
        self._test_game = MarbleGame((self._player_b, "Player B", 'B'), (self._player_w, "Player W", 'W'))
        self.json_string_init = json.dumps(
            {
                "board": json.dumps({
                    "grid": "WW   BBWW R BB  RRR   RRRRR   RRR  BB R WWBB   WW",
                    "previous_state": " " * 49,
                }),
                "players": json.dumps({
                    "Player B ID": {
                            "name": "Player B",
                            "color": 'B',
                            "red_marbles_captured": 0,
                            "opponent_marbles_captured": 0,
                        },
                    "Player W ID":
                        {
                            "name": "Player W",
                            "color": 'W',
                            "red_marbles_captured": 0,
                            "opponent_marbles_captured": 0,
                        },
                },
                ),
                "current_turn": None,
                "winner": None,
            },
            sort_keys=True,
        )
        self.json_string_mid = json.dumps(
            {
                "board": json.dumps({
                    "grid":           " W   BBWW R BBW RRR   RRRRR   RRR  BB R WWBB   WW",
                    "previous_state": "WW   BBWW R BB  RRR   RRRRR   RRR  BB R WWBB   WW",
                }),
                "players": json.dumps({
                    "Player B ID": {
                            "name": "Player B",
                            "color": 'B',
                            "red_marbles_captured": 0,
                            "opponent_marbles_captured": 0,
                        },
                    "Player W ID":
                        {
                            "name": "Player W",
                            "color": 'W',
                            "red_marbles_captured": 0,
                            "opponent_marbles_captured": 0,
                        },
                },
                ),
                "current_turn": "Player B ID",
                "winner": None,
            },
            sort_keys=True,
        )

    def test_encode(self):
        """Tests whether MarbleGame is encoded as expected"""
        # test encoding the game in its initial state
        self.assertEqual(self.json_string_init, json.dumps(self._test_game, cls=MarbleGameEncoder, sort_keys=True))

        # test encoding after the first move has taken place
        self._test_game.make_move("Player W ID", (0, 0), 'B')
        self.assertEqual(self.json_string_mid, json.dumps(self._test_game, cls=MarbleGameEncoder, sort_keys=True))

    def test_decode(self):
        """Tests whether MarbleGame is decoded as expected"""
        # decode the string
        game = json.loads(self.json_string_mid, cls=MarbleGameDecoder)

        # check whether an instance of MarbleGame was returned
        self.assertIsInstance(game, MarbleGame)

        # check whether the board state is set as expected
        self.assertEqual(" W   BBWW R BBW RRR   RRRRR   RRR  BB R WWBB   WW", game._game_board.grid_as_str)
        self.assertEqual("WW   BBWW R BB  RRR   RRRRR   RRR  BB R WWBB   WW", game._game_board.previous_grid_as_str)

        # check whether the game state is set as expected
        players_expected = {
            "Player B ID":
                {
                    "name": "Player B",
                    "color": 'B',
                    "opponent_marbles_captured": 0,
                    "red_marbles_captured": 0,
                },

            "Player W ID":
                {
                    "name": "Player W",
                    "color": 'W',
                    "opponent_marbles_captured": 0,
                    "red_marbles_captured": 0,
                }
        }
        self.assertDictEqual(players_expected, game._players)
        self.assertEqual("Player B ID", game.current_turn)
        self.assertIsNone(game.winner)

    def test_encode_then_decode(self):
        """Tests whether MarbleGame can be encoded then decoded to the same state"""
        encoded_json = json.dumps(self._test_game, cls=MarbleGameEncoder)
        decoded_game = json.loads(encoded_json, cls=MarbleGameDecoder)
        for var in vars(self._test_game):
            if var == "_game_board":
                # GameBoard doesn't have __eq__ defined, so we need to compare its properties individually
                original_board = self._test_game._game_board
                decoded_board = decoded_game._game_board
                for board_var in vars(self._test_game._game_board):
                    self.assertEqual(getattr(original_board, board_var), getattr(decoded_board, board_var))
            else:
                self.assertEqual(getattr(self._test_game, var), getattr(decoded_game, var))


if __name__ == '__main__':
    unittest.main()

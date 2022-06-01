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
# Description: Contains logic for an AI that plays the marble game.

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Final, Union
from pickle import dumps as pickle, loads as unpickle
from .marble_game import MarbleGame

# define constants
POS_INF: Final = float("inf")
NEG_INF: Final = float("-inf")


@dataclass
class Node:
    """Represents a node in the decision tree"""
    game_state: MarbleGame
    value: Union[int, float]
    move: tuple[tuple[int, int], str] = None        # this *must* be filled when depth == 1
    parent: Node = None                             # None => root node
    children: list = field(default_factory=list)    # empty => leaf node

    def add_child(self, node: Node):
        """Adds the specified node as a child of this node, and updates its parent to refer to this node"""
        node.parent = self
        self.children.append(node)

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.value == other.value
        if isinstance(other, (int, float)):
            return self.value == other
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Node):
            return self.value < other.value
        if isinstance(other, (int, float)):
            return self.value < other
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, Node):
            return self.value <= other.value
        if isinstance(other, (int, float)):
            return self.value <= other
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Node):
            return self.value > other.value
        if isinstance(other, (int, float)):
            return self.value > other
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, Node):
            return self.value >= other.value
        if isinstance(other, (int, float)):
            return self.value >= other
        return NotImplemented


def heuristic_factory(maximizer_id: str, minimizer_id: str) -> Callable[[MarbleGame], Union[int, float]]:
    """
    Creates a function that returns the heuristic value of a MarbleGame.

    :param maximizer_id: the player ID of the maximizing player
    :param minimizer_id: the player ID of the minimizing player
    :return: a closure that returns the heuristic value of a MarbleGame
    """
    def heuristic(game: MarbleGame) -> Union[int, float]:
        """Returns the heuristic value of the game"""
        # calculate the delta between the maximizer's "score" and the minimizer's
        maximizer_score = game.get_captured(maximizer_id) + game.get_opponent_captured(maximizer_id)
        minimizer_score = game.get_captured(minimizer_id) + game.get_opponent_captured(minimizer_id)
        value = maximizer_score - minimizer_score
        # if one of the players has won, pad the score
        if game.winner == maximizer_id:
            value += 100
        if game.winner == minimizer_id:
            value -= 100
        return maximizer_score - minimizer_score
    return heuristic


def alpha_beta_search(
        root_node: Node,
        heuristic_function: Callable[[MarbleGame], Union[int, float]],
        maximizer_id: str,
        minimizer_id: str,
        maximum_search_depth: int,
) -> Node:
    """
    Generates and searches a decision tree to determine the best possible resulting game state for the maximizing
    player, beginning with the specified root node and applying alpha-beta pruning thereafter. Assumes that it is the
    maximizing player's turn first, and the maximizing player may make at least one legal move.

    **Note:** this function should not be used to pit one AI against another, as this may result in an endless
    `ko fight <https://en.wikipedia.org/wiki/Ko_fight>`_

    :param root_node: the root node of the decision tree
    :param heuristic_function: a function that takes a game state and outputs a heuristic value
    :param maximizer_id: the player ID of the maximizing player
    :param minimizer_id: the player ID of the minimizing player
    :param maximum_search_depth: the maximum depth to search the decision tree
    :return: the node that results in the best state for the maximizer
    """
    # this is just a wrapper for alpha_beta_helper
    def alpha_beta_helper(
            current: Node, depth_remaining: int, alpha: Union[Node, float], beta: Union[Node, float], maximizer: bool
    ) -> Node:
        """
        Helper function for alpha_beta_search.

        :param current: the node currently being visited (initially, the root node passed to the outer function)
        :param depth_remaining: the remaining depth to search the tree (initially, the maximum search depth)
        :param alpha: the node with the best value found so far for the maximizer (initially, -inf)
        :param beta: the node with the best value found so far for the minimizer (initially, +inf)
        :param maximizer: True if it's the maximizing player's turn, otherwise False
        :return: the node that results in the best state for the maximizer
        """
        # base case: we've searched at the maximum depth, or the current node represents an end state
        if depth_remaining == 0 or current.game_state.winner is not None:
            return current
        # recursive step: generate and search child nodes depth-first, keeping track of alpha (maximizer's best) and
        #                 beta (minimizer's best) and short-circuiting the search when a node that yields a worse result
        #                 for the player is found
        saved_game_state = pickle(current.game_state)   # save game state so we can copy it later
        if maximizer:
            best_node = NEG_INF
            for move in current.game_state.generate_possible_moves(maximizer_id):
                # generate child node
                new_game_state: MarbleGame = unpickle(saved_game_state)
                new_game_state.make_move(maximizer_id, *move)
                child = Node(new_game_state, heuristic_function(new_game_state), move)
                current.add_child(child)
                # continue searching
                best_node = max(best_node, alpha_beta_helper(child, depth_remaining - 1, alpha, beta, False))
                alpha = max(best_node, alpha)
                if alpha >= beta:
                    return alpha
            return best_node
        else:
            best_node = POS_INF
            for move in current.game_state.generate_possible_moves(minimizer_id):
                # generate child node
                new_game_state: MarbleGame = unpickle(saved_game_state)
                new_game_state.make_move(minimizer_id, *move)
                child = Node(new_game_state, heuristic_function(new_game_state), move)
                current.add_child(child)
                # continue searching
                best_node = min(best_node, alpha_beta_helper(child, depth_remaining - 1, alpha, beta, True))
                beta = min(best_node, beta)
                if beta <= alpha:
                    return beta
            return best_node
    return alpha_beta_helper(root_node, maximum_search_depth, NEG_INF, POS_INF, True)


def make_move_ai(ai_id: str, game: MarbleGame, max_depth: int = 3) -> bool:
    """
    Makes a move for the specified AI player.

    :param ai_id: the player ID of the AI player
    :param game: the MarbleGame where the move should take place
    :param max_depth: the maximum number of moves to look ahead
    :return: True if the move is successful, otherwise False
    """
    # ensure the AI player is able to make a move
    if game.winner is not None or game.current_turn not in {None, ai_id} or ai_id not in game.player_ids:
        return False

    # construct the decision tree
    opponent_id = game.player_ids.difference({ai_id}).pop()        # it's guaranteed that ai_id is in game.players
    heuristic_function = heuristic_factory(ai_id, opponent_id)
    decision_tree_root = Node(game, heuristic_function(game))

    # get the best possible end state for the AI player and make the move that would lead the AI there
    node = alpha_beta_search(decision_tree_root, heuristic_function, ai_id, opponent_id, max_depth)
    # search for and return the move that resulted in the
    while node.parent is not decision_tree_root:
        node = node.parent
    return game.make_move(ai_id, *node.move)

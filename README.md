#### Description
A virtual representation of a board game based on the rules of Kuba

#### Basic Game Rules
- Any player can start the game. Players then alternate turns. There are no bonus turns.
- Game ends when a player wins.
- The initial setup of the board will is as shown in the figure [here](https://sites.google.com/site/boardandpieces/list-of-games/kuba)
- Win conditions:
  - A player wins by pushing off and capturing seven neutral red stones or by pushing off all the opposing stones.
  - A player who has no legal moves available has lost the game.
- Rules to move a marble:
  - You need an empty space (or the edge of the board) on the side you are pushing away from.
  - A player cannot undo a move the opponent just made if it leads to the exact same board position
- Directions are explained in the following image:
  
    ![directions](https://user-images.githubusercontent.com/32501313/117386394-b08b1180-ae9b-11eb-9779-9bbd8531c91d.PNG)

    - Vertical moves are "forward" (up) and "backward" (down)
    - Horizontal moves are "right" and "left"

#### Example code use:
```
game = KubaGame(('PlayerA', 'W'), ('PlayerB', 'B'))
game.get_marble_count() #returns (8,8,13)
game.get_captured('PlayerA')
game.get_winner() #returns None
game.make_move('PlayerA', (6,5), 'F')
game.get_current_turn() #returns 'PlayerB' because PlayerA has just played.
game.make_move('PlayerA', (6,5), 'L') #Cannot make this move
game.get_marble((5,5)) #returns 'W'
```

## KubaLibre

### Description
In short, a virtual representation of a board game based on the rules of [Kuba](https://boardgamegeek.com/boardgame/1337/kuba),
implemented as a full-stack webapp.

### Live Demo
https://marble-game.herokuapp.com/

### API Specifications
https://marble-game.herokuapp.com/redoc

### Deployment
#### Build Instructions
1. Define environment variables
2. Install `docker`
3. Run `docker compose build` from the project root directory
4. Start the docker containers (e.g. `docker compose up`)

#### Environment Variables
Define the following environment variables in `.env` in the project root directory:
###### Required
* FASTAPI_HOST: the server's hostname
* FASTAPI_PORT: the port uvicorn should listen on
* FASTAPI_MONGODB_URI: a URI that connects to your MongoDB cluster/server
* FASTAPI_DB_NAME: the name of the MongoDB database
* FASTAPI_PLAYER_COLLECTION_NAME: the name of the collection to use for player data
* FASTAPI_GAME_COLLECTION_NAME: the name of the collection to be used for game data
* REACT_APP_DOMAIN: the Auth0 application's domain name
* REACT_APP_CLIENT_ID: the Auth0 application's client ID

###### Optional
* FASTAPI_DEBUG: set to True to cause the uvicorn server will restart when changes are detected
* FASTAPI_APP_NAME: set a name to be displayed as the webpage title for the API documentation pages

#### Disclaimer
This source code is only intended as a demonstration. Before attempting to deploy this, make sure you fully consider
security best practices (CORS, authentication, etc.)

### Project Structure
#### api
Houses the backend API, built with [Uvicorn](https://www.uvicorn.org/), [FastAPI](https://fastapi.tiangolo.com/), [Pydantic](https://pydantic-docs.helpmanual.io/),
MongoDB and [Motor](https://motor.readthedocs.io/en/stable/). This implements the model and controller and allows game states
to be stored and retrieved from a MongoDB database.
##### marble_game
Houses the game logic, including a decision-making AI. This is all you need to actually play the game.
#### marble_game_ui
Houses the web frontend view, built with React, MaterialUI and Auth0 (for user authentication).
#### tests
Self-explanatory. Mostly focused on testing the game logic and JSON serialization.

### Basic Game Rules
- Any player can start the game. Players then alternate turns. There are no bonus turns, unlike in the original game.
- The game ends when a player wins.
- The initial setup of the board is as shown in the figure [here](https://sites.google.com/site/boardandpieces/list-of-games/kuba)
- Win conditions:
  - A player wins by pushing off and capturing seven neutral red stones or by pushing off all the opposing stones.
  - A player who has no legal moves available has lost the game.
- Rules to move a marble:
  - You need an empty space (or the edge of the board) on the side you are pushing away from.
  - A player cannot undo a move the opponent just made if it leads to the exact same board position
- Directions are as follows:
  - Vertical moves are "forward" (up) and "backward" (down)
  - Horizontal moves are "left" and "right"

### Do I need a rocks glass to play?
No

// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { MoveResponse, GameResponse, PlayerResponse, ErrorResponse, GameState } from "./types";

// TODO BEARER TOKEN
const token = ``;


// ----------------------------------------------  MOVE ----------------------------------------------
/**
 * Makes a move to update the game. Resolves to {@link MoveResponse} if fulfilled, {@link ErrorResponse} if rejected.
 *
 * @param playerID the player's 24-hex digit ObjectID
 * @param gameID the game's 24-hex digit ObjectID
 * @param rowCoord the row coordinate (0..6)
 * @param colCoord the col coordinate (0..6)
 * @param direction the direction of movement ('F', 'B', 'R' or 'L')
 */
export async function move(
    playerID: string,
    gameID: string,
    rowCoord: number,
    colCoord: number,
    direction: string
): Promise<MoveResponse> {
    const response = await fetch(`/game/${gameID}/make-move`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
            'player_id': playerID,
            'row_coord': rowCoord,
            'col_coord': colCoord,
            'direction': direction,
        }),
    });

    if (!response.ok) {
        return Promise.reject(await response.json());
    }

    return await response.json();
}


// ----------------------------------------------  GAME  ----------------------------------------------
/**
 * Retrieves game data. Resolves to {@link GameResponse} if fulfilled {@link ErrorResponse} if rejected.
 *
 * @param gameID the game's 24-hex digit ObjectID
 */
export async function getGame(gameID: string): Promise<GameResponse> {
    const response = await fetch(`/game/${gameID}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
           'Authorization': `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        return Promise.reject(await response.json());
    }

    const parsedResponse = await response.json();
    decodeGameResponse(parsedResponse);
    return parsedResponse;
}


/**
 * Creates a one player game (v. AI). Resolves to {@link GameResponse} if fulfilled, {@link ErrorResponse} if rejected.
 *
 * @param playerID the player's 24-hex digit ObjectID
 * @param playerMarbleColor the player's marble color ('B' or 'W')
 */
export async function createOnePlayerGame(playerID: string, playerMarbleColor: 'B' | 'W'): Promise<GameResponse> {
    const response = await fetch(`/game/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
           'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
            'player_one_id': playerID,
            'player_one_color': playerMarbleColor,
        }),
    });

    if (!response.ok) {
        return Promise.reject(await response.json());
    }

    const parsedResponse = await response.json();
    decodeGameResponse(parsedResponse);
    return parsedResponse;
}

// --------------------------------------------  PLAYER  --------------------------------------------
/**
 * Retrieves player data. Resolves to {@link PlayerResponse} if fulfilled, {@link ErrorResponse} if rejected.
 *
 * @param playerID the player's 24-hex digit ObjectID
 */
export async function getUser(playerID: string): Promise<PlayerResponse> {
    const response = await fetch(`/player/${playerID}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        return Promise.reject(await response.json());
    }

    return await response.json();
}


/**
 * Retrieves game data for the specified player's current games, paginated using the specified skip and limit.
 * Resolves to {@link GameResponse}[] if fulfilled, {@link ErrorResponse} if rejected.
 *
 * @param playerID the player's 24-hex digit ObjectID
 * @param skip pagination offset (if paginating, should be set to previous request's skip + limit)
 * @param limit maximum number of games to return with each request
 */
export async function getUserCurrentGames(playerID: string, skip: number, limit: number): Promise<GameResponse[]> {
    const response = await fetch(`/player/${playerID}/games/current?skip=${skip}&limit=${limit}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
             'Authorization': `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        return Promise.reject(await response.json());
    }

    const parsedResponse = await response.json();
    parsedResponse.forEach(decodeGameResponse);
    return parsedResponse;
}

/**
 * Retrieves game data for the specified player's completed games, paginated using the specified skip and limit.
 * Resolves to {@link GameResponse}[] if fulfilled, {@link ErrorResponse} if rejected.
 *
 * @param playerID the player's 24-hex digit ObjectID
 * @param skip pagination offset (if paginating, should be set to previous request's skip + limit)
 * @param limit maximum number of games to return with each request
 */
export async function getUserCompletedGames(playerID: string, skip: number, limit:number): Promise<GameResponse[]> {
    const response = await fetch(`/player/${playerID}/games/completed?skip=${skip}&limit=${limit}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
             'Authorization': `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        return Promise.reject(await response.json());
    }

    const parsedResponse = await response.json();
    parsedResponse.forEach(decodeGameResponse);
    return parsedResponse;
}

// ----------------------------------------------  HELPERS  ----------------------------------------------

/**
 * Mutates gameResponse by decoding its game_state from JSON object to {@link GameState}
 * 
 * @param gameResponse object containing JSON-encoded `game_state`
 * 
 */
function decodeGameResponse (gameResponse: any) {
    if (!gameResponse.hasOwnProperty('game_state')) {
        return;
    }

    // parse the game state, which has board and players encoded as JSON
    gameResponse.game_state = JSON.parse(
        gameResponse.game_state,
        (key, value) => {
            switch (key) {
                case 'board':
                    return JSON.parse(value);
                case 'players':
                    return JSON.parse(value);
                default:
                    return value;
            }
        }
    )   
}

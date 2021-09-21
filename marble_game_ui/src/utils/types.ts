export type MarbleCharacter = 'B' | 'R' | 'W'  | ' ';
export type MarbleCharacterGrid = MarbleCharacter[][];

export type GameState = {
    'board': {
        'grid': string,
        'previous_state': string,
    },
    'players': {
        playerOneID: {
            'color': 'B' | 'W',
            'red_marbles_captured': number,
            'opponent_marbles_captured': number
        },
        playerTwoID: {
            'color': 'B' | 'W',
            'red_marbles_captured': number,
            'opponent_marbles_captured': number
        },
        'current_turn': string;
    }
}

export type ErrorResponse = {
    'detail': Array<{
        'loc': Array<string>,
        'msg': string,
        'type': string }>,
}

export type MoveResponse = {
    'move_successful': boolean,
    'game_complete': boolean,
}

export type GameResponse = {
    'id': string,
    'player_ids': Array<string>,
    'game_state': GameState,
    'versus_ai': boolean,
    'completed': boolean,
}

export type PlayerResponse = {
    'id': string,
    'current_games': Array<string>,
    'completed_games': Array<string>,
}

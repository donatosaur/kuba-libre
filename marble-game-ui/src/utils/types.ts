export type MarbleCharacter = 'B' | 'R' | 'W'  | ' ';
export type MarbleCharacterGrid = MarbleCharacter[][];

export type GameState = {
    'board': {
        'grid': string,
        'previous_state': string,
    },
    'players': {
        [key: string]: {
            'color': 'B' | 'W',
            'red_marbles_captured': number,
            'opponent_marbles_captured': number,
        }
    },
    'current_turn': string,
    'winner': string,
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
    '_id': string,
    'player_ids': Array<string>,
    'game_state': GameState,
    'versus_ai': boolean,
    'completed': boolean,
}

export type PlayerResponse = {
    '_id': string,
    'current_games': Array<string>,
    'completed_games': Array<string>,
}

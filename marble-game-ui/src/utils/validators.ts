import { ErrorResponse, MoveResponse, GameResponse, PlayerResponse } from './types';


export function isErrorResponse (obj: any): obj is ErrorResponse {
    return (obj as ErrorResponse).detail !== undefined;
}

export function isMoveResponse (obj: any): obj is MoveResponse {
    return (obj as MoveResponse).move_successful !== undefined;
}

export function isGameResponse (obj: any): obj is GameResponse {
    return (obj as GameResponse).game_state !== undefined;
}

export function isPlayerResponse (obj: any): obj is PlayerResponse {
    return (obj as PlayerResponse).current_games !== undefined;
}

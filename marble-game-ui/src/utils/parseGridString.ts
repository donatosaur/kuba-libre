import { MarbleCharacter, MarbleCharacterGrid } from './types';

/**
 * Parses a 49-character string of MarbleCharacters ('B', 'R', 'W', ' ') and returns a
 * 7x7 2D array containing those characters, in order.
 *
 * @param gridString a 49-character string of MarbleCharacters
 */
export function parseGridString(gridString: string): MarbleCharacterGrid {
    const grid: Array<Array<MarbleCharacter>> = new Array<Array<MarbleCharacter>>()
    for (let i = 0; i < 7; i++) {
        grid.push(new Array<MarbleCharacter>());
    }

    for (let i = 0; i < gridString.length; i++) {
        // the row is located at index // 7, the column at index % 7
        grid[Math.trunc(i / 7)][Math.trunc(i % 7)] = gridString[i] as MarbleCharacter;
    }

    return grid;
}

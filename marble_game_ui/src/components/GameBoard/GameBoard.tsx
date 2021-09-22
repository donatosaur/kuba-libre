import React, { useState, useEffect } from 'react';

import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import { AlertColor } from '@mui/material/Alert';

import { Marble } from './Marble';
import { MessageStack } from './MessageStack';
import { parseGridString, callAPI, isErrorResponse } from '../../utils';

// define radius of each marble
const marbleSize = 50;

type GameBoardProps = {
  playerID: string;
  gameID: string;
}

export function GameBoard({ playerID, gameID }: GameBoardProps) {
  const [alert, setAlert] = useState<{severity: AlertColor; message: string} | null>(null);
  const [sourceCoords, setSourceCoords] = useState<number[] | null>(null);
  const [boardState, setBoardState] = useState<string>(' '.repeat(49));
  const [turnTracker, setTurnTracker] = useState(0);
  

  // get the board state on page load and on every new turn
  useEffect(() => {
    const abortController = new AbortController();
    void async function getGameString() {
      try {
        const game = await callAPI.getGame(gameID);
        setBoardState(game.game_state.board.grid);
      } catch (err) {
        if (isErrorResponse(err)) {
          for (const errorDetail of err.detail) {
            console.log({ severity: 'error', message: `${errorDetail.type}: ${errorDetail.msg}` });
          }
        }
        return;
      }
    }();
    // prevent memory leaks: abort request if component is no longer mounted
    return () => abortController.abort();
  }, [turnTracker, gameID]);

  const resetPositionHooks = () => {
    setSourceCoords(null);
  }

  // event handlers
  const selectSource = (event: React.PointerEvent, rowCoord: number, colCoord: number) => {
    // console.log('selected source:', rowCoord, colCoord);
    event.preventDefault();
    setSourceCoords([rowCoord, colCoord]);
  }

  const selectDestination = async (event: React.PointerEvent, rowCoord: number, colCoord: number) => {
    // console.log('selected dest:', rowCoord, colCoord);
    event.preventDefault();
    
    // if the source wasn't successfully captured, reset the state hooks
    if (sourceCoords === null) {
      // console.log('source coordinates were not captured');
      resetPositionHooks();
      return;
    }

    const deltaRow = Math.round(rowCoord - sourceCoords[0]);
    const deltaCol = Math.round(colCoord - sourceCoords[1]);
    
    // check whether the marble was moved at all; cancel the move if it wasn't
    if (deltaRow === 0 && deltaCol === 0) {
      resetPositionHooks();
      return;
    }

    // check for invalid states
     if (Math.abs(deltaRow) > 0 && Math.abs(deltaCol) > 0) {
      // the user moved the marble diagonally
      setAlert({
        severity:'warning', 
        message:'Please only swipe up/down or left/right.'
      });
      resetPositionHooks();
      return;
    }
    
    // map movement to direction
    let direction: 'F' | 'B' | 'R' | 'L';
    if (deltaCol > 0) {
        direction = 'R';
    } else if (deltaCol < 0) {
        direction = 'L';
    } else if (deltaRow < 0) {
        direction = 'F';  // forward = up
    } else {
        // (deltaRow > 0) is the only other possibility here
        direction = 'B';  // backward = down
    }

    // make the move
    try {
      const moveResult = await callAPI.move(playerID as string, gameID, sourceCoords[0], sourceCoords[1], direction);
      
      if (!moveResult.move_successful) {
        // alert the user that the move failed; TODO: provide a link to the rules
        setAlert({ severity:'info', message:'The proposed move was invalid. Please try again.' });
      } else {
        // notify the user that the move was successful, and whether there was a winner
        const alertInfo = moveResult.game_complete 
          ? { severity:'success' as AlertColor, message:'Move successfully recorded. Win state.' }
          : { severity:'info' as AlertColor, message:'Move successfully recorded.' };
        setAlert(alertInfo);
        
        // increment the turnTracker to trigger useEffect listener
        setTurnTracker(turnTracker + 1);
      }
    } catch (err) {
      if (isErrorResponse(err)) {
        for (const errorDetail of err.detail) {
          console.log({ severity: 'error', message: `${errorDetail.type}: ${errorDetail.msg}` });
        }
      }
    }
    
    // reset position & selection hooks after a small delay (most mobile browsers need time to process touch events)
    setTimeout(() => {
      resetPositionHooks();
    }, 400)
  }

  // parse input to 2D-array
  const gridArray = parseGridString(boardState);

  return (
    <>
      <Grid
        container
        spacing={0}
        direction="column"
        onPointerLeave={() => resetPositionHooks()}
      >

        {/* Map Rows */}
        { gridArray.map((row, i) => {
            return (
              <Grid container spacing={0}>

              {/* Map Cells */}
              { row.map((marbleColor, j) => {
                  return (
                    <Grid item
                      onPointerDown={(event) => selectSource(event, i, j)}
                      onPointerUp={(event) => selectDestination(event, i, j)}
                    >
                      <Paper square sx={{p: 0.5, m: 0.1}}>
                        <Marble color={marbleColor} size={marbleSize} />
                      </Paper>
                    </Grid>
                  )
                })}

              </Grid>
            );
          })}

      </Grid>

      {/* TODO: add effect listener so that multiple alerts are displayed */}
      { alert && <MessageStack {...alert} /> }
    </>
  );
}

import React, { useState, useEffect } from 'react';

import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import { AlertColor } from '@mui/material/Alert';

// dialog imports
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Button from '@mui/material/Button';

import { Marble } from './Marble';
import { MessageStack } from './MessageStack';
import { parseGridString, callAPI, isErrorResponse } from '../../utils';

// define radius of each marble
const marbleSize = 50;

type GameBoardProps = {
  playerID: string;
  gameID: string;
  setDisplayGameBoard: (b: boolean) => void;
}

type ScoreBoard = {
  playerMarbleColor: string;
  playerRedCaptured: number;
  opponentRedCaptured: number;
}

export function GameBoard({ playerID, gameID, setDisplayGameBoard }: GameBoardProps) {
  /* ------------------------------ State Hooks ------------------------------ */
  // message state hooks
  const [alertMessage, setAlertMessage] = useState<{severity: AlertColor; message: string} | null>(null);
  const [winner, setWinner] = useState<string | null>(null);

  // move state hooks
  const [sourceCoords, setSourceCoords] = useState<number[] | null>(null);
  const [sourceTargetData, setSourceTargetData] = useState<number[] | null>(null);

  // board state hooks
  const [boardState, setBoardState] = useState<string>(' '.repeat(49));
  const [scoreBoard, setScoreBoard] = useState<ScoreBoard | null>(null);
  const [turnTracker, setTurnTracker] = useState(0);


  /* ------------------------------ Effect Hooks ------------------------------ */
  // get the board state on page load and on every new turn
  useEffect(() => {
    const abortController = new AbortController();
    void async function getGameData() {
      try {
        const gameData = await callAPI.getGame(gameID);
        setBoardState(gameData.game_state.board.grid);

        // get data for the score board
        let [marbleColor, playerRed, opponentRed] = ['', 0, 0];
        for (const id of gameData.player_ids) {
          if (id === playerID) {
            marbleColor = gameData['game_state']['players'][id]['color'];
            playerRed = gameData['game_state']['players'][id]['red_marbles_captured'];
          } else {
            opponentRed = gameData['game_state']['players'][id]['red_marbles_captured'];
          }
        }
        setScoreBoard({
          playerMarbleColor: marbleColor === 'B' ? 'Black' : 'White',
          playerRedCaptured: playerRed,
          opponentRedCaptured: opponentRed,
        });

        // check if there's a winner
        if (gameData.game_state.winner !== null) {
          setWinner(gameData.game_state.winner);
        }
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


  /* ------------------------------ Event Handlers ------------------------------ */
  const resetPositionHooks = () => {
    setSourceCoords(null);
    setSourceTargetData(null);
  }

  const selectSource = (event: React.PointerEvent, rowCoord: number, colCoord: number) => {
    event.preventDefault();
    setSourceCoords([rowCoord, colCoord]);
    setSourceTargetData([event.pointerId, event.clientX, event.clientY]);
  }

  const selectDestination = async (event: React.PointerEvent, rowCoord: number, colCoord: number) => {
    event.preventDefault();

    // if the source wasn't successfully captured, reset the state hooks
    if (sourceCoords === null || sourceTargetData === null) {
      console.warn('source coordinates were not captured');
      resetPositionHooks();
      return;
    }

    // ignore multi-touch events
    if (event.pointerType !== 'mouse' && event.pointerId !== sourceTargetData[0]) {
      return;
    }

    /**
     * At this point, we'll need to treat mouse events different from touch/stylus events. The latter type
     * will only fire on the originating element, even if the pointer has since moved onto a different one.
     * A workaround for this is to use the pointer's client coordinates to guess the intended direction of
     * movement; while this isn't as precise as using the grid coordinates, it should be good enough.
     */
    let deltaRow = Math.round(event.pointerType === 'mouse'
      ? rowCoord - sourceCoords[0]
      : event.clientY - sourceTargetData[2]  // y -> row
    );
    let deltaCol = Math.round(
      event.pointerType === 'mouse'
      ? colCoord - sourceCoords[1]
      : event.clientX - sourceTargetData[1] // x -> col
    );

    // check for invalid states (i.e., the marble was moved diagonally)
    const invalid = event.pointerType === 'mouse'
      ? Math.abs(deltaRow) > 0 && Math.abs(deltaCol) > 0
      : Math.abs(Math.abs(deltaRow) - Math.abs(deltaCol)) < 40
    if (invalid) {
      setAlertMessage({
        severity:'warning', message:'Please swipe vertically or horizontally and at least one square over'
      });
      resetPositionHooks();
      return;
    }

    // check whether the marble was moved at all
    if (deltaRow === 0 && deltaCol === 0) {
      console.log('not moved')
      resetPositionHooks();
      return;
    }

    // if this isn't a mouse event, discard the smaller coordinate delta to determine the direction of movement
    if (event.pointerType !== 'mouse') {
      if (Math.abs(deltaRow) > Math.abs(deltaCol)) {
        deltaCol = 0;
      } else {
        deltaRow = 0;
      }
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
      let time = performance.now();  // capture the time so we can insert a small delay for updating the board
      const moveResult = await callAPI.move(playerID as string, gameID, sourceCoords[0], sourceCoords[1], direction);
      time = time !== undefined ? performance.now() - time : 1000;  // in case there was an issue capturing start time
      
      if (!moveResult.move_successful) {
        // alert the user that the move failed
        setAlertMessage({ severity:'info', message:'The proposed move was invalid' });
      } else {
        // increment the turnTracker (after a short delay for ux) to trigger effect listener
        setTimeout( () => {
          setTurnTracker(turnTracker + 1);
        }, time > 500 ? 500 - time : 0)
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


  /* ------------------------------ Scoreboard ------------------------------ */
  const ScoreBoard = () => {
    if (scoreBoard === null) {
      return null;
    }

    return (
      <Container maxWidth="xs" sx={{ my: 3 }}>
        <Paper sx={{ border:1 }}>
          <Box
            sx={{
              mt: 0.5,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
           }}
          >
            <Typography variant="body2">
              {`Your marble color: ${scoreBoard.playerMarbleColor}`}
            </Typography>
          </Box>
          <Box
            sx={{
              mt: 0,
              mb: 0.5,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
           }}
          >
            <Typography variant="body2">
              {`Red marbles captured: ${scoreBoard.playerRedCaptured}–${scoreBoard.opponentRedCaptured}`}
            </Typography>
          </Box>
        </Paper>
      </Container>
    );
  }


  /* ------------------------------ Redirect Dialog ------------------------------ */
  const RedirectDialog = () => {
    setTimeout( () => {}, 1000);
    return(
      <Dialog
        open={true}
        onClose={() => setDisplayGameBoard(false)}
      >
        <DialogTitle>The game has ended</DialogTitle>
        <DialogContent sx={{ml: 1, py: 0}}>
          { winner === playerID ? '🎉 You won!' : '🤖 You lost'}
        </DialogContent>
        <DialogActions sx={{pt: 1}}>
          <Button onClick={() => setDisplayGameBoard(false)} autoFocus>
            Got it
          </Button>
        </DialogActions>
      </Dialog>
    );
  }

  /* ------------------------------ Game Board ------------------------------ */
  return (
    <>
      <Grid
        container
        spacing={0}
        direction="column"
        onPointerLeave={() => resetPositionHooks()}
      >

        {/* Map Rows */}
        { parseGridString(boardState).map((row, i) => {
            return (
              <Grid container wrap="nowrap" spacing={0}>

              {/* Map Cells */}
              { row.map((marbleColor, j) => {
                 return (
                   <Grid item
                     onPointerDown={(event) => selectSource(event, i, j)}
                     onPointerUp={(event) => selectDestination(event, i, j)}
                   >
                     <Paper
                       square
                       sx={{
                         p: 0.5,
                         m: 0.1,
                         '&:hover': {
                           backgroundColor: 'lightgrey'
                         }
                       }}>
                       <Marble color={marbleColor} size={marbleSize} />
                     </Paper>
                   </Grid>
                 )
                })}

              </Grid>
            );
          })}

      </Grid>

      { scoreBoard && <ScoreBoard /> }
      { winner && <RedirectDialog /> }
      { alertMessage && <MessageStack {...alertMessage} setAlert={setAlertMessage} /> }
    </>
  );
}

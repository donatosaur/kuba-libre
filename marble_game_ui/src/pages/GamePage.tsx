import React, { useState, useEffect } from 'react';

import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableFooter from '@mui/material/TableFooter';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import IconButton from '@mui/material/IconButton';
import AddCircleOutlineOutlinedIcon from '@mui/icons-material/AddCircleOutlineOutlined';
import PlayCircleOutlineOutlinedIcon from '@mui/icons-material/PlayCircleOutlineOutlined';
import ArrowBackIosOutlinedIcon from '@mui/icons-material/ArrowBackIosOutlined';

import { useAuth0 } from '@auth0/auth0-react';
import { callAPI, isErrorResponse, GameResponse } from '../utils';
import { SwipeableTabs, GameBoard } from '../components';

// set the claims key whose value is the playerID
const key = "http://database_id"

export function GamePage() {
  const { isAuthenticated, getIdTokenClaims } = useAuth0();
  const [playerID, setPlayerID] = useState<string | null>(null);
  const [currentGames, setCurrentGames] = useState<GameResponse[]>([]);
  const [completedGames, setCompletedGames] = useState<GameResponse[]>([]);
  const [displayGameBoard, setDisplayGameBoard] = useState(false);
  const [gameID, setGameID] = useState<string | null>(null);

  useEffect( () => {
    void async function getPlayerID() {
      if (!isAuthenticated) {
        console.log('User is not authenticated.');
        return;
      }
    const claims = await getIdTokenClaims();
    if (!Boolean(claims[key])) {
        console.log(`Error: missing claims key=${key}`);
        return;
    }
    setPlayerID(claims[key]);
    }();
    // eslint-disable-next-line
  }, [isAuthenticated, playerID]);

  // get the user's games
  useEffect( () => {
    if (playerID === null || displayGameBoard) {
      return;
    }
    const abortController = new AbortController();
    void async function getGames() {
      try {
        const currentResponse = await callAPI.getUserCurrentGames(playerID, 0, 100);
        setCurrentGames(currentResponse);
        const completedResponse = await callAPI.getUserCompletedGames(playerID, 0, 100);
        setCompletedGames(completedResponse);
      } catch (err) {
        if (isErrorResponse(err)) {
          for (const errorDetail of err.detail) {
            console.log(`Error: ${errorDetail.type}: ${errorDetail.msg}`);
          }
        }
        return;
      }
    }();
    return () => abortController.abort();
    // when displayGameBoard becomes false (e.g. the user tabs back to this page), refresh data
  }, [isAuthenticated, playerID, displayGameBoard]);

  const onCreateGame = async () => {
    if (playerID === null) {
      return;
    }
    try {
      // select a random marble color for the player
      const marbleColor = ['B', 'W'][Math.round(Math.random())];
      const gameResponse = await callAPI.createOnePlayerGame(playerID, marbleColor as 'B' | 'W');
      currentGames.push(gameResponse);
      setGameID(gameResponse._id);
      setDisplayGameBoard(true);
    } catch (err) {
      if (isErrorResponse(err)) {
        for (const errorDetail of err.detail) {
          console.log(`Error: ${errorDetail.type}: ${errorDetail.msg}`);
        }
        return;
      }
    }
  }

  const onReturn = (event: React.MouseEvent) => {
    event.preventDefault();
    setGameID(null);
    setDisplayGameBoard(false);
  }

  const GameTable = (headerData: string[], rowData: GameResponse[]) => {
    return (
      <TableContainer component={Paper}>
      <Table sx={{ minWidth: 650 }} aria-label="table of user's games">

        <TableHead>
          <TableRow>
            {headerData.map((columnTitle) => {
              return (
                <TableCell align="center">
                  <Typography variant="body1" align="inherit">
                    {columnTitle}
                  </Typography>
                </TableCell>
              );
            })}
          </TableRow>
        </TableHead>

        <TableBody>
          {rowData.map((gameData) => {
            // determine whose turn it is (or who won the game)
            let currentTurnOrWinner: string;
            if (gameData['completed']) {
              currentTurnOrWinner = gameData['game_state']['winner'] === playerID
                ? 'You'
                : `Opponent`;
            } else {
              currentTurnOrWinner = gameData['game_state']['current_turn'] === playerID
                ? 'Your Turn'
                : `Opponent's Turn`;
            }

            const marbleColor = gameData['game_state']['players'][playerID as string]['color'] === 'B'
              ? 'Black'   // 'B' marble
              : 'White';  // 'W' marble

            // determine which score belongs to which player
            let [playerRed, playerOpp, opponentRed, opponentOpp] = [0, 0, 0, 0];
            for (const id of gameData.player_ids) {
              if (id === playerID) {
                playerRed = gameData['game_state']['players'][id]['red_marbles_captured'];
                playerOpp = gameData['game_state']['players'][id]['opponent_marbles_captured'];
              } else {
                opponentRed = gameData['game_state']['players'][id]['red_marbles_captured'];
                opponentOpp = gameData['game_state']['players'][id]['opponent_marbles_captured'];
              }
            }
            const score = `Red: ${playerRed}–${opponentRed}\nOther: ${playerOpp}–${opponentOpp}`

            return (
              <TableRow
                key={gameData._id}
                // sx={{'&:last-child td, &:last-child th': {border: 0}}}  // disable border on last element
              >
                <TableCell align="center">{gameData._id}</TableCell>
                <TableCell align="center">{marbleColor}</TableCell>
                <TableCell align="center">{currentTurnOrWinner}</TableCell>
                <TableCell align="center">{score}</TableCell>
                <TableCell align="right">
                  <IconButton
                    size="large"
                    edge="start"
                    color="inherit"
                    aria-label="play this game"
                    sx={{ mr: 2 }}
                    onClick={(event) => {
                      event.preventDefault();
                      setGameID(gameData._id);
                      setDisplayGameBoard(true);
                    }}
                >
                <PlayCircleOutlineOutlinedIcon />
              </IconButton>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>

        <TableFooter>
          <TableRow>
            <TableCell />
            <TableCell />
            <TableCell />
            <TableCell />

            <TableCell align="right">
              <IconButton
              size="large"
              edge="start"
              color="inherit"
              aria-label="play new game"
              sx={{ mr: 2 }}
              onClick={onCreateGame}
              >
                <AddCircleOutlineOutlinedIcon />
              </IconButton>
            </TableCell>
          </TableRow>
        </TableFooter>

      </Table>
    </TableContainer>
    );
  }

  // construct tables to pass to tabs
  const currentHeaders = ['Game ID', 'Your Marble Color', 'Current Turn', 'Current Score', '']
  const completedHeaders = ['Game ID', 'Your Marble Color', 'Winner', 'Score', '']
  const currentGameTable = GameTable(currentHeaders, currentGames);
  const completedGameTable = GameTable(completedHeaders, completedGames);

  return (
    <>
      {!displayGameBoard &&
        <SwipeableTabs
          tabLabels={['Current Games', 'Completed Games']}
          tabChildren={[currentGameTable, completedGameTable]}
        />
      }

      {displayGameBoard && playerID && gameID &&
        <Container component="main" maxWidth="lg">

            <IconButton
              size="medium"
              edge="start"
              color="inherit"
              aria-label="play new game"
              sx={{ mr: 2 }}
              onClick={onReturn}
              >

                <ArrowBackIosOutlinedIcon />
                &nbsp;&nbsp;Return to table
              </IconButton>
          <GameBoard playerID={playerID} gameID={gameID} />
        </Container>
      }
    </>
  );
}

import * as React from 'react';

import Container from '@mui/material/Container'
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List'
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';

export function InstructionsPage() {
  return (
    <>
      <Container sx={{mt: '2vh'}}>
        <Typography variant="h3" align="center" gutterBottom>
          Instructions
        </Typography>

        <Grid container>
          <List sx={{mb: '1em', mx: '20vw'}}>
             <ListItem>
               <ListItemText
                 primary='Objective'
                 secondary={
                   'A player wins by pushing off seven neutral red marbles, by pushing off all of their ' +
                   'opponents\' marbles, or by locking their opponent out of the ability to make a move.'
                 }
               />
             </ListItem>
             <ListItem>
               <ListItemText
                 primary='How to Make a Move'
                 secondary={
                   'Click (or press) and drag the marble you want to move in the direction that you want to move it.'
                 }
               />
             </ListItem>
             <ListItem>
               <ListItemText
                 primary='Rules of Movement'
                 secondary={
                   'To move a marble, there must be an empty space (including the edge of the board) opposite the ' +
                   'direction of movement.'
                 }
               />
             </ListItem>
             <ListItem>
               <ListItemText
                 primary='Ko Rule'
                 secondary={
                   'You may not move a marble such that it undoes your opponents\' last move ' +
                   'and recreates the board position that existed when their turn began.'
                 }
               />
             </ListItem>
             <ListItem>
               <ListItemText
                 primary='Directions of Movement'
                 secondary={
                   'Vertical moves are forward (up) / backward (down). Horizontal moves are left / right.'
                 }
               />
             </ListItem>
          </List>
        </Grid>
      </Container>
    </>
  )
}

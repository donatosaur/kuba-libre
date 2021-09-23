import * as React from 'react';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';

export function HomePage() {
  return (
    <>
      <Container component="main" maxWidth="sm">
        <Typography variant="h3" align="center" gutterBottom>
          Welcome!
        </Typography>

        <Typography variant="body1" align="center" gutterBottom>
          Welcome Text Placeholder
        </Typography>
      </Container>
    </>
  )
}

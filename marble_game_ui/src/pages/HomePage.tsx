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

        <Typography variant="body1" align="left" gutterBottom>
          This is a live demo site for KubaLibre. To get started, simply use the login
          button above to log in or create an account.
        </Typography>
      </Container>
    </>
  )
}

import { useEffect } from 'react';
import { useHistory } from 'react-router-dom';

import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';


export function ErrorPage() {
  const history = useHistory();

  useEffect(() => {
    setTimeout(() => history.push('/'), 2000)
  })

  return(
    <>
      <Container maxWidth="sm" sx={{mt: '2vh'}}>
        <Typography variant="h5" align="center" gutterBottom>
          Error 404 Page Not Found
        </Typography>

        <Typography variant="body1" align="center" gutterBottom>
          Redirecting...
        </Typography>
      </Container>
    </>
  )
}

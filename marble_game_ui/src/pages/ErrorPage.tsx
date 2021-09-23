import { useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';


export function ErrorPage() {
  const history = useHistory();

  useEffect(() => {
    setTimeout(() => history.push('/'), 2000)
  })

  return(
    <>
      <Container maxWidth="sm">
        <Box sx ={{mt: 2}}>
          <Typography variant="h4" align="center">Error 404: Page Not Found</Typography>
        </Box>
        <Box sx ={{mt: 2}}>
          <Typography variant="h6" align="center">Redirecting...</Typography>
        </Box>
      </Container>
    </>
  )
}

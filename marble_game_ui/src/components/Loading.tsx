import CircularProgress from '@mui/material/CircularProgress';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Backdrop from '@mui/material/Backdrop'

/**
 * Creates a CircularProgress spinner to indicate that a page or component is loading. Dims the viewport
 * while displayed.
 *
 * @constructor
 */
export function Loading() {
  return (
    // <Box
    // sx={{
    //   marginTop: 8,
    //   display: 'flex',
    //   flexDirection: 'column',
    //   alignItems: 'center',
    //   justifyContent: 'center',
    // }}
    // >
    //   <Container maxWidth="xs">
    <div>
      <Backdrop open={true}>
        <CircularProgress color="secondary" />
      </Backdrop>
    </div>
    //       </Container>
    // </Box>

  );
}

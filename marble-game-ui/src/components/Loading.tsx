import CircularProgress from '@mui/material/CircularProgress';
import Backdrop from '@mui/material/Backdrop'

/**
 * Creates a CircularProgress spinner to indicate that a page or component is loading. Dims the viewport
 * while displayed.
 *
 * @constructor
 */
export function Loading() {
  return (
    <div>
      <Backdrop open={true}>
        <CircularProgress color="secondary" />
      </Backdrop>
    </div>
  );
}

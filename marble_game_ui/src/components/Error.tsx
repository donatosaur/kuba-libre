import React, { useState } from 'react';

import Alert from '@mui/material/Alert';
import Snackbar from "@mui/material/Snackbar";

/**
 * Creates a snackbar with an error alert, centered at the bottom of the viewport.
 *
 * @param message error message to be displayed
 * @constructor
 */
export function Error({ message }: { message: string }) {
  const [open, setOpen] = useState(true);

  const handleClose = (event?: React.SyntheticEvent | React.MouseEvent, reason?: string) => {
    //  keep the alert open if the user clicks outside of the alert box
    if (reason === 'clickaway') {
      return;
    }

    setOpen(false);
  };

  return (
    <Snackbar
      anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      open={open}
      autoHideDuration={8000}
      onClose={handleClose}
    >
      <Alert onClose={handleClose} severity="error" sx={{ width: '100%' }}>
        {message}
      </Alert>
    </Snackbar>
  );
}

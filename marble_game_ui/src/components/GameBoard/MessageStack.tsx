import React, { useState } from 'react';
import Alert,{ AlertColor }  from '@mui/material/Alert';
import Snackbar from '@mui/material/Snackbar';

export function MessageStack({ severity, message }: { severity: AlertColor, message: string }) {
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
      anchorOrigin={{vertical: 'bottom', horizontal: 'center'}}
      open={open}
      autoHideDuration={6000}
      onClose={handleClose}
    >
      <Alert onClose={handleClose} severity={severity} sx={{width: '100%'}}>
        {message}
      </Alert>
    </Snackbar>
  );
}

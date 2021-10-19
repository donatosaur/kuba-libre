import React, { useState } from 'react';
import Alert,{ AlertColor }  from '@mui/material/Alert';
import Snackbar from '@mui/material/Snackbar';

// type definitions
type MessageStackProps = {
  severity: AlertColor;
  message: string;
  setAlert: (p: null) => void; // to make alert null on close
}

export function MessageStack({ severity, message, setAlert }: MessageStackProps) {
  const [open, setOpen] = useState(true);

  const handleClose = (event?: React.SyntheticEvent | React.MouseEvent, reason?: string) => {
    //  keep the alert open if the user clicks outside of the alert box
    if (reason === 'clickaway') {
      return;
    }
    setAlert(null);
    setOpen(false);
  };

  return (
    <Snackbar
      anchorOrigin={{vertical: 'top', horizontal: 'center'}}
      open={open}
      autoHideDuration={6000}
      onClose={handleClose}
      sx={{
        mt: 1,
      }}
    >
      <Alert onClose={handleClose} severity={severity} sx={{width: '100%'}}>
        {message}
      </Alert>
    </Snackbar>
  );
}

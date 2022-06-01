import { createTheme } from '@mui/material/styles';

// defines default styles for the app
const theme = createTheme({
  palette: {
    primary: {
      main: '#37474f',
    },
    secondary: {
      main: '#F9AA33',
    },
    error: {
      main: '#FF1744',
    },
  },
  components: {
    MuiGrid: {
      styleOverrides: {
        root: {
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'center',
        }
      }
    },
  },
});

export default theme;

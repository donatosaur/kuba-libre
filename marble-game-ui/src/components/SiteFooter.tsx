import { Link as RouterLink } from 'react-router-dom';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Link from '@mui/material/Link';

/**
 * Creates a page footer
 *
 * @constructor
 */
export function SiteFooter() {
  return (
    <Box sx={{ flexGrow: 1 }}>

      {/* this box is here to prevent the AppBar from being rendered over page elements */}
      <Box component="div" sx={{ display: 'block', pb: '6em' }} />

      <AppBar
        position="fixed"
        color="primary"
        sx={{
          top: 'auto',
          bottom: 0,
          py: 3,
          px: 2,
          backgroundColor: (theme) =>
            theme.palette.mode === 'light'
              ? theme.palette.grey[200]
              : theme.palette.grey[800],
        }}
      >

        <Container maxWidth="md">
          {/* Copyright */}
          <Typography variant="body2" color="text.secondary" align="center">
            {`Source code Ⓒ 2021 Donato Quartuccia. See `}
            <Link href="https://github.com/donatosaur/marble-game/blob/main/LICENSE">
              {`license`}
            </Link>
            {` for details. This site is for demonstration only.`}
          </Typography>

          {/* Disclaimer */}

          <Typography variant="body2" color="text.secondary" align="center">

            <Link component={RouterLink} to="/terms">
              {`Terms of Use`}
            </Link>
            {' | '}
            <Link component={RouterLink} to="/privacy">
              {`Privacy Policy`}
            </Link>
          </Typography>
        </Container>

      </AppBar>
    </Box>
  );
}

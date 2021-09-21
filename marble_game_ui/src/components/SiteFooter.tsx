import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';

/**
 * Creates a page footer
 *
 * @constructor
 */
export function SiteFooter() {
  return (
    <Box sx = {{mt: 2}}>
      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: 'auto',
          backgroundColor: (theme) =>
            theme.palette.mode === 'light'
              ? theme.palette.grey[200]
              : theme.palette.grey[800],
        }}
      >
        <Container maxWidth="sm">

          {/* Copyright */}
          <Typography variant="body1" align="center">
            Copyright Placeholder
          </Typography>

          {/* Disclaimer */}
          <Typography variant="body2" color="text.secondary" align="center">
            This is an unsecure development build. For demonstration and education purposes only.
          </Typography>

        </Container>
      </Box>
    </Box>
  );
}

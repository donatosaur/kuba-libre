import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import { useAuth0 } from "@auth0/auth0-react";
import useMediaQuery from '@mui/material/useMediaQuery';

// component imports
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import SwipeableDrawer from '@mui/material/SwipeableDrawer';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import MenuIcon from '@mui/icons-material/Menu';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Divider from '@mui/material/Divider'

// icon imports
import AccountCircle from "@mui/icons-material/AccountCircle";
import GridOnOutlinedIcon from '@mui/icons-material/GridOnOutlined';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';


type SiteHeaderProps = {
  drawerWidth: number;
  headerText: string;
}

/**
 * Creates a site header with a swipeable navigation drawer (toggled via menu button or swipe), login via login button
 * (displayed if user is not authenticated) and logout via account menu (displayed if user is authenticated).
 *
 * @param drawerWidth width of the swipeable navigation drawer
 * @param headerText text to be displayed on the header appbar
 * @constructor
 */
export function SiteHeader({ drawerWidth, headerText }: SiteHeaderProps) {
  const { isAuthenticated, loginWithRedirect, logout } = useAuth0();
  const history = useHistory();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [drawerOpen, setDrawerOpen] = React.useState(false);

  // iOS swipe back action conflicts with drawer discovery
  const iOS = typeof navigator !== 'undefined' && /iPad|iPhone|iPod/.test(navigator.userAgent);
  const isMobileDevice = useMediaQuery('(max-width:768px)');

  // event handlers
  const toggleDrawer = (open: boolean) =>
    (event: React.KeyboardEvent | React.MouseEvent) => {
      // accessibility: ignore tab & shift key presses used for navigation
      if (
        event?.type === 'keydown' && (
          (event as React.KeyboardEvent).key === 'Tab' ||
          (event as React.KeyboardEvent).key === 'Shift')
      ) {
        return;
      }

      setDrawerOpen(open);
    };
    
  const handleLogout = () => {
    setAnchorEl(null);
    logout({ returnTo: window.location.origin });
  }

  // JSX element
  return (
    <Box sx={{ flexGrow: 1 }}>
       <AppBar position="sticky" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
            onClick={toggleDrawer(!drawerOpen)}
          >
            <MenuIcon />
          </IconButton>

          {/* Title */}
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {headerText}
          </Typography>

          {/* Account Popup Menu (authenticated) & Login Button (not authenticated) */}
          {isAuthenticated
            ? <Box>
                <IconButton
                  size="large"
                  aria-label="account menu with logout"
                  aria-controls="menu-appbar"
                  aria-haspopup="true"
                  onClick={(event: React.MouseEvent<HTMLElement>) => setAnchorEl(event.currentTarget)}
                  color="inherit"
                >
                  <AccountCircle />
                </IconButton>
                <Menu
                  id="menu-appbar"
                  anchorEl={anchorEl}
                  anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'right',
                  }}
                  keepMounted
                  transformOrigin={{
                    vertical: 'top',
                    horizontal: 'right',
                  }}
                  open={Boolean(anchorEl)}
                  onClose={() => setAnchorEl(null)}
                >
                  <MenuItem onClick={handleLogout}>Log Out</MenuItem>
                </Menu>
              </Box>
            : <Button color="inherit" onClick={loginWithRedirect}>Login</Button>
          }
          
        </Toolbar>
      </AppBar>

      <SwipeableDrawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
        }}
        disableBackdropTransition={!iOS || !isMobileDevice}
        disableDiscovery={iOS}
        anchor="left"
        open={drawerOpen}
        onClose={toggleDrawer(false)}
        onOpen={toggleDrawer(true)}
      >
        <Toolbar />
        <Box
          sx={{ width: drawerWidth, overflow: 'auto' }}
          role="presentation"
          onClick={toggleDrawer(false)}
          onKeyDown={toggleDrawer(false)}
        >
          {/* Drawer Menu Items */}
          <List>
            <ListItem button key="Instructions" onClick={() => history.push('/instructions')}>
              <ListItemIcon>
                 <HelpOutlineIcon />
              </ListItemIcon>
              <ListItemText primary="Instructions" />
            </ListItem>
            <Divider />
            <ListItem button key="Games" onClick={() => history.push('/games')}>
              <ListItemIcon>
                 <GridOnOutlinedIcon />
              </ListItemIcon>
              <ListItemText primary="Play Kuba" />
            </ListItem>
            <Divider />
          </List>

        </Box>
      </SwipeableDrawer>

    </Box>
  );
}

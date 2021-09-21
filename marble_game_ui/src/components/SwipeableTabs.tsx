import React from 'react';
import SwipeableViews from 'react-swipeable-views';
import AppBar from '@mui/material/AppBar';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Box from '@mui/material/Box';

type TabPanelProps = {
  children: React.ReactNode;
  index: number;
  value: number;
}

type SwipeableTabProps = {
  tabLabels: string[];
  tabChildren: React.ReactNode[];
}

/**
 * Creates a full-width tab panel, with tabs that can be navigated by swiping or clicking the tab label.
 *
 * Pass labels for each tab as {@link tabLabels} and the content that should be displayed as {@link tabChildren}.
 * Tabs are rendered in order and arrays must be equal in length. *
 * @constructor
 */
export function SwipeableTabs({ tabLabels, tabChildren }: SwipeableTabProps) {
  const [value, setValue] = React.useState(0);

  // ensure tab prop arrays have the same length
  if (tabLabels.length !== tabChildren.length) {
    console.log('Error: tabLabels and tabChildren should have the same length');
    return (<></>);
  }

  const a11yProps = (index: number) => {
    return {
      id: `full-width-tab-${index}`,
      'aria-controls': `full-width-tabpanel-${index}`,
    };
  }
  const TabPanel = ({ children, value, index }: TabPanelProps) => {
    return (
      <div
        role="tabpanel"
        hidden={value !== index}
        id={`full-width-tabpanel-${index}`}
        aria-labelledby={`full-width-tab-${index}`}
      >
        {value === index && (
          <Box sx={{ p: 3 }}>
            {children}
          </Box>
        )}
      </div>
    );
  }

  return (
    <Box sx={{ bgcolor: 'background.paper', width: 500 }}>
      <AppBar position="static">
        <Tabs
          value={value}
          onChange={(event: React.SyntheticEvent, newValue: number) => setValue(newValue)}
          indicatorColor="secondary"
          textColor="inherit"
          variant="fullWidth"
          aria-label="tabs"
        >
          {tabLabels.map((label, i) =>
            <Tab label={label} {...a11yProps(i)} />
          )}
        </Tabs>
      </AppBar>
      <SwipeableViews
        index={value}
        onChangeIndex={(index: number) => setValue(index)}
      >
        {tabChildren.map((children, i) =>
          <TabPanel value={value} index={i}>
            {children}
          </TabPanel>
        )}
      </SwipeableViews>
    </Box>
  );
}

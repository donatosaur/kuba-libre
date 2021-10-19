import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';

import { Error, ProtectedRoute, Loading, SiteHeader, SiteFooter } from './components';
import { ErrorPage, HomePage, GamePage, ProfilePage } from './pages';

export default function App() {
  const { isLoading, error } = useAuth0();

  if (isLoading) {
    return <Loading />;
  }

  return (
    <Router>
        <SiteHeader drawerWidth={220} headerText={'KubaLibre'}/>

        {error && <Error message={error.message} />}

        <Switch>
          <Route exact path="/" component={HomePage} />
          <ProtectedRoute exact path="/games/" component={GamePage} />
          <ProtectedRoute exact path="/profile/" component={ProfilePage} />
          <Route path="*" component={ErrorPage}/>
        </Switch>

        <SiteFooter />
    </Router>
  );
}

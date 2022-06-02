import React from 'react';
import { Route } from 'react-router-dom';
import { withAuthenticationRequired } from '@auth0/auth0-react';
import { Loading } from './Loading'

/**
 * A route component that enforces authentication before loading the specified component. Automatically
 * redirects the user to the login page if they are not authenticated.
 *
 * @constructor
 */
export const ProtectedRoute = ({ component, ...rest }: React.PropsWithChildren<any>) => (
  <Route
    render={(props) => {
      let Component = withAuthenticationRequired(component, {
        onRedirecting: () => <Loading />,
      });
      return <Component {...props} />;
    }}
    {...rest}
  />
);

import React, { useState } from 'react';
import { BrowserRouter as Router, Route } from 'react-router-dom';
// page and component imports
import logo from './logo.svg';
import HomePage from './pages/HomePage'

// import pages and router


function App() {


  return (
    <div className="App">
      <Router>
        <header className='App-header'>
          <Route path="/" exact>
            <HomePage/>

          </Route>
          <img src={logo} className="App-logo" alt="logo" />
          <p>
            Edit <code>src/App.tsx</code> and save to reload.
          </p>
        </header>
     </Router>
    </div>
  );
}

export default App;
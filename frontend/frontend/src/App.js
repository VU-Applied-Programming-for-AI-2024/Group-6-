import React from 'react';
import { BrowserRouter , Routes, Route } from 'react-router-dom';
import Navbar from './NavBar';
import './App.css'; // Importing styles for the App component
import './NavBar.css'; // Importing styles for the Navbar component
import Favourites from './Favourites'; 
import "./Favourites.css"; // Importing styles for the Favourites component
import "./Starting11.css"; // Importing styles for the StartingEleven component
import StartingEleven from './Starting11'; 
import Home from './Home';
import NotFound from './NotFound';
import "./Home.css"; // Importing styles for the Home component
import Login from './Login';
import { useState } from 'react';
import PlayerDetails from './playerDetails';
import LatestNews from './LatestNews';

/**
 * Main component for the application.
 * Manages user state, selected player, and favorite players.
 */
function App() {
  const [user, setUser] = useState(null); // State to manage user authentication
  const [selectedPlayer, setSelectedPlayer] = useState(null); // State to track selected player
  const [favorites, setFavorites] = useState([]); // State to track favorite players
  const [startingEleven, setStartingEleven] = useState({});
  
  return (
    <>
    <BrowserRouter>
        <Navbar user = {user} setUser = {setUser}/> {/* Navbar component */}
        <Routes>
          {/* Route for the home page */}
          <Route path="/" element={
            <Home setSelectedPlayer={setSelectedPlayer}
            user={user} favorites = {favorites} setFavorites = {setFavorites}/>
            } />
          
          {/* Route for the favorites page */}
          <Route path="/favourites" element={
            <Favourites favorites = {favorites} setFavorites={setFavorites} user={user} setSelectedPlayer={setSelectedPlayer} startingEleven={startingEleven}/>
            } />
        
          {/* Route for the starting eleven page */}
          <Route path="/startingeleven" element={
            <StartingEleven user={user} setStartingEleven={setStartingEleven}/>
            } />
          
          

          {/* Route for the login page */}
          <Route path="/login" element={
            <Login setUser = {setUser} />
            } />

          
          

          {/* Route for any other paths */}
          <Route path = "*" element={
              <NotFound />
              } />

          {/* Route for displaying player details */}
          <Route path="/player/:playerId" element={
            <PlayerDetails player={selectedPlayer} setSelectedPlayer={setSelectedPlayer}/>
            } />
        </Routes>
        
    </BrowserRouter>
    </>
  );
}

export default App;

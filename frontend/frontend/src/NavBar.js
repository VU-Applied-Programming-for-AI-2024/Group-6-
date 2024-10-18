import React from 'react';
import { Link } from 'react-router-dom';
import { useEffect } from 'react';

const Navbar = ({ user, setUser }) => {
  // Function to handle user logout
  const handleLogout = () => {
    setUser(null);
  };
  
  return (
    <nav className="navbar">
      <h1 className="logo">Football Gladiators</h1>
      <ul>
        <li><Link to="/">Home</Link></li>
        <li><Link to="/favourites">Favourites</Link></li>
        <li><Link to="/startingeleven">Starting 11</Link></li>
        
        {user ? (
          <>
            <li className="profile">Welcome, {user.username}</li>
            <li className = "logout"><button onClick={handleLogout}>Logout</button></li>
          </>
        ) : (
          <li><Link to="/login" className="login">Login/Register</Link></li>
        )}
      </ul>
    </nav>
  );
};

export default Navbar;
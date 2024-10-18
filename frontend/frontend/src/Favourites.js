import React, { useState, useEffect } from 'react';
import './Favourites.css';
import { useLocation, useNavigate } from 'react-router-dom';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';

const Favourites = ({ user, setSelectedPlayer, startingEleven }) => {
  const [favorites, setFavorites] = useState([]);
  const location = useLocation();
  const navigate = useNavigate();
  const fromStarting11 = location.state?.from === 'startingeleven';
  const position = location.state?.position;

  // Fetch favorites data on component mount
  useEffect(() => {
    if (user) {
      fetch(`http://127.0.0.1:5000/api/users/${user.username}/players`)
        .then(response => response.json())
        .then(data => setFavorites(data))
        .catch(error => console.error('Error fetching user favorites:', error));
    }
  }, [user]);

  // Function to handle navigation to more details page
  const handleMoreDetails = (player) => {
    setSelectedPlayer(player);
    navigate(`/player/${player.name}`, { state: { player, from: 'favourites' } });
  };

  // Function to add player to starting eleven
  const handleAddToTeam = (player_id) => {
    if (fromStarting11 && position) {
      fetch(`http://127.0.0.1:5000/api/startingeleven/${user.username}`)
        .then(response => response.json())
        .then(startingEleven => {
          const playerExists = startingEleven.some(player => player.player_id === player_id);
          if (playerExists) {
            alert('Player already in team');
          } else {
            fetch(`http://127.0.0.1:5000/api/startingeleven/${user.username}`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ position, player_id })
            })
            .then(response => response.json())
            .then(data => {
              if (data.message === 'Player added to starting eleven') {
                navigate('/startingeleven');
              }
            })
            .catch(error => console.error('Error adding player to starting eleven:', error));
          }
        })
        .catch(error => console.error('Error fetching starting eleven:', error));
    }
  };

  // Function to remove player from favorites
  const handleRemoveFromFavorites = async (name) => {
    if (!user) {
      alert("Please log in to remove players from favorites");
      return;
    }
    setFavorites(prevFavorites => prevFavorites.filter(player => player.name !== name));
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/users/${user.username}/favorite_players`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });
      if (response.ok) {
        console.log('Player removed from favorites');
      } else {
        console.error('Error removing player from favorites');
      }
    } catch (error) {
      console.error('Error during removing favorite:', error);
    }
  };

  // Render empty message if no user is logged in
  if (!user) {
    return <p className="empty-message">Please log in to view favorites.</p>;
  }

  const hasFavorites = favorites.length > 0;

  return (
    <div>
      {!hasFavorites && (
        <p className="empty-message">You currently have no favorites.</p>
      )}
      <div className="favourites-container">
        {hasFavorites && favorites.map((player) => (
          <div key={player.name} className="card">
            <IconButton>
              <DeleteIcon className="remove-from-favorites" onClick={() => handleRemoveFromFavorites(player.name)} />
            </IconButton>
            <div className="card-content">
              <h3>{player.name}</h3>
              <p><strong>Team:</strong> {player.team}</p>
              <p><strong>Position:</strong> {player.position}</p>
              <img className="player-image" src={player.img} alt={player.name} width="130" />
              <button className="add-to-team" onClick={() => handleMoreDetails(player)}>More Details</button>
              {fromStarting11 && (
                <button className="add-to-team" onClick={() => handleAddToTeam(player.player_id)}>Add to team</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Favourites;

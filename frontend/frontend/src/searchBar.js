import React, { useState,useEffect } from 'react';
import './searchBar.css';
import StarBorderIcon from '@mui/icons-material/StarBorder';
import SearchIcon from '@mui/icons-material/Search';
import StarIcon from '@mui/icons-material/Star';
import { useNavigate } from 'react-router-dom';

const SearchBar = ({ user, setSelectedPlayer, favorites, setFavorites }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const navigate = useNavigate();

  const handleInputChange = (event) => {
    setQuery(event.target.value);
  };
  useEffect(() => {
    // This effect will trigger a re-render if `favorites` updates
    setResults(prevResults => prevResults.map(player => {
      const isFavorite = favorites.some(fav => fav.name === player.name);
      return { ...player, isFavorite };
    }));
  }, [user, favorites]);

  const handleKeyPress = async (event) => {
    if (event.key === 'Enter') {
      const query = event.target.value;
      try {
        const response = await fetch(`http://127.0.0.1:5000/search?q=${query}`);
        const data = await response.json();

        console.log('Fetched data:', data); // Log the data structure

        if (data && Array.isArray(data) && data.length > 0) {
          const footballPlayers = data.map(player => ({
            position: player.position.split('/').pop() || 'Unknown Position',
            team: player.team.split('/').pop().replace(/_/g, ' ') || 'Unknown Team',
            name: player.name.replace(/_/g, ' ') || 'Unknown Player',
            market_value: player.marketValue || 'Not Available',
            nationality: player.nationality || 'Not Available',
            height: player.height || 'Not Available',
            img: player.img || 'No Image',
            birthDate: player.birth_date || 'Unknown Date',
            wage: player.wage || 'Not Available',
            potential: player.potential || 'Not Available',
            rating: player.rating || 'Not Available',
            description: player.description || 'No Description',
            foot: player.foot || 'Not Specified'
            
          }));

          setResults(footballPlayers);
          console.log('Search results:', footballPlayers);
        } else {
          console.error('No results found or invalid data structure');
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    }
  };

  const toggleFavorite = async (player) => {
    if (!user) {
      alert("Please log in to favorite players");
      return;
    }

    const isFavorite = favorites.some(fav => fav.name === player.name);

    if (isFavorite) {
      // Remove from favorites
      setFavorites(prevFavorites => prevFavorites.filter(fav => fav.name !== player.name));

      try {
        const response = await fetch(`http://127.0.0.1:5000/api/users/${user.username}/favorite_players`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ name: player.name }), // Use player_id for deletion
        });
        const data = await response.json();
        if (response.ok) {
          console.log('Player removed from favorites:', data);
        } else {
          console.error('Error removing player from favorites:', data.message);
        }
      } catch (error) {
        console.error('Error during removing favorite:', error);
      }
    } else {
      // Add to favorites
      const playerData = {
        position: player.position.split('/').pop() || 'Unknown Position',
            team: player.team.split('/').pop().replace(/_/g, ' ') || 'Unknown Team',
            name: player.name.replace(/_/g, ' ') || 'Unknown Player',
            market_value: player.market_value || 'Not Available',
            nationality: player.nationality || 'Not Available',
            height: player.height || 'Not Available',
            img: player.img || 'No Image',
            birthDate: player.birthDate || 'Unknown Date',
            wage: player.wage || 'Not Available',
            potential: player.potential || 'Not Available',
            rating: player.rating || 'Not Available',
            description: player.description || 'No Description',
            foot: player.foot || 'Not Specified'
      };

      setFavorites(prevFavorites => [...prevFavorites, playerData]);
     
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/users/${user.username}/favorite_players`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(playerData),
        });
        
        const data = await response.json();
        if (response.ok) {
          console.log('Player added to favorites:', data);
        } else {
          console.error('Error adding player to favorites:', data.message);
        }
      } catch (error) {
        console.error('Error during adding favorite:', error);
      }
    }
  };

  // Function to navigate to the player's details page
  const handleMoreDetails = (player) => {
    setSelectedPlayer(player);
    navigate(`/player/${player.name}`, { state: { player, from: 'search' } }); // Adding state to pass the player
  };

  return (
    <div className="search-bar">
      <h1 className="bar-title">Search for your favourite players <SearchIcon style={{ fontSize: 28, verticalAlign: 'middle', marginLeft: '5px' }} /></h1>
      <input
        type="text"
        value={query}
        onChange={handleInputChange}
        onKeyDown={handleKeyPress}
        placeholder="Search players..."
      />
      <ul className="search-results">
        {results.map((player, index) => (
          <li key={index} className="result">
            <div className="player-info">
              <div>
                <strong>Name:</strong> {player.name}
              </div>
              <div>
                <strong>Team:</strong> {player.team}
              </div>
              <div>
                <strong>Position:</strong> {player.position}
              </div>
              <div>
                <strong>Rating:</strong> {player.rating}
              </div>
              <div>
                <strong>Potential:</strong> {player.potential}
              </div>
              <div>
                <strong>Foot:</strong> {player.foot}
              </div>
            </div>
            <div className="player-image">
              {player.img ? (
                <img src={player.img} width="100" alt={player.name} />
              ) : (
                <div>No image available</div>
              )}
            </div>
            <div className="player-actions">
              {player.isFavorite ? (
                <StarIcon onClick={() => toggleFavorite(player)} style={{ fontSize: 50 }} />
              ) : (
                <StarBorderIcon onClick={() => toggleFavorite(player)} style={{ fontSize: 50 }} />
              )}
              <button className="more-details" onClick={() => handleMoreDetails(player)}>More Details</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default SearchBar;

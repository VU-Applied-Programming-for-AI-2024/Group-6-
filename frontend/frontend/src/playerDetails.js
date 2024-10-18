import React from 'react';
import './playerDetails.css';
import { useLocation } from 'react-router-dom';
import { differenceInYears } from 'date-fns';

const PlayerDetails = () => {
  const location = useLocation();
  const player = location.state?.player || null;  // Get the player from state

  // Parse market value (handling millions and thousands)
  const parseMarketValue = (value) => {
    if (!value) return 0;
    const numValue = parseFloat(value.replace(/[^\d.]/g, ''));
    if (value.includes('M')) {
      return numValue * 1_000_000;  // Million
    } else if (value.includes('K')) {
      return numValue * 1_000;      // Thousand
    }
    return numValue;  // No suffix (assumed as just a number)
  };

  const playerPotential = player?.potential ? parseFloat(player.potential) : 50;
  const playerRating = player?.rating ? parseFloat(player.rating) : 50;
  const playerMarketValue = player?.market_value ? parseMarketValue(player.market_value) : 0;
  
  const playerValueScore = (playerPotential - playerRating + 1) * playerMarketValue / 1e6;
  
  // Scale the value score for the progress bar (cap at 100%)
  const maxScore = 1000;  // Example max value
  const valuePercentage = Math.min((Math.log10(playerValueScore + 1) / Math.log10(maxScore)) * 100, 100);
  // Calculate player's age
  const dateOfBirth = player ? new Date(player.birthDate) : null;
  const playerAge = dateOfBirth ? differenceInYears(new Date(), dateOfBirth) : 'Unknown';

  if (!player) {
    return <div>Loading...</div>;
  }

  return (
    <div className="player-details">
      <div className="player-card">
        <h1 className='player-name'>{player.name}</h1>
        {player.img && <img src={player.img} alt={player.name} className="player-image" />}
        <div className="player-info">
          <p><strong>Team:</strong> {player.team || 'Information not available'}</p>
          <p><strong>Position:</strong> {player.position || 'Information not available'}</p>
          <p><strong>Age:</strong> {playerAge}</p>
          <p><strong>Nationality:</strong> {player.nationality || 'Information not available'}</p>
          <p><strong>Birth Date:</strong> {player.birthDate || 'Information not available'}</p>
          <p><strong>Height:</strong> {player.height || 'Information not available'}</p>
          <p><strong>Market Value:</strong> {player.market_value || 'Information not available'}</p>
          <p><strong>Current Rating:</strong> {player.rating || 'Information not available'}</p>
          <p><strong>Potential:</strong> {player.potential || 'Information not available'}</p>
          <p><strong>Wage:</strong> {player.wage || 'Information not available'}</p>
          <p><strong>Description:</strong> {player.description || 'Information not available'}</p>
        </div>

        {/* Progress bar for player's value */}
        <div className="player-value">
          <p><strong>Player Value:</strong></p>
          <div className="progress-bar">
            <div className="progress" style={{ width: `${valuePercentage}%` }}></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlayerDetails;

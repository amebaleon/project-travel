



import React, { useState } from 'react';
import LocationModal from './LocationModal';

const TravelCard = ({ dailyPlan }) => {
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);

  const handleMouseEnter = (recommendation) => {
    setSelectedRecommendation(recommendation);
  };

  const handleMouseLeave = () => {
    setSelectedRecommendation(null);
  };

  return (
    <div 
      className={`travel-card ${selectedRecommendation ? 'expanded' : ''}`}
      onMouseLeave={handleMouseLeave}
    >
      <h3>{dailyPlan.date}</h3>
      <ul>
        {dailyPlan.recommendations.map((recommendation, index) => (
          <li
            key={index}
            onMouseEnter={() => handleMouseEnter(recommendation)}
          >
            {recommendation.name}
          </li>
        ))}
      </ul>
      {selectedRecommendation && <LocationModal location={selectedRecommendation} visible={!!selectedRecommendation} />}
    </div>
  );
};

export default TravelCard;

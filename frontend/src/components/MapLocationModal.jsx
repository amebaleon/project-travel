import React, { useState } from 'react';
import './MapLocationModal.css';

const MapLocationModal = ({ locations, onClose, onLocationClick }) => {
  const [selectedLocation, setSelectedLocation] = useState(null);

  if (!locations || locations.length === 0) {
    return null;
  }

  const handleClick = (location) => {
    setSelectedLocation(location);
    onLocationClick(location);
  };

  return (
    <div className="map-location-modal-overlay">
      <div className="map-location-modal-content">
        <button className="map-location-modal-close" onClick={onClose}>&times;</button>
        <h3>선택된 날짜의 여행지</h3>
        <ul>
          {locations.map((location, index) => (
            <li
              key={index}
              className={selectedLocation && selectedLocation.name === location.name ? 'selected' : ''}
              onClick={() => handleClick(location)}
            >
              {location.name}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default MapLocationModal;

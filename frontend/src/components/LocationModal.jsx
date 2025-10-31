
import React from 'react';
import './LocationModal.css';

const LocationModal = ({ location, visible }) => {
  return (
    <div className={`location-modal ${visible ? 'visible' : ''}`}>
      {location.image_url && (
        <img 
          src={location.image_url} 
          alt={location.name} 
          style={{ width: '100%', height: '150px', objectFit: 'cover', borderRadius: '10px 10px 0 0' }} 
        />
      )}
      <div style={{ padding: '20px' }}>
        <h4>{location.name}</h4>
        <p>{location.description}</p>
        <p><strong>Activity:</strong> {location.activity}</p>
        <p><strong>Address:</strong> {location.address}</p>
      </div>
    </div>
  );
};

export default LocationModal;

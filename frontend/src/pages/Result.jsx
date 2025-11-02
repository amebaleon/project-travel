
import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { KakaoMap } from '../components/KakaoMap';
import CalendarView from '../components/CalendarView';
import MapLocationModal from '../components/MapLocationModal';

function Result() {
  const location = useLocation();
  const { recommendation } = location.state || {};

  const [selectedDayRecommendations, setSelectedDayRecommendations] = useState([]);
  const [showMapModal, setShowMapModal] = useState(false);
  const [mapCenter, setMapCenter] = useState(null);

  useEffect(() => {
    if (recommendation && recommendation.daily_recommendations && recommendation.daily_recommendations.length > 0) {
      // Set initial selected day recommendations to the first day's recommendations
      setSelectedDayRecommendations(recommendation.daily_recommendations[0].recommendations);
      // Set initial map center to the first location of the first day
      if (recommendation.daily_recommendations[0].recommendations.length > 0) {
        const firstLocation = recommendation.daily_recommendations[0].recommendations[0];
        if (typeof firstLocation.latitude === 'number' && typeof firstLocation.longitude === 'number') {
          setMapCenter({ latitude: firstLocation.latitude, longitude: firstLocation.longitude });
        } else {
          // If initial first location has invalid coords, do nothing to let KakaoMap's default center take effect
        }
      }
      setShowMapModal(true); // Show modal initially for the first day
    }
  }, [recommendation]);

  const handleDateSelect = (date, dailyRecommendations) => {
    setSelectedDayRecommendations(dailyRecommendations);
    setShowMapModal(dailyRecommendations.length > 0); // Show modal only if there are recommendations
    if (dailyRecommendations.length > 0) {
      const firstLocation = dailyRecommendations[0];
      if (typeof firstLocation.latitude === 'number' && typeof firstLocation.longitude === 'number') {
        setMapCenter({ latitude: firstLocation.latitude, longitude: firstLocation.longitude });
      } else {
        // If first location has invalid coords, do nothing to retain previous valid center
      }
    } else {
      // If no recommendations, do nothing to retain previous valid center
    }
  };

  const handleLocationClick = (location) => {
    setMapCenter({ latitude: location.latitude, longitude: location.longitude });
  };

  const handleCloseMapModal = () => {
    setShowMapModal(false);
  };

  if (!recommendation || !recommendation.daily_recommendations) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#fff' }}>
        <h1>추천 정보를 찾을 수 없습니다.</h1>
        <p>이전 페이지로 돌아가 다시 시도해주세요.</p>
      </div>
    );
  }

  return (
    <div className="result-container row">
      <div className="map-container col-md-6">
        <KakaoMap recommendations={selectedDayRecommendations} centerLocation={mapCenter} />
        {showMapModal && selectedDayRecommendations.length > 0 && (
          <MapLocationModal
            locations={selectedDayRecommendations}
            onClose={handleCloseMapModal}
            onLocationClick={handleLocationClick}
          />
        )}
      </div>
      <div className="result-content col-md-6">
        <CalendarView
          recommendations={recommendation.daily_recommendations}
          onDateSelect={handleDateSelect}
          calendarWidth="600px"
        />
      </div>
    </div>
  );
}

export { Result };


import React from 'react';
import { useLocation } from 'react-router-dom';
import KakaoMap from '../components/KakaoMap';
import TravelCard from '../components/TravelCard';
import './Result.css';

function Result() {
  const location = useLocation();
  const { recommendation } = location.state || {};

  if (!recommendation || !recommendation.daily_recommendations) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#fff' }}>
        <h1>추천 정보를 찾을 수 없습니다.</h1>
        <p>이전 페이지로 돌아가 다시 시도해주세요.</p>
      </div>
    );
  }

  return (
    <div className="result-container">
      <div className="map-container">
        <KakaoMap recommendations={recommendation.daily_recommendations} />
      </div>
      <div className="cards-container">
        <h1>AI 여행 추천 결과</h1>
        {recommendation.daily_recommendations.length > 0 ? (
          recommendation.daily_recommendations.map((dailyPlan, index) => (
            <TravelCard key={index} dailyPlan={dailyPlan} />
          ))
        ) : (
          <p>AI 추천 결과를 불러오지 못했습니다.</p>
        )}
      </div>
    </div>
  );
}

export default Result;

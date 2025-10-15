import RecommendationCard from './RecommendationCard';
import '../components.css';

const ResultsDisplay = ({ data, onBack }) => {
  if (!data) return null;

  const { daily_recommendations, is_verified_success, agent_search_log } = data;

  return (
    <div className="results-container">
      <div className="results-header">
        <h1>AI 추천 결과</h1>
        <button onClick={onBack}>다시 추천받기</button>
      </div>
      
      <div className={`summary-box ${is_verified_success ? 'summary-success' : 'summary-fail'}`}>
        <strong>전체 검증 상태:</strong> {is_verified_success ? '모든 정보 검증 성공' : '일부 정보 검증 실패 또는 오류'}
      </div>

      {daily_recommendations.map((daily_plan) => (
        <div key={daily_plan.date} className="daily-plan">
          <h2>{new Date(daily_plan.date).toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })}</h2>
          <div className="cards-grid">
            {daily_plan.recommendations.map((item, index) => (
              <RecommendationCard key={index} item={item} />
            ))}
          </div>
        </div>
      ))}

      <div className="agent-log">
        <h4>[참고] AI Agent 검색 로그</h4>
        <pre>{agent_search_log}</pre>
      </div>
    </div>
  );
};

export default ResultsDisplay;

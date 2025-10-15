import '../components.css';

// 신뢰도 점수에 따라 클래스 이름을 반환하는 헬퍼 함수
const getReliabilityClass = (score) => {
  if (score > 80) return 'high-reliability';
  if (score > 50) return 'medium-reliability';
  return 'low-reliability';
};

const VerificationDetails = ({ details }) => {
  if (!details) return null;

  const reliabilityClass = getReliabilityClass(details.reliability_score);

  return (
    <div className="verification-details">
      <h4>
        실시간 검증 결과 <span className={`reliability-badge ${reliabilityClass}`}>{details.reliability_score}점</span>
      </h4>
      <p><strong>운영 상태:</strong> {details.operating_status}</p>
      <p><strong>가격 정보:</strong> {details.latest_price_info}</p>
      <p><strong>특이사항:</strong> {details.schedule_change_and_notes}</p>
      <p className="reliability-reason"><em>({details.reliability_reason})</em></p>
    </div>
  );
};

const RecommendationCard = ({ item }) => {
  return (
    <div className="card">
      {item.image_url && <img src={item.image_url} alt={item.name} className="card-image" />}
      <div className="card-content">
        <h3>{item.name}</h3>
        <p className="card-address">{item.address}</p>
        <p>{item.description}</p>
        <p><strong>추천 활동:</strong> {item.activity}</p>
        <VerificationDetails details={item.verification_details} />
      </div>
    </div>
  );
};

export default RecommendationCard;

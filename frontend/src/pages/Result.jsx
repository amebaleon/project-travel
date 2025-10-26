import React from "react";
import { useLocation } from "react-router-dom";

function Result() {
  const location = useLocation();
  const { recommendation } = location.state || {};

  if (!recommendation) {
    return (
      <div style={{ padding: "20px", textAlign: "center", color: "#333" }}>
        <h1>추천 정보를 찾을 수 없습니다.</h1>
        <p>이전 페이지로 돌아가 다시 시도해주세요.</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "20px", maxWidth: "800px", margin: "auto", fontFamily: "Arial, sans-serif" }}>
      <h1 style={{ textAlign: "center", color: "#007bff", marginBottom: "30px" }}>AI 여행 추천 결과</h1>

      {recommendation.daily_recommendations.length > 0 ? (
        recommendation.daily_recommendations.map((dailyRec, index) => (
          <div key={index} style={{ marginBottom: "40px", border: "1px solid #eee", borderRadius: "8px", padding: "20px", boxShadow: "0 2px 4px rgba(0,0,0,0.05)" }}>
            <h2 style={{ color: "#333", marginBottom: "20px", borderBottom: "2px solid #007bff", paddingBottom: "10px" }}>
              {dailyRec.date} 일차
            </h2>
            {dailyRec.recommendations.length > 0 ? (
              dailyRec.recommendations.map((item, itemIndex) => (
                <div key={itemIndex} style={{ display: "flex", marginBottom: "20px", borderBottom: "1px dashed #eee", paddingBottom: "20px", alignItems: "flex-start" }}>
                  {item.image_url && (
                    <img
                      src={item.image_url}
                      alt={item.name}
                      style={{ width: "120px", height: "120px", objectFit: "cover", borderRadius: "8px", marginRight: "20px", flexShrink: 0 }}
                    />
                  )}
                  <div style={{ flexGrow: 1 }}>
                    <h3 style={{ color: "#555", marginTop: "0", marginBottom: "5px" }}>{item.name}</h3>
                    <p style={{ color: "#666", fontSize: "0.9em", marginBottom: "5px" }}>{item.description}</p>
                    <p style={{ color: "#777", fontSize: "0.8em", marginBottom: "5px" }}>주소: {item.address}</p>
                    <p style={{ color: "#777", fontSize: "0.8em", marginBottom: "5px" }}>활동: {item.activity}</p>
                    {item.operating_hours && <p style={{ color: "#777", fontSize: "0.8em", marginBottom: "5px" }}>운영 시간: {item.operating_hours}</p>}
                    {item.start_date && item.end_date && (
                      <p style={{ color: "#777", fontSize: "0.8em", marginBottom: "5px" }}>기간: {item.start_date} ~ {item.end_date}</p>
                    )}
                    {item.verification_details && (
                      <div style={{ marginTop: "10px", padding: "10px", backgroundColor: "#f8f9fa", borderRadius: "5px", borderLeft: "3px solid #ffc107" }}>
                        <h4 style={{ color: "#ffc107", fontSize: "0.9em", marginTop: "0", marginBottom: "5px" }}>검증 정보:</h4>
                        <p style={{ fontSize: "0.8em", margin: "0" }}>운영 상태: {item.verification_details.operating_status}</p>
                        <p style={{ fontSize: "0.8em", margin: "0" }}>종료/취소 여부: {item.verification_details.end_or_cancel_status}</p>
                        <p style={{ fontSize: "0.8em", margin: "0" }}>최신 가격: {item.verification_details.latest_price_info}</p>
                        <p style={{ fontSize: "0.8em", margin: "0" }}>일정 변경: {item.verification_details.schedule_change_and_notes}</p>
                        <p style={{ fontSize: "0.8em", margin: "0" }}>신뢰도: {item.verification_details.reliability_score} ({item.verification_details.reliability_reason})</p>
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <p style={{ color: "#666" }}>이 날짜에 추천된 장소가 없습니다.</p>
            )}
          </div>
        ))
      ) : (
        <p style={{ textAlign: "center", color: "#666" }}>AI 추천 결과를 불러오지 못했습니다.</p>
      )}

      {recommendation.agent_search_log && (
        <div style={{ marginTop: "50px", borderTop: "1px solid #eee", paddingTop: "30px" }}>
          <h2 style={{ color: "#333", marginBottom: "20px" }}>AI 에이전트 검색 로그</h2>
          <pre style={{ backgroundColor: "#f4f4f4", padding: "15px", borderRadius: "8px", overflowX: "auto", whiteSpace: "pre-wrap", wordBreak: "break-all" }}>
            {recommendation.agent_search_log}
          </pre>
        </div>
      )}
    </div>
  );
}

export default Result;

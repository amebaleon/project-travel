import React, { useState } from "react";
import { useLocation } from "react-router-dom";

function Result() {
  const location = useLocation();
  const { recommendation } = location.state || {};
  const [expandedActivity, setExpandedActivity] = useState(null);

  const handleActivityClick = (dailyRecIndex, itemIndex) => {
    if (expandedActivity && expandedActivity.dailyRecIndex === dailyRecIndex && expandedActivity.itemIndex === itemIndex) {
      setExpandedActivity(null);
    } else {
      setExpandedActivity({ dailyRecIndex, itemIndex });
    }
  };

  if (!recommendation || !recommendation.daily_recommendations) {
    return (
      <div style={{ padding: "20px", textAlign: "center", color: "#fff" }}>
        <h1>추천 정보를 찾을 수 없습니다.</h1>
        <p>이전 페이지로 돌아가 다시 시도해주세요.</p>
      </div>
    );
  }

  return (
    <div
      style={{
        padding: "20px",
        maxWidth: "1200px",
        margin: "auto",
        fontFamily: "Arial, sans-serif",
        backgroundColor: "rgba(255, 255, 255, 0.15)", // Liquid glass background
        backdropFilter: "blur(10px)", // Glassmorphism blur effect
        border: "1px solid rgba(255, 255, 255, 0.3)", // Light translucent border
        borderRadius: "15px",
        boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.37)", // Glassmorphism shadow
        color: "#000", // Default text color for contrast
        minHeight: "80vh", // Ensure it takes up enough space
        display: "flex",
        flexDirection: "column",
      }}
    >
      <h1 style={{ textAlign: "center", color: "#000", marginBottom: "30px", paddingTop: "20px" }}>AI 여행 추천 결과</h1>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "20px" }}>
        {recommendation.daily_recommendations.length > 0 ? (
          recommendation.daily_recommendations.map((dailyRec, dailyRecIndex) => (
            <div key={dailyRecIndex} style={{ border: "1px solid rgba(255, 255, 255, 0.4)", borderRadius: "8px", overflow: "hidden", boxShadow: "0 2px 8px rgba(0,0,0,0.05)", backgroundColor: "rgba(255, 255, 255, 0.2)" }}>
              <div style={{ backgroundColor: "rgba(0, 123, 255, 0.7)", color: "#fff", padding: "15px", fontSize: "1.2em", fontWeight: "bold", textAlign: "center" }}>
                {dailyRec.date} 일차
              </div>
              <div style={{ padding: "15px" }}>
                {dailyRec.recommendations.length > 0 ? (
                  dailyRec.recommendations.map((item, itemIndex) => (
                    <div
                      key={itemIndex}
                      onClick={() => handleActivityClick(dailyRecIndex, itemIndex)}
                      style={{
                        marginBottom: "10px",
                        padding: "10px",
                        border: "1px solid rgba(255, 255, 255, 0.5)",
                        borderRadius: "5px",
                        cursor: "pointer",
                        backgroundColor: expandedActivity && expandedActivity.dailyRecIndex === dailyRecIndex && expandedActivity.itemIndex === itemIndex ? "rgba(255, 255, 255, 0.4)" : "rgba(255, 255, 255, 0.15)",
                        transition: "background-color 0.3s ease",
                        display: "flex",
                        alignItems: "center",
                        gap: "10px",
                        color: "#000", // Ensure text color is visible
                      }}
                    >
                      <div style={{ flexGrow: 1 }}>
                        <h3 style={{ color: "#000", marginTop: "0", marginBottom: "0", fontSize: "1.1em" }}>{item.name}</h3>
                      </div>

                      {expandedActivity && expandedActivity.dailyRecIndex === dailyRecIndex && expandedActivity.itemIndex === itemIndex && (
                        <div style={{ marginTop: "10px", paddingTop: "10px", borderTop: "1px dashed rgba(255, 255, 255, 0.5)", width: "100%" }}>
                          {item.image_url && (
                            <img
                              src={item.image_url}
                              alt={item.name}
                              style={{ width: "100%", maxHeight: "200px", objectFit: "cover", borderRadius: "8px", marginBottom: "10px" }}
                            />
                          )}
                          <p style={{ color: "#333", fontSize: "0.85em", margin: "0" }}>{item.activity} - {item.address}</p>
                          <p style={{ color: "#000", fontSize: "0.9em", marginBottom: "5px" }}>{item.description}</p>
                          {item.operating_hours && <p style={{ color: "#333", fontSize: "0.8em", marginBottom: "5px" }}>운영 시간: {item.operating_hours}</p>}
                          {item.start_date && item.end_date && (
                            <p style={{ color: "#333", fontSize: "0.8em", marginBottom: "5px" }}>기간: {item.start_date} ~ {item.end_date}</p>
                          )}
                          {item.verification_details && (
                            <div style={{ marginTop: "10px", padding: "10px", backgroundColor: "rgba(255, 255, 255, 0.1)", borderRadius: "5px", borderLeft: "3px solid #ffc107" }}>
                              <h4 style={{ color: "#ffc107", fontSize: "0.9em", marginTop: "0", marginBottom: "5px" }}>검증 정보:</h4>
                              <p style={{ color: "#333", fontSize: "0.8em", margin: "0" }}>운영 상태: {item.verification_details.operating_status}</p>
                              <p style={{ color: "#333", fontSize: "0.8em", margin: "0" }}>종료/취소 여부: {item.verification_details.end_or_cancel_status}</p>
                              <p style={{ color: "#333", fontSize: "0.8em", margin: "0" }}>최신 가격: {item.verification_details.latest_price_info}</p>
                              <p style={{ color: "#333", fontSize: "0.8em", margin: "0" }}>일정 변경: {item.verification_details.schedule_change_and_notes}</p>
                              <p style={{ color: "#333", fontSize: "0.8em", margin: "0" }}>신뢰도: {item.verification_details.reliability_score} ({item.verification_details.reliability_reason})</p>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <p style={{ color: "#333" }}>이 날짜에 추천된 장소가 없습니다.</p>
                )}
              </div>
            </div>
          ))
        ) : (
          <p style={{ textAlign: "center", color: "#333" }}>AI 추천 결과를 불러오지 못했습니다.</p>
        )}
      </div>
    </div>
  );
}export default Result;

import React, { useState } from "react";

const Card = ({ item, isSelected, onClick }) => (
  <div
    onClick={onClick}
    style={{
      padding: "15px 20px",
      margin: "5px",
      border: `2px solid ${
        isSelected ? "#007bff" : "#e0e0e0"
      }`,
      borderRadius: "8px",
      cursor: "pointer",
      backgroundColor: isSelected ? "#e7f3ff" : "#f9f9f9",
      color: isSelected ? "#007bff" : "#333",
      fontWeight: isSelected ? "bold" : "normal",
      transition: "all 0.3s ease",
      textAlign: "center",
      minWidth: "100px",
      flexGrow: 1,
      boxShadow: isSelected
        ? "0 4px 8px rgba(0, 123, 255, 0.2)"
        : "0 2px 4px rgba(0, 0, 0, 0.05)",
    }}
  >
    {item}
  </div>
);

export default function TravelInput({ onClose, navigate }) {
  const [step, setStep] = useState(0);
  const [selectedRegion, setSelectedRegion] = useState(""); // 단일 선택으로 변경
  const [selectedInterest, setSelectedInterest] = useState(""); // 단일 선택으로 변경
  const [gender, setGender] = useState("");
  const [birthYear, setBirthYear] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const regions = ["서울", "부산", "전주", "제주"]; // destinations -> regions
  const interests = ["음식", "문화", "자연", "쇼핑"]; // categories -> interests
  const genders = ["남", "여", "선택 안함"];

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 100 }, (_, i) => currentYear - i);

  // 단일 선택을 위한 핸들러
  const handleRegionSelect = (region) => {
    setSelectedRegion(region);
  };

  const handleInterestSelect = (interest) => {
    setSelectedInterest(interest);
  };

  const handleNext = () => {
    setStep((prev) => prev + 1);
  };

  const handlePrevious = () => {
    setStep((prev) => prev - 1);
  };

  const handleSubmit = async () => {
    const age = birthYear ? currentYear - parseInt(birthYear) : 0; // birthYear가 없으면 0으로 처리

    const requestBody = {
      region: selectedRegion,
      start_date: startDate, // YYYY-MM-DD 형식으로 이미 저장됨
      end_date: endDate, // YYYY-MM-DD 형식으로 이미 저장됨
      age: age,
      gender: gender === "선택 안함" ? "" : gender, // 선택 안함이면 빈 문자열로
      interests: [selectedInterest], // 단일 선택이므로 배열에 담아서 보냄
    };

    console.log("백엔드로 보낼 데이터:", requestBody);

    try {
      const response = await fetch("http://localhost:8000/recommend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "백엔드 응답 오류");
      }

      const result = await response.json();
      console.log("백엔드 응답:", result);

      // 결과 페이지로 이동하며 데이터 전달
      navigate("/result", { state: { recommendation: result } });
      onClose(); // 모달 닫기
    } catch (error) {
      console.error("API 호출 중 오류 발생:", error);
      alert(`여행 추천을 받는 중 오류가 발생했습니다: ${error.message}`);
    }
  };

  const renderStep = () => {
    switch (step) {
      case 0:
        return (
          <>
            <h3 style={{ color: "#fff", marginBottom: "10px" }}>
              어디로 가시나요?
            </h3>
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "10px",
                justifyContent: "center",
              }}
            >
              {regions.map((region) => (
                <Card
                  key={region}
                  item={region}
                  isSelected={selectedRegion === region}
                  onClick={() => handleRegionSelect(region)}
                />
              ))}
            </div>
          </>
        );
      case 1:
        return (
          <>
            <h3 style={{ color: "#fff", marginBottom: "10px" }}>
              어떤 종류의 여행을 원하시나요?
            </h3>
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "10px",
                justifyContent: "center",
              }}
            >
              {interests.map((interest) => (
                <Card
                  key={interest}
                  item={interest}
                  isSelected={selectedInterest === interest}
                  onClick={() => handleInterestSelect(interest)}
                />
              ))}
            </div>
          </>
        );
      case 2:
        return (
          <>
            <h3 style={{ color: "#fff", marginBottom: "10px" }}>
              성별 (선택 사항)
            </h3>
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "10px",
                justifyContent: "center",
                marginBottom: "20px",
              }}
            >
              {genders.map((g) => (
                <Card
                  key={g}
                  item={g}
                  isSelected={gender === g}
                  onClick={() => setGender(g)}
                />
              ))}
            </div>

            <h3 style={{ color: "#fff", marginBottom: "10px" }}>
              출생 연도 (선택 사항)
            </h3>
            <select
              value={birthYear}
              onChange={(e) => setBirthYear(e.target.value)}
              style={{
                width: "100%",
                padding: "10px",
                borderRadius: "5px",
                border: "1px solid rgba(255, 255, 255, 0.5)", // Lighter border
                boxSizing: "border-box",
                backgroundColor: "rgba(255, 255, 255, 0.2)", // More translucent background
                color: "#fff", // White text
                appearance: "none", // Remove default arrow
                backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M7 10l5 5 5-5z'/%3E%3C/svg%3E")`, // Custom arrow
                backgroundRepeat: "no-repeat",
                backgroundPosition: "right 10px center",
                backgroundSize: "16px",
              }}
            >
              <option value="" style={{ backgroundColor: "#333", color: "#fff" }}>선택 안함</option>
              {years.map((year) => (
                <option key={year} value={year} style={{ backgroundColor: "#333", color: "#fff" }}>
                  {year}
                </option>
              ))}
            </select>
          </>
        );
      case 3:
        return (
          <>
            <h3 style={{ color: "#fff", marginBottom: "10px" }}>
              여행 일정 (선택 사항)
            </h3>
            <div style={{ display: "flex", gap: "10px", marginBottom: "10px" }}>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                style={{
                  width: "50%",
                  padding: "10px",
                  borderRadius: "5px",
                  border: "1px solid rgba(255, 255, 255, 0.5)", // Lighter border
                  boxSizing: "border-box",
                  backgroundColor: "rgba(255, 255, 255, 0.2)", // More translucent background
                  color: "#fff", // White text
                  // For date input, the text color of the placeholder and selected date might be hard to change consistently across browsers.
                  // A custom date picker component would be needed for full control.
                }}
              />
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                style={{
                  width: "50%",
                  padding: "10px",
                  borderRadius: "5px",
                  border: "1px solid rgba(255, 255, 255, 0.5)", // Lighter border
                  boxSizing: "border-box",
                  backgroundColor: "rgba(255, 255, 255, 0.2)", // More translucent background
                  color: "#fff", // White text
                }}
              />
            </div>
          </>
        );
      default:
        return null;
    }
  };

  return (
    <div
      style={{
        backgroundColor: "rgba(255, 255, 255, 0.15)", // Translucent white background
        backdropFilter: "blur(10px)", // Glassmorphism blur effect
        border: "1px solid rgba(255, 255, 255, 0.3)", // Light translucent border
        padding: "30px",
        borderRadius: "15px",
        boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.37)", // Glassmorphism shadow
        width: "90%",
        maxWidth: "600px",
        position: "relative",
        maxHeight: "80vh",
        overflowY: "auto",
        color: "#fff", // Adjust text color for better contrast on translucent background
      }}
    >
      <button
        onClick={onClose}
        style={{
          position: "absolute",
          top: "15px",
          right: "15px",
          background: "none",
          border: "none",
          fontSize: "24px",
          cursor: "pointer",
          color: "#fff", // White close button for contrast
        }}
      >
        &times;
      </button>
      <h2 style={{ textAlign: "center", marginBottom: "25px", color: "#fff" }}>
        여행 정보 입력
      </h2>

      <div style={{ minHeight: "200px", marginBottom: "20px" }}>
        {renderStep()}
      </div>

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginTop: "20px",
          paddingTop: "20px",
          borderTop: "1px solid rgba(255, 255, 255, 0.3)", // Translucent border for separator
        }}
      >
        {step > 0 && (
          <button
            onClick={handlePrevious}
            style={{
              padding: "10px 20px",
              backgroundColor: "rgba(108, 117, 125, 0.7)",
              color: "white",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
              fontSize: "16px",
            }}
          >
            이전
          </button>
        )}
        {step < 3 && (
          <button
            onClick={handleNext}
            style={{
              padding: "10px 20px",
              backgroundColor: "rgba(0, 123, 255, 0.7)",
              color: "white",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
              fontSize: "16px",
              marginLeft: step === 0 ? 'auto' : '0',
            }}
          >
            다음
          </button>
        )}
        {step === 3 && (
          <button
            onClick={handleSubmit}
            style={{
              padding: "10px 20px",
              backgroundColor: "rgba(40, 167, 69, 0.7)",
              color: "white",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
              fontSize: "16px",
              marginLeft: "auto",
            }}
          >
            제출
          </button>
        )}
      </div>
    </div>
  );
}
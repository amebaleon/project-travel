import React, { useState, useRef, useEffect } from "react";
import "./YearScroller.css";
import "./DateRangePicker.css";
import Loading from "./Loading";
import DateRangePicker from "./DateRangePicker";
import { addDays } from 'date-fns';

function debounce(func, wait) {
  let timeout;
  return function(...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), wait);
  };
}

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

const STEP_TRANSITION_DURATION = 300; // ms

const YearScroller = ({ years, selectedYear, onYearChange, onScrollEnd }) => {
  const scrollerRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startY, setStartY] = useState(0);
  const [scrollTop, setScrollTop] = useState(0);

  const debouncedScrollEnd = debounce(onScrollEnd, 200);

  useEffect(() => {
    const scroller = scrollerRef.current;
    if (scroller && selectedYear) {
      const yearIndex = years.indexOf(selectedYear);
      if (yearIndex > -1) {
        const itemHeight = scroller.scrollHeight / years.length;
        const targetScrollTop = yearIndex * itemHeight - scroller.clientHeight / 2 + itemHeight / 2;
        scroller.scrollTop = targetScrollTop;
      }
    }
  }, [selectedYear, years]);

  const handleMouseDown = (e) => {
    setIsDragging(true);
    setStartY(e.pageY - scrollerRef.current.offsetTop);
    setScrollTop(scrollerRef.current.scrollTop);
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    e.preventDefault();
    const y = e.pageY - scrollerRef.current.offsetTop;
    const walk = (y - startY) * 2; // aribitrary multiplier
    scrollerRef.current.scrollTop = scrollTop - walk;
    handleScroll();
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    if(onScrollEnd) debouncedScrollEnd();
  };

  const handleScroll = () => {
    const scroller = scrollerRef.current;
    if (scroller) {
      const itemHeight = scroller.scrollHeight / years.length;
      const selectedIndex = Math.round((scroller.scrollTop + scroller.clientHeight / 2 - itemHeight / 2) / itemHeight);
      const year = years[selectedIndex];
      if (year && year !== selectedYear) {
        onYearChange(year);
      }
    }
  };

  return (
    <div
      ref={scrollerRef}
      className="year-scroller"
      onMouseDown={handleMouseDown}
      onMouseLeave={handleMouseUp}
      onMouseUp={handleMouseUp}
      onMouseMove={handleMouseMove}
    >
      <ul className="year-list">
        {years.map((year) => (
          <li
            key={year}
            className={`year-item ${year === selectedYear ? "selected" : ""}`}
          >
            {year}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default function TravelInput({ onClose, navigate }) {
  const [step, setStep] = useState(0);
  const [stepOpacity, setStepOpacity] = useState(1);
  const [selectedRegion, setSelectedRegion] = useState(""); // 단일 선택으로 변경
  const [selectedInterest, setSelectedInterest] = useState(""); // 단일 선택으로 변경
  const [gender, setGender] = useState("");
  const [birthYear, setBirthYear] = useState(new Date().getFullYear());
  const [dateRange, setDateRange] = useState([{
    startDate: new Date(),
    endDate: addDays(new Date(), 7),
    key: 'selection'
  }]);
  const [loading, setLoading] = useState(false);

  const regions = ["서울", "부산", "전주", "제주"]; // destinations -> regions
  const interests = ["음식", "문화", "자연", "쇼핑"]; // categories -> interests
  const genders = ["남", "여", "선택 안함"];

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 2099 - 1901 + 1 }, (_, i) => 2099 - i);

  // 단일 선택을 위한 핸들러
  const handleRegionSelect = (region) => {
    setSelectedRegion(region);
    handleNext();
  };

  const handleInterestSelect = (interest) => {
    setSelectedInterest(interest);
    handleNext();
  };

  const handleDateChange = (ranges) => {
    setDateRange([ranges.selection]);
  }

  const handleNext = () => {
    setStepOpacity(0);
    setTimeout(() => {
      setStep((prev) => prev + 1);
      setStepOpacity(1);
    }, STEP_TRANSITION_DURATION);
  };

  const handlePrevious = () => {
    setStepOpacity(0);
    setTimeout(() => {
      setStep((prev) => prev - 1);
      setStepOpacity(1);
    }, STEP_TRANSITION_DURATION);
  };

  const handleSubmit = async () => {
    setLoading(true);
    const age = birthYear ? currentYear - parseInt(birthYear) : 0; // birthYear가 없으면 0으로 처리

    const requestBody = {
      region: selectedRegion,
      start_date: dateRange[0].startDate.toISOString().slice(0,10),
      end_date: dateRange[0].endDate.toISOString().slice(0,10),
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
    } finally {
      setLoading(false);
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
              성별(선택 사항)
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
                  onClick={() => {
                    setGender(g);
                    handleNext();
                  }}
                />
              ))}
            </div>
          </>
        );
      case 3:
        return (
          <>
            <h3 style={{ color: "#fff", marginBottom: "10px" }}>
              언제 여행을 떠나시나요?
            </h3>
            <DateRangePicker ranges={dateRange} onChange={handleDateChange} />
          </>
        );
        case 4:
            return (
              <>
                <h3 style={{ color: "#fff", marginBottom: "20px" }}>
                  출생 연도 (선택 사항)
                </h3>
                <YearScroller years={years} selectedYear={birthYear} onYearChange={setBirthYear} />
              </>
            );
      default:
        return null;
    }
  };

  return (
    <>
      {loading && <Loading />}
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

        <div
          style={{
            minHeight: "200px",
            marginBottom: "20px",
            opacity: stepOpacity,
            transition: `opacity ${STEP_TRANSITION_DURATION}ms ease-in-out`,
          }}
        >
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
                padding: "8px 15px", // Simplified padding
                backgroundColor: "rgba(108, 117, 125, 0.5)", // More translucent
                color: "white",
                border: "none",
                borderRadius: "5px",
                cursor: "pointer",
                fontSize: "14px", // Smaller font size
              }}
            >
              이전
            </button>
          )}
          {step === 3 && (
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
              }}
            >
              다음
            </button>
          )}
          {step === 4 && (
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
              }}
            >
              완료
            </button>
          )}
        </div>
      </div>
    </>
  );
}
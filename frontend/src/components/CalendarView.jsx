import React, { useState, useEffect } from 'react';
import './CalendarView.css';

const CalendarView = ({ recommendations, onDateSelect, className, calendarWidth }) => {
  const [selectedDate, setSelectedDate] = useState(null);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [showDetails, setShowDetails] = useState(false); // New state for details visibility

  useEffect(() => {
    if (recommendations && recommendations.length > 0) {
      const firstDate = new Date(recommendations[0].date);
      setCurrentMonth(new Date(firstDate.getFullYear(), firstDate.getMonth(), 1));

      // Set initial selected date and call onDateSelect for the first day with recommendations
      const initialSelectedDate = recommendations[0].date;
      setSelectedDate(initialSelectedDate);
      setShowDetails(true); // Show details for the initial selected date
      if (onDateSelect) {
        onDateSelect(initialSelectedDate, recommendations[0].recommendations);
      }
    }
  }, [recommendations]);

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className={`calendar-view-container ${className}`}>
        <h1>AI 여행 추천 결과</h1>
        <p>AI 추천 결과를 불러오지 못했습니다.</p>
      </div>
    );
  }

  const dailyRecommendationsMap = new Map();
  recommendations.forEach(dailyPlan => {
    dailyRecommendationsMap.set(dailyPlan.date, dailyPlan.recommendations);
  });

  const renderCalendar = () => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    const firstDayOfMonth = new Date(year, month, 1).getDay(); // 0 for Sunday, 1 for Monday, etc.
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    const calendarDays = [];
    // Fill leading empty days
    for (let i = 0; i < firstDayOfMonth; i++) {
      calendarDays.push(<div key={`empty-prev-${i}`} className="calendar-day empty"></div>);
    }

    // Fill days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const fullDate = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      const hasRecommendations = dailyRecommendationsMap.has(fullDate);
      const isSelected = selectedDate === fullDate;

      calendarDays.push(
        <div
          key={fullDate}
          className={`calendar-day ${hasRecommendations ? 'has-recommendations' : ''} ${isSelected ? 'selected' : ''}`}
          onClick={() => {
            if (hasRecommendations) {
              if (selectedDate === fullDate) {
                // If clicking the same day, toggle details visibility
                setShowDetails(prev => !prev);
              }
              else {
                setSelectedDate(fullDate);
                setShowDetails(true);
                if (onDateSelect) {
                  onDateSelect(fullDate, dailyRecommendationsMap.get(fullDate) || []);
                }
              }
            } else {
              // If clicking an empty day, hide details and clear selection
              setSelectedDate(null);
              setShowDetails(false);
              if (onDateSelect) {
                onDateSelect(null, []); // Clear map if no recommendations
              }
            }
          }}
        >
          <div className="date">{day}</div>
          {hasRecommendations && (
            <div className="recommendation-dots">
              {dailyRecommendationsMap.get(fullDate).slice(0, 3).map((rec, idx) => (
                <span key={idx} className="dot"></span>
              ))}
              {dailyRecommendationsMap.get(fullDate).length > 3 && <span className="dot-more">...</span>}
            </div>
          )}
        </div>
      );
    }

    return calendarDays;
  };

  const goToPreviousMonth = () => {
    setCurrentMonth(prevMonth => new Date(prevMonth.getFullYear(), prevMonth.getMonth() - 1, 1));
    setSelectedDate(null); // Clear selection when changing month
    setShowDetails(false); // Hide details when changing month
    if (onDateSelect) {
      onDateSelect(null, []); // Clear map
    }
  };

  const goToNextMonth = () => {
    setCurrentMonth(prevMonth => new Date(prevMonth.getFullYear(), prevMonth.getMonth() + 1, 1));
    setSelectedDate(null); // Clear selection when changing month
    setShowDetails(false); // Hide details when changing month
    if (onDateSelect) {
      onDateSelect(null, []); // Clear map
    }
  };

  return (
    <div className={`calendar-view-container ${className}`}>
      <div className="calendar-navigation" style={{ maxWidth: calendarWidth }}>
        <button onClick={goToPreviousMonth}>&lt;</button>
        <h2>{currentMonth.toLocaleString('default', { month: 'long', year: 'numeric' })}</h2>
        <button onClick={goToNextMonth}>&gt;</button>
      </div>
      <div className="calendar-grid" style={{ maxWidth: calendarWidth }}>
        <div className="days-of-week">
          <div>Sun</div>
          <div>Mon</div>
          <div>Tue</div>
          <div>Wed</div>
          <div>Thu</div>
          <div>Fri</div>
          <div>Sat</div>
        </div>
        <div className="days-of-month">
          {renderCalendar()}
        </div>
      </div>
    </div>
  );
};

export default CalendarView;
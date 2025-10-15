import { useState } from 'react';
import '../components.css';

const InputForm = ({ onSubmit, isLoading }) => {
  const [region, setRegion] = useState('서울');
  const [startDate, setStartDate] = useState('2025-10-20');
  const [endDate, setEndDate] = useState('2025-10-22');
  const [age, setAge] = useState(30);
  const [gender, setGender] = useState('남성');
  const [interests, setInterests] = useState(['음식', '문화']);

  const handleInterestChange = (e) => {
    const { value, checked } = e.target;
    if (checked) {
      setInterests((prev) => [...prev, value]);
    } else {
      setInterests((prev) => prev.filter((interest) => interest !== value));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ region, startDate, endDate, age, gender, interests });
  };

  return (
    <form onSubmit={handleSubmit} className="form-container">
      <h2>여행 정보 입력</h2>
      
      <div className="form-group">
        <label>지역</label>
        <select value={region} onChange={(e) => setRegion(e.target.value)}>
          <option value="서울">서울</option>
          <option value="부산">부산</option>
          <option value="제주">제주</option>
          <option value="전주">전주</option>
        </select>
      </div>

      <div className="form-group">
        <label>여행 시작일</label>
        <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
      </div>

      <div className="form-group">
        <label>여행 종료일</label>
        <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
      </div>

      <div className="form-group">
        <label>나이</label>
        <input type="number" value={age} onChange={(e) => setAge(parseInt(e.target.value, 10))} />
      </div>

      <div className="form-group">
        <label>성별</label>
        <select value={gender} onChange={(e) => setGender(e.target.value)}>
          <option value="남성">남성</option>
          <option value="여성">여성</option>
        </select>
      </div>

      <div className="form-group">
        <label>관심사</label>
        <div className="checkbox-group">
          {['음식', '문화', '자연', '쇼핑'].map((interest) => (
            <label key={interest}>
              <input
                type="checkbox"
                value={interest}
                checked={interests.includes(interest)}
                onChange={handleInterestChange}
              />
              {interest}
            </label>
          ))}
        </div>
      </div>

      <button type="submit" disabled={isLoading}>
        {isLoading ? '추천 생성 중...' : 'AI 추천 받기'}
      </button>
    </form>
  );
};

export default InputForm;

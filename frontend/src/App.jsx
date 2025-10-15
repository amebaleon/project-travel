import { useState } from 'react';
import InputForm from './components/InputForm';
import './App.css'; // App.css를 다시 포함시킵니다.

import ResultsDisplay from './components/ResultsDisplay';

function App() {
  const [page, setPage] = useState('input');
  const [recommendations, setRecommendations] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleRecommend = async (formData) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('http://127.0.0.1:8000/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          // interests는 예시 데이터에 맞게 배열로 전달
          interests: formData.interests,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'API 요청에 실패했습니다.');
      }

      const data = await response.json();
      setRecommendations(data);
      setPage('results');
    } catch (err) {
      setError(err.message);
      // 에러 발생 시 입력 페이지에 머무르도록 페이지 전환 로직을 제거합니다.
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    setPage('input');
    setRecommendations(null);
  };

  return (
    <div className="app-container">
      {error && <div className="error-message">오류: {error}</div>}
      {page === 'input' ? (
        <InputForm onSubmit={handleRecommend} isLoading={isLoading} />
      ) : (
        <ResultsDisplay data={recommendations} onBack={handleBack} />
      )}
    </div>
  );
}

export default App;

import React from "react";

export default function TravelInput({ query, setQuery, onClose }) {
  return (
    <section style={{ maxWidth: 640 }}>
      <h2>여행 검색 (입력 화면)</h2>
      <input
        aria-label="travel-input"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="가고 싶은 곳을 입력하세요"
        style={{
          width: "100%",
          padding: 8,
          fontSize: 16,
          boxSizing: "border-box",
        }}
      />
      <div style={{ marginTop: 12 }}>
        <button onClick={() => onClose && onClose()} style={{ marginRight: 8 }}>
          시작
        </button>
        <button onClick={() => setQuery("")}>초기화</button>
      </div>
      <p style={{ color: "#666", marginTop: 12 }}>
        입력 화면이 아니면 배경 이미지가 자동으로 전환됩니다.
      </p>
    </section>
  );
}

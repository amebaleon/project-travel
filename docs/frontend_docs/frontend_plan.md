# 프론트엔드 구현 계획 (수정안)

이 문서는 AI 여행 추천 서비스의 프론트엔드 구현 계획을 상세히 정의합니다.

---

### 1. 개요

- **핵심 목표:** 사용자가 여행 정보를 입력하는 페이지와 AI 추천 결과를 보여주는 페이지를 분리하여, 사용자 경험과 유지보수성을 향상시킨다.
- **기술 스택:** React, Bootstrap, `react-router-dom`, `react-kakao-maps-sdk`
- **라우팅 전략:** **Hash Router** (`HashRouter`)를 사용하여, 서버 설정 없이 클라이언트 사이드 라우팅을 간편하게 구현합니다. (예: `/#/`, `/#/result`)

---

### 2. 페이지 (Screens)

`react-router-dom`으로 관리되는 최상위 화면 단위입니다.

- **`HomePage.jsx` (경로: `/#/`)**

  - **역할:** 애플리케이션의 메인 페이지. 사용자가 여행 조건을 입력하는 UI를 제공합니다.

- **`ResultPage.jsx` (경로: `/#/result`)**
  - **역할:** AI의 여행 추천 결과를 보여주는 페이지. URL의 쿼리 파라미터를 읽어 API를 호출하고, 그 결과를 지도와 카드 리스트 형태로 시각화합니다.

---

### 3. 컴포넌트 상세 구조

#### `App.jsx` (애플리케이션 최상위)

- **역할:** `HashRouter`를 사용하여 각 URL 경로에 맞는 페이지 컴포넌트(`HomePage`, `ResultPage`)를 연결하고 렌더링합니다.

---

#### `pages/HomePage.jsx` (메인 페이지)

- **역할:** 사용자 입력을 받고, 입력된 정보를 바탕으로 결과 페이지로 이동시키는 역할을 합니다.
- **상태 (State):**
  - `formData`: 사용자가 입력하는 폼 데이터(지역, 날짜, 나이 등)를 관리하는 객체.
- **주요 로직:**
  - '추천받기' 버튼 클릭 시, `formData`를 쿼리 스트링으로 변환하여 `/#/result?region=서울&...` 형태로 만든 후, 해당 URL로 이동시킵니다.
- **포함하는 컴포넌트:**

  - **`components/UserInputForm.jsx`**
    - **역할:** 지역, 날짜, 나이, 성별, 관심사 등 실제 입력 UI들을 포함하는 폼.
    - **Props:**
      - `formData` (Object): 현재 폼 데이터를 표시하기 위해 상위(`HomePage`)에서 전달받음.
      - `onFormChange` (Function): 폼 내용 변경 시 상위(`HomePage`)의 `formData` 상태를 업데이트하는 함수.
      - `onSubmit` (Function): 폼 제출 시 상위(`HomePage`)의 페이지 이동 함수를 호출.

---

#### `pages/ResultPage.jsx` (결과 페이지)

- **역할:** URL의 쿼리 파라미터를 읽어 API를 호출하고, 결과를 자식 컴포넌트에 전달하여 화면에 표시합니다.
- **상태 (State):**
  - `apiResponse`: 백엔드로부터 받은 추천 결과 JSON.
  - `isLoading` (Boolean): API 요청 처리 중 상태 (로딩 스피너 표시용).
  - `error` (Object | String): API 요청 실패 시 에러 정보.
- **주요 로직:**
  - `useEffect` 훅을 사용하여 페이지가 처음 렌더링될 때, URL의 쿼리 파라미터를 읽습니다.
  - 읽어온 파라미터를 바탕으로 백엔드 `/recommend` API를 호출합니다.
  - 응답 결과를 `apiResponse`, `isLoading`, `error` 상태에 저장합니다.
- **포함하는 컴포넌트:**

  - **`components/ResultDisplay.jsx`**

    - **역할:** `isLoading`, `error`, `apiResponse` 상태에 따라 로딩 UI, 에러 메시지, 또는 실제 결과(`MapView`, `DailyPlanList`)를 선택적으로 보여주는 컨테이너.
    - **Props:**
      - `isLoading` (Boolean)
      - `error` (Object | String)
      - `response` (Object)

  - **`components/MapView.jsx`**

    - **역할:** `react-kakao-maps-sdk`를 사용하여 추천된 모든 장소의 위치를 지도에 마커로 표시.
    - **Props:**
      - `places` (Array): 추천된 모든 장소의 이름과 좌표(`latitude`, `longitude`)가 담긴 배열.

  - **`components/DailyPlanList.jsx`**

    - **역할:** 일자별 추천 계획을 리스트 형태로 보여주기 위해 `DailyPlanCard`들을 반복 렌더링.
    - **Props:**
      - `dailyPlans` (Array): `response.daily_recommendations` 배열.

  - **`components/DailyPlanCard.jsx`**

    - **역할:** '1일차 (2025-10-26)'와 같이 하루 단위의 추천 목록을 감싸는 카드 UI.
    - **Props:**
      - `plan` (Object): 하루치 계획 데이터 (`{ date, recommendations }`).

  - **`components/RecommendationItem.jsx`**
    - **역할:** 추천된 개별 장소의 상세 정보(이름, 설명, 주소, 이미지 등)를 보여주는 UI.
    - **Props:**
      - `item` (Object): 개별 추천 장소 데이터.

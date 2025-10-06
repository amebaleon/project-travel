# 프론트엔드 구현 계획

이 문서는 AI 여행 추천 서비스의 프론트엔드 구현 계획을 정의합니다.

---

### 1. 핵심 목표

- 사용자가 여행 정보를 입력하고, AI가 추천한 일정을 지도와 함께 확인하는 단일 페이지 애플리케이션(SPA)을 구축합니다.
- **기술 스택:** React, Bootstrap, `react-kakao-maps-sdk`

---

### 2. 화면 (Screens)

- **`MainPage` (메인 페이지):** 우리 애플리케이션의 유일한 페이지입니다. 이 페이지 안에 아래에 설명할 모든 컴포넌트가 포함됩니다.

---

### 3. 컴포넌트 구조 및 Props

`src/` 폴더 아래에 `components` 폴더를 만들어 컴포넌트들을 관리합니다.

**`App.jsx` (최상위 컴포넌트)**

- **역할:** 전체 레이아웃(예: 헤더, 푸터)을 관리하고, `MainPage`를 렌더링합니다.
- **상태(State):**
    - `apiResponse`: 백엔드로부터 받은 전체 추천 결과(JSON)를 저장합니다.
    - `isLoading`: API 요청이 진행 중인지 여부를 저장합니다. (로딩 스피너 표시용)
    - `error`: API 요청 실패 시 에러 메시지를 저장합니다.

**1. `UserInputForm.jsx` (사용자 입력 폼)**

- **역할:** 지역, 날짜, 나이, 성별, 관심사 등 모든 사용자 입력을 받는 폼 영역입니다.
- **Props:**
    - `onSubmit(formData)` (함수): '추천받기' 버튼 클릭 시 `App.jsx`에 있는 API 요청 함수를 호출합니다. `formData`에는 모든 입력값이 담겨 있습니다.
    - `isLoading` (boolean): 로딩 중일 때 '추천받기' 버튼을 비활성화하는 데 사용됩니다.

**2. `ResultDisplay.jsx` (결과 표시 영역)**

- **역할:** API 응답 상태에 따라 로딩 스피너, 에러 메시지, 또는 실제 추천 결과를 보여주는 컨테이너입니다.
- **Props:**
    - `apiResponse` (객체): `App.jsx`로부터 받은 API 응답 데이터 전체입니다.
    - `isLoading` (boolean): 로딩 상태.
    - `error` (객체 또는 문자열): 에러 상태.

**3. `MapView.jsx` (지도 뷰)**

- **역할:** `react-kakao-maps-sdk`를 사용하여 추천된 모든 장소의 위치를 지도에 마커로 표시합니다.
- **Props:**
    - `dailyPlans` (배열): 추천된 모든 일자별 계획 데이터 (`apiResponse.daily_recommendations`). 이 안의 장소 좌표를 사용하여 마커를 찍습니다.

**4. `DailyPlanList.jsx` (일자별 추천 목록)**

- **역할:** 여러 개의 `DailyPlanCard`를 리스트 형태로 렌더링합니다.
- **Props:**
    - `dailyPlans` (배열): `apiResponse.daily_recommendations` 데이터를 받습니다.

**5. `DailyPlanCard.jsx` (일자별 추천 카드)**

- **역할:** "1일차 (2025-10-26)" 와 같이 하루의 추천 목록을 감싸는 카드입니다.
- **Props:**
    - `plan` (객체): 하루치 계획 데이터 (`{ date: "...", recommendations: [...] }`).

**6. `RecommendationItem.jsx` (개별 추천 항목)**

- **역할:** 추천된 개별 장소(관광지, 음식점 등)의 상세 정보를 보여주는 UI 요소입니다. (Bootstrap Card 활용)
- **Props:**
    - `item` (객체): 개별 추천 장소 데이터 (`{ name, description, address, image_url, ... }`).

---

### 4. 데이터 흐름

1.  사용자가 **`UserInputForm`**에 정보를 입력합니다.
2.  '추천받기' 버튼을 누르면 `onSubmit` 함수가 호출되어 **`App.jsx`**로 모든 입력 데이터가 전달됩니다.
3.  **`App.jsx`**는 `isLoading` 상태를 `true`로 바꾸고, 백엔드 `/recommend` API를 호출합니다.
4.  API 응답이 오면, `isLoading`을 `false`로 바꾸고, 성공 시 `apiResponse` 상태에 결과를 저장하고, 실패 시 `error` 상태에 에러를 저장합니다.
5.  **`ResultDisplay`**는 `isLoading`, `error`, `apiResponse` 상태가 변경됨에 따라 자동으로 리렌더링되어 로딩 스피너, 에러 메시지, 또는 결과(`MapView`, `DailyPlanList`)를 화면에 보여줍니다.

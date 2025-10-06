# 파일 및 함수 설명 가이드

이 문서는 백엔드 애플리케이션을 구성하는 각 파일과 주요 함수의 역할 및 기능에 대해 설명합니다.

---

## 1. `main.py`

- **역할**: FastAPI 애플리케이션의 진입점(Entry Point)입니다. 현재는 `uvicorn`을 직접 실행하는 대신, `backend` 폴더의 `main.py`가 이 역할을 수행합니다. (이 파일은 추후 uvicorn 실행 스크립트로 사용될 수 있습니다.)

---

## 2. `src/app.py`

- **역할**: FastAPI 앱의 핵심 설정과 API 엔드포인트를 정의하는 파일입니다.

- **주요 함수:**
  - `startup_event()`: 애플리케이션이 시작될 때 단 한 번 실행됩니다. 데이터베이스 테이블 생성, 데이터 로딩, 주간 데이터 업데이트 스케줄링 등의 초기화 작업을 수행합니다.
  - `recommend(user_request: UserRequest, db: Session)`: `/recommend` 경로의 POST 요청을 처리하는 메인 API 엔드포인트입니다. 사용자 요청을 받아 DB에서 정보를 조회하고, AI 모델을 호출하여 최종 추천 결과를 반환하며, 모든 과정을 로그로 기록합니다.

---

## 3. `src/db.py`

- **역할**: 데이터베이스와의 모든 상호작용(연결, 세션, 스키마, CRUD)을 관리하는 파일입니다.

- **주요 함수:**
  - `get_db()`: API 요청마다 독립적인 데이터베이스 세션을 생성하고, 요청이 끝나면 세션을 닫는 의존성 주입 함수입니다.
  - `fetch_and_store_tour_data()`: Tour API로부터 데이터를 가져와 DB에 저장하는 함수입니다. (현재는 `seed_data.py`의 더미 데이터를 사용)
  - `schedule_tour_data_update()`: `fetch_and_store_tour_data` 함수를 매주 월요일 0시에 실행하도록 스케줄링합니다.
  - `get_tourist_info_from_db(...)`: 사용자의 요청(지역, 관심사, 날짜)에 맞는 관광 정보를 데이터베이스에서 조회하고, 결과를 딕셔너리 리스트로 반환합니다.
  - `log_ai_interaction(...)`: AI 추천 과정의 모든 정보(사용자 요청, AI 응답, 토큰 사용량 등)를 `ai_log` 테이블에 저장합니다.

---

## 4. `src/llm.py`

- **역할**: OpenAI의 언어 모델(LLM) 및 LangChain Agent와 관련된 모든 로직을 처리하는 파일입니다.

- **주요 함수:**
  - `generate_initial_recommendations(...)`: 사용자의 요청과 DB에서 조회한 관광지 목록을 프롬프트로 구성하여, GPT-5-mini 모델을 호출하고 초기 여행 추천 JSON을 생성합니다.
  - `verify_recommendation_with_agent(...)`: 정보 변동성이 높은(`is_variable=True`) 장소에 대해, 웹 검색 Agent를 호출하여 실시간 정보(운영 여부, 가격 등)를 검증합니다.
  - `get_ai_recommendations(...)`: AI 추천의 전체 과정을 총괄하는 메인 함수입니다. 초기 추천 생성, 실시간 정보 검증, 최종 응답 객체 생성을 모두 담당합니다.

---

## 5. `src/openapi.py`

- **역할**: API의 데이터 구조(Pydantic 모델)와 데이터베이스 테이블 구조(SQLAlchemy ORM 모델)를 함께 정의하는 파일입니다.

- **주요 클래스:**
  - `UserRequest`: `/recommend` API가 받는 사용자 요청의 데이터 형식을 정의합니다.
  - `RecommendationResponse`: `/recommend` API가 반환하는 최종 응답의 데이터 형식을 정의합니다.
  - `TouristInfo`: `tourist_info` 데이터베이스 테이블의 구조를 파이썬 클래스로 정의한 ORM 모델입니다. `to_dict()` 메서드를 포함하여 객체를 딕셔너리로 쉽게 변환할 수 있습니다.
  - `AiLog`: `ai_log` 테이블의 구조를 정의한 ORM 모델입니다.

---

## 6. `src/seed_data.py`

- **역할**: 개발 및 테스트 단계에서 사용할 초기 더미 데이터를 정의하는 파일입니다.

- **주요 함수:**
  - `insert_dummy_tour_data(db: Session)`: 미리 정의된 다양한 지역의 관광지, 음식점, 축제 데이터를 `TouristInfo` 객체 리스트로 생성하여 DB 세션에 추가합니다.

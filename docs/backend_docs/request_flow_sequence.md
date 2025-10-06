# 요청 처리 순서 (`/recommend`)

이 문서는 사용자가 `/recommend` API에 여행 추천을 요청했을 때, 백엔드 시스템 내부에서 어떤 순서로 데이터가 흐르고 함수가 호출되는지 단계별로 설명합니다.

---

### 전체 흐름 요약

`사용자 요청` -> `API 엔드포인트 (app.py)` -> `DB 조회 (db.py)` -> `AI 추천 생성 (llm.py)` -> `(실시간 검증)` -> `AI 로그 저장 (db.py)` -> `최종 응답`

---

### 상세 처리 순서

**1. HTTP 요청 수신**

-   **파일**: `src/app.py`
-   **함수**: `recommend(user_request: UserRequest, ...)`
-   **설명**: 사용자가 `POST /recommend` 경로로 보낸 HTTP 요청을 FastAPI가 수신합니다. 요청 본문(Body)에 포함된 JSON 데이터는 `UserRequest` Pydantic 모델로 자동 변환 및 검증됩니다.
    -   **입력**: `user_request` (지역, 날짜, 나이, 성별, 관심사 포함)
    -   `get_db` 함수가 호출되어 이 요청을 위한 데이터베이스 세션(`db`)이 생성됩니다.

**2. 관광 정보 조회**

-   **파일**: `src/app.py` -> `src/db.py`
-   **함수**: `get_tourist_info_from_db(db, region, interests, ...)`
-   **설명**: `app.py`의 `recommend` 함수가 `db.py`의 `get_tourist_info_from_db` 함수를 호출하여 AI에게 전달할 관광지 목록을 가져옵니다.
    -   **파라미터**: `db` 세션, `user_request`의 `region`, `interests`, `start_date`, `end_date`가 인자로 전달됩니다.
    -   함수 내부에서는 이 인자들을 사용하여 SQLAlchemy 쿼리를 생성하고, 데이터베이스에서 조건에 맞는 `TouristInfo` 레코드들을 조회합니다.
    -   조회된 각 레코드는 `to_dict()` 메서드를 통해 딕셔너리로 변환됩니다.
    -   **반환**: 관광지 정보가 담긴 딕셔너리 리스트(`List[dict]`)가 `app.py`로 반환됩니다.

**3. AI 추천 생성 요청**

-   **파일**: `src/app.py` -> `src/llm.py`
-   **함수**: `get_ai_recommendations(user_request, tourist_info_data)`
-   **설명**: `app.py`가 `llm.py`의 `get_ai_recommendations` 함수를 호출하여 본격적인 AI 추천 생성을 시작합니다.
    -   **파라미터**: `user_request` (딕셔너리 형태)와 2단계에서 얻은 관광지 딕셔너리 리스트(`tourist_info_data`)가 인자로 전달됩니다.

**4. 초기 추천 목록 생성 (LLM 호출)**

-   **파일**: `src/llm.py`
-   **함수**: `generate_initial_recommendations(user_request, tourist_info_json)`
-   **설명**: `get_ai_recommendations` 함수 내부에서 호출됩니다. AI에게 보낼 프롬프트를 만들고 GPT-5-mini 모델을 직접 호출합니다.
    -   `INITIAL_RECOMMENDATION_PROMPT_TEMPLATE`에 사용자 정보와 관광지 목록(JSON 문자열)을 채워 전체 프롬프트를 완성합니다.
    -   OpenAI API를 호출하여 초기 여행 추천이 담긴 JSON 응답 문자열을 받습니다.
    -   **반환**: AI가 생성한 추천 목록 JSON 문자열과 사용된 토큰 수를 `get_ai_recommendations` 함수로 반환합니다.

**5. 실시간 정보 검증 (Agent 호출)**

-   **파일**: `src/llm.py`
-   **함수**: `verify_recommendation_with_agent(item_name, content_id, ...)`
-   **설명**: `get_ai_recommendations` 함수가 4단계에서 받은 추천 목록을 하나씩 확인합니다. 만약 추천된 장소의 `is_variable` 속성이 `True`이면, 이 함수를 호출하여 실시간 검증을 수행합니다.
    -   `VERIFICATION_PROMPT_TEMPLATE`에 검증할 장소의 정보를 채워 Agent용 프롬프트를 완성합니다.
    -   LangChain의 `agent_executor`가 웹 검색 도구(`DuckDuckGoSearchRun`)를 사용하여 정보 검증을 시도합니다.
    -   **반환**: 검증 결과가 담긴 JSON 문자열을 `get_ai_recommendations` 함수로 반환합니다. (현재는 인증 문제로 실제 검색은 동작하지 않음)

**6. 최종 응답 생성**

-   **파일**: `src/llm.py`
-   **함수**: `get_ai_recommendations(...)`
-   **설명**: `get_ai_recommendations` 함수는 4단계의 초기 추천과 5단계의 검증 결과를 종합하여, API 명세에 맞는 최종 `RecommendationResponse` Pydantic 모델 객체를 생성합니다.
    -   **반환**: `RecommendationResponse` 객체가 `app.py`로 반환됩니다.

**7. AI 상호작용 로그 저장**

-   **파일**: `src/app.py` -> `src/db.py`
-   **함수**: `log_ai_interaction(db, ...)`
-   **설명**: `app.py`의 `recommend` 함수는 최종 응답을 사용자에게 보내기 직전에, `db.py`의 `log_ai_interaction` 함수를 호출하여 추천 과정의 모든 기록을 `ai_log` 테이블에 저장합니다.
    -   **파라미터**: 사용자 요청, 최종 AI 응답, 토큰 사용량, Agent 로그 등이 인자로 전달됩니다.

**8. HTTP 응답 반환**

-   **파일**: `src/app.py`
-   **함수**: `recommend(...)`
-   **설명**: `log_ai_interaction` 함수 호출 후, `app.py`는 6단계에서 받은 `RecommendationResponse` 객체를 최종 HTTP 응답으로 변환하여 사용자(클라이언트)에게 전송합니다.

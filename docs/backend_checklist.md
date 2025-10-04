# 백엔드 개발 체크리스트

## 1. 프로젝트 설정 및 데이터 모델링

- [x] 1.1. **`main.py`**: uvicorn 서버 실행을 위한 기본 시작점 코드 작성
- [x] 1.2. **`openapi.py`**: 사용자 요청(`UserRequest`) Pydantic 모델 정의
- [x] 1.3. **`openapi.py`**: AI 추천 단일 항목(`RecommendationItem`) Pydantic 모델 정의
- [x] 1.4. **`openapi.py`**: 최종 API 응답(`RecommendationResponse`) Pydantic 모델 정의
- [x] 1.5. **`openapi.py`**: `tourist_info` 테이블을 위한 SQLAlchemy ORM 모델(`TouristInfo`) 정의
- [x] 1.6. **`openapi.py`**: `ai_log` 테이블을 위한 SQLAlchemy ORM 모델(`AiLog`) 정의

## 2. 데이터베이스 및 데이터 캐싱

- [x] 2.1. **`db.py`**: SQLAlchemy와 `.env` 파일을 이용한 데이터베이스 연결 설정
- [x] 2.2. **`db.py`**: 데이터베이스 세션 관리를 위한 `get_db` 함수 구현
- [x] 2.3. **`db.py`**: DB 스키마(`app.sql`)와 ORM 모델 일치 여부 확인
- [x] 2.4. **`db.py`**: Tour API로부터 관광 데이터를 가져오는 외부 API 연동 함수 구현
- [x] 2.5. **`db.py`**: `APScheduler`를 사용하여 매주 Tour API 데이터를 DB에 저장하는 스케줄링 작업 설정
- [x] 2.6. **`db.py`**: `tourist_info` 테이블에서 조건에 맞는 관광 정보를 조회하는 함수 구현
- [x] 2.7. **`db.py`**: AI 상호작용 로그를 `ai_log` 테이블에 저장하는 함수 구현

## 3. AI 및 Agent 핵심 로직

- [ ] 3.1. **`llm.py`**: OpenAI GPT-5 mini API 클라이언트 초기화
- [ ] 3.2. **`llm.py`**: LangChain의 `DuckDuckGoSearchRun` 도구 정의
- [ ] 3.3. **`llm.py`**: LLM과 검색 도구를 결합하여 실시간 검증 Agent 생성
- [ ] 3.4. **`llm.py`**: 초기 추천을 위한 프롬프트 템플릿 작성
- [ ] 3.5. **`llm.py`**: LLM을 호출하여 초기 추천 목록을 생성하는 함수 구현
- [ ] 3.6. **`llm.py`**: Agent를 통한 실시간 검증을 위한 프롬프트 템플릿 작성
- [ ] 3.7. **`llm.py`**: `is_variable` 플래그가 지정된 항목에 대해 Agent를 호출하여 정보(운영 여부, 가격 등)를 검증하는 함수 구현 (타임아웃 포함)
- [ ] 3.8. **`llm.py`**: AI 추천 생성 및 검증 과정을 총괄하는 메인 함수 구현
- [ ] 3.9. **`llm.py`**: 최종 AI 응답을 Pydantic 모델에 맞춰 파싱하고 유효성을 검증하는 기능 추가

## 4. API 엔드포인트 및 통합

- [ ] 4.1. **`app.py`**: FastAPI 앱 인스턴스 생성 및 `/recommend` 엔드포인트 기본 구조 작성
- [ ] 4.2. **`app.py`**: `/recommend`에서 `db.py`를 호출하여 사용자 요청에 맞는 DB 데이터를 가져오는 로직 연동
- [ ] 4.3. **`app.py`**: `/recommend`에서 `llm.py`를 호출하여 AI 추천 및 검증 결과를 가져오는 로직 연동
- [ ] 4.4. **`app.py`**: `/recommend`에서 `db.py`를 호출하여 AI 상호작용을 로깅하는 로직 연동
- [ ] 4.5. **`app.py`**: 최종 결과를 `RecommendationResponse` 모델에 맞춰 클라이언트에 반환하도록 구현

## 5. 최종화

- [ ] 5.1. **전체 코드 검토**: 주석, 타입 힌트, PRD 요구사항 준수 여부 최종 확인
- [ ] 5.2. **`.env.example` 파일 생성**: 필요한 환경 변수 목록을 명시한 예제 파일 생성

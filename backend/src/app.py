"""
FastAPI 메인 파일임. API 엔드포인트, 앱 시작 이벤트, 의존성 주입 정의하는 곳.
"""

import logging
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.openapi import UserRequest, RecommendationResponse
from src.llm import get_ai_recommendations
from src.db import get_db, get_tourist_info_from_db, log_ai_interaction, schedule_tour_data_update, fetch_and_store_tour_data

# 로거 설정하는거
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# FastAPI 앱 인스턴스 만드는거
app = FastAPI(
    title="AI Travel Recommender API",
    description="사용자 맞춤형 여행 일정을 추천하는 AI 기반 API",
    version="1.0.0"
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 프론트엔드 서버 주소
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)


@app.on_event("startup")
async def startup_event():
    """
    앱 시작될 때 실행되는 이벤트 핸들러임.
    - DB 스키마는 db.py에서 초기화됨.
    - 매주 데이터 업데이트 스케줄링 햇음.
    - 앱 시작할 때 데이터 바로 채워넣음.
    """
    logger.info("[App] 애플리케이션 시작 이벤트가 트리거되었습니다.")
    
    # 1. 매주 데이터 업데이트 스케줄링 하는거
    schedule_tour_data_update()
    
    # 2. 시작할때 바로 데이터 채움
    # (db.py에서 테이블 맨날 지우고 다시 만드니까, 항상 최신 더미 데이터로 채워지는거임)
    fetch_and_store_tour_data()
    logger.info("[App] 애플리케이션 시작 준비가 완료되었습니다.")


@app.post("/recommend", response_model=RecommendationResponse)
async def recommend(user_request: UserRequest, db: Session = Depends(get_db)):
    """
    사용자 요청 받아서 AI 여행 추천 반환하는 메인 API 엔드포인트임.

    흐름:
    1. 사용자 요청(지역, 관심사, 날짜)에 맞는 관광 정보 DB에서 조회하는거.
    2. 조회된 데이터랑 사용자 요청을 LLM(`get_ai_recommendations`)에 넘겨서 추천 결과 받는거.
    3. AI 상호작용(요청, 응답, 검증 결과)을 DB에 기록하는거.
    4. 최종 추천 결과를 클라이언트한테 반환하는거.
    """
    logger.info(f"[App] /recommend 엔드포인트 호출됨. 요청: {user_request.model_dump_json()}")

    # 1. DB에서 조건 맞는 관광 정보 조회하는거
    tourist_info_data = get_tourist_info_from_db(
        db=db,
        region=user_request.region,
        interests=user_request.interests,
        start_date=user_request.start_date,
        end_date=user_request.end_date
    )

    # 조회된 정보 없으면 404 에러 반환하는거
    if not tourist_info_data:
        logger.warning("[App] 사용자의 요청에 맞는 관광 정보를 DB에서 찾을 수 없습니다.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="요청하신 지역과 관심사에 맞는 관광 정보를 찾을 수 없습니다."
        )

    # 2. LLM 불러서 AI 추천 만드는거
    try:
        ai_response = await get_ai_recommendations(user_request.model_dump(), tourist_info_data)
    except Exception as e:
        logger.error(f"[App] AI 추천 생성 중 심각한 오류 발생: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 추천 생성에 실패했습니다: {e}"
        )

    # 3. AI 상호작용 결과 기록하는거
    # 에러 발생해도 사용자한테 추천 결과 그냥 반환하는거
    try:
        log_ai_interaction(
            db=db,
            request_time=datetime.now(),
            user_input_json=user_request.model_dump_json(),
            ai_response_json=ai_response.model_dump_json(),
            total_tokens=ai_response.total_tokens,
            agent_search_log=ai_response.agent_search_log,
            is_verified_success=ai_response.is_verified_success
        )
    except Exception as e:
        logger.error(f"[App] AI 상호작용 로그 저장 실패: {e}", exc_info=True)
        # 로깅 실패가 메인 기능에 영향 안주게 예외 처리하는거

    logger.info("[App] 성공적으로 AI 추천 응답을 반환합니다.")
    return ai_response
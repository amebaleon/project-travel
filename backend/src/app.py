"""
FastAPI 애플리케이션의 메인 파일입니다.
API 엔드포인트, 애플리케이션 시작 이벤트, 의존성 주입 등을 정의합니다.
"""

import logging
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.openapi import UserRequest, RecommendationResponse
from src.llm import get_ai_recommendations
from src.db import get_db, get_tourist_info_from_db, log_ai_interaction, schedule_tour_data_update, fetch_and_store_tour_data

# 로거 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="AI Travel Recommender API",
    description="사용자 맞춤형 여행 일정을 추천하는 AI 기반 API",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """
    애플리케이션이 시작될 때 실행되는 이벤트 핸들러입니다.
    - 데이터베이스 스키마는 db.py에서 초기화됩니다.
    - 주간 데이터 업데이트를 스케줄링합니다.
    - 애플리케이션 시작 시 즉시 데이터를 채웁니다.
    """
    logger.info("[App] 애플리케이션 시작 이벤트가 트리거되었습니다.")
    
    # 1. 주간 데이터 업데이트 스케줄링
    schedule_tour_data_update()
    
    # 2. 시작 시 즉시 데이터 채우기
    # (db.py에서 테이블을 매번 삭제하고 다시 생성하므로, 항상 최신 더미 데이터가 채워집니다.)
    fetch_and_store_tour_data()
    logger.info("[App] 애플리케이션 시작 준비가 완료되었습니다.")


@app.post("/recommend", response_model=RecommendationResponse)
async def recommend(user_request: UserRequest, db: Session = Depends(get_db)):
    """
    사용자 요청을 받아 AI 기반 여행 추천을 반환하는 메인 API 엔드포인트입니다.

    동작 흐름:
    1. 사용자 요청(지역, 관심사, 날짜)에 맞는 관광 정보를 데이터베이스에서 조회합니다.
    2. 조회된 데이터와 사용자 요청을 LLM(`get_ai_recommendations`)에 전달하여 추천 결과를 받습니다.
    3. AI 상호작용(요청, 응답, 검증 결과)을 데이터베이스에 로깅합니다.
    4. 최종 추천 결과를 클라이언트에게 반환합니다.
    """
    logger.info(f"[App] /recommend 엔드포인트 호출됨. 요청: {user_request.model_dump_json()}")

    # 1. 데이터베이스에서 조건에 맞는 관광 정보 조회
    tourist_info_data = get_tourist_info_from_db(
        db=db,
        region=user_request.region,
        interests=user_request.interests,
        start_date=user_request.start_date,
        end_date=user_request.end_date
    )

    # 조회된 정보가 없으면 404 오류 반환
    if not tourist_info_data:
        logger.warning("[App] 사용자의 요청에 맞는 관광 정보를 DB에서 찾을 수 없습니다.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="요청하신 지역과 관심사에 맞는 관광 정보를 찾을 수 없습니다."
        )

    # 2. LLM을 호출하여 AI 추천 생성
    try:
        ai_response = await get_ai_recommendations(user_request.model_dump(), tourist_info_data)
    except Exception as e:
        logger.error(f"[App] AI 추천 생성 중 심각한 오류 발생: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 추천 생성에 실패했습니다: {e}"
        )

    # 3. AI 상호작용 결과 로깅
    # 이 과정에서 오류가 발생하더라도 사용자에게는 추천 결과를 그대로 반환합니다.
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
        # 로깅 실패가 주 기능에 영향을 주지 않도록 예외를 다시 발생시키지 않음

    logger.info("[App] 성공적으로 AI 추천 응답을 반환합니다.")
    return ai_response
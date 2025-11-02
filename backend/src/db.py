"""
DB 연결, 세션 관리, 스키마 생성, 데이터 CRUD 함수들이 잇는
DB 상호작용 핵심 로직 파일임.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, or_, text, and_
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, List, Optional
from datetime import date, datetime
from apscheduler.schedulers.background import BackgroundScheduler

import logging

from src.openapi import Base, TouristInfo, AiLog # ORM 모델 가져오는거
from src.models import UserRequest, VerificationDetails, RecommendationItem, DailyRecommendation, RecommendationResponse

# 로거 설정하는거
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- DB 설정하는거 ---

# .env 파일에서 환경 변수 불러오는거
# 프로젝트 루트의 .env 파일 경로 정확하게 지정해야함.
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL 환경 변수가 .env 파일에 설정되지 않았습니다.")

logger.info(f"[DB] 데이터베이스 연결 URL을 사용합니다: {DATABASE_URL}")

# SQLAlchemy 엔진이랑 세션 만드는거
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- DB 스키마 관리하는거 ---

# 앱 시작할때 테이블 스키마 초기화하는거.
# checkfirst=True: 테이블 잇을때만 삭제해서 필요없는 에러 막는거.

logger.info("[DB] 모든 테이블을 ORM 모델 정의에 따라 생성합니다.")
Base.metadata.create_all(bind=engine)


# --- DB 세션 의존성 주입하는거 ---

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI 의존성 주입 시스템에서 쓸 DB 세션 생성기임.
    API 요청마다 독립적인 세션을 주고, 요청 끝나면 세션 알아서 닫음.

    Yields:
        Session: SQLAlchemy DB 세션 객체
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# --- 데이터 조회랑 로깅하는거 ---

def log_ai_interaction(
    db: Session,
    request_time: datetime,
    user_input_json: str,
    ai_response_json: str,
    total_tokens: Optional[int],
    agent_search_log: Optional[str],
    is_verified_success: bool
):
    """
    AI 상호작용 로그(사용자 요청, AI 응답, 검증 결과 등)를 ai_log 테이블에 저장함.

    Args:
        db (Session): DB 세션.
        request_time (datetime): 요청 시간.
        user_input_json (str): JSON 형식의 사용자 입력.
        ai_response_json (str): JSON 형식의 AI 응답.
        total_tokens (Optional[int]): 사용된 총 토큰 수.
        agent_search_log (Optional[str]): Agent의 검색 과정 로그.
        is_verified_success (bool): 최종 검증 성공 여부.
    """
    try:
        ai_log_entry = AiLog(
            request_time=request_time,
            user_input_json=user_input_json,
            ai_response_json=ai_response_json,
            total_tokens=total_tokens,
            agent_search_log=agent_search_log,
            is_verified_success=is_verified_success
        )
        db.add(ai_log_entry)
        db.commit()
        db.refresh(ai_log_entry)
        logger.info(f"[DB] AI 상호작용 로그가 성공적으로 저장되었습니다 (ID: {ai_log_entry.log_id}).")
    except Exception as e:
        db.rollback()
        logger.error(f"[DB] AI 상호작용 로그 저장 중 오류 발생: {e}")

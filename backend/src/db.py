"""
데이터베이스 연결, 세션 관리, 스키마 생성 및 데이터 CRUD(생성, 읽기, 업데이트, 삭제) 함수를 포함하는
데이터베이스 상호작용의 핵심 로직 파일입니다.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, or_, text, and_
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, List, Optional
from datetime import date, datetime
from apscheduler.schedulers.background import BackgroundScheduler

import logging

from src.openapi import Base, TouristInfo, AiLog # ORM 모델 임포트
from src.seed_data import insert_dummy_tour_data # seed_data.py에서 함수 임포트

# 로거 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- 데이터베이스 설정 ---

# .env 파일에서 환경 변수 로드
# 프로젝트 루트의 .env 파일 경로를 정확히 지정합니다.
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL 환경 변수가 .env 파일에 설정되지 않았습니다.")

logger.info(f"[DB] 데이터베이스 연결 URL을 사용합니다: {DATABASE_URL}")

# SQLAlchemy 엔진 및 세션 생성
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 데이터베이스 스키마 관리 ---

# 애플리케이션 시작 시 테이블 스키마를 초기화합니다.
# checkfirst=True: 테이블이 존재할 경우에만 삭제 명령을 실행하여 불필요한 오류를 방지합니다.
logger.info("[DB] 기존 tourist_info 테이블을 삭제합니다 (존재하는 경우).")
TouristInfo.__table__.drop(engine, checkfirst=True)

logger.info("[DB] 모든 테이블을 ORM 모델 정의에 따라 생성합니다.")
Base.metadata.create_all(bind=engine)


# --- 데이터베이스 세션 의존성 주입 ---

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI의 의존성 주입 시스템에서 사용할 데이터베이스 세션 생성기입니다.
    API 요청마다 독립적인 세션을 제공하고, 요청이 끝나면 세션을 자동으로 닫습니다.

    Yields:
        Session: SQLAlchemy 데이터베이스 세션 객체
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- 데이터 스케줄링 및 관리 ---

def fetch_and_store_tour_data():
    """
    Tour API로부터 데이터를 가져와 DB에 저장하는 함수 (현재는 더미 데이터 사용).
    APScheduler에 의해 주기적으로 호출됩니다.
    """
    logger.info("[DB] Tour API 데이터 가져오기 및 저장을 시작합니다 (더미 구현).")
    db = SessionLocal()
    try:
        # 앱 시작 시 테이블이 이미 삭제되고 재생성되므로, TRUNCATE는 더 이상 필요하지 않습니다.
        # 더미 데이터 삽입 로직은 seed_data.py의 함수를 호출합니다.
        insert_dummy_tour_data(db)
        db.commit()
        
        # 삽입된 레코드 수 확인 및 로깅
        record_count = db.query(TouristInfo).count()
        logger.info(f"[DB] 더미 데이터 삽입 완료. 총 {record_count}개의 레코드가 tourist_info 테이블에 저장되었습니다.")
    except Exception as e:
        db.rollback()
        logger.error(f"[DB] Tour API 데이터 저장 중 오류 발생: {e}")
    finally:
        db.close()

def schedule_tour_data_update():
    """
    APScheduler를 사용하여 매주 Tour API 데이터를 DB에 업데이트하는 스케줄링을 설정합니다.
    """
    scheduler = BackgroundScheduler()
    # 매주 월요일 0시에 fetch_and_store_tour_data 함수를 실행하도록 작업을 추가합니다.
    scheduler.add_job(fetch_and_store_tour_data, 'cron', day_of_week='mon', hour=0, minute=0)
    scheduler.start()
    logger.info("[DB] Tour API 데이터 주간 자동 업데이트가 스케줄되었습니다.")


# --- 데이터 조회 및 로깅 ---

def get_tourist_info_from_db(db: Session, region: str, interests: List[str], start_date: date, end_date: date) -> List[dict]:
    """
    사용자 요청(지역, 관심사, 여행 기간)에 따라 tourist_info 테이블에서 관광 정보를 조회합니다.

    Args:
        db (Session): 데이터베이스 세션.
        region (str): 필터링할 지역.
        interests (List[str]): 필터링할 관심사 목록.
        start_date (date): 여행 시작일.
        end_date (date): 여행 종료일.

    Returns:
        List[dict]: 조회된 관광 정보의 딕셔너리 리스트.
    """
    logger.info(f"[DB] 관광 정보 조회 시작: region={region}, interests={interests}, start_date={start_date}, end_date={end_date}")
    
    # 기본 쿼리: 지역 필터링
    query = db.query(TouristInfo).filter(TouristInfo.region == region)

    # 관심사 필터링: 하나 이상의 관심사에 대해 OR 조건으로 검색
    if interests:
        or_conditions = [TouristInfo.category_tag.like(f"%{interest}%") for interest in interests]
        query = query.filter(or_(*or_conditions))

    # 날짜 필터링:
    # 1. 축제/행사가 아닌 모든 정보는 항상 포함시킵니다.
    # 2. 축제/행사인 경우, 사용자의 여행 기간과 축제 기간이 하루라도 겹치면 포함시킵니다.
    query = query.filter(
        or_(
            TouristInfo.content_type != "축제/행사",
            and_(
                TouristInfo.start_date <= end_date,
                TouristInfo.end_date >= start_date
            )
        )
    )

    # 쿼리 실행 및 결과 로깅
    # 참고: 아래 로그는 실제 실행될 SQL이 아닌 SQLAlchemy의 쿼리 객체를 보여줍니다.
    logger.info(f"[DB] 실행될 쿼리 객체: {query}")
    tourist_info_records = query.all()
    logger.info(f"[DB] 총 {len(tourist_info_records)}개의 관광 정보를 찾았습니다.")

    # ORM 객체 리스트를 딕셔너리 리스트로 변환 (openapi.py에 정의된 to_dict 사용)
    return [record.to_dict() for record in tourist_info_records]

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
    AI 상호작용 로그(사용자 요청, AI 응답, 검증 결과 등)를 ai_log 테이블에 저장합니다.

    Args:
        db (Session): 데이터베이스 세션.
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

"""
데이터베이스 연결, 세션 관리, Tour API 연동 및 데이터 저장을 담당하는 파일입니다.
"""
import os
import sys
import requests
from datetime import datetime, date # date import 추가
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler # APScheduler import 추가

# 모듈 경로 해결
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.openapi import TouristInfo, AiLog, UserRequest, RecommendationResponse

# .env 파일 로드
load_dotenv(dotenv_path='C:/Dev/ai-travel/backend/.env')

# --- 환경 변수 및 상수 ---
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
TOUR_API_KEY = os.getenv("TOUR_API_KEY")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

AREA_CODES = {"서울": 1, "부산": 6, "전주": 37, "제주": 39}
CONTENT_TYPE_IDS = {"자연": 12, "문화": 14, "쇼핑": 38, "음식": 39}

# --- DB 설정 ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- DB 함수 ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Tour API 연동 ---
def fetch_tour_api_data(area_code: int, content_type_id: int, page_no: int = 1, num_of_rows: int = 20):
    endpoint = "http://api.visitkorea.or.kr/openapi/service/rest/KorService/areaBasedList"
    params = {
        "ServiceKey": TOUR_API_KEY,
        "numOfRows": num_of_rows,
        "pageNo": page_no,
        "MobileOS": "ETC",
        "MobileApp": "ai-travel",
        "_type": "json",
        "listYN": "Y",
        "arrange": "A",
        "areaCode": area_code,
        "contentTypeId": content_type_id,
    }
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        header = data.get("response", {}).get("header", {})
        if header.get("resultCode") != "0000":
            print(f"API Error for area {area_code}, content {content_type_id}: {header.get('resultMsg')}")
            return []
        items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        return [items] if items and not isinstance(items, list) else items
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# --- 데이터베이스 CRUD ---
def update_all_tour_data():
    """모든 지역 및 콘텐츠 유형에 대해 Tour API 데이터를 가져와 DB에 저장합니다."""
    print("--- Starting scheduled data update... ---")
    db = SessionLocal()
    try:
        for region_name, area_code in AREA_CODES.items():
            for theme_name, content_type_id in CONTENT_TYPE_IDS.items():
                print(f"Fetching data for {region_name} - {theme_name}...")
                items = fetch_tour_api_data(area_code, content_type_id)
                if not items:
                    continue

                # 기존 데이터 삭제
                db.query(TouristInfo).filter(
                    TouristInfo.region == region_name,
                    TouristInfo.content_type == str(content_type_id)
                ).delete(synchronize_session=False)

                # 새 데이터 추가
                new_infos = []
                for item in items:
                    new_info = TouristInfo(
                        content_id=item.get('contentid'),
                        name_ko=item.get('title'),
                        region=region_name,
                        address=item.get('addr1'),
                        latitude=float(item.get('mapy', 0.0)),
                        longitude=float(item.get('mapx', 0.0)),
                        content_type=str(item.get('contenttypeid')),
                        category_tag=theme_name,
                        image_url=item.get('firstimage'),
                        is_variable=False,
                        last_crawled_date=date.today()
                    )
                    all_new_infos.append(new_info)
                
                db.add_all(all_new_infos)
                db.commit()
                print(f"  > Saved {len(new_infos)} items.")
        print("--- Scheduled data update finished. ---")
    except Exception as e:
        db.rollback()
        print(f"An error occurred during DB update: {e}")
    finally:
        db.close()

def get_tourist_info_by_criteria(region: str, theme: str):
    """특정 지역 및 테마에 맞는 관광 정보를 DB에서 조회합니다."""
    db = SessionLocal()
    try:
        results = db.query(TouristInfo).filter(
            TouristInfo.region == region,
            TouristInfo.category_tag == theme
        ).all()
        return results
    finally:
        db.close()

def save_ai_log(user_input: UserRequest, ai_response: RecommendationResponse, agent_log: str, total_tokens: int, is_success: bool):
    """AI 상호작용 로그를 ai_log 테이블에 저장합니다."""
    db = SessionLocal()
    try:
        new_log = AiLog(
            request_time=datetime.now(),
            user_input_json=user_input.model_dump_json(),
            ai_response_json=ai_response.model_dump_json(),
            agent_search_log=agent_log,
            total_tokens=total_tokens,
            is_verified_success=is_success
        )
        db.add(new_log)
        db.commit()
        print(f"Successfully saved AI log with ID: {new_log.log_id}")
    except Exception as e:
        db.rollback()
        print(f"Error saving AI log: {e}")
    finally:
        db.close()

# --- 스케줄러 설정 ---
scheduler = BackgroundScheduler()
# 앱 시작 시 한 번 실행
scheduler.add_job(update_all_tour_data, 'date') 
# 매주 일요일 자정에 실행
scheduler.add_job(update_all_tour_data, 'cron', day_of_week='sun', hour=0)
scheduler.start()

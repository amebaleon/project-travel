"""
외부 openapi(tourapi)에서 정보 가져오는 파이썬 파일임
"""
from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, Date, DateTime, JSON, TEXT
from sqlalchemy.ext.declarative import declarative_base

from src.models import UserRequest, VerificationDetails, RecommendationItem, DailyRecommendation, RecommendationResponse





Base = declarative_base()

class TouristInfo(Base):
    """
    tourist_info 테이블이랑 매핑되는 SQLAlchemy ORM 모델임.
    Tour API에서 수집된 관광 정보 저장하는거.

    Attributes:
        id (int): 고유 식별 번호 (DB 자체 관리용)
        content_id (str): Tour API의 고유 콘텐츠 ID
        name_ko (str): 관광지/시설의 한국어 이름
        region (str): 지역 정보 (예: 서울, 부산)
        address (str): 상세 주소
        latitude (Decimal): 위도
        longitude (Decimal): 경도
        content_type (str): Tour API의 대분류
        category_tag (str): AI 관심사 매칭용 상세 태그
        image_url (str): 대표 이미지 URL
        is_variable (bool): 정보 변동성 플래그 (True면 Agent 검증 대상)
        last_crawled_date (Date): 최종 업데이트 일자
        start_date (Date): 축제/행사 시작일 (nullable)
        end_date (Date): 축제/행사 종료일 (nullable)
        operating_hours (String): 운영 시간 (nullable)
    """
    __tablename__ = 'tourist_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(String(50), nullable=False)
    name_ko = Column(String(255), nullable=False)
    region = Column(String(20), nullable=False)
    address = Column(String(512), nullable=False)
    latitude = Column(DECIMAL(10, 7), nullable=False)
    longitude = Column(DECIMAL(10, 7), nullable=False)
    content_type = Column(String(50), nullable=False)
    category_tag = Column(String(100), nullable=False)
    image_url = Column(String(1024), nullable=True)
    is_variable = Column(Boolean, nullable=False)
    last_crawled_date = Column(Date, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    operating_hours = Column(String(255), nullable=True)

    def to_dict(self):
        """ORM 객체를 딕셔너리로 바꾸는거."""
        return {
            "content_id": self.content_id,
            "name_ko": self.name_ko,
            "region": self.region,
            "address": self.address,
            "latitude": float(self.latitude),
            "longitude": float(self.longitude),
            "content_type": self.content_type,
            "category_tag": self.category_tag,
            "image_url": self.image_url,
            "is_variable": self.is_variable,
            "last_crawled_date": self.last_crawled_date.isoformat() if self.last_crawled_date else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "operating_hours": self.operating_hours
        }

class AiLog(Base):
    """
    ai_log 테이블이랑 매핑되는 SQLAlchemy ORM 모델임.
    AI 추천 만들고 검증하는 과정 기록하는거.

    Attributes:
        log_id (int): 고유 로그 번호
        request_time (DateTime): AI 추천 요청 시각
        user_input_json (JSON): 사용자 입력 정보
        ai_response_json (JSON): GPT-5 mini가 반환한 최종 추천 결과
        total_tokens (int): 요청에 사용된 총 토큰 수
        agent_search_log (TEXT): LangChain Agent의 웹 검색 기록 및 결과
        is_verified_success (bool): Agent 검증 성공 여부
    """
    __tablename__ = 'ai_log'

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    request_time = Column(DateTime, nullable=False)
    user_input_json = Column(JSON, nullable=False)
    ai_response_json = Column(JSON, nullable=False)
    total_tokens = Column(Integer, nullable=True)
    agent_search_log = Column(TEXT, nullable=True)
    is_verified_success = Column(Boolean, nullable=False)

"""
외부 openapi(tourapi)에서 정보 가져오는 파이썬 파일임
"""
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, Date, DateTime, JSON, TEXT
from sqlalchemy.ext.declarative import declarative_base
from datetime import date # datetime.date 사용을 위해 date 임포트

class UserRequest(BaseModel):
    """
    사용자 요청 나타내는 Pydantic 모델임. PRD에 잇는 5가지 핵심 데이터 기반으로 햇음.

    Attributes:
        region (str): 여행 지역 (예: 서울, 부산, 전주, 제주)
        start_date (date): 여행 시작일
        end_date (date): 여행 종료일
        age (int): 사용자 나이
        gender (str): 사용자 성별
        interests (List[str]): 사용자 관심사 목록 (예: 음식, 문화, 자연, 쇼핑)
    """
    region: str
    start_date: date
    end_date: date
    age: int
    gender: str
    interests: List[str]

class VerificationDetails(BaseModel):
    """
    Agent 실시간 검증 결과 나타내는 Pydantic 모델임.

    Attributes:
        operating_status (str): 검색된 운영 여부 및 실제 존재 여부
        end_or_cancel_status (str): 검색된 종료 또는 취소 여부
        latest_price_info (str): 검색된 최신 가격 정보
        schedule_change_and_notes (str): 검색된 일정 변경 여부 및 특이사항
        reliability_score (int): 정보의 신뢰도 점수 (0-100)
        reliability_reason (str): 신뢰도 평가 근거
    """
    operating_status: str
    end_or_cancel_status: str
    latest_price_info: str
    schedule_change_and_notes: str
    reliability_score: int
    reliability_reason: str

class RecommendationItem(BaseModel):
    """
    AI 추천 단일 항목 나타내는 Pydantic 모델임.
    tourist_info 테이블 정보 기반이고, AI가 만든 정보랑 검증 결과 추가되는거.

    Attributes:
        name (str): 추천 장소 이름 (tourist_info.name_ko)
        description (str): AI가 생성한 장소에 대한 간단한 설명
        address (str): 장소의 주소 (tourist_info.address)
        latitude (float): 위도 (tourist_info.latitude)
        longitude (float): 경도 (tourist_info.longitude)
        image_url (Optional[str]): 추천 장소 이미지 URL (tourist_info.image_url)
        activity (str): AI가 제안하는 해당 장소에서의 활동
        verification_details (Optional[VerificationDetails]): 검증 결과에 대한 상세 내용
    """
    name: str
    description: str
    address: str
    latitude: float
    longitude: float
    image_url: Optional[str]
    activity: str
    verification_details: Optional[VerificationDetails] = None
    start_date: Optional[date] = None # 축제/행사 시작일
    end_date: Optional[date] = None # 축제/행사 종료일
    operating_hours: Optional[str] = None # 운영 시간 (예: "09:00-18:00", "24시간", "매일", "주말 휴무")

class DailyRecommendation(BaseModel):
    """
    하루 여행 일정 나타내는 Pydantic 모델임.
    """
    date: date # 해당 일자의 날짜
    recommendations: List[RecommendationItem] # 해당 일자에 추천되는 장소 목록

class RecommendationResponse(BaseModel):
    """
    최종 API 응답 나타내는 Pydantic 모델임.

    Attributes:
        daily_recommendations (List[DailyRecommendation]): AI가 추천하는 일자별 장소 목록
        is_verified_success (bool): 모든 변동 항목이 성공적으로 검증되었는지 여부
        agent_search_log (str): LangChain Agent의 웹 검색 기록 및 결과
        total_tokens (Optional[int]): AI 추천 생성에 사용된 총 토큰 수
    """
    daily_recommendations: List[DailyRecommendation]
    is_verified_success: bool
    agent_search_log: str
    total_tokens: Optional[int] = None # AI 추천 생성에 사용된 총 토큰 수

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

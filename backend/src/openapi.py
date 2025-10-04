"""
외부 openapi(tourapi)에서 정보 가져오는 파이썬 파일
"""
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, Date, DateTime, JSON, TEXT
from sqlalchemy.ext.declarative import declarative_base

class UserRequest(BaseModel):
    """
    사용자 요청을 나타내는 Pydantic 모델입니다. PRD에 명시된 5가지 핵심 데이터를 기반으로 합니다.

    Attributes:
        region (str): 여행 지역 (예: 서울, 부산, 전주, 제주)
        start_date (str): 여행 시작일
        end_date (str): 여행 종료일
        age (int): 사용자 나이
        gender (str): 사용자 성별
        interests (List[str]): 사용자 관심사 목록 (예: 음식, 문화, 자연, 쇼핑)
    """
    region: str
    start_date: str
    end_date: str
    age: int
    gender: str
    interests: List[str]

class RecommendationItem(BaseModel):
    """
    AI 추천 단일 항목을 나타내는 Pydantic 모델입니다.
    tourist_info 테이블의 정보를 기반으로 하며, AI가 생성한 정보와 검증 결과가 추가됩니다.

    Attributes:
        name (str): 추천 장소 이름 (tourist_info.name_ko)
        description (str): AI가 생성한 장소에 대한 간단한 설명
        address (str): 장소의 주소 (tourist_info.address)
        latitude (float): 위도 (tourist_info.latitude)
        longitude (float): 경도 (tourist_info.longitude)
        image_url (Optional[str]): 추천 장소 이미지 URL (tourist_info.image_url)
        activity (str): AI가 제안하는 해당 장소에서의 활동
        is_verified (bool): Agent에 의한 실시간 검증 여부
        verification_details (Optional[str]): 검증 결과에 대한 상세 내용 (예: '정상 운영', '가격 변동: 5000원')
    """
    name: str
    description: str
    address: str
    latitude: float
    longitude: float
    image_url: Optional[str]
    activity: str
    is_verified: bool = False
    verification_details: Optional[str] = None

class RecommendationResponse(BaseModel):
    """
    최종 API 응답을 나타내는 Pydantic 모델입니다.

    Attributes:
        recommendations (List[RecommendationItem]): AI가 추천하는 장소 목록
    """
    recommendations: List[RecommendationItem]

Base = declarative_base()

class TouristInfo(Base):
    """
    tourist_info 테이블과 매핑되는 SQLAlchemy ORM 모델입니다.
    Tour API로부터 수집된 관광 정보를 저장합니다.

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

class AiLog(Base):
    """
    ai_log 테이블과 매핑되는 SQLAlchemy ORM 모델입니다.
    AI의 추천 생성 및 검증 과정을 로깅합니다.

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

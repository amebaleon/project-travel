from datetime import date
from pydantic import BaseModel
from typing import List, Optional

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
    latitude: Optional[float] = None
    longitude: Optional[float] = None
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

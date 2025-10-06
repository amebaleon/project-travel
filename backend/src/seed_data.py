"""
개발 및 테스트 단계에서 사용할 더미 관광 데이터를 정의하는 파일입니다.
실제 Tour API 연동 전까지 임시 데이터 소스로 사용됩니다.
"""

import logging
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session

from src.openapi import TouristInfo # ORM 모델 임포트

# 로거 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def insert_dummy_tour_data(db: Session):
    """
    미리 정의된 더미 관광 데이터를 생성하여 데이터베이스 세션에 추가합니다.
    
    - 이 함수는 데이터를 세션에 추가할 뿐, commit은 하지 않습니다.
    - 트랜잭션 관리는 이 함수를 호출하는 쪽(예: db.py의 fetch_and_store_tour_data)에서 담당합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션 객체.
    """
    logger.info("[Seed] 더미 관광 데이터 생성 및 DB 세션에 추가를 시작합니다.")
    today = date.today()
    
    # 아래에 미리 정의된 다양한 지역과 카테고리의 더미 데이터 리스트입니다.
    dummy_data = [
        # 서울
        TouristInfo(
            content_id="SEOUL001", name_ko="남산공원", region="서울", address="서울 용산구 남산공원길 105",
            latitude=Decimal("37.5509"), longitude=Decimal("126.9903"), content_type="관광지",
            category_tag="자연_공원", image_url="https://example.com/namsan.jpg", is_variable=False,
            last_crawled_date=today, operating_hours="매일 00:00-24:00"
        ),
        TouristInfo(
            content_id="SEOUL003", name_ko="국립중앙박물관", region="서울", address="서울 용산구 서빙고로 137",
            latitude=Decimal("37.5234"), longitude=Decimal("126.9792"), content_type="관광지",
            category_tag="문화_박물관", image_url="https://example.com/nmk.jpg", is_variable=False,
            last_crawled_date=today, operating_hours="화-일 10:00-18:00 (월요일 휴관)"
        ),
        TouristInfo(
            content_id="SEOUL005", name_ko="명동교자 본점", region="서울", address="서울 중구 명동10길 29",
            latitude=Decimal("37.5624"), longitude=Decimal("126.9870"), content_type="음식점",
            category_tag="음식_한식", image_url="https://example.com/myeongdonggyoja.jpg", is_variable=True,
            last_crawled_date=today, operating_hours="매일 10:30-21:30"
        ),
        TouristInfo(
            content_id="SEOUL006", name_ko="서울 빛초롱 축제 2025", region="서울", address="서울 종로구 청계천로 1",
            latitude=Decimal("37.5696"), longitude=Decimal("126.9770"), content_type="축제/행사",
            category_tag="축제_빛축제", image_url="https://example.com/seoullantern.jpg", is_variable=True,
            last_crawled_date=today, start_date=date(2025, 11, 1), end_date=date(2025, 11, 30), operating_hours="정보 없음"
        ),
        TouristInfo(
            content_id="SEOUL013", name_ko="광장시장", region="서울", address="서울 종로구 창경궁로 88",
            latitude=Decimal("37.5700"), longitude=Decimal("126.9900"), content_type="관광지",
            category_tag="문화_전통시장", image_url="https://example.com/gwangjang.jpg", is_variable=False,
            last_crawled_date=today, operating_hours="매일 09:00-22:00"
        ),

        # 부산
        TouristInfo(
            content_id="BUSAN001", name_ko="해운대 해수욕장", region="부산", address="부산 해운대구 우동",
            latitude=Decimal("35.1587"), longitude=Decimal("129.1609"), content_type="관광지",
            category_tag="자연_해변", image_url="https://example.com/haeundae.jpg", is_variable=False,
            last_crawled_date=today, operating_hours="매일 00:00-24:00"
        ),
        TouristInfo(
            content_id="BUSAN003", name_ko="감천문화마을", region="부산", address="부산 사하구 감천동",
            latitude=Decimal("35.0994"), longitude=Decimal("129.0290"), content_type="관광지",
            category_tag="문화_마을", image_url="https://example.com/gamcheon.jpg", is_variable=False,
            last_crawled_date=today, operating_hours="매일 09:00-18:00"
        ),
        TouristInfo(
            content_id="BUSAN004", name_ko="자갈치시장", region="부산", address="부산 중구 자갈치해안로 52",
            latitude=Decimal("35.0940"), longitude=Decimal("129.0270"), content_type="음식점",
            category_tag="음식_해산물", image_url="https://example.com/jagalchi.jpg", is_variable=True,
            last_crawled_date=today, operating_hours="매일 08:00-22:00"
        ),
        TouristInfo(
            content_id="BUSAN005", name_ko="부산 불꽃축제 2025", region="부산", address="부산 수영구 광안해변로 219",
            latitude=Decimal("35.1530"), longitude=Decimal("129.1180"), content_type="축제/행사",
            category_tag="축제_불꽃", image_url="https://example.com/busanfireworks.jpg", is_variable=True,
            last_crawled_date=today, start_date=date(2025, 10, 24), end_date=date(2025, 10, 26), operating_hours="정보 없음"
        ),

        # 제주
        TouristInfo(
            content_id="JEJU001", name_ko="한라산 국립공원", region="제주", address="제주 제주시 1100로 2070-61",
            latitude=Decimal("33.3625"), longitude=Decimal("126.5292"), content_type="관광지",
            category_tag="자연_산", image_url="https://example.com/hallasan.jpg", is_variable=False,
            last_crawled_date=today, operating_hours="매일 00:00-24:00"
        ),
        TouristInfo(
            content_id="JEJU004", name_ko="동문시장 야시장", region="제주", address="제주 제주시 관덕로14길 20",
            latitude=Decimal("33.5141"), longitude=Decimal("126.5292"), content_type="음식점",
            category_tag="음식_시장", image_url="https://example.com/dongmun.jpg", is_variable=True,
            last_crawled_date=today, operating_hours="매일 18:00-24:00"
        ),

        # 전주
        TouristInfo(
            content_id="JEONJU001", name_ko="전주 한옥마을", region="전주", address="전북 전주시 완산구 기린대로 99",
            latitude=Decimal("35.8143"), longitude=Decimal("127.1533"), content_type="관광지",
            category_tag="문화_마을", image_url="https://example.com/jeonjuhanok.jpg", is_variable=False,
            last_crawled_date=today, operating_hours="매일 00:00-24:00"
        ),
        TouristInfo(
            content_id="JEONJU002", name_ko="전주 비빔밥축제 2025", region="전주", address="전북 전주시 완산구 현무1길 20",
            latitude=Decimal("35.8150"), longitude=Decimal("127.1490"), content_type="축제/행사",
            category_tag="축제_음식", image_url="https://example.com/jeonjubibimbap.jpg", is_variable=True,
            last_crawled_date=today, start_date=date(2025, 10, 9), end_date=date(2025, 10, 12), operating_hours="정보 없음"
        ),
    ]
    
    db.add_all(dummy_data)

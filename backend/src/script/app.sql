CREATE TABLE tourist_info (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '고유 식별 번호 (DB 자체 관리용)',
    content_id VARCHAR(50) NOT NULL COMMENT 'Tour API의 고유 콘텐츠 ID',
    name_ko VARCHAR(255) NOT NULL COMMENT '관광지/시설의 한국어 이름',
    region VARCHAR(20) NOT NULL COMMENT '지역 정보 (예: 서울, 부산)',
    address VARCHAR(512) NOT NULL COMMENT '상세 주소 (지도 연동 및 Agent 검색 입력용)',
    latitude DECIMAL(10, 7) NOT NULL COMMENT '위도',
    longitude DECIMAL(10, 7) NOT NULL COMMENT '경도',
    content_type VARCHAR(50) NOT NULL COMMENT 'Tour API의 대분류 (예: 관광지, 음식점, 축제)',
    category_tag VARCHAR(100) NOT NULL COMMENT 'AI 관심사 매칭용 상세 태그 (예: 음식_한식)',
    image_url VARCHAR(1024) NULL COMMENT '대표 이미지 URL',
    is_variable BOOLEAN NOT NULL COMMENT '정보 변동성 플래그: TRUE면 Agent의 실시간 검증 대상',
    last_crawled_date DATE NOT NULL COMMENT 'APScheduler를 통한 최종 업데이트 일자'
);

-- 2. ai_log: GPT-5 mini 요청 및 검증 로그 테이블
CREATE TABLE ai_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '고유 로그 번호',
    request_time DATETIME NOT NULL COMMENT 'AI 추천 요청이 들어온 시각',
    user_input_json JSON NOT NULL COMMENT '사용자 입력 정보 전체 (지역, 일정, 나이, 성별, 관심사)',
    ai_response_json JSON NOT NULL COMMENT 'GPT-5 mini가 반환한 최종 추천 결과',
    total_tokens INT NULL COMMENT '해당 요청에 사용된 총 토큰 수 (비용 모니터링용)',
    agent_search_log TEXT NULL COMMENT 'LangChain Agent의 웹 검색 기록 및 결과',
    is_verified_success BOOLEAN NOT NULL COMMENT 'Agent 검증 성공 여부 (모든 변동 항목이 정상 운영/유효함)'
);
"""
OpenAI API 호출, LangChain Agent 생성 및 실행 등
LLM(거대 언어 모델) 관련 핵심 로직 담당하는 파일임.
"""

import os
import json
import asyncio
import logging

# 로거 설정
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("ddgs").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from typing import Optional, List, Tuple
from datetime import date, datetime

from dotenv import load_dotenv
from openai import OpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent, Tool
from langchain import hub

from src.models import UserRequest, RecommendationResponse, RecommendationItem, VerificationDetails, DailyRecommendation
from src.kakao_maps import get_coords_for_location


# --- 초기 설정 ---

# 로거 설정
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("ddgs").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# .env 파일에서 환경 변수 불러오는거
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY 환경 변수가 .env 파일에 설정되지 않았습니다.")

KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")
if not KAKAO_API_KEY:
    raise ValueError("KAKAO_API_KEY 환경 변수가 .env 파일에 설정되지 않았습니다.")

# --- 클라이언트랑 Agent 초기화 ---

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)

# LangChain Agent 설정
search_tool = DuckDuckGoSearchRun()
llm_agent = ChatOpenAI(model_name="gpt-5-mini", temperature=0, stop_sequences=[], streaming=False)
tools = [search_tool]
prompt_hub_template = hub.pull("hwchase17/openai-tools-agent")
agent = create_openai_tools_agent(llm_agent, tools, prompt_hub_template)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True, max_iterations=25)


# --- 프롬프트 템플릿 정의 ---

INITIAL_RECOMMENDATION_PROMPT_TEMPLATE = """
당신은 한국 여행 전문가 AI Agent입니다.
사용자 정보를 기반으로, DuckDuckGoSearchRun 도구를 사용하여 최적의 여행지를 추천해주세요.

---
[사용자 정보]
- 지역: {region}
- 여행 기간: {duration}일 ({start_date} ~ {end_date})
- 나이: {age}
- 성별: {gender}
- 관심사: {interests}

--- 
[지시사항]
1. 사용자 정보를 바탕으로 각 날짜별로 2~3개의 여행지를 추천해주세요.
2. 각 여행지에 대한 간략한 설명과 추천 이유를 포함해주세요.
3. 각 여행지에서의 활동을 제안해주세요.
4. 각 여행지의 주소를 포함해주세요.
5. 축제/행사 정보가 있다면, 시작일과 종료일을 포함해주세요.
6. 운영 시간이 있다면, 운영 시간을 포함해주세요.
7. 추천 결과는 다음 JSON 형식으로 반환해주세요:
```json
{{
    "daily_recommendations": [
        {{
            "date": "YYYY-MM-DD",
            "recommendations": [
                {{
                    "name": "추천 여행지 1 이름",
                    "description": "추천 이유 및 간략 설명",
                    "activity": "AI가 제안하는 해당 장소에서의 활동",
                    "address": "장소 주소",
                    "start_date": "YYYY-MM-DD (축제/행사 시)",
                    "end_date": "YYYY-MM-DD (축제/행사 시)",
                    "operating_hours": "운영 시간 (예: 09:00-18:00)"
                }}
            ]
        }}
    ]
}}
```
"""

VERIFICATION_PROMPT_TEMPLATE = """
당신은 여행 정보 검증 전문가 AI Agent입니다.
주어진 여행지 정보에 대해 실시간 웹 검색을 통해 다음 항목들을 검증하고, 그 결과와 함께 정보의 신뢰도를 평가하여 JSON 형식으로 보고해야 합니다.

---
[검증 대상 여행지 정보]
- 이름: {item_name}
- 기존 정보:
  - 시작일: {start_date}
  - 종료일: {end_date}
  - 운영 시간: {operating_hours}

---
[검증 항목]
1. 현재 운영 여부 (예: 영업 중, 폐업, 임시 휴업 등) 및 실제 존재 여부
2. 행사/축제의 종료 또는 취소 여부 (예: 이미 종료됨, 취소됨)
3. 최신 가격 정보 (입장료, 주요 서비스 서비스 가격 등)
4. 일정 변경 여부 및 특이사항 (예: 예약 필수, 특정 요일 휴무, 특별 행사 등)

---
[지시사항]
1. DuckDuckGoSearchRun 도구를 사용하여 `{item_name}`에 대한 최신 정보를 검색하세요.
2. 검색 결과를 바탕으로 위에 명시된 검증 항목들에 대한 답변을 찾으세요.
3. 모든 검증 항목에 대한 정보를 찾을 수 없는 경우, "정보 없음"으로 표시하세요.
4. 검색된 정보의 출처(공식 웹사이트, 최신 뉴스 등)를 바탕으로 신뢰도를 0(매우 낮음)부터 100(매우 높음)까지의 점수로 평가하고, 평가 근거를 간략하게 작성하세요.
5. 검증 결과는 다음 JSON 형식으로 반환해주세요:
```json
{{
    "verification_results": {{
        "operating_status": "검색된 운영 여부",
        "end_or_cancel_status": "검색된 종료/취소 여부",
        "latest_price_info": "검색된 최신 가격 정보",
        "schedule_change_and_notes": "검색된 일정 변경 및 특이사항"
    }},
    "reliability_score": 100,
    "reliability_reason": "신뢰도 평가 근거"
}}
```
"""

# --- 헬퍼 함수 ---

def _create_error_verification_details(reason: str, notes: str) -> VerificationDetails:
    """Agent 검증하다 에러나면 쓸 VerificationDetails 객체 만드는거."""
    return VerificationDetails(
        operating_status="검증 실패",
        end_or_cancel_status="정보 없음",
        latest_price_info="정보 없음",
        schedule_change_and_notes=notes,
        reliability_score=0,
        reliability_reason=reason
    )

# --- 핵심 로직 ---

async def verify_recommendation_with_agent(item_name: str, start_date: Optional[str], end_date: Optional[str], operating_hours: Optional[str], timeout: int = 120) -> str:
    """
    정보 변동성 높은 항목(`is_variable=True`)은 LangChain Agent 불러서 실시간 정보 검증하는거.
    """
    prompt = VERIFICATION_PROMPT_TEMPLATE.format(
        item_name=item_name,
        start_date=start_date or "N/A",
        end_date=end_date or "N/A",
        operating_hours=operating_hours or "N/A"
    )

    try:
        logger.info(f"[Agent] {item_name}")
        response = await asyncio.wait_for(
            agent_executor.ainvoke({"input": prompt}),
            timeout=timeout
        )
        logger.info(f"[Agent] {item_name}검증 완료.")
        return response.get("output", "")
    except asyncio.TimeoutError:
        logger.warning(f"[Agent] {item_name} 검증 시간 초과.")
        return json.dumps({"error": "Agent verification timed out"})
    except Exception as e:
        logger.error(f"[Agent] {item_name} 검증 중 오류 발생: {e}")
        return json.dumps({"error": str(e)})

async def get_ai_recommendations(user_request: UserRequest) -> RecommendationResponse:
    """
    AI 추천 생성 및 검증을 수행하는 메인 함수.
    - 최적화: 정보 변동성이 높은 항목들의 실시간 정보 검증을 순차적이 아닌 병렬로 수행하여 응답 시간을 단축.
    """
    # 1. LangChain Agent를 통해 초기 추천 목록 생성
    start_date_obj = user_request.start_date
    end_date_obj = user_request.end_date
    duration_days = (end_date_obj - start_date_obj).days + 1

    initial_recommendation_prompt = INITIAL_RECOMMENDATION_PROMPT_TEMPLATE.format(
        region=user_request.region,
        duration=duration_days,
        start_date=start_date_obj.strftime("%Y-%m-%d"),
        end_date=end_date_obj.strftime("%Y-%m-%d"),
        age=user_request.age,
        gender=user_request.gender,
        interests=", ".join(user_request.interests),
    )

    agent_search_logs = []
    total_tokens_used = 0 # Agent 사용 시 토큰 계산은 복잡하므로 일단 0으로 설정

    try:
        logger.info("[Agent] 초기 추천 생성을 위해 LangChain Agent를 호출합니다.")
        agent_response = await agent_executor.ainvoke({"input": initial_recommendation_prompt})
        initial_recommendations_str = agent_response.get("output", "")
        # TODO: LangChain Agent의 토큰 사용량 추적 로직 추가 필요
        logger.info("[Agent] LangChain Agent 호출 완료.")
        try:
            # Find the start and end of the JSON block
            json_start = initial_recommendations_str.find('{')
            json_end = initial_recommendations_str.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = initial_recommendations_str[json_start:json_end]
                initial_recommendations_data = json.loads(json_str)
            else:
                raise json.JSONDecodeError("No JSON object found", initial_recommendations_str, 0)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"[Agent] 초기 추천 결과 파싱 실패: {e} (응답: {initial_recommendations_str})", exc_info=True)
            return RecommendationResponse(daily_recommendations=[], is_verified_success=False, agent_search_log=f"Agent 응답 파싱 오류: {e}", total_tokens=0)
    except Exception as e:
        logger.error(f"[Agent] 초기 추천 생성 중 오류 발생: {e}", exc_info=True)
        return RecommendationResponse(daily_recommendations=[], is_verified_success=False, agent_search_log=f"Agent 호출 오류: {e}", total_tokens=0)

    final_daily_recommendations: List[DailyRecommendation] = []
    overall_is_verified_success = True

    # 2. 추천 항목 파싱 및 검증 대기 목록 생성
    items_to_verify = [] # (RecommendationItem, original_item_data) 튜플을 저장할 리스트

    for daily_plan_data in initial_recommendations_data.get("daily_recommendations", []):
        current_date_str = daily_plan_data.get("date")
        if not current_date_str:
            logger.warning("[LLM] 응답에 날짜(`date`) 필드가 누락되었습니다. 해당 일일 계획을 건너뜁니다.")
            overall_is_verified_success = False
            agent_search_logs.append("LLM 응답에 날짜 필드 누락")
            continue
        try:
            current_date = datetime.strptime(current_date_str, "%Y-%m-%d").date()
        except ValueError:
            logger.warning(f"[LLM] 날짜 형식이 잘못되었습니다: {current_date_str}. 해당 일일 계획을 건너뜜니다.")
            overall_is_verified_success = False
            agent_search_logs.append(f"LLM이 잘못된 날짜 형식 반환: {current_date_str}")
            continue

        daily_recommendation_items: List[RecommendationItem] = []
        for item_data in daily_plan_data.get("recommendations", []):
            try:
                # 카카오맵 API를 통해 위도, 경도 가져오기 (AI가 주소를 제공했다고 가정)
                latitude, longitude = None, None
                should_verify = True
                if item_data.get("address"):
                    latitude, longitude = get_coords_for_location(KAKAO_API_KEY, item_data["address"])
                    if latitude is None or longitude is None:
                        logger.warning(f"[KakaoMap] {item_data['address']}에 대한 좌표를 찾을 수 없습니다.")
                        agent_search_logs.append(f"KakaoMap: {item_data['address']} 좌표 찾기 실패")
                        # 좌표를 찾지 못하면 해당 항목은 검증 실패로 간주
                        item_data["verification_details"] = _create_error_verification_details(
                            "KakaoMap 좌표 찾기 실패", f"주소: {item_data['address']}"
                        ).model_dump()
                        overall_is_verified_success = False
                        should_verify = False
                
                recommendation_item = RecommendationItem(
                    name=item_data.get("name", "이름 없음"),
                    description=item_data.get("description", "AI가 생성한 설명이 없습니다."),
                    activity=item_data.get("activity", "AI가 제안한 활동이 없습니다."),
                    address=item_data.get("address"),
                    latitude=latitude,
                    longitude=longitude,
                    image_url=item_data.get("image_url"),
                    start_date=datetime.strptime(item_data["start_date"], "%Y-%m-%d").date() if item_data.get("start_date") else None,
                    end_date=datetime.strptime(item_data["end_date"], "%Y-%m-%d").date() if item_data.get("end_date") else None,
                    operating_hours=item_data.get("operating_hours")
                )

                if "verification_details" in item_data:
                    recommendation_item.verification_details = VerificationDetails(**item_data["verification_details"])

                if should_verify:
                    items_to_verify.append((recommendation_item, item_data))
                daily_recommendation_items.append(recommendation_item)

            except Exception as e:
                logger.error(f"[LLM] 추천 항목 파싱 중 오류 발생: {e} (데이터: {item_data})", exc_info=True)
                overall_is_verified_success = False
                agent_search_logs.append(f"추천 항목 파싱 오류: {e} (데이터: {item_data})")
                # 파싱 오류가 발생한 항목은 검증 실패로 간주하고 다음 항목으로 넘어감
                continue

        final_daily_recommendations.append(DailyRecommendation(date=current_date, recommendations=daily_recommendation_items))

    # 3. 병렬로 정보 검증 실행
    if items_to_verify:
        logger.info(f"[Agent] 총 {len(items_to_verify)}개의 항목에 대한 병렬 정보 검증을 시작합니다.")
        verification_tasks = []
        for item, original_item_data in items_to_verify:
            # Agent 검증 시 필요한 정보만 전달
            verification_tasks.append(
                verify_recommendation_with_agent(
                    item.name,
                    item.start_date.isoformat() if item.start_date else None,
                    item.end_date.isoformat() if item.end_date else None,
                    item.operating_hours
                )
            )
        verification_results = await asyncio.gather(*verification_tasks, return_exceptions=True)
        logger.info("[Agent] 모든 병렬 정보 검증이 완료되었습니다.")

        # 4. 검증 결과 처리
        for i, (item, _) in enumerate(items_to_verify):
            result = verification_results[i]

            if isinstance(result, Exception):
                overall_is_verified_success = False
                error_message = f"Agent 검증 중 예외 발생: {result}"
                agent_search_logs.append(f"{item.name}: 검증 실패 - {error_message}")
                item.verification_details = _create_error_verification_details("Agent 검증 중 예외 발생", str(result))
                continue

            verification_result_str = result
            try:
                verification_json = json.loads(verification_result_str)
                if "error" in verification_json:
                    overall_is_verified_success = False
                    agent_search_logs.append(f"{item.name}: 검증 실패 - {verification_json['error']}")
                    item.verification_details = _create_error_verification_details("Agent 검증 중 오류 발생", verification_json['error'])
                else:
                    verification_data = verification_json.get("verification_results", {})
                    item.verification_details = VerificationDetails(
                        operating_status=verification_data.get("operating_status", "정보 없음"),
                        end_or_cancel_status=verification_data.get("end_or_cancel_status", "정보 없음"),
                        latest_price_info=verification_data.get("latest_price_info", "정보 없음"),
                        schedule_change_and_notes=verification_data.get("schedule_change_and_notes", "정보 없음"),
                        reliability_score=verification_json.get("reliability_score", 0),
                        reliability_reason=verification_json.get("reliability_reason", "정보 없음")
                    )
                    if item.verification_details.reliability_score < 50:
                        overall_is_verified_success = False
                        agent_search_logs.append(f"{item.name}: 검증 실패 - 신뢰도 점수 낮음 ({item.verification_details.reliability_score}) - {item.verification_details.reliability_reason}")
                    else:
                        agent_search_logs.append(f"{item.name}: 검증 성공")
            except json.JSONDecodeError:
                overall_is_verified_success = False
                agent_search_logs.append(f"{item.name}: 검증 실패 - Agent가 반환한 JSON 파싱 오류")
                item.verification_details = _create_error_verification_details("Agent 응답 JSON 파싱 오류", verification_result_str)
            except Exception as e:
                overall_is_verified_success = False
                agent_search_logs.append(f"{item.name}: 검증 실패 - 예상치 못한 오류: {e}")
                item.verification_details = _create_error_verification_details("Agent 검증 결과 처리 중 오류", str(e))

    return RecommendationResponse(
        daily_recommendations=final_daily_recommendations,
        is_verified_success=overall_is_verified_success,
        agent_search_log="\n".join(agent_search_logs),
        total_tokens=total_tokens_used
    )

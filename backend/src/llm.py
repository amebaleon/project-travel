"""
OpenAI API 호출, LangChain Agent 생성 및 실행 등
LLM(거대 언어 모델) 관련 핵심 로직 담당하는 파일임.
"""

import os
import json
import asyncio
import logging
from typing import Optional, List, Tuple
from datetime import date, datetime

from dotenv import load_dotenv
from openai import OpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain import hub

from src.openapi import RecommendationResponse, RecommendationItem, VerificationDetails, DailyRecommendation

# --- 초기 설정 ---

# 로거 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# .env 파일에서 환경 변수 불러오는거
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY 환경 변수가 .env 파일에 설정되지 않았습니다.")

# --- 클라이언트랑 Agent 초기화 ---

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)

# LangChain Agent 설정
search_tool = DuckDuckGoSearchRun()
llm_agent = ChatOpenAI(model_name="gpt-5-mini", temperature=0, stop_sequences=[], streaming=False)
tools = [search_tool]
prompt_hub_template = hub.pull("hwchase17/openai-tools-agent")
agent = create_openai_tools_agent(llm_agent, tools, prompt_hub_template)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True)


# --- 프롬프트 템플릿 정의 ---

INITIAL_RECOMMENDATION_PROMPT_TEMPLATE = """
당신은 한국 여행 전문가 AI 어시스턴트입니다.
사용자의 여행 계획을 돕기 위해, 제공된 사용자 정보와 관광지 데이터를 기반으로 **여행 기간 동안 각 날짜별로** 최적의 여행지를 추천해주세요.

---
[사용자 정보]
- 지역: {region}
- 여행 기간: {duration}일 ({start_date} ~ {end_date})
- 나이: {age}
- 성별: {gender}
- 관심사: {interests}

---
[사용 가능한 관광지 데이터 (JSON 형식)]
{tourist_info_json}

---
[지시사항]
1. 사용자 정보와 관광지 데이터를 종합하여, 사용자의 관심사에 가장 부합하는 여행지를 **여행 기간 동안 각 날짜별로** 추천해주세요.
2. 각 날짜별로 2~3개의 추천 장소를 포함해주세요.
3. 추천하는 각 여행지에 대해 간략한 설명과 함께 추천 이유를 덧붙여주세요.
4. 각 추천 여행지에 대해 AI가 제안하는 활동을 포함해주세요.
5. **반드시** 제공된 관광지 데이터에 있는 `content_id`를 사용하여 추천 목록을 구성해야 합니다.
6. 추천 결과는 다음 JSON 형식으로 반환해주세요:
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
                    "content_id": "관광지 데이터에 있는 content_id 중 하나"
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
- 이름: {item_name} (content_id: {content_id})
- 기존 정보:
  - 시작일: {start_date}
  - 종료일: {end_date}
  - 운영 시간: {operating_hours}

---
[검증 항목]
1. 현재 운영 여부 (예: 영업 중, 폐업, 임시 휴업 등) 및 실제 존재 여부
2. 행사/축제의 종료 또는 취소 여부 (예: 이미 종료됨, 취소됨)
3. 최신 가격 정보 (입장료, 주요 서비스 가격 등)
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

async def generate_initial_recommendations(user_request: dict, tourist_info_json: str) -> Tuple[str, Optional[int]]:
    """
    GPT-5-mini 모델 불러서 사용자 요청이랑 DB 정보로 초기 추천 목록 만드는거.
    """
    start_date_obj = user_request["start_date"]
    end_date_obj = user_request["end_date"]
    duration_days = (end_date_obj - start_date_obj).days + 1

    prompt = INITIAL_RECOMMENDATION_PROMPT_TEMPLATE.format(
        region=user_request["region"],
        duration=duration_days,
        start_date=start_date_obj.strftime("%Y-%m-%d"),
        end_date=end_date_obj.strftime("%Y-%m-%d"),
        age=user_request["age"],
        gender=user_request["gender"],
        interests=", ".join(user_request["interests"]),
        tourist_info_json=tourist_info_json
    )

    logger.info("[LLM] 초기 추천 생성을 위해 GPT-5-mini를 호출합니다.")
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are a helpful travel assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=1
    )
    
    total_tokens = response.usage.total_tokens if response.usage else None
    logger.info(f"[LLM] GPT-5-mini 호출 완료. 사용된 토큰: {total_tokens}")
    return response.choices[0].message.content, total_tokens

async def verify_recommendation_with_agent(item_name: str, content_id: str, start_date: Optional[str], end_date: Optional[str], operating_hours: Optional[str], timeout: int = 120) -> str:
    """
    정보 변동성 높은 항목(`is_variable=True`)은 LangChain Agent 불러서 실시간 정보 검증하는거.
    """
    prompt = VERIFICATION_PROMPT_TEMPLATE.format(
        item_name=item_name,
        content_id=content_id,
        start_date=start_date or "N/A",
        end_date=end_date or "N/A",
        operating_hours=operating_hours or "N/A"
    )

    try:
        logger.info(f"[Agent] {item_name}({content_id})에 대한 실시간 정보 검증을 시작합니다.")
        response = await asyncio.wait_for(
            agent_executor.ainvoke({"input": prompt}),
            timeout=timeout
        )
        logger.info(f"[Agent] {item_name}({content_id}) 검증 완료.")
        return response.get("output", "")
    except asyncio.TimeoutError:
        logger.warning(f"[Agent] {item_name}({content_id}) 검증 시간 초과.")
        return json.dumps({"error": "Agent verification timed out"})
    except Exception as e:
        logger.error(f"[Agent] {item_name}({content_id}) 검증 중 오류 발생: {e}")
        return json.dumps({"error": str(e)})

async def get_ai_recommendations(user_request: dict, tourist_info_data: list) -> RecommendationResponse:
    """
    AI 추천 생성 및 검증을 수행하는 메인 함수.
    - 최적화: 정보 변동성이 높은 항목들의 실시간 정보 검증을 순차적이 아닌 병렬로 수행하여 응답 시간을 단축.
    """
    tourist_info_json = json.dumps(tourist_info_data, ensure_ascii=False, indent=2)

    # 1. LLM을 통해 초기 추천 목록 생성
    try:
        initial_recommendations_str, total_tokens_used = await generate_initial_recommendations(user_request, tourist_info_json)
        initial_recommendations_data = json.loads(initial_recommendations_str)
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"[LLM] 초기 추천 결과 파싱 실패: {e}")
        return RecommendationResponse(daily_recommendations=[], is_verified_success=False, agent_search_log="LLM 응답 파싱 오류", total_tokens=0)

    final_daily_recommendations: List[DailyRecommendation] = []
    is_verified_success = True
    agent_search_logs = []
    tourist_info_map = {item['content_id']: item for item in tourist_info_data}

    # 2. 추천 항목 파싱 및 검증 대기 목록 생성
    items_to_verify = [] # (recommendation_item, tourist_info_entry) 튜플을 저장할 리스트

    for daily_plan_data in initial_recommendations_data.get("daily_recommendations", []):
        current_date_str = daily_plan_data.get("date")
        if not current_date_str:
            logger.warning("[LLM] 응답에 날짜(`date`) 필드가 누락되었습니다. 해당 일일 계획을 건너뜁니다.")
            is_verified_success = False
            agent_search_logs.append("LLM 응답에 날짜 필드 누락")
            continue
        try:
            current_date = datetime.strptime(current_date_str, "%Y-%m-%d").date()
        except ValueError:
            logger.warning(f"[LLM] 날짜 형식이 잘못되었습니다: {current_date_str}. 해당 일일 계획을 건너뜁니다.")
            is_verified_success = False
            agent_search_logs.append(f"LLM이 잘못된 날짜 형식 반환: {current_date_str}")
            continue

        daily_recommendation_items: List[RecommendationItem] = []
        for item_data in daily_plan_data.get("recommendations", []):
            content_id = item_data.get("content_id")
            tourist_info_entry = tourist_info_map.get(content_id)

            if not tourist_info_entry:
                logger.warning(f"[LLM] 추천한 content_id({content_id})가 DB에 없습니다. 해당 추천을 건너뜁니다.")
                is_verified_success = False
                agent_search_logs.append(f"LLM이 유효하지 않은 content_id 추천: {content_id}")
                continue

            recommendation_item = RecommendationItem(
                name=item_data.get("name", tourist_info_entry["name_ko"]),
                description=item_data.get("description", "AI가 생성한 설명이 없습니다."),
                activity=item_data.get("activity", "AI가 제안한 활동이 없습니다."),
                address=tourist_info_entry['address'],
                latitude=tourist_info_entry['latitude'],
                longitude=tourist_info_entry['longitude'],
                image_url=tourist_info_entry.get('image_url'),
                start_date=tourist_info_entry.get('start_date'),
                end_date=tourist_info_entry.get('end_date'),
                operating_hours=tourist_info_entry.get('operating_hours')
            )

            if tourist_info_entry.get('is_variable', False):
                items_to_verify.append((recommendation_item, tourist_info_entry))
            else:
                recommendation_item.verification_details = VerificationDetails(
                    operating_status="변동성 낮음", end_or_cancel_status="해당 없음", latest_price_info="해당 없음",
                    schedule_change_and_notes="실시간 정보 변동성이 낮은 항목입니다.",
                    reliability_score=100, reliability_reason="사전 수집된 데이터 기반"
                )
            daily_recommendation_items.append(recommendation_item)
        
        final_daily_recommendations.append(DailyRecommendation(date=current_date, recommendations=daily_recommendation_items))

    # 3. 병렬로 정보 검증 실행
    if items_to_verify:
        logger.info(f"[Agent] 총 {len(items_to_verify)}개의 항목에 대한 병렬 정보 검증을 시작합니다.")
        verification_tasks = [
            verify_recommendation_with_agent(
                item.name, item_data['content_id'],
                item_data.get('start_date'), item_data.get('end_date'), item_data.get('operating_hours')
            ) for item, item_data in items_to_verify
        ]
        verification_results = await asyncio.gather(*verification_tasks, return_exceptions=True)
        logger.info("[Agent] 모든 병렬 정보 검증이 완료되었습니다.")

        # 4. 검증 결과 처리
        for i, result in enumerate(verification_results):
            item_to_update, _ = items_to_verify[i]

            if isinstance(result, Exception):
                is_verified_success = False
                error_message = f"Agent 검증 중 예외 발생: {result}"
                agent_search_logs.append(f"{item_to_update.name}: 검증 실패 - {error_message}")
                item_to_update.verification_details = _create_error_verification_details("Agent 검증 중 예외 발생", str(result))
                continue

            verification_result_str = result
            try:
                verification_json = json.loads(verification_result_str)
                if "error" in verification_json:
                    is_verified_success = False
                    agent_search_logs.append(f"{item_to_update.name}: 검증 실패 - {verification_json['error']}")
                    item_to_update.verification_details = _create_error_verification_details("Agent 검증 중 오류 발생", verification_json['error'])
                else:
                    verification_data = verification_json.get("verification_results", {})
                    item_to_update.verification_details = VerificationDetails(
                        operating_status=verification_data.get("operating_status", "정보 없음"),
                        end_or_cancel_status=verification_data.get("end_or_cancel_status", "정보 없음"),
                        latest_price_info=verification_data.get("latest_price_info", "정보 없음"),
                        schedule_change_and_notes=verification_data.get("schedule_change_and_notes", "정보 없음"),
                        reliability_score=verification_json.get("reliability_score", 0),
                        reliability_reason=verification_json.get("reliability_reason", "정보 없음")
                    )
                    agent_search_logs.append(f"{item_to_update.name}: 검증 성공")
            except json.JSONDecodeError:
                is_verified_success = False
                agent_search_logs.append(f"{item_to_update.name}: 검증 실패 - Agent가 반환한 JSON 파싱 오류")
                item_to_update.verification_details = _create_error_verification_details("Agent 응답 JSON 파싱 오류", verification_result_str)
            except Exception as e:
                is_verified_success = False
                agent_search_logs.append(f"{item_to_update.name}: 검증 실패 - 예상치 못한 오류: {e}")
                item_to_update.verification_details = _create_error_verification_details("Agent 검증 결과 처리 중 오류", str(e))

    return RecommendationResponse(
        daily_recommendations=final_daily_recommendations,
        is_verified_success=is_verified_success,
        agent_search_log="\n".join(agent_search_logs),
        total_tokens=total_tokens_used
    )

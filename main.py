"""
FastAPI 기반 스토리 편집 API 서버
"""
import json
import logging
import sys
import os
from typing import Dict, Any
from contextlib import asynccontextmanager

# FastAPI 관련 import
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# LangChain import
from langchain.schema import HumanMessage

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 프로젝트 모듈 import
try:
    from source.models.llm_handler import (
        initialize_llm, initialize_llm_async, 
        create_prompt_template, generate_game_data, generate_game_data_async
    )
    from source.utils.prompts import get_system_prompt
    from source.utils.config import load_api_key
    from source.utils.async_handler import AsyncTaskManager
except ImportError as e:
    print(f"모듈 로드 실패: {e}")
    sys.exit(1)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 전역 변수
llm_model = None
prompt_template = None
task_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 애플리케이션 라이프사이클 관리"""
    global llm_model, prompt_template, task_manager
    
    # 시작 시 초기화
    try:
        # API 키 확인
        api_key = load_api_key()
        if not api_key:
            logger.error("Google API 키가 설정되지 않았습니다.")
            raise ValueError("Google API 키가 설정되지 않았습니다.")
        
        # 비동기 작업 관리자 초기화
        task_manager = AsyncTaskManager()
        
        # LLM 모델 초기화 (비동기)
        logger.info("LLM 모델 비동기 초기화 중...")
        llm_model = await initialize_llm_async()
        
        # 프롬프트 템플릿 생성
        system_prompt = get_system_prompt()
        prompt_template = create_prompt_template(system_prompt)
        
        logger.info("FastAPI 서버 비동기 초기화 완료")
        
    except Exception as e:
        logger.error(f"서버 초기화 실패: {e}")
        # 동기 방식으로 폴백 시도
        try:
            logger.info("동기 방식으로 LLM 초기화 재시도...")
            llm_model = initialize_llm()
            logger.info("동기 방식 LLM 초기화 완료")
        except Exception as fallback_error:
            logger.error(f"동기 방식 초기화도 실패: {fallback_error}")
            raise e
    
    yield
    
    # 종료 시 정리
    try:
        if task_manager:
            logger.info("비동기 작업 관리자 종료 중...")
            await task_manager.cleanup()
            logger.info("비동기 작업 관리자 정리 완료")
        
        logger.info("FastAPI 서버 종료 정리 완료")
        
    except Exception as e:
        logger.error(f"서버 종료 중 오류: {e}")


# FastAPI 앱 초기화 (lifespan 이벤트 핸들러 사용)
app = FastAPI(
    title="Story Edit API",
    description="AI 기반 스토리 편집 API",
    version="1.0.0",
    lifespan=lifespan
)

# 요청 모델 정의
class StoryEditRequest(BaseModel):
    chapterId: str
    story: str
    editRequest: str

class ScenarioResponse(BaseModel):
    chapterId: str
    story: str
    isCustom: bool
    summary: str


def run_llm_for_edit(original_story: str, edit_request: str) -> str:
    """
    기존 스토리를 편집하여 새로운 시나리오 데이터를 생성합니다.
    
    Args:
        original_story (str): 편집할 원본 스토리 JSON 문자열
        edit_request (str): 편집 요청 사항
        
    Returns:
        str: 편집된 시나리오 JSON 문자열
    """
    global llm_model, prompt_template
    
    try:
        if not llm_model or not prompt_template:
            raise ValueError("LLM 모델이 초기화되지 않았습니다.")
        
        # 스토리 편집을 위한 시스템 프롬프트 생성
        story_edit_prompt = f"""당신은 10세 아동을 위한 투자 교육 스토리 편집 전문가입니다.

주요 역할:
1. 기존 스토리 데이터 분석 및 수정
2. 사용자 요청에 따른 특정 부분 편집 (캐릭터 이름, 이벤트, 대화)
3. 아동 친화적 언어 유지
4. 투자 교육 목적 보존
5. JSON 구조 일관성 유지

처리 범위:
✅ 스토리 내용 편집 (캐릭터, 이벤트, 대화)
✅ 난이도 조절 (쉽게/어렵게)
✅ 교육적 가치 강화
✅ 특정 턴의 상황, 뉴스 수정
✅ 캐릭터 이름 변경
❌ JSON 구조 변경 (7턴 유지 필수)
❌ 실제 투자 조언
❌ 기술적/프로그래밍 질문

편집 지침:
- 원본 스토리의 투자 교육 목적과 구조를 유지하세요
- 7턴의 게임 흐름을 그대로 유지하세요
- 각 턴의 turn_number, result, news, news_tag, stocks 구조를 유지하세요
- 요청된 부분만 수정하고 나머지는 최대한 원본을 유지하세요

원본 스토리:
{original_story}

편집 요청:
{edit_request}

위 편집 요청에 따라 원본 스토리를 수정하여 완전한 JSON 배열로 반환하세요.
반드시 다음과 같은 JSON 배열 형식으로 응답하세요:
[
  {{
    "turn_number": 1,
    "result": "게임 상황 설명",
    "news": "관련 뉴스나 이벤트",
    "news_tag": "all",
    "stocks": [
      {{
        "name": "상점/캐릭터 이름",
        "risk_level": "위험도 설명",
        "description": "상점 설명",
        "before_value": 100,
        "current_value": 100,
        "expectation": "기대/전망"
      }}
    ]
  }}
]"""
        
        # LLM을 통해 스토리 편집
        result = generate_game_data(llm_model, prompt_template, story_edit_prompt)
        
        if not result:
            raise ValueError("LLM에서 유효한 응답을 생성하지 못했습니다.")
        
        return result
        
    except Exception as e:
        logger.error(f"LLM 스토리 편집 중 오류: {e}")
        raise


async def run_llm_for_edit_async(original_story: str, edit_request: str) -> str:
    """
    기존 스토리를 편집하여 새로운 시나리오 데이터를 생성합니다. (비동기 버전)
    
    Args:
        original_story (str): 편집할 원본 스토리 JSON 문자열
        edit_request (str): 편집 요청 사항
        
    Returns:
        str: 편집된 시나리오 JSON 문자열
    """
    global llm_model, prompt_template
    
    try:
        if not llm_model or not prompt_template:
            raise ValueError("LLM 모델이 초기화되지 않았습니다.")
        
        # 스토리 편집을 위한 시스템 프롬프트 생성
        story_edit_prompt = f"""당신은 10세 아동을 위한 투자 교육 스토리 편집 전문가입니다.

주요 역할:
1. 기존 스토리 데이터 분석 및 수정
2. 사용자 요청에 따른 특정 부분 편집 (캐릭터 이름, 이벤트, 대화)
3. 아동 친화적 언어 유지
4. 투자 교육 목적 보존
5. JSON 구조 일관성 유지

처리 범위:
✅ 스토리 내용 편집 (캐릭터, 이벤트, 대화)
✅ 난이도 조절 (쉽게/어렵게)
✅ 교육적 가치 강화
✅ 특정 턴의 상황, 뉴스 수정
✅ 캐릭터 이름 변경
❌ JSON 구조 변경 (7턴 유지 필수)
❌ 실제 투자 조언
❌ 기술적/프로그래밍 질문

편집 지침:
- 원본 스토리의 투자 교육 목적과 구조를 유지하세요
- 7턴의 게임 흐름을 그대로 유지하세요
- 각 턴의 turn_number, result, news, news_tag, stocks 구조를 유지하세요
- 요청된 부분만 수정하고 나머지는 최대한 원본을 유지하세요

원본 스토리:
{original_story}

편집 요청:
{edit_request}

위 편집 요청에 따라 원본 스토리를 수정하여 완전한 JSON 배열로 반환하세요.
반드시 다음과 같은 JSON 배열 형식으로 응답하세요:
[
  {{
    "turn_number": 1,
    "result": "게임 상황 설명",
    "news": "관련 뉴스나 이벤트",
    "news_tag": "all",
    "stocks": [
      {{
        "name": "상점/캐릭터 이름",
        "risk_level": "위험도 설명",
        "description": "상점 설명",
        "before_value": 100,
        "current_value": 100,
        "expectation": "기대/전망"
      }}
    ]
  }}
]"""
        
        # LLM을 통해 스토리 편집 (비동기)
        result = await generate_game_data_async(llm_model, prompt_template, story_edit_prompt)
        
        if not result:
            raise ValueError("LLM에서 유효한 응답을 생성하지 못했습니다.")
        
        return result
        
    except Exception as e:
        logger.error(f"LLM 스토리 편집 중 오류: {e}")
        raise


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Story Edit API Server",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    global llm_model, prompt_template, task_manager
    
    return {
        "status": "healthy",
        "llm_initialized": llm_model is not None,
        "prompt_template_ready": prompt_template is not None,
        "task_manager_ready": task_manager is not None,
        "async_support": True
    }


@app.get("/async-status")
async def async_status():
    """비동기 작업 상태 확인 엔드포인트"""
    global task_manager
    
    if not task_manager:
        return {
            "task_manager_available": False,
            "message": "비동기 작업 관리자가 초기화되지 않았습니다."
        }
    
    return {
        "task_manager_available": True,
        "active_tasks": task_manager.get_active_task_count(),
        "total_completed": task_manager.get_completed_task_count(),
        "server_mode": "async_enabled"
    }


@app.get("/performance")
async def performance_metrics():
    """시스템 성능 메트릭 엔드포인트"""
    try:
        import psutil
        import os
        
        # 시스템 정보
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # 프로세스 정보
        process = psutil.Process(os.getpid())
        process_memory = process.memory_info()
        
        return {
            "system": {
                "cpu_percent": cpu_percent,
                "memory_total": memory.total,
                "memory_available": memory.available,
                "memory_percent": memory.percent
            },
            "process": {
                "pid": os.getpid(),
                "memory_rss": process_memory.rss,
                "memory_vms": process_memory.vms,
                "cpu_percent": process.cpu_percent()
            },
            "async_status": {
                "task_manager_available": task_manager is not None,
                "active_tasks": task_manager.get_active_task_count() if task_manager else 0,
                "completed_tasks": task_manager.get_completed_task_count() if task_manager else 0
            }
        }
    except ImportError:
        return {
            "error": "psutil not installed",
            "async_status": {
                "task_manager_available": task_manager is not None,
                "active_tasks": task_manager.get_active_task_count() if task_manager else 0,
                "completed_tasks": task_manager.get_completed_task_count() if task_manager else 0
            }
        }
    except Exception as e:
        return {"error": f"Performance metrics error: {str(e)}"}


@app.post("/edit-scenario", response_model=ScenarioResponse)
async def edit_scenario(request: StoryEditRequest):
    """
    기존 스토리 편집 엔드포인트
    
    Args:
        request: 스토리 편집 요청 데이터 (chapterId, story, editRequest)
        
    Returns:
        ScenarioResponse: 편집된 시나리오 응답
    """
    try:
        logger.info(f"스토리 편집 요청 받음 - chapterId: {request.chapterId}, 편집 요청: {request.editRequest[:100]}...")
        
        # 입력 검증
        if not request.chapterId or not request.chapterId.strip():
            raise HTTPException(status_code=400, detail="chapterId는 비어있을 수 없습니다.")
        
        if not request.story or not request.story.strip():
            raise HTTPException(status_code=400, detail="원본 스토리는 비어있을 수 없습니다.")
            
        if not request.editRequest or not request.editRequest.strip():
            raise HTTPException(status_code=400, detail="편집 요청은 비어있을 수 없습니다.")
        
        # 원본 스토리 JSON 유효성 검증
        try:
            original_story_data = json.loads(request.story)
            if not isinstance(original_story_data, list):
                raise ValueError("원본 스토리 데이터는 배열 형태여야 합니다.")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="원본 스토리가 유효한 JSON 형식이 아닙니다.")
        
        # LLM을 통해 스토리 편집 (비동기 우선, 실패시 동기 방식)
        logger.info("LLM을 통한 비동기 스토리 편집 시작...")
        try:
            edited_story_json = await run_llm_for_edit_async(request.story, request.editRequest.strip())
        except Exception as async_error:
            logger.warning(f"비동기 처리 실패, 동기 방식으로 재시도: {async_error}")
            edited_story_json = run_llm_for_edit(request.story, request.editRequest.strip())
        
        if not edited_story_json:
            raise HTTPException(status_code=500, detail="스토리 편집에 실패했습니다.")
        
        # 편집된 스토리 JSON 유효성 검증
        try:
            edited_story_data = json.loads(edited_story_json)
            if not isinstance(edited_story_data, list):
                raise ValueError("편집된 스토리 데이터는 배열 형태여야 합니다.")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="편집된 시나리오가 유효한 JSON 형식이 아닙니다.")
        
        # 스토리 요약 생성 (LLM 기반)
        story_summary = await generate_story_summary_with_llm(edited_story_json)
        
        # 응답 데이터 구성 (한글 보존, 기존 chapterId 유지)
        scenario_response_data = {
            "chapterId": request.chapterId.strip(),
            "story": json.dumps(edited_story_data, ensure_ascii=False, separators=(',', ':')),
            "isCustom": True,
            "summary": story_summary
        }
        
        logger.info(f"스토리 편집 완료 - chapterId: {request.chapterId}")
        
        # 클라이언트에 응답 반환
        return ScenarioResponse(**scenario_response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"스토리 편집 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")


@app.post("/edit-scenario-async", response_model=ScenarioResponse)
async def edit_scenario_async(request: StoryEditRequest):
    """
    기존 스토리 편집 엔드포인트 (완전 비동기 버전)
    
    Args:
        request: 스토리 편집 요청 데이터 (chapterId, story, editRequest)
        
    Returns:
        ScenarioResponse: 편집된 시나리오 응답
    """
    try:
        logger.info(f"비동기 스토리 편집 요청 받음 - chapterId: {request.chapterId}, 편집 요청: {request.editRequest[:100]}...")
        
        # 입력 검증
        if not request.chapterId or not request.chapterId.strip():
            raise HTTPException(status_code=400, detail="chapterId는 비어있을 수 없습니다.")
        
        if not request.story or not request.story.strip():
            raise HTTPException(status_code=400, detail="원본 스토리는 비어있을 수 없습니다.")
            
        if not request.editRequest or not request.editRequest.strip():
            raise HTTPException(status_code=400, detail="편집 요청은 비어있을 수 없습니다.")
        
        # 원본 스토리 JSON 유효성 검증
        try:
            original_story_data = json.loads(request.story)
            if not isinstance(original_story_data, list):
                raise ValueError("원본 스토리 데이터는 배열 형태여야 합니다.")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="원본 스토리가 유효한 JSON 형식이 아닙니다.")
        
        # LLM을 통해 스토리 편집 (완전 비동기)
        logger.info("LLM을 통한 완전 비동기 스토리 편집 시작...")
        edited_story_json = await run_llm_for_edit_async(request.story, request.editRequest.strip())
        
        if not edited_story_json:
            raise HTTPException(status_code=500, detail="스토리 편집에 실패했습니다.")
        
        # 편집된 스토리 JSON 유효성 검증
        try:
            edited_story_data = json.loads(edited_story_json)
            if not isinstance(edited_story_data, list):
                raise ValueError("편집된 스토리 데이터는 배열 형태여야 합니다.")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="편집된 시나리오가 유효한 JSON 형식이 아닙니다.")
        
        # 스토리 요약 생성 (LLM 기반)
        story_summary = await generate_story_summary_with_llm(edited_story_json)
        
        # 응답 데이터 구성 (한글 보존, 기존 chapterId 유지)
        scenario_response_data = {
            "chapterId": request.chapterId.strip(),
            "story": json.dumps(edited_story_data, ensure_ascii=False, separators=(',', ':')),
            "isCustom": True,
            "summary": story_summary
        }
        
        logger.info(f"비동기 스토리 편집 완료 - chapterId: {request.chapterId}")
        
        # 클라이언트에 응답 반환
        return ScenarioResponse(**scenario_response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"비동기 스토리 편집 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")


def generate_story_summary(story_json: str) -> str:
    """
    스토리 JSON에서 게임 흐름, 주식 종목 변화를 포함한 요약을 생성합니다.
    
    Args:
        story_json (str): 스토리 JSON 문자열
        
    Returns:
        str: 게임 흐름과 주식 종목 변화가 포함된 스토리 요약
    """
    try:
        import json
        story_data = json.loads(story_json)
        
        if not isinstance(story_data, list) or len(story_data) == 0:
            return "알 수 없는 스토리"
        
        # 게임 구조 분석
        turn_count = len(story_data)
        
        # 주식 종목 흐름 분석
        stock_analysis = analyze_stock_trends(story_data)
        
        # 시작, 중간, 끝 턴 분석
        start_turn = story_data[0].get('result', '') if len(story_data) > 0 else ''
        middle_turn = story_data[turn_count // 2].get('result', '') if turn_count > 2 else ''
        end_turn = story_data[-1].get('result', '') if len(story_data) > 1 else ''
        
        # 전체 스토리 텍스트 합치기
        all_text = ' '.join([turn.get('result', '') for turn in story_data]).lower()
        
        # 주요 캐릭터 추출
        main_character = extract_main_character(all_text)
        
        # 게임 진행 패턴 분석
        investment_elements = []
        if '투자' in all_text or '주식' in all_text:
            investment_elements.append('투자 결정')
        if '수익' in all_text or '이익' in all_text:
            investment_elements.append('수익 관리')
        if '위험' in all_text or '손실' in all_text:
            investment_elements.append('위험 대응')
        
        # 스토리 진행 흐름 분석
        story_flow = analyze_story_flow(start_turn, middle_turn, end_turn)
        
        # 요약 생성
        summary_parts = []
        
        # 주인공 정보
        if main_character:
            summary_parts.append(f"{main_character}의")
        
        # 게임 구조
        summary_parts.append(f"{turn_count}턴")
        
        # 주식 종목 흐름 (핵심 정보)
        if stock_analysis:
            summary_parts.append(f"[{stock_analysis}]")
        
        return ' '.join(summary_parts)
        
    except Exception as e:
        logger.error(f"스토리 요약 생성 실패: {e}")
        return "투자교육 게임 스토리"


def analyze_stock_trends(story_data: list) -> str:
    """
    스토리 데이터에서 주식 종목들의 흐름을 분석합니다.
    
    Args:
        story_data (list): 스토리 턴 데이터 리스트
        
    Returns:
        str: 주식 종목 흐름 요약
    """
    try:
        stock_trends = {}
        
        # 각 턴의 주식 데이터 수집
        for turn in story_data:
            stocks = turn.get('stocks', [])
            for stock in stocks:
                stock_name = stock.get('name', '')
                if not stock_name:
                    continue
                
                before_value = stock.get('before_value', 0)
                current_value = stock.get('current_value', 0)
                
                if stock_name not in stock_trends:
                    stock_trends[stock_name] = {
                        'values': [],
                        'changes': [],
                        'risk_level': stock.get('risk_level', ''),
                        'description': stock.get('description', '')
                    }
                
                stock_trends[stock_name]['values'].append({
                    'before': before_value,
                    'current': current_value,
                    'change': current_value - before_value
                })
        
        if not stock_trends:
            return ""
        
        # 주요 종목 분석 (최대 2개)
        trend_summaries = []
        
        for stock_name, data in list(stock_trends.items())[:2]:
            if not data['values']:
                continue
                
            # 전체 변화 계산
            first_value = data['values'][0]['before']
            last_value = data['values'][-1]['current']
            total_change = last_value - first_value
            
            # 변화 패턴 분석
            changes = [v['change'] for v in data['values']]
            positive_changes = sum(1 for c in changes if c > 0)
            negative_changes = sum(1 for c in changes if c < 0)
            
            # 흐름 판단
            if total_change > 0:
                if positive_changes > negative_changes:
                    trend = "상승세"
                else:
                    trend = "회복세"
            elif total_change < 0:
                if negative_changes > positive_changes:
                    trend = "하락세"
                else:
                    trend = "등락"
            else:
                trend = "변동 없음"
            
            # 원본 종목명 사용
            trend_summaries.append(f"{stock_name} {trend}")
        
        return ', '.join(trend_summaries)
        
    except Exception as e:
        logger.error(f"주식 흐름 분석 실패: {e}")
        return ""


def extract_main_character(all_text: str) -> str:
    """전체 텍스트에서 주인공을 추출합니다."""
    character_patterns = {
        '달빛도둑': ['달빛도둑', '달빛 도둑'],
        '햇빛도둑': ['햇빛도둑', '햇빛 도둑'],
        '마법사': ['마법사', '마법왕국'],
        '아기돼지': ['아기돼지', '돼지'],
        '푸드트럭 사장': ['푸드트럭', '음식', '요리사']
    }
    
    for char, patterns in character_patterns.items():
        if any(pattern in all_text for pattern in patterns):
            return char
    
    return ""


def analyze_story_flow(start_turn: str, middle_turn: str, end_turn: str) -> list:
    """스토리 흐름을 분석합니다."""
    story_flow = []
    
    # 시작 부분 분석
    if '시작' in start_turn or '모험' in start_turn:
        story_flow.append('모험 시작')
    elif '왕국' in start_turn or '마법' in start_turn:
        story_flow.append('세계관 소개')
    
    # 중간 부분 분석
    if middle_turn:
        if '선택' in middle_turn or '결정' in middle_turn:
            story_flow.append('핵심 선택')
        elif '문제' in middle_turn or '위기' in middle_turn:
            story_flow.append('위기 상황')
        elif '성장' in middle_turn or '배움' in middle_turn:
            story_flow.append('학습 과정')
    
    # 끝 부분 분석
    if end_turn:
        if '성공' in end_turn or '완성' in end_turn:
            story_flow.append('성공적 완료')
        elif '교훈' in end_turn or '배움' in end_turn:
            story_flow.append('교훈 정리')
    
    return story_flow


async def generate_story_summary_with_llm(story_json: str) -> str:
    """
    LLM을 활용하여 스토리의 흐름과 종목별 등락을 자연스럽게 요약합니다.
    
    Args:
        story_json (str): 스토리 JSON 문자열
        
    Returns:
        str: LLM이 생성한 스토리 요약
    """
    global llm_model, prompt_template
    
    try:
        if not llm_model or not prompt_template:
            logger.warning("LLM 모델이 초기화되지 않았습니다.")
            return generate_story_summary(story_json)
        
        # 스토리 요약을 위한 프롬프트 생성
        summary_prompt = f"""당신은 10세 아동을 위한 투자교육 게임 스토리 분석 전문가입니다.

아래 JSON 스토리 데이터를 분석하여 자연스럽고 매끄러운 한 문장 요약을 생성해주세요.

요약 작성 지침:
- 120자 이내로 자연스럽게 작성 (공백 포함)
- 아이들이 이해하기 쉬운 친근한 언어 사용
- 주인공과 주요 종목들의 흐름을 스토리로 연결
- 딱딱한 형식보다는 매끄럽고 흥미로운 표현 우선
- 종목명은 간략히 줄여서 표현 (예: "달빛 방패" → "방패", "목걸이 훔치기" → "목걸이")
- 상승/하락을 자연스러운 표현으로 (예: "크게 올랐어요", "많이 떨어졌네요", "쭉쭉 올랐어요")

좋은 예시:
"달빛도둑이 은월 왕국에서 모험하며 방패가 쭉쭉 올라 대성공을 거뒀어요!"
"아기돼지들이 집짓기 투자로 벽돌집이 크게 오르며 늑대를 물리쳤어요!"

스토리 데이터:
{story_json}

위 스토리를 분석하여 아이들이 좋아할 만한 자연스럽고 재미있는 한 문장 요약을 생성해주세요."""

        # LLM을 통해 요약 생성 (비동기)
        try:
            # 단순 텍스트 생성을 위한 직접 호출
            messages = [{"role": "user", "content": summary_prompt}]
            response = await llm_model.ainvoke([HumanMessage(content=summary_prompt)])
            summary_result = response.content
        except Exception as async_error:
            logger.warning(f"비동기 요약 생성 실패, 동기 방식으로 재시도: {async_error}")
            try:
                response = llm_model.invoke([HumanMessage(content=summary_prompt)])
                summary_result = response.content
            except Exception as sync_error:
                logger.error(f"동기 방식 요약 생성도 실패: {sync_error}")
                summary_result = None
        
        if not summary_result:
            logger.warning("LLM 요약 생성 실패, 기본 요약으로 대체합니다.")
            return generate_story_summary(story_json)
        
        # 요약 텍스트 정리 (JSON이나 불필요한 태그 제거)
        summary_text = summary_result.strip()
        
        # JSON 형태로 반환된 경우 텍스트만 추출
        if summary_text.startswith('{') or summary_text.startswith('['):
            try:
                import re
                # 간단한 텍스트 추출 시도
                text_match = re.search(r'"([^"]+)"', summary_text)
                if text_match:
                    summary_text = text_match.group(1)
            except:
                pass
        
        # 불필요한 따옴표나 특수문자 제거
        summary_text = summary_text.replace('"', '').replace("'", '').strip()
        
        # 요약이 너무 길면 자연스럽게 잘라내기 (120자 제한)
        if len(summary_text) > 120:
            # 문장이 끝나는 지점에서 자르기 시도
            cut_point = 117
            while cut_point > 80 and summary_text[cut_point] not in ['!', '?', '.', '요', '다', '네', '죠']:
                cut_point -= 1
            
            if cut_point <= 80:  # 적절한 자를 지점을 못 찾으면 강제로 자르기
                summary_text = summary_text[:117] + "..."
            else:
                summary_text = summary_text[:cut_point + 1]
        
        return summary_text if summary_text else generate_story_summary(story_json)
        
    except Exception as e:
        logger.error(f"LLM 스토리 요약 생성 중 오류: {e}")
        # 오류 발생 시 기존 규칙 기반 요약으로 대체
        return generate_story_summary(story_json)


if __name__ == "__main__":
    # 서버 실행
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8004,
        log_level="info"
    )

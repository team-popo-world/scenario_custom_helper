"""
스토리 편집 컴포넌트 - 기존 스토리 수정 전용 (비동기 지원)
"""
import streamlit as st
import json
import os
import asyncio
from typing import List, Dict, Tuple, Optional
from source.models.llm_handler import (
    initialize_llm, 
    initialize_llm_async,
    create_prompt_template, 
    generate_game_data,
    generate_game_data_async,
    generate_game_data_stream,
    generate_multiple_scenarios_async
)
from source.utils.prompts import get_system_prompt, get_story_modification_prompt
from source.components.story_editor import StoryEditor
from source.utils.chatbot_helper import ChatbotHelper
from source.utils.security import security_validator
from source.utils.performance import performance_monitor
from source.utils.async_handler import (
    AsyncTaskManager,
    run_async_in_streamlit
)
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

class GameCustomizer:
    def __init__(self):
        """스토리 편집기 초기화"""
        self.llm = None
        self.story_editor = StoryEditor()
        self.chatbot_helper = ChatbotHelper()
        self.max_retries = 3
        self.async_manager = AsyncTaskManager()
        self.initialize_llm_model()
        
    def initialize_llm_model(self) -> bool:
        """LLM 모델 초기화"""
        try:
            performance_monitor.start_timer("llm_initialization")
            self.llm = initialize_llm()
            duration = performance_monitor.end_timer("llm_initialization")
            logger.info(f"LLM 초기화 완료 ({duration:.2f}초)")
            return True
        except Exception as e:
            logger.error(f"LLM 초기화 실패: {str(e)}")
            st.error(f"LLM 모델 초기화에 실패했습니다: {str(e)}")
            return False

    async def initialize_llm_async(self):
        """비동기 LLM 모델 초기화"""
        try:
            self.llm = await initialize_llm_async()
            logger.info("비동기 LLM 초기화 완료")
            return True
        except Exception as e:
            logger.error(f"비동기 LLM 초기화 실패: {str(e)}")
            raise Exception(f"비동기 LLM 모델 초기화에 실패했습니다: {str(e)}")

    def modify_existing_story(self, story_name: str, user_request: str, chat_history=None) -> Tuple[Optional[str], Dict]:
        """기존 스토리를 사용자 요청에 따라 수정"""
        performance_monitor.start_timer("story_modification")
        
        # 보안 검증
        security_result = security_validator.validate_content_security(user_request)
        if not security_result["is_safe"]:
            logger.warning(f"보안 검증 실패: {security_result['issues']}")
            return None, {"error": f"보안 검증 실패: {', '.join(security_result['issues'])}"}
        
        # 입력 정화
        user_request = security_validator.sanitize_input(user_request)
        
        if not self.llm:
            error_msg = "LLM 모델이 초기화되지 않았습니다. 설정을 확인해주세요."
            logger.error(error_msg)
            return None, {"error": error_msg}
        
        # 현재 세션에 로드된 스토리 데이터 사용
        original_story = st.session_state.get('current_game_data')
        
        # 세션 데이터가 없으면 파일에서 로드 시도
        if not original_story:
            try:
                original_story = self.story_editor.load_story(story_name)
                if not original_story:
                    error_msg = f"'{story_name}' 스토리를 찾을 수 없습니다. 파일이 존재하는지 확인해주세요."
                    logger.error(error_msg)
                    return None, {"error": error_msg}
            except Exception as e:
                error_msg = f"스토리 로드 중 오류: {str(e)}"
                logger.error(error_msg)
                return None, {"error": error_msg}
        
        try:
            # 수정 요청 분석
            modification_analysis = self.story_editor.analyze_modification_request(user_request)
            
            # 대화 컨텍스트 포함
            conversation_summary = self.chatbot_helper.create_conversation_summary(chat_history or [])
            
            # 스토리 수정을 위한 프롬프트 생성
            story_json = json.dumps(original_story, ensure_ascii=False, indent=2)
            modification_prompt = get_story_modification_prompt(
                story_json, user_request, modification_analysis['type']
            )
            
            # 프롬프트 템플릿 생성
            prompt_template = create_prompt_template(get_system_prompt())
            
            # 수정된 스토리 생성
            modified_story_data = generate_game_data(self.llm, prompt_template, modification_prompt)
            
            # 수정된 스토리 검증
            analysis_result = {
                "intent": {
                    "type": modification_analysis['type'],
                    "target_turn": modification_analysis.get('target_turn'),
                    "confidence": 0.9
                },
                "validation": None,
                "suggestions": []
            }
            
            if modified_story_data:
                try:
                    # JSON 파싱 시도
                    if isinstance(modified_story_data, str):
                        parsed_data = json.loads(modified_story_data)
                    else:
                        parsed_data = modified_story_data
                    
                    # 데이터 타입 확인 및 보정
                    if not isinstance(parsed_data, list):
                        # 만약 딕셔너리에서 'story_data' 키가 있다면 추출
                        if isinstance(parsed_data, dict) and 'story_data' in parsed_data:
                            parsed_data = parsed_data['story_data']
                        else:
                            analysis_result["validation"] = {
                                "is_valid": False,
                                "issues": ["스토리 데이터는 리스트 형태여야 합니다."]
                            }
                            return modified_story_data, analysis_result
                    
                    is_valid, errors = self.story_editor.validate_story_structure(parsed_data)
                    analysis_result["validation"] = {
                        "is_valid": is_valid,
                        "issues": errors if not is_valid else []
                    }
                    
                    if is_valid:
                        # 수정된 스토리 저장
                        self.story_editor.save_modified_story(parsed_data, story_name)
                        analysis_result["suggestions"] = [
                            "스토리가 성공적으로 수정되었습니다.",
                            "다른 부분도 수정하고 싶으시면 말씀해주세요."
                        ]
                    
                except json.JSONDecodeError:
                    analysis_result["validation"] = {
                        "is_valid": False,
                        "issues": ["생성된 데이터가 유효한 JSON 형식이 아닙니다."]
                    }
            
            return modified_story_data, analysis_result
            
        except Exception as e:
            return None, {"error": f"스토리 수정 중 오류가 발생했습니다: {str(e)}"}
    
    
    async def modify_existing_story_async(self, story_name: str, user_request: str, chat_history=None) -> Tuple[Optional[str], Dict]:
        """기존 스토리를 비동기로 수정"""
        performance_monitor.start_timer("story_modification_async")
        
        # 보안 검증
        security_result = security_validator.validate_content_security(user_request)
        if not security_result["is_safe"]:
            logger.warning(f"보안 검증 실패: {security_result['issues']}")
            return None, {"error": f"보안 검증 실패: {', '.join(security_result['issues'])}"}
        
        try:
            # 기존 스토리 로드
            original_story = self.story_editor.load_story(story_name)
            if not original_story:
                return None, {"error": f"스토리 '{story_name}'를 찾을 수 없습니다."}
            
            # 프롬프트 생성
            system_prompt = get_system_prompt()
            modification_prompt = get_story_modification_prompt(
                original_story, 
                user_request, 
                chat_history or []
            )
            
            prompt_template = create_prompt_template(system_prompt)
            
            # 비동기 LLM 호출
            result = await generate_game_data_async(self.llm, prompt_template, modification_prompt)
            
            if result:
                duration = performance_monitor.end_timer("story_modification_async")
                logger.info(f"비동기 스토리 수정 완료 ({duration:.2f}초)")
                return result, {"success": True, "duration": duration}
            else:
                return None, {"error": "LLM이 유효한 응답을 생성하지 못했습니다."}
                
        except Exception as e:
            logger.error(f"비동기 스토리 수정 중 오류: {e}")
            return None, {"error": f"스토리 수정 중 오류 발생: {str(e)}"}
    
    def modify_story_with_streaming(self, story_name: str, user_request: str, 
                                  container, chat_history=None) -> Tuple[Optional[str], Dict]:
        """스트리밍으로 스토리 수정"""
        async def stream_callback(token):
            await self.streaming_handler.stream_callback(token)
        
        async def modify_with_stream():
            # 기존 스토리 로드
            original_story = self.story_editor.load_story(story_name)
            if not original_story:
                return None, {"error": f"스토리 '{story_name}'를 찾을 수 없습니다."}
            
            # 프롬프트 생성
            system_prompt = get_system_prompt()
            modification_prompt = get_story_modification_prompt(
                original_story, 
                user_request, 
                chat_history or []
            )
            
            prompt_template = create_prompt_template(system_prompt)
            
            # 스트리밍으로 생성
            result = await generate_game_data_stream(
                self.llm, 
                prompt_template, 
                modification_prompt,
                stream_callback
            )
            
            return result, {"success": True}
        
        # 스트리밍 시작
        import threading
        streaming_thread = threading.Thread(
            target=self.streaming_handler.start_streaming,
            args=(container,)
        )
        streaming_thread.start()
        
        # 비동기 작업 실행
        task_id = self.async_manager.run_async_task(
            f"stream_modify_{story_name}",
            modify_with_stream
        )
        
        # 작업 완료 대기
        while not self.async_manager.is_task_completed(task_id):
            import time
            time.sleep(0.5)
        
        # 스트리밍 중지
        self.streaming_handler.stop_streaming()
        streaming_thread.join()
        
        # 결과 반환
        try:
            return self.async_manager.get_task_result(task_id)
        except Exception as e:
            return None, {"error": str(e)}
    
    async def modify_multiple_stories_async(self, story_modifications: List[Dict]) -> List[Dict]:
        """여러 스토리를 병렬로 수정"""
        tasks = []
        
        for modification in story_modifications:
            story_name = modification['story_name']
            user_request = modification['request']
            chat_history = modification.get('chat_history', [])
            
            task = self.modify_existing_story_async(story_name, user_request, chat_history)
            tasks.append(task)
        
        # 병렬 실행
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 처리
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'story_name': story_modifications[i]['story_name'],
                    'success': False,
                    'error': str(result)
                })
            else:
                story_data, metadata = result
                processed_results.append({
                    'story_name': story_modifications[i]['story_name'],
                    'success': metadata.get('success', False),
                    'data': story_data,
                    'metadata': metadata
                })
        
        return processed_results
    
    def get_task_status(self, task_id: str) -> Dict:
        """작업 상태 확인"""
        return self.async_manager.get_task_status(task_id)
    
    def cancel_task(self, task_id: str):
        """작업 취소"""
        self.async_manager.cancel_task(task_id)
    
    def get_story_summary(self, story_name: str):
        """스토리 요약 정보 반환"""
        story_data = self.story_editor.load_story(story_name)
        if not story_data:
            return None
        
        # 스토리 데이터 분석
        summary = {
            'total_turns': len(story_data) if isinstance(story_data, list) else 0,
            'characters': [],
            'last_modified': 'Unknown'
        }
        
        # 캐릭터 추출
        all_chars = set()
        if isinstance(story_data, list):
            for turn in story_data:
                if 'stocks' in turn:
                    for stock in turn['stocks']:
                        name = stock.get('name', '')
                        if name:
                            all_chars.add(name)
        summary['characters'] = list(all_chars)
        
        return summary
    
    def get_available_stories(self) -> List[str]:
        """GameCustomizer에서 사용할 수 있는 스토리 목록을 반환합니다."""
        return self.story_editor.get_available_stories()
    
    def run_async_modification(self, story_name: str, user_request: str) -> str:
        """
        Streamlit UI에서 비동기 스토리 수정을 실행합니다.
        
        Args:
            story_name (str): 수정할 스토리 이름
            user_request (str): 사용자 수정 요청
            
        Returns:
            str: 작업 ID
        """
        try:
            # 비동기 작업 생성
            async def async_task():
                return await self.modify_existing_story_async(story_name, user_request)
            
            task_id = f"modify_{story_name}_{len(self.async_manager.tasks)}"
            
            # 비동기 작업 시작
            self.async_manager.run_async_task(task_id, async_task)
            
            return task_id
            
        except Exception as e:
            logger.error(f"비동기 수정 작업 시작 실패: {str(e)}")
            st.error(f"작업 시작에 실패했습니다: {str(e)}")
            return ""

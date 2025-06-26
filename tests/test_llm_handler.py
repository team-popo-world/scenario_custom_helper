"""
LLM Handler 테스트
"""
import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, patch, AsyncMock

# 프로젝트 루트를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from source.models.llm_handler import (
    initialize_llm,
    initialize_llm_async,
    generate_game_data,
    generate_game_data_async,
    parse_and_validate_json,
    create_prompt_template
)


class TestLLMHandler:
    """LLM Handler 테스트 클래스"""
    
    def test_create_prompt_template(self):
        """프롬프트 템플릿 생성 테스트"""
        system_prompt = "테스트 시스템 프롬프트"
        template = create_prompt_template(system_prompt)
        
        assert template is not None
        assert hasattr(template, 'format') or hasattr(template, 'format_messages')
    
    def test_parse_and_validate_json_valid(self):
        """유효한 JSON 파싱 테스트"""
        valid_json = '[{"turn_number": 1, "result": "테스트", "news": "뉴스", "stocks": []}]'
        result = parse_and_validate_json(valid_json)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        assert "turn_number" in result[0]
    
    def test_parse_and_validate_json_invalid(self):
        """잘못된 JSON 파싱 테스트"""
        invalid_json = '{"invalid": json}'
        result = parse_and_validate_json(invalid_json)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_initialize_llm_async(self):
        """비동기 LLM 초기화 테스트"""
        with patch('source.models.llm_handler.load_api_key', return_value='test_key'):
            with patch('source.models.llm_handler.ChatGoogleGenerativeAI'):
                llm = await initialize_llm_async()
                assert llm is not None
    
    @pytest.mark.asyncio
    async def test_generate_game_data_async_mock(self):
        """비동기 게임 데이터 생성 모의 테스트"""
        mock_llm = AsyncMock()
        mock_response = Mock()
        mock_response.content = '[{"turn_number": 1, "result": "테스트", "news": "뉴스", "stocks": []}]'
        mock_llm.ainvoke.return_value = mock_response
        
        result, metadata = await generate_game_data_async("테스트 프롬프트", mock_llm)
        
        assert result is not None
        assert isinstance(result, list)
        assert metadata is not None


if __name__ == "__main__":
    pytest.main([__file__])

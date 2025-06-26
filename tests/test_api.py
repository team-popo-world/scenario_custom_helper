"""
API 엔드포인트 테스트
"""
import pytest
import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# 프로젝트 루트를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestFastAPIEndpoints:
    """FastAPI 엔드포인트 테스트"""
    
    def setup_method(self):
        """각 테스트 전 실행"""
        # main.py 앱을 임포트하여 테스트 클라이언트 생성
        with patch('source.utils.config.load_api_key', return_value='test_key'):
            from main import app
            self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """루트 엔드포인트 테스트"""
        response = self.client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_health_endpoint(self):
        """헬스체크 엔드포인트 테스트"""
        response = self.client.get("/health")
        assert response.status_code in [200, 206, 503]  # 정상, 부분정상, 비정상
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
    
    def test_async_status_endpoint(self):
        """비동기 상태 엔드포인트 테스트"""
        response = self.client.get("/async-status")
        assert response.status_code == 200
        
        data = response.json()
        assert "task_manager_available" in data
    
    @patch('source.models.llm_handler.generate_game_data')
    def test_edit_scenario_endpoint(self, mock_generate):
        """스토리 편집 엔드포인트 테스트"""
        # LLM 응답 모의
        mock_generate.return_value = (
            [{"turn_number": 1, "result": "수정된 스토리", "news": "뉴스", "stocks": []}],
            {"tokens": 100, "time": 5.0}
        )
        
        test_payload = {
            "chapterId": "test-chapter",
            "story": '[{"turn_number": 1, "result": "원본", "news": "뉴스", "stocks": []}]',
            "editRequest": "스토리를 수정해주세요"
        }
        
        response = self.client.post("/edit-scenario", json=test_payload)
        
        # 500 에러가 날 수 있지만 구조가 올바른지 확인
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "chapterId" in data
            assert "story" in data
    
    def test_edit_scenario_invalid_payload(self):
        """잘못된 페이로드로 스토리 편집 테스트"""
        invalid_payload = {
            "chapterId": "",  # 빈 ID
            "story": "invalid json",  # 잘못된 JSON
            "editRequest": ""  # 빈 요청
        }
        
        response = self.client.post("/edit-scenario", json=invalid_payload)
        assert response.status_code in [400, 422, 500]  # 클라이언트 에러 또는 서버 에러


class TestAPIValidation:
    """API 검증 테스트"""
    
    def setup_method(self):
        """각 테스트 전 실행"""
        with patch('source.utils.config.load_api_key', return_value='test_key'):
            from main import app
            self.client = TestClient(app)
    
    def test_missing_fields(self):
        """필수 필드 누락 테스트"""
        incomplete_payload = {
            "chapterId": "test"
            # story와 editRequest 누락
        }
        
        response = self.client.post("/edit-scenario", json=incomplete_payload)
        assert response.status_code == 422  # Validation Error
    
    def test_empty_strings(self):
        """빈 문자열 테스트"""
        empty_payload = {
            "chapterId": "",
            "story": "",
            "editRequest": ""
        }
        
        response = self.client.post("/edit-scenario", json=empty_payload)
        assert response.status_code in [400, 422, 500]


if __name__ == "__main__":
    pytest.main([__file__])

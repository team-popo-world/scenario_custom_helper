"""
스토리 게임 커스터마이저 - 메인 애플리케이션
"""
import streamlit as st
import sys
import os
import logging
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 모듈 import with error handling
try:
    from source.components.game_customizer import GameCustomizer
    from source.ui.sidebar import render_sidebar
    from source.ui.story_selector import render_story_selector
    from source.ui.chat_interface import render_chat_interface
    from source.ui.story_viewer import render_story_viewer
    from source.ui.info_tabs import render_info_tabs
    from source.ui.system_management import render_system_management
    from source.utils.config import load_api_key
    from source.utils.performance import performance_monitor
    from source.utils.security import security_validator
    from source.utils.error_handler import error_handler
except ImportError as e:
    st.error(f"모듈 로드 실패: {e}")
    st.stop()


def initialize_session_state():
    """세션 상태 초기화"""
    defaults = {
        'chat_history': [],
        'current_game_data': None,
        'current_story_name': None,
        'customizer': None,
        'app_initialized': False,
        'error_count': 0,
        'last_error_time': None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # customizer는 별도로 초기화
    if st.session_state.customizer is None:
        st.session_state.customizer = GameCustomizer()
        
    # 편집 모드로 고정
    if 'work_mode' not in st.session_state:
        st.session_state.work_mode = "edit"
        
    if 'investment_focus' not in st.session_state:
        st.session_state.investment_focus = "story_editing"


def check_api_key():
    """API 키 확인"""
    api_key = load_api_key()
    if not api_key:
        st.error("⚠️ Google API 키가 설정되지 않았습니다. .env 파일에 GOOGLE_API_KEY를 설정해주세요.")
        st.stop()
    return api_key


def setup_page():
    """페이지 설정"""
    st.set_page_config(
        page_title="🎮 투자 교육 스토리 편집기",
        page_icon="✏️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 페이지 헤더
    st.title("🎮 투자 교육 스토리 편집기")
    st.markdown("기존 스토리를 AI와 함께 수정하고 개선해보세요!")


def main():
    """메인 애플리케이션"""
    try:
        # 페이지 설정
        setup_page()
        
        # 세션 상태 초기화
        initialize_session_state()
        
        # API 키 확인
        check_api_key()
        
        # 시스템 상태 체크
        performance_monitor.start_timer("main_app")
        
        try:
            # 사이드바 렌더링
            render_sidebar()
            
            # 시스템 관리 모드 체크
            if st.session_state.get('show_system_management', False):
                render_system_management()
                return
            
            # 스토리가 선택되지 않은 경우 스토리 선택기 표시
            if not st.session_state.get('current_game_data'):
                render_story_selector()
                return
            
            # 스토리가 선택된 경우 편집 인터페이스 표시
            col1, col2 = st.columns([1, 1])
            
            # 왼쪽: 채팅 인터페이스
            with col1:
                st.subheader("💬 AI 스토리 편집기")
                render_chat_interface(st.session_state.customizer)
            
            # 오른쪽: 스토리 뷰어
            with col2:
                st.subheader("📖 스토리 미리보기")
                render_story_viewer(st.session_state.customizer)
            
            # 하단: 정보 탭들
            render_info_tabs()
            
        finally:
            performance_monitor.end_timer("main_app")
            
    except Exception as e:
        error_handler.handle_error(e, "메인 애플리케이션")
        st.error("애플리케이션에서 오류가 발생했습니다. 페이지를 새로고침해주세요.")
        logger.error(f"Main application error: {e}", exc_info=True)


if __name__ == "__main__":
    main()

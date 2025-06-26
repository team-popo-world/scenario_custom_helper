#!/bin/bash
set -e

# 환경 변수 검증
check_env_vars() {
    echo "🔍 환경 변수 확인 중..."
    
    if [ -z "$GOOGLE_API_KEY" ]; then
        echo "⚠️  경고: GOOGLE_API_KEY가 설정되지 않았습니다."
        echo "   Docker 실행 시 -e GOOGLE_API_KEY=your_api_key를 추가해주세요."
    else
        echo "✅ GOOGLE_API_KEY 확인됨"
    fi
}

# 디렉토리 권한 확인
setup_directories() {
    echo "📁 디렉토리 설정 중..."
    
    # saved_stories 디렉토리가 쓰기 가능한지 확인
    if [ ! -w "saved_stories" ]; then
        echo "⚠️  saved_stories 디렉토리 권한 수정 중..."
        chmod 755 saved_stories logs 2>/dev/null || true 2>/dev/null || echo "⚠️ 권한 변경 실패 - 무시하고 계속진행" 
    fi
    
    echo "✅ 디렉토리 설정 완료"
}

# 애플리케이션 시작
start_application() {
    case "$1" in
        "streamlit")
            echo "🚀 Streamlit 앱 시작 중..."
            exec streamlit run app.py \
                --server.address=0.0.0.0 \
                --server.port=8501 \
                --server.headless=true \
                --server.fileWatcherType=none \
                --browser.gatherUsageStats=false
            ;;
        "fastapi")
            echo "🚀 FastAPI 서버 시작 중..."
            echo "   비동기 처리 기능 활성화됨"
            exec uvicorn main:app \
                --host 0.0.0.0 \
                --port 8004 \
                --workers 1 \
                --loop asyncio \
                --log-level info
            ;;
        "both")
            echo "🚀 Streamlit과 FastAPI 동시 시작 중..."
            echo "   비동기 처리 기능 활성화됨"
            # FastAPI를 백그라운드에서 실행
            uvicorn main:app --host 0.0.0.0 --port 8004 --workers 1 --loop asyncio &
            # Streamlit을 포어그라운드에서 실행
            exec streamlit run app.py \
                --server.address=0.0.0.0 \
                --server.port=8501 \
                --server.headless=true \
                --server.fileWatcherType=none \
                --browser.gatherUsageStats=false
            ;;
        *)
            echo "❌ 알 수 없는 서비스: $1"
            echo "사용법: docker-entrypoint.sh [streamlit|fastapi|both]"
            exit 1
            ;;
    esac
}

# 메인 실행
main() {
    echo "🐳 Making Story Chatbot Docker 컨테이너 시작"
    echo "================================================"
    
    check_env_vars
    setup_directories
    
    # 기본값은 streamlit
    SERVICE=${1:-streamlit}
    start_application "$SERVICE"
}

main "$@"

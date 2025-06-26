#!/bin/bash

# Docker 빌드 및 실행 스크립트

set -e

echo "🐳 Docker 빌드 및 실행 스크립트"
echo "=============================="

build_image() {
    echo "🔨 Docker 이미지 빌드 중..."
    docker build -t story-edit-app:latest .
    echo "✅ 빌드 완료"
}

run_api() {
    echo "🚀 FastAPI 서버 실행"
    docker run -d \
        --name story-api \
        -p 8004:8004 \
        -e GOOGLE_API_KEY="${GOOGLE_API_KEY}" \
        -v "$(pwd)/saved_stories:/app/saved_stories" \
        -v "$(pwd)/logs:/app/logs" \
        story-edit-app:latest fastapi
    
    echo "✅ FastAPI 서버 시작됨 (포트: 8004)"
}

run_web() {
    echo "🖥️ Streamlit 웹앱 실행"
    docker run -d \
        --name story-web \
        -p 8501:8501 \
        -e GOOGLE_API_KEY="${GOOGLE_API_KEY}" \
        -v "$(pwd)/saved_stories:/app/saved_stories" \
        story-edit-app:latest streamlit
    
    echo "✅ Streamlit 웹앱 시작됨 (포트: 8501)"
}

case "$1" in
    "build")
        build_image
        ;;
    "api")
        build_image
        run_api
        ;;
    "web")
        build_image
        run_web
        ;;
    "compose")
        echo "🐳 Docker Compose로 전체 스택 실행"
        docker-compose up -d
        ;;
    "stop")
        echo "🛑 컨테이너 정지"
        docker stop story-api story-web 2>/dev/null || true
        docker-compose down 2>/dev/null || true
        ;;
    "clean")
        echo "🧹 컨테이너 및 이미지 정리"
        docker stop story-api story-web 2>/dev/null || true
        docker rm story-api story-web 2>/dev/null || true
        docker rmi story-edit-app:latest 2>/dev/null || true
        ;;
    *)
        echo "사용법: $0 {build|api|web|compose|stop|clean}"
        echo ""
        echo "명령어:"
        echo "  build    - Docker 이미지 빌드"
        echo "  api      - FastAPI 서버만 실행"
        echo "  web      - Streamlit 웹앱만 실행"
        echo "  compose  - Docker Compose로 전체 실행"
        echo "  stop     - 모든 컨테이너 정지"
        echo "  clean    - 컨테이너 및 이미지 정리"
        exit 1
        ;;
esac

# 멀티스테이지 빌드 - 빌드 스테이지
FROM python:3.10-slim as builder

# 메타데이터 추가
LABEL maintainer="knell999@example.com"
LABEL description="AI Story Editing System with Streamlit and FastAPI"
LABEL version="2.0.0"

# UV 설치 (빌드 스테이지에서만)
RUN pip install uv

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일만 먼저 복사 (캐시 최적화)
COPY requirements.txt pyproject.toml ./

# 의존성을 시스템에 설치
RUN uv pip install --system -r requirements.txt

# 프로덕션 스테이지
FROM python:3.10-slim as production

# 시스템 패키지 업데이트 및 런타임 필수 패키지만 설치
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Python 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/app/.local/bin:$PATH"

# non-root 사용자 생성 (보안 강화)
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 작업 디렉토리 설정
WORKDIR /app

# 빌드 스테이지에서 설치된 Python 패키지 복사
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 프로젝트 파일 복사 (소유자를 appuser로 설정)
COPY --chown=appuser:appuser . .

# 저장된 스토리 디렉토리 생성 및 권한 설정
RUN mkdir -p saved_stories logs && \
    chown -R appuser:appuser saved_stories logs && \
    chmod 755 saved_stories logs

# non-root 사용자로 전환
USER appuser

# 포트 노출 (Streamlit과 FastAPI 모두)
EXPOSE 8501 8004

# 헬스체크 추가 (비동기 엔드포인트 포함)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8004/health && curl -f http://localhost:8004/async-status || exit 1

# 시작 스크립트 실행 권한 설정
COPY --chown=appuser:appuser docker-entrypoint.sh /usr/local/bin/
USER root
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
USER appuser

# 기본 명령어 설정 (docker-compose에서 override 가능)
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["fastapi"]

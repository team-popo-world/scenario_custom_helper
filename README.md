# 📖 투자 교육 스토리 편집기 (Scenario Custom Helper)

AI 기반 투자 교육 게임 스토리 편집 및 커스터마이징 도구입니다. Google Gemini를 활용하여 기존 스토리를 아동 친화적으로 편집하고, 투자 교육 목적에 맞게 개선할 수 있습니다.

## 🎯 주요 기능

- **AI 스토리 편집**: Google Gemini를 활용한 지능형 스토리 편집
- **투자 교육 최적화**: 10세 아동 대상 투자 교육 콘텐츠 특화
- **실시간 미리보기**: 편집 중인 스토리를 실시간으로 확인
- **JSON 구조 보존**: 7턴 게임 구조와 주식 데이터 일관성 유지
- **REST API 지원**: FastAPI 기반 HTTP API 엔드포인트 제공
- **성능 모니터링**: 시스템 자원 사용량 및 작업 상태 추적

## 🏗️ 시스템 아키텍처

```
scenario_custom_helper/
├── main.py                 # FastAPI 서버 (API 엔드포인트)
├── app.py                  # Streamlit 웹 인터페이스
├── source/
│   ├── components/         # 핵심 비즈니스 로직
│   │   ├── game_customizer.py
│   │   └── story_editor.py
│   ├── models/             # AI/LLM 모델 관리
│   │   └── llm_handler.py
│   ├── ui/                 # 사용자 인터페이스 컴포넌트
│   │   ├── chat_interface.py
│   │   ├── story_viewer.py
│   │   └── ...
│   └── utils/              # 유틸리티 함수들
│       ├── config.py
│       ├── prompts.py
│       └── ...
├── saved_stories/          # 저장된 스토리 파일들
└── logs/                   # 애플리케이션 로그
```

## 🚀 설치 및 실행

### 1. 환경 설정

```bash
# 의존성 설치 (Python 3.10+ 필요)
pip install -r requirements.txt

# 또는 uv 사용
uv pip install -r requirements.txt
```

### 2. API 키 설정

`.env` 파일을 프로젝트 루트에 생성:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

### 3. 실행 방법

#### Streamlit 웹 인터페이스
```bash
streamlit run app.py
```

#### FastAPI 서버
```bash
python main.py
# 또는
uvicorn main:app --host 0.0.0.0 --port 8004
```

#### Docker 실행
```bash
# Docker Compose 사용
docker-compose up -d

# 또는 직접 Docker 빌드
docker build -t scenario-editor .
docker run -p 8004:8004 -p 8501:8501 scenario-editor
```

## 📚 API 사용법

### 스토리 편집 API

**POST** `/edit-scenario`

```json
{
  "chapterId": "chapter_001",
  "story": "[{\"turn_number\": 1, \"result\": \"...\", \"stocks\": [...]}]",
  "editRequest": "캐릭터 이름을 '달빛도둑'에서 '별빛마법사'로 변경해주세요"
}
```

**응답:**
```json
{
  "chapterId": "chapter_001",
  "story": "[{편집된 스토리 JSON}]",
  "isCustom": true,
  "summary": "투자 전략 요약",
  "reply": "편집 완료 안내 메시지"
}
```

### 시스템 상태 확인

- `GET /health` - 헬스 체크
- `GET /performance` - 성능 메트릭
- `GET /async-status` - 비동기 작업 상태

## 💡 사용 예시

### 웹 인터페이스 사용
1. 브라우저에서 `http://localhost:8501` 접속
2. 사이드바에서 기존 스토리 선택
3. 채팅 인터페이스에서 편집 요청 입력
4. 실시간으로 편집 결과 확인

### API 직접 호출
```python
import requests

response = requests.post('http://localhost:8004/edit-scenario', json={
    'chapterId': 'test_001',
    'story': '기존 스토리 JSON',
    'editRequest': '원하는 편집 내용'
})

print(response.json())
```

## 🔧 기술 스택

- **Backend**: Python 3.10+, FastAPI, Uvicorn
- **Frontend**: Streamlit
- **AI/LLM**: Google Gemini (via LangChain)
- **비동기 처리**: AsyncIO, Aiohttp
- **패키지 관리**: UV, Requirements.txt
- **컨테이너화**: Docker, Docker Compose
- **모니터링**: psutil, 커스텀 성능 모니터

## 📝 스토리 구조

투자 교육 게임은 7턴으로 구성되며, 각 턴은 다음 구조를 가집니다:

```json
{
  "turn_number": 1,
  "result": "게임 상황 설명",
  "news": "관련 뉴스나 이벤트",
  "news_tag": "all",
  "stocks": [
    {
      "name": "상점/캐릭터 이름",
      "risk_level": "위험도 설명",
      "description": "상점 설명",
      "before_value": 100,
      "current_value": 120,
      "expectation": "기대/전망"
    }
  ]
}
```

## 🛡️ 보안 고려사항

- API 키는 환경변수로 관리
- 입력 데이터 검증 및 JSON 파싱 예외 처리
- 스토리 편집은 교육적 목적으로만 제한
- 시스템 리소스 모니터링 및 제한

## 🔍 로깅 및 모니터링

- 모든 API 요청/응답 로깅
- 성능 메트릭 수집 (CPU, 메모리 사용량)
- 비동기 작업 상태 추적
- 오류 발생 시 상세 로그 기록

## 📋 개발 정보

- **개발 언어**: Python 3.10+
- **프로젝트 버전**: 1.0.0
- **라이센스**: MIT
- **의존성 관리**: pyproject.toml, requirements.txt 병행

---

문의사항이나 개선 요청은 이슈를 통해 알려주시기 바랍니다.
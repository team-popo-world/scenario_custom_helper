# 🎮 AI 스토리 편집 시스템

Google Gemini AI를 활용한 투자 교육용 스토리 편집 시스템입니다.  
**Streamlit 웹 인터페이스**와 **FastAPI REST API** 두 가지 방식으로 제공됩니다.

## ✨ 주요 기능

### 🎯 핵심 편집 기능
- **📚 스토리 파일 인식**: `saved_stories` 폴더의 JSON 파일 자동 인식 및 로드
- **💬 자연어 편집**: "달빛도둑을 햇빛도둑으로 바꿔줘" 같은 자연어 요청으로 편집
- **🎭 세밀한 편집**: 캐릭터, 배경, 이벤트, 대화 등 요소별 맞춤 수정
- **🔍 실시간 검증**: 수정된 스토리의 JSON 구조와 품질 자동 검증
- **📊 편집 분석**: 사용자 의도 분석 및 개선 제안 제공

### 🌐 이중 인터페이스
- **🖥️ Streamlit 웹앱**: 직관적인 UI로 실시간 편집 (`app.py`)
- **🔌 FastAPI 서버**: RESTful API로 시스템 연동 (`main.py`)
- **📱 반응형 UI**: 데스크톱과 모바일 모두 지원
- **🔄 실시간 동기화**: 편집 결과 즉시 반영

### 🛡️ 보안 및 안전
- **콘텐츠 필터링**: 부적절한 내용 자동 차단
- **민감정보 보호**: 개인정보 및 금융정보 검출 및 마스킹
- **아동 안전**: 교육용 콘텐츠에 적합한 안전 장치
- **요청 검증**: 프로젝트 범위 외 질문 필터링

### ⚡ 성능 및 시스템
- **응답 캐싱**: 유사한 요청에 대한 빠른 응답
- **성능 모니터링**: 실시간 시스템 상태 추적
- **에러 처리**: 통합 에러 관리 및 자동 복구
- **Docker 지원**: 컨테이너 기반 배포

### 📋 편의 기능
- **💾 스토리 저장**: 수정된 스토리를 사용자 지정 제목으로 저장
- **📋 수정 히스토리**: 모든 편집 요청과 변경사항 추적 및 기록
- **🎯 교육적 가치**: 10세 아동을 위한 투자 교육 게임에 최적화

## 📁 프로젝트 구조

```
scenario_custom_helper/
├── 📱 app.py                        # 메인 Streamlit 웹앱
├── 🔌 main.py                       # FastAPI REST API 서버
├── 📋 requirements.txt              # Python 패키지 의존성
├── ⚙️  pyproject.toml               # UV 프로젝트 설정
├── 🚀 run_app.sh                    # Streamlit 실행 스크립트
├── 🐳 Dockerfile                    # Docker 이미지 설정
├── 🐳 docker-compose.yml           # Docker Compose 설정
├── 🔐 .env                          # 환경 변수 (생성 필요)
├── 📝 README.md                     # 프로젝트 문서
├── 📖 docs/                         # 기술 문서
│   └── TECHNICAL_ARCHITECTURE.md   # 기술 아키텍처 가이드
├── 📂 source/                       # 소스 코드
│   ├── 🔧 components/
│   │   ├── game_customizer.py      # 🎯 스토리 편집 핵심 로직
│   │   └── story_editor.py         # 📝 스토리 편집 도우미
│   ├── 🤖 models/
│   │   └── llm_handler.py          # Google Gemini API 처리
│   ├── 🎨 ui/
│   │   ├── sidebar.py              # 사이드바 (편집 가이드)
│   │   ├── story_selector.py       # 스토리 선택기
│   │   ├── chat_interface.py       # 💬 AI 편집 채팅 인터페이스
│   │   ├── story_viewer.py         # 스토리 미리보기
│   │   ├── info_tabs.py            # 정보 및 가이드 탭
│   │   └── system_management.py    # 🔧 시스템 관리 UI
│   └── 🛠️ utils/
│       ├── config.py               # ⚙️ API 설정 및 환경 변수
│       ├── prompts.py              # 📝 AI 편집용 프롬프트 템플릿
│       ├── story_manager.py        # 📁 스토리 파일 관리 및 I/O
│       ├── chatbot_helper.py       # 🤖 챗봇 도우미 기능
│       ├── security.py             # 🔒 보안 검증 및 콘텐츠 필터링
│       ├── performance.py          # ⚡ 성능 최적화 및 캐싱
│       ├── error_handler.py        # 🚨 통합 에러 처리 시스템
│       ├── async_handler.py        # ⚡ 비동기 처리 유틸리티
│       └── logging_config.py       # 📊 통합 로깅 시스템
└── 📚 saved_stories/               # 편집 대상 스토리 파일들
    ├── game_scenario_magic_kingdom_*.json     # 🏰 마법왕국 스토리
    ├── game_scenario_foodtruck_kingdom_*.json # 🚚 푸드트럭 스토리
    ├── game_scenario_moonlight_thief_*.json   # 🌙 달빛도둑 스토리
    └── game_scenario_three_little_pigs_*.json # 🐷 아기돼지 삼형제 스토리
```
## 🚀 빠른 시작

### 📋 사전 요구사항
- **Python**: 3.10 이상
- **Google Gemini API Key**: [Google AI Studio](https://makersuite.google.com/app/apikey)에서 발급

### 🔧 설치 및 실행

#### 방법 1: 기본 Python 환경

```bash
# 저장소 클론
git clone <repository_url>
cd making_story_chatbot

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
```

#### 방법 2: UV 패키지 매니저 (권장)

```bash
# UV 설치 (필요한 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 프로젝트 클론 및 설정
git clone <repository_url>
cd making_story_chatbot

# 환경 변수 설정
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env

# Streamlit 앱 실행
./run_app.sh
```

### 🎮 애플리케이션 실행

#### **1. 🖥️ Streamlit 웹앱 (권장)**
```bash
# 직접 실행
streamlit run app.py

# 또는 스크립트 사용
./run_app.sh
```
웹 브라우저에서 `http://localhost:8501`로 접속

#### **2. 🔌 FastAPI REST API**
```bash
# API 서버 실행
python main.py
```
- API 서버: `http://localhost:8000`
- API 문서: `http://localhost:8000/docs` (Swagger UI)
- 헬스체크: `http://localhost:8000/health`

#### **3. 🐳 Docker로 실행**

**Docker Compose (전체 스택):**
```bash
# 환경 변수 설정
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# 모든 서비스 실행 (Streamlit + FastAPI)
docker-compose up -d

# 개별 서비스 실행
docker-compose up streamlit  # Streamlit만
docker-compose up fastapi    # FastAPI만
```

**개별 Docker 실행:**
```bash
# 이미지 빌드
docker build -t story-editor .

# Streamlit 컨테이너 실행
docker run -d -p 8501:8501 -e GOOGLE_API_KEY=your_api_key_here story-editor

# FastAPI 컨테이너 실행
docker run -d -p 8000:8000 -e GOOGLE_API_KEY=your_api_key_here story-editor fastapi
```

## 🎮 사용법

### **🌐 두 가지 사용 방법**

#### **1. 🖥️ Streamlit 웹 인터페이스 (일반 사용자)**
- 브라우저에서 `http://localhost:8501` 접속
- 직관적인 UI로 스토리 편집
- 실시간 미리보기 및 채팅 인터페이스
- 드래그 앤 드롭으로 파일 업로드

#### **2. 🔌 FastAPI REST API (개발자/시스템 연동)**  
- `http://localhost:8000/docs`에서 API 문서 확인
- `POST /edit-scenario` 엔드포인트 사용
- JSON 기반 요청/응답
- 다른 시스템과의 연동 가능

### 📝 API 사용 예시

**요청 (POST /edit-scenario):**
```json
{
  "chapterId": "4444",
  "story": "[{\"turn_number\":1,\"result\":\"달빛도둑의 모험이 시작됩니다...\"}]",
  "editRequest": "달빛도둑을 햇빛도둑으로 바꿔줘"
}
```

**응답:**
```json
{
  "chapterId": "4444",
  "story": "[{\"turn_number\":1,\"result\":\"햇빛도둑의 모험이 시작됩니다...\"}]",
  "isCustom": true,
  "summary": "햇빛도둑의 7턴 [햇빛 보물 상승세, 마법의 상점 회복세]"
}
```

**응답 필드 설명:**
- `chapterId`: 요청한 챕터 ID
- `story`: 편집된 스토리 JSON (문자열 형태)
- `isCustom`: 편집 여부 (항상 true)
- `summary`: 스토리 요약 - 주인공, 턴 수, 주요 주식 종목의 원본명과 흐름(상승세/하락세/회복세) 정보

### 🎯 Streamlit 웹앱 사용법

### 1. 스토리 선택 및 로드
1. 메인 페이지에서 편집하고 싶은 스토리를 선택
2. "📖 불러오기" 버튼을 클릭하여 스토리 로드
3. 스토리가 성공적으로 로드되면 편집 모드로 전환

### 2. AI와 대화로 스토리 편집
편집 인터페이스에서 자연어로 요청하세요:

**캐릭터 수정:**
- "주인공의 이름을 민수로 바꿔줘"
- "달빛도둑을 햇빛도둑으로 바꿔줘"
- "악역을 더 매력적으로 만들어줘"

**이벤트 수정:**
- "3턴 이벤트를 더 재미있게 만들어줘"
- "마법 요소를 추가해줘"
- "더 스릴 넘치는 모험으로 바꿔줘"

**배경 수정:**
- "배경을 우주로 바꿔줘"
- "더 신비로운 분위기로 만들어줘"
- "현대적인 도시 배경으로 변경해줘"

**대화 수정:**
- "대화를 더 재미있게 수정해줘"
- "아이들이 이해하기 쉽게 바꿔줘"
- "더 감동적인 대화로 만들어줘"

### 3. 결과 확인 및 품질 검증
- ✨ AI가 의도를 분석하고 적절한 수정 적용
- 📊 실시간으로 수정된 게임 턴 수 표시
- ✅ 자동 품질 검증 및 이슈 보고
- 💡 추가 개선 제안 제공

### 4. 수정된 스토리 저장
- 📖 **미리보기**: 수정된 스토리 내용을 확인
- 💾 **사용자 지정 제목**: 원하는 제목으로 스토리 저장
- 📋 **수정 히스토리**: 모든 편집 요청이 자동으로 기록됨
- ✏️ **구분 표시**: 스토리 목록에서 수정된 스토리 구분

**저장 방법:**
1. 스토리 수정 완료 후 저장 옵션 확인
2. 원하는 제목 입력 (예: "수정된 달빛도둑 스토리")
3. '💾 저장하기' 버튼 클릭
4. 저장 완료 후 스토리 목록에서 ✏️ 표시로 확인

## 💡 주요 기능 상세

### 🎯 스토리 편집 특징
- **JSON 구조 유지**: 7턴 게임 구조를 완벽하게 보존
- **세밀한 편집**: turn_number, result, news, stocks 각 필드별 수정
- **교육적 가치**: 투자 교육 목적에 맞는 적절한 내용 유지
- **아동 친화적**: 10세 아동에게 적합한 언어와 표현 사용

### 🛡️ 보안 및 검증
- **입력 검증**: 요청 데이터의 유효성 자동 검사
- **JSON 검증**: 원본 및 편집된 스토리의 구조 검증
- **콘텐츠 필터링**: 부적절한 편집 요청 자동 차단
- **에러 처리**: 다양한 오류 상황에 대한 안전한 처리

### ⚡ 성능 최적화
- **LLM 최적화**: Google Gemini Pro를 직접 사용하여 빠른 응답
- **프롬프트 엔지니어링**: 정확한 편집을 위한 특화된 프롬프트
- **캐싱 시스템**: 반복적인 요청에 대한 빠른 응답
- **비동기 처리**: FastAPI의 비동기 처리로 높은 성능

### 🔧 시스템 관리
- **실시간 모니터링**: 헬스체크 및 시스템 상태 확인
- **로깅 시스템**: 모든 요청과 응답에 대한 상세 로그
- **에러 추적**: 문제 발생 시 상세한 에러 정보 제공
- **Docker 지원**: 컨테이너 기반 안정적 배포

## 📖 사용법

### 🎮 기본 편집 워크플로우

1. **스토리 업로드**: 좌측 사이드바에서 JSON 파일 업로드
2. **편집 요청**: 자연어로 원하는 수정사항 입력
3. **결과 확인**: AI가 편집한 스토리 검토
4. **반복 편집**: 필요시 추가 수정 요청
5. **저장**: 최종 결과 다운로드

### 📝 편집 요청 예시

```text
# 캐릭터 대사 수정
"주인공의 첫 번째 대사를 더 친근하게 바꿔주세요"

# 투자 교육 요소 추가
"2번째 시나리오에 주식 투자의 기본 개념을 추가해주세요"

# 스토리 톤 변경
"전체적인 분위기를 더 밝고 긍정적으로 만들어주세요"

# 시나리오 확장
"게임 중반부에 위험 관리에 대한 새로운 상황을 추가해주세요"
```

### 🔒 보안 가이드라인

- **적절한 요청만**: 투자 교육 스토리 편집 관련 요청만 처리
- **안전한 콘텐츠**: 교육에 적합한 건전한 내용으로 제한
- **개인정보 제외**: 실제 개인정보나 민감 데이터 입력 금지

## 🏗️ 아키텍처

### 📊 시스템 구조
```
🌐 사용자 인터페이스
├── 🖥️  Streamlit 웹앱 (app.py)
│   ├── 사용자 친화적 UI
│   ├── 실시간 편집 인터페이스
│   └── 스토리 미리보기
│
└── 🔌 FastAPI REST API (main.py)
    ├── RESTful 엔드포인트
    ├── Swagger UI 문서
    └── 시스템 연동 인터페이스

🧠 핵심 로직 계층
├── 🎯 GameCustomizer (스토리 편집 엔진)
├── 🤖 LLM Handler (Google Gemini 연동)
├── 🔒 Security Filter (보안 검증)
└── 📁 Story Manager (파일 관리)

🛠️ 유틸리티 계층
├── ⚙️  Config (환경 설정)
├── 🚨 Error Handler (에러 처리)
├── ⚡ Performance Monitor (성능 관리)
└── 📝 Prompts (프롬프트 템플릿)
```

### 🔄 데이터 플로우
```
📝 사용자 요청
    ↓
🔍 입력 검증 (JSON, 필수 필드)
    ↓
🛡️ 보안 검증 (콘텐츠 필터링)
    ↓
🎯 편집 요청 분석
    ↓
🤖 Google Gemini LLM 호출
    ↓
✅ 응답 검증 (JSON 구조)
    ↓
📊 결과 반환 (Streamlit/API)
```

### 🎯 FastAPI 엔드포인트
- **GET /** - 루트 엔드포인트
- **GET /health** - 헬스체크  
- **POST /edit-scenario** - 스토리 편집 (메인 기능)
  - 응답에 `summary` 필드 포함: 시나리오 요약 정보 제공
- **POST /edit-scenario-async** - 비동기 스토리 편집
  - 응답에 `summary` 필드 포함: 시나리오 요약 정보 제공
- **GET /docs** - API 문서 (Swagger UI)

## 🛠️ 개발 정보

### 🔧 기술 스택
- **Frontend**: Streamlit 1.28+
- **Backend**: FastAPI 0.104+ & Python 3.10+
- **LLM**: Google Gemini Pro 1.5
- **데이터**: JSON 기반 스토리 구조
- **패키지 관리**: UV (추천) 또는 pip
- **컨테이너**: Docker & Docker Compose

### 📦 주요 의존성
```python
# 웹 프레임워크
streamlit>=1.28.0
fastapi>=0.104.0
uvicorn>=0.24.0

# LLM 프레임워크  
langchain>=0.1.0
langchain-google-genai>=2.0.0
google-generativeai>=0.8.0

# 환경 관리
python-dotenv>=1.0.0
```

### 🔍 핵심 모듈 설명

#### 🎯 편집 엔진
- **`main.py`**: FastAPI 서버 및 REST API 엔드포인트
- **`app.py`**: Streamlit 웹앱 메인 인터페이스
- **`game_customizer.py`**: 스토리 편집 핵심 로직
- **`llm_handler.py`**: Google Gemini API 통신

#### 🛠️ 유틸리티
- **`config.py`**: 환경 변수 및 API 키 관리
- **`prompts.py`**: LLM용 프롬프트 템플릿
- **`story_manager.py`**: JSON 파일 읽기/쓰기
- **`security.py`**: 보안 검증 및 필터링

#### 🎨 UI 컴포넌트
- **`chat_interface.py`**: AI 채팅 인터페이스
- **`story_viewer.py`**: 스토리 미리보기
- **`story_selector.py`**: 스토리 선택 UI
- **`sidebar.py`**: 사이드바 및 설정

## 🚀 배포

### 🌐 로컬 개발 환경

```bash
# Streamlit 개발 서버
streamlit run app.py --server.port 8501

# FastAPI 개발 서버  
python main.py
```

### 🐳 Docker 배포

**단일 컨테이너:**
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501 8000
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Docker Compose (권장):**
```yaml
version: '3.8'
services:
  story-editor:
    build: .
    ports:
      - "8501:8501"  # Streamlit
      - "8000:8000"  # FastAPI
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./saved_stories:/app/saved_stories
```

### ☁️ 클라우드 배포 옵션

**Streamlit Cloud:**
1. GitHub 레포지토리 연결
2. Secrets에 `GOOGLE_API_KEY` 설정
3. `streamlit run app.py` 자동 배포

**기타 플랫폼:**
- **Heroku**: Procfile 설정으로 배포
- **Railway**: GitHub 연동 자동 배포  
- **Google Cloud Run**: 컨테이너 기반 배포
- **AWS ECS**: Docker 기반 스케일링 배포

## 📊 성능 및 최적화

### 🚀 주요 성능 지표
- **응답 속도**: Google Gemini 직접 연동으로 빠른 처리
- **메모리 효율**: 최소한의 의존성으로 가벼운 실행
- **안정성**: 엄격한 JSON 검증 및 에러 처리
- **확장성**: FastAPI의 비동기 처리 지원

### 📈 최적화 사항
1. **의존성 최소화**: LangChain 제거로 시작 시간 단축
2. **직접 API 호출**: Google AI SDK 직접 사용
3. **구조화된 프롬프트**: 정확한 편집을 위한 특화 프롬프트
4. **에러 복구**: 자동 재시도 및 안전한 fallback

### 🔧 트러블슈팅

#### 일반적인 문제들
1. **API 키 오류**: 
   ```bash
   # .env 파일 확인
   cat .env
   # 환경 변수 확인
   echo $GOOGLE_API_KEY
   ```

2. **포트 충돌**:
   ```bash
   # 포트 사용 확인
   lsof -i :8501
   lsof -i :8000
   ```

3. **Docker 메모리 부족**:
   ```bash
   # 메모리 제한 설정
   docker run --memory=2g story-editor
   ```

#### 성능 모니터링
- **헬스체크**: `http://localhost:8000/health`
- **로그 확인**: 터미널에서 실시간 로그 모니터링
- **메모리 사용량**: Docker stats 또는 시스템 모니터

## 🔧 유지보수 및 모니터링

### 📊 시스템 모니터링
```bash
# 헬스체크
curl http://localhost:8000/health

# API 문서 접근
curl http://localhost:8000/docs

# 로그 확인
docker logs <container_id>
```

### 🛠️ 개발 모드
```bash
# 핫 리로드 모드로 실행
streamlit run app.py --server.runOnSave true

# FastAPI 개발 모드
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 📈 향후 개선 계획
- **다국어 지원**: 영어, 중국어 스토리 편집
- **고급 편집**: 스토리 구조 자동 분석 및 제안
- **배치 처리**: 여러 스토리 동시 편집
- **버전 관리**: Git 기반 스토리 변경 이력 관리
- **A/B 테스트**: 다양한 편집 결과 비교

## 📋 업데이트 로그

### v2.0.0 - 이중 인터페이스 완성 ✅
- **FastAPI 서버**: REST API 기반 시스템 연동 지원
- **Streamlit 웹앱**: 사용자 친화적 웹 인터페이스  
- **Docker 지원**: 컨테이너 기반 배포 환경
- **성능 최적화**: 의존성 최소화 및 직접 API 연동

### v1.5.0 - 핵심 기능 안정화 ✅
- **JSON 검증**: 엄격한 입출력 데이터 검증
- **에러 처리**: 포괄적인 예외 상황 대응
- **보안 강화**: 입력 검증 및 콘텐츠 필터링
- **프롬프트 최적화**: 정확한 편집을 위한 특화 프롬프트

### v1.0.0 - 기본 편집 기능 ✅
- **핵심 기능**: Google Gemini API 기반 스토리 편집
- **파일 호환성**: JSON 배열 형식 지원
- **사용성**: 자연어 편집 요청 및 실시간 검증
- **안정성**: 기본적인 에러 처리 및 세션 관리

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 교육용 목적으로 자유롭게 사용 가능합니다.

## 🤝 기여하기

### 기여 방법
1. **이슈 리포트**: 버그나 개선사항 제안
2. **코드 기여**: Pull Request 환영
3. **문서 개선**: README 및 코드 주석 개선
4. **테스트 추가**: 기능별 테스트 케이스 작성

### 개발 가이드라인
```bash
# 개발 환경 설정
git clone <repository_url>
cd making_story_chatbot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 코드 스타일 확인
black source/
flake8 source/
```

## 📞 지원 및 문의

- **GitHub Issues**: 버그 리포트 및 기능 요청
- **Discussions**: 일반적인 질문 및 토론
- **Email**: 프로젝트 관련 직접 문의

---

## 🎯 빠른 참고

### 🔧 필수 명령어
```bash
# Streamlit 앱 실행
streamlit run app.py

# FastAPI 서버 실행  
python main.py

# Docker 실행
docker-compose up -d

# 헬스체크
curl http://localhost:8000/health
```

### 🔑 필수 설정
```bash
# .env 파일 생성
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

### 📚 주요 URL
- **Streamlit 앱**: http://localhost:8501
- **FastAPI 문서**: http://localhost:8000/docs  
- **헬스체크**: http://localhost:8000/health

---

**⭐ 도움이 되셨다면 Star를 눌러주세요!**

**🚀 지금 바로 시작**: `streamlit run app.py` 실행 후 브라우저에서 접속하세요!

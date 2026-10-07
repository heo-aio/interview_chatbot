# AI 면접관 챗봇

AI 서비스 개발자 면접을 준비하다가, 혼자 연습할 때 질문해 줄 사람이 없어서 만들어 본 챗봇입니다.
프로젝트를 설명하면 면접관이 한 번에 질문 하나씩 던지고, 면접이 끝나면 피드백을 줍니다.

## 아래와 같이 동작

- 프로젝트 설명을 보내면 면접관이 한 줄로 요약하고 질문을 1개 합니다.
- 답변에서 모호한 부분을 골라 꼬리질문을 합니다. (왜 그 방법을 썼는지, 다른 대안은 없었는지 등)
- 질문이 5개 끝나거나 "종료"를 입력하면 피드백을 줍니다.
  - 잘한 점 / 아쉬운 점 / 더 좋은 답변 예시 / 다음 준비
- "모르겠어요"라고 하면 정답 대신 힌트를 한 줄만 줍니다.
- 면접과 상관없는 질문(점심 메뉴 등)은 정중히 거절합니다.

이 규칙들은 전부 시스템 프롬프트(`app/prompts/system_prompt.py`)에 적어 두었고,
역할 → 톤 → 언어 → 제약 순서로 작성했습니다.

## 사용한 기술

- Python
- FastAPI, Uvicorn (백엔드)
- OpenAI SDK (OpenAI 호환 API 호출)
- Streamlit (채팅 화면)

## 폴더 구조

```
mini_project/
├─ app/
│  ├─ main.py                  # FastAPI 앱 시작점
│  ├─ routers/chat.py          # POST /chat/stream
│  ├─ schemas/chat.py          # 요청 형식 (message, model, temperature)
│  ├─ services/
│  │  ├─ chat_service.py       # 메시지 조립, 캐시 확인, 에러 처리
│  │  └─ cache.py              # 메모리 캐시
│  ├─ clients/openai_client.py # LLM 호출 (스트리밍)
│  ├─ prompts/
│  │  ├─ system_prompt.py      # 면접관 시스템 프롬프트
│  │  └─ demo_qeustions.py     # 데모용 질문 5개
│  └─ core/
│     ├─ config.py             # .env 읽기
│     └─ logging_config.py     # 로그 설정
└─ frontend/streamlit_app.py   # 채팅 화면
```

## 실행 방법

1. 가상환경을 만들고 켭니다.

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. 패키지를 설치합니다.

```bash
pip install fastapi uvicorn openai python-dotenv streamlit requests
```

3. 프로젝트 최상위 폴더에 `.env` 파일을 만들고 아래처럼 채웁니다.

```
MLAPI_API_KEY=발급받은_키
MLAPI_MODEL=사용할_모델_이름
MLAPI_BASE_URL=API_주소
```

`MLAPI_BASE_URL`을 비워 두면 OpenAI 기본 주소로 호출합니다.

4. 서버를 켭니다. (터미널 1)

```bash
uvicorn app.main:app --reload
```

5. 채팅 화면을 켭니다. (터미널 2)

```bash
streamlit run frontend/streamlit_app.py
```

브라우저에서 `http://localhost:8501`이 열립니다.
화면 없이 API만 테스트하고 싶으면 `http://127.0.0.1:8000/docs`에서 `POST /chat/stream`을 직접 호출해 볼 수 있어요.

요청 예시:

```json
{"message": "저는 PDF 기반 RAG 챗봇을 만들었어요. 사용 기술은 Python, LangChain, ChromaDB입니다."}
```

`model`, `temperature`는 선택이라 안 보내면 기본값을 씁니다.

## 만들면서 신경 쓴 부분

- 답변을 한 번에 주지 않고 스트리밍으로 한 글자씩 흘려보냅니다. (`StreamingResponse`)
- 같은 질문과 설정이면 LLM을 다시 부르지 않고 캐시에서 답을 줍니다. 메시지, 모델, temperature를 합쳐서 sha256 해시를 키로 썼습니다.
- 캐시 HIT/MISS와 응답 시간을 로그로 남겨서 동작을 눈으로 확인할 수 있게 했습니다.
- LLM 호출이 실패해도 서버가 죽지 않고 `[ERROR]` 메시지를 돌려줍니다.
- API 키는 `.env`에만 두고 깃에는 올리지 않았습니다.

## 아직 부족한 점

- **이전 대화를 기억하지 못합니다.** 지금은 매 요청마다 시스템 프롬프트와 질문 1개만 보내서, 꼬리질문이 앞 내용을 이어받지 못합니다. 대화 기록(history)을 같이 보내도록 고칠 예정입니다.
- 캐시가 메모리에만 있어서 서버를 껐다 켜면 사라집니다.
- 테스트 코드가 없습니다.
- 파일 이름 `demo_qeustions.py`에 오타가 있어서 나중에 고치려고 합니다.

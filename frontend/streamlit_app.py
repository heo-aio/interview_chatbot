import codecs
import sys
from pathlib import Path

import requests
import streamlit as st

# 프로젝트 최상위 폴더를 import 경로에 추가 (app 폴더의 데모 질문을 가져오기 위해)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from app.prompts.demo_qeustions import DEMO_Q
except Exception:
    DEMO_Q = []

API_URL = "http://127.0.0.1:8000/chat/stream"
DONE_MARKERS = ["\\n[DONE]", "\n[DONE]", "[DONE]"]


def stream_reply(message: str, history: list):
    """FastAPI 서버에 질문을 보내고, 답변을 조각 단위로 yield 한다."""
    decoder = codecs.getincrementaldecoder("utf-8")()  # 한글이 chunk 경계에서 깨지지 않게
    payload = {"message": message, "history": history}
    with requests.post(API_URL, json=payload, stream=True, timeout=60) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=None):
            text = decoder.decode(chunk)
            for marker in DONE_MARKERS:
                text = text.replace(marker, "")
            if text:
                yield text


st.set_page_config(page_title="AI 면접관", page_icon="🎤")
st.title("🎤 AI 서비스 개발자 면접관")
st.caption("프로젝트를 설명하면 면접관이 질문합니다. 면접을 끝내려면 '종료'라고 입력하세요.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 사이드바: 새 면접 시작 + 데모 질문
with st.sidebar:
    if st.button("🔄 새 면접 시작", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if DEMO_Q:
        st.divider()
        st.subheader("데모 질문")
        for i, q in enumerate(DEMO_Q):
            if st.button(q, key=f"demo_{i}", use_container_width=True):
                st.session_state.pending = q
                st.rerun()

# 지금까지의 대화 그리기
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 입력 받기 (직접 입력 또는 사이드바 데모 질문)
pending = st.session_state.pop("pending", None)
prompt = st.chat_input("답변을 입력하세요") or pending

if prompt:
    history = list(st.session_state.messages)  # 이번 질문 이전의 대화

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            reply = st.write_stream(stream_reply(prompt, history))
        except requests.exceptions.ConnectionError:
            reply = "⚠️ 서버에 연결할 수 없어요. `uvicorn app.main:app --reload`가 켜져 있는지 확인하세요."
            st.error(reply)
        except Exception as e:
            reply = f"⚠️ 에러: {type(e).__name__}: {e}"
            st.error(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Анализ документов", layout="wide")


st.markdown(
    """
    <style>
    /* Контейнер чата */
    .chat-container {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 1rem;
        height: 600px;              /* Увеличил высоту (было 400px) */
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        scroll-behavior: smooth;
        margin-bottom: 0.5rem;      /* небольшой отступ снизу перед быстрыми промтами */
    }

    /* Сообщения */
    .msg-row {
        display: flex;
        margin-bottom: 0.5rem;
    }
    .msg-row.user {
        justify-content: flex-end;
    }
    .msg-row.assistant {
        justify-content: flex-start;
    }

    .bubble {
        max-width: 75%;
        padding: 0.5rem 0.75rem;
        border-radius: 12px;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .user-bubble {
        background-color: #4a90e2;
        color: white;
        border-top-right-radius: 0;
    }
    .assistant-bubble {
        background-color: #333333;
        color: #f5f5f5;
        border-top-left-radius: 0;
    }

    /* Стили для select */
    div[data-baseweb="select"] > div {
        background-color: #262626 !important;
        color: white !important;
        border: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def load_chat_history(document_id: int, headers_: dict):
    response_hist = requests.get(f"{API_URL}/chat/chat/history", params={"document_id": document_id}, headers=headers_)
    if response_hist.status_code == 200:
        data = response_hist.json()
        return data.get("history", [])
    else:
        st.error(f"Ошибка при загрузке истории: {response_hist.text}")
        return []


if "access_token" not in st.session_state or not st.session_state.access_token:
    st.warning("Пожалуйста, войдите в систему через главную страницу.")
    st.switch_page("pages/auth_page.py")

headers = {"Authorization": f"Bearer {st.session_state.access_token}"}


st.subheader("📄 Выберите документ")
response = requests.get(f"{API_URL}/documents/my", headers=headers)

if response.status_code == 200:
    documents = response.json()
    if not documents:
        st.info("Нет доступных документов для анализа.")
        st.stop()
else:
    st.error("Не удалось загрузить список документов")
    st.stop()

doc_names = [doc["filename"] for doc in documents]
selected_doc_name = st.selectbox("Документ", doc_names)
selected_doc = next(doc for doc in documents if doc["filename"] == selected_doc_name)
selected_doc_id = selected_doc["id"]


st.subheader("⚙️ Модель")
model_names = ["gpt-4o-mini", "mistralai/mistral-nemo:free"]
if "selected_model" not in st.session_state:
    st.session_state.selected_model = model_names[0]

selected_model = st.radio(
    "Модель ответа",
    model_names,
    index=model_names.index(st.session_state.selected_model),
    horizontal=True,
    label_visibility="collapsed",
    key="model_select"
)
st.session_state.selected_model = selected_model




chat_history = load_chat_history(selected_doc_id, headers)

chat_html = '<div class="chat-container" id="chat-box">'
for msg in chat_history:
    role = msg.get("role", "assistant")
    text = msg.get("message", "")
    chat_html += f'<div class="msg-row {role}"><div class="bubble {role}-bubble">{text}</div></div>'
chat_html += '</div>'

st.markdown(chat_html, unsafe_allow_html=True)

st.markdown(
    """
    <script>
    const chatBox = window.parent.document.getElementById('chat-box');
    if (chatBox) {
        chatBox.scrollTop = chatBox.scrollHeight;
    }
    </script>
    """,
    unsafe_allow_html=True
)

prompt_options = {
    "📝 Сгенерировать резюме": {"type": "summary"},
    "🧠 Основные тезисы": {"type": "key_points"},
    "❓ Список вопросов": {"type": "faq"},
    "📌 Ключевые имена и термины": {"type": "entities"}
}

prompt_key = f"prompt_select_{selected_doc_id}"
handled_key = f"{prompt_key}_handled"

if prompt_key not in st.session_state:
    st.session_state[prompt_key] = "Быстрый запрос"
if handled_key not in st.session_state:
    st.session_state[handled_key] = None

prompt_list = ["Быстрый запрос"] + list(prompt_options.keys())
current_index = prompt_list.index(st.session_state[prompt_key]) if st.session_state[prompt_key] in prompt_list else 0

selected_prompt = st.selectbox(
    "Быстрый запрос",
    prompt_list,
    index=current_index,
    key=prompt_key,
    label_visibility="collapsed"
)

if selected_prompt != "Быстрый запрос" and st.session_state.get(handled_key) != selected_prompt:
    prompt = {
        "document_id": selected_doc_id,
        "message": selected_prompt,
        "model": st.session_state.selected_model
    }

    with st.spinner(f"Отвечает {st.session_state.selected_model}... ⏳"):
        res = requests.post(
            f"{API_URL}/chat/chat/request",
            headers=headers,
            json=prompt,
            timeout=300
        )

    st.session_state[handled_key] = selected_prompt

    st.rerun()



user_input = st.chat_input("Введите сообщение...")

if user_input:
    prompt = {
        "document_id": selected_doc_id,
        "message": user_input,
        "model": st.session_state.selected_model
    }

    with st.spinner(f"Отвечает {st.session_state.selected_model}... ⏳"):
        res = requests.post(
            f"{API_URL}/chat/chat/request",
            headers=headers,
            json=prompt
        )
    st.rerun()

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
model_names = ["GPT-5", "DeepSeek"]
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


if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

if selected_doc_id not in st.session_state.chat_history:
    st.session_state.chat_history[selected_doc_id] = []


converted = []
for m in st.session_state.chat_history[selected_doc_id]:
    if isinstance(m, tuple) and len(m) == 2:
        role, text = m
        converted.append({"role": role, "text": text})
    elif isinstance(m, dict):
        converted.append(m)
st.session_state.chat_history[selected_doc_id] = converted


chat_html = '<div class="chat-container" id="chat-box">'
for msg in st.session_state.chat_history[selected_doc_id]:
    role = msg.get("role", "assistant")
    text = msg.get("text", "")
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
    prompt_data = prompt_options[selected_prompt].copy()
    prompt_data["model"] = st.session_state.selected_model

    st.session_state.chat_history[selected_doc_id].append({"role": "user", "text": selected_prompt})

    with st.spinner(f"Отвечает {st.session_state.selected_model}... ⏳"):
        res = requests.post(
            f"{API_URL}/documents/{selected_doc_id}/analyze",
            headers=headers,
            json=prompt_data,
            timeout=60
        )
        if res.status_code == 200:
            result = res.json().get("result", "")
            st.session_state.chat_history[selected_doc_id].append({"role": "assistant", "text": result})
        else:
            st.session_state.chat_history[selected_doc_id].append({
                "role": "assistant",
                "text": f"Ошибка: {res.status_code} {res.text}"
            })

    st.session_state[handled_key] = selected_prompt

    st.rerun()



user_input = st.chat_input("Введите сообщение...")

if user_input:
    st.session_state.chat_history[selected_doc_id].append({"role": "user", "text": user_input})

    payload = {"type": "question", "question": user_input, "model": st.session_state.selected_model}

    with st.spinner(f"Отвечает {st.session_state.selected_model}... ⏳"):
        res = requests.post(
            f"{API_URL}/documents/{selected_doc_id}/analyze",
            headers=headers,
            json=payload
        )
        if res.status_code == 200:
            result = res.json()["result"]
            st.session_state.chat_history[selected_doc_id].append({"role": "assistant", "text": result})
        else:
            st.session_state.chat_history[selected_doc_id].append({
                "role": "assistant",
                "text": f"Ошибка: {res.status_code} {res.text}"
            })
    st.rerun()

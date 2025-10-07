import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("🧠 Анализ документов")

if "access_token" not in st.session_state or not st.session_state.access_token:
    st.warning("Пожалуйста, войдите в систему через главную страницу.")
    st.switch_page("pages/auth_page.py")

headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

st.subheader("📄 Выберите документ для анализа")
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
selected_doc_name = st.selectbox("Выберите документ", doc_names)

selected_doc = next(doc for doc in documents if doc["filename"] == selected_doc_name)
selected_doc_id = selected_doc["id"]

st.subheader("⚡ Выберите тип анализа")
analysis_type = st.radio(
    "Варианты:",
    ["📝 Резюме документа", "❓ Ответить на вопрос по документу"]
)

user_question = None
if analysis_type == "❓ Ответить на вопрос по документу":
    user_question = st.text_area("Введите ваш вопрос:")

if st.button("🚀 Запустить анализ"):
    with st.spinner("Анализируем документ... ⏳"):
        payload = {"type": analysis_type, "question": user_question}
        res = requests.post(
            f"{API_URL}/documents/{selected_doc_id}/analyze",
            headers=headers,
            json=payload
        )

    if res.status_code == 200:
        result = res.json()
        st.success("✅ Анализ завершён")
        st.markdown("### 📊 Результат:")
        st.write(result["result"])
    else:
        st.error(f"Ошибка анализа: {res.text}")

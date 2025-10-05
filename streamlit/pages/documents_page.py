import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("📂 Мои документы")

if "access_token" not in st.session_state:
    st.warning("Пожалуйста, войдите в систему через главную страницу.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
st.write("DEBUG TOKEN:", st.session_state.access_token)

# 📤 Загрузка нового документа
st.subheader("📤 Загрузить новый документ")
uploaded_file = st.file_uploader("Выберите файл")
if uploaded_file and st.button("Загрузить"):
    files = {
        "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
    }
    response = requests.post(f"{API_URL}/documents/upload", files=files, headers=headers)

    if response.status_code == 200:
        st.success(f"✅ Файл `{uploaded_file.name}` успешно загружен")
    else:
        st.error(f"❌ Ошибка загрузки: {response.text}")

# 📄 Список загруженных документов
st.subheader("📄 Список документов")
response = requests.get(f"{API_URL}/documents/my", headers=headers)
if response.status_code == 200:
    docs = response.json()
    if docs:
        for doc in docs:
            st.write(f"📎 {doc['filename']} — загружен {doc['uploaded_at']}")
    else:
        st.info("Нет загруженных документов.")
else:
    st.error("Не удалось получить список документов.")


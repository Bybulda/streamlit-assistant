# streamlit_app/app.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Document Assistant", page_icon="📄", layout="wide")

# Инициализация состояния сессии
if "access_token" not in st.session_state:
    st.session_state.access_token = None

# Заголовок
st.title("📄 Document Assistant")
name = None

# Если пользователь не вошёл — форма логина
if st.session_state.access_token is None:
    st.subheader("🔐 Авторизация")
    username = st.text_input("Имя пользователя")
    password = st.text_input("Пароль", type="password")
    if st.button("Войти"):
        response = requests.post(
            f"{API_URL}/auth/login",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            name = username
            st.session_state.access_token = token
            st.success("✅ Успешный вход")
            st.rerun()
        else:
            st.error("❌ Неверные учетные данные")

else:
    # Если вошёл — показываем меню и кнопку выхода
    col1, col2 = st.columns([6, 1])
    with col1:
        st.write(f"Привет, **{name}** 👋")
    with col2:
        if st.button("🚪 Выйти"):
            st.session_state.access_token = None
            st.rerun()

    st.sidebar.success("Выберите страницу в меню слева ⬅️")

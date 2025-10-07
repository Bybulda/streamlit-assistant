import streamlit as st
import requests

API_URL = "http://localhost:8000"  # замени на свой адрес бекэнда

st.set_page_config(page_title="🔐 Авторизация", page_icon="🔑", layout="centered")


if "access_token" not in st.session_state:
    st.session_state.access_token = None

st.title("🤖 AI Assistant")
st.caption("Добро пожаловать! Войдите в систему или создайте аккаунт, чтобы продолжить.")


tab_login, tab_register = st.tabs(["🔑 Вход", "📝 Регистрация"])

# -------------------- ВХОД --------------------
with tab_login:
    st.subheader("Вход в систему")

    login_username = st.text_input("Имя пользователя", key="login_username")
    login_password = st.text_input("Пароль", type="password", key="login_password")

    if st.button("Войти", use_container_width=True, type="primary"):
        if not login_username or not login_password:
            st.warning("Пожалуйста, заполните все поля.")
        else:
            try:
                r = requests.post(
                    f"{API_URL}/auth/login",
                    data={"username": login_username, "password": login_password},
                )
                if r.status_code == 200:
                    token = r.json().get("access_token")
                    st.session_state.access_token = token
                    st.success(f"✅ Добро пожаловать, {login_username}!")
                    st.rerun()
                else:
                    st.error("❌ Неверное имя пользователя или пароль.")
            except Exception as e:
                st.error(f"Ошибка подключения к серверу: {e}")


with tab_register:
    st.subheader("Создать новый аккаунт")

    reg_username = st.text_input("Имя пользователя", key="reg_username")
    reg_password = st.text_input("Пароль", type="password", key="reg_password")
    reg_confirm = st.text_input("Повторите пароль", type="password", key="reg_confirm")

    if st.button("Зарегистрироваться", use_container_width=True):
        if not reg_username or not reg_password or not reg_confirm:
            st.warning("⚠️ Все поля обязательны для заполнения.")
        elif reg_password != reg_confirm:
            st.error("❌ Пароли не совпадают.")
        else:
            try:
                r = requests.post(
                    f"{API_URL}/auth/register",
                    params={"username": reg_username, "password": reg_password},
                )
                if r.status_code == 200:
                    st.success("✅ Аккаунт успешно создан! Теперь вы можете войти.")
                elif r.status_code == 409:
                    st.error("👤 Пользователь с таким именем уже существует.")
                else:
                    st.error(f"Ошибка регистрации: {r.text}")
            except Exception as e:
                st.error(f"Ошибка подключения к серверу: {e}")

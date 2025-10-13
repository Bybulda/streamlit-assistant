import streamlit as st

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if not st.session_state.access_token:
    st.switch_page("pages/auth_page.py")

st.sidebar.success("✅ Вы вошли в систему")
if st.sidebar.button("🚪 Выйти"):
    st.session_state.access_token = None
    st.switch_page("pages/auth_page.py")

st.title("🤖 AI Assistant")
st.write("Добро пожаловать! Выберите страницу в меню слева.")

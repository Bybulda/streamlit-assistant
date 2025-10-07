import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

if "access_token" not in st.session_state or not st.session_state.access_token:
    st.switch_page("pages/auth_page.py")

headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

st.title("📚 Мои документы")

st.subheader("📤 Загрузить новый документ")
uploaded_file = st.file_uploader("Выберите файл")

if uploaded_file and st.button("Загрузить"):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    res = requests.post(f"{API_URL}/documents/upload", files=files, headers=headers)
    if res.status_code == 200:
        st.success(f"✅ Файл `{uploaded_file.name}` успешно загружен")
    else:
        st.error(f"❌ Ошибка загрузки: {res.text}")

st.subheader("📄 Список загруженных документов")


def load_documents():
    response = requests.get(f"{API_URL}/documents/my", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Не удалось получить список документов.")
        return []


docs = load_documents()

if docs:
    for doc in docs:
        try:
            formatted_date = datetime.fromisoformat(doc['uploaded_at']).strftime("%d.%m.%Y %H:%M")
        except Exception:
            formatted_date = doc.get('uploaded_at', '-')

        with st.expander(f"📎 {doc['filename']}  —  {formatted_date}"):
            action = st.radio(
                "Выберите действие:",
                ["📥 Скачать", "🗑 Удалить"],
                key=f"action_{doc['id']}",
                horizontal=True
            )

            if action == "📥 Скачать":
                if st.button("⬇ Скачать файл", key=f"dl_{doc['id']}"):
                    download_url = f"{API_URL}/documents/{doc['id']}/download"
                    r = requests.get(download_url, headers=headers)
                    if r.status_code == 200:
                        st.download_button(
                            label=f"Скачать {doc['filename']}",
                            data=r.content,
                            file_name=doc['filename'],
                            mime="application/octet-stream",
                            key=f"save_{doc['id']}"
                        )
                    else:
                        st.error("Не удалось скачать файл")

            elif action == "🗑 Удалить":
                if st.button("Удалить документ", key=f"del_{doc['id']}"):
                    delete_url = f"{API_URL}/documents/{doc['id']}"
                    r = requests.delete(delete_url, headers=headers)
                    if r.status_code == 200:
                        st.success(f"Документ `{doc['filename']}` удалён 🧹")
                        st.rerun()
                    else:
                        st.error("Ошибка при удалении файла")
else:
    st.info("📭 У вас пока нет загруженных документов.")

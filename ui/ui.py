import streamlit as st
import requests
import json

# FastAPI sunucumuzun adresi. Docker kullanmıyorsak localhost'tur.
API_URL = "http://127.0.0.1:8000/api/query"

# --- Streamlit Arayüz Ayarları ---

st.set_page_config(
    page_title="AI Asistanı",
    page_icon="😎"
)

st.title("😎 AI Asistanı")
st.caption("GitHub kullanıcıları, repoları, swagger url hakkında sorular sorun...")

# --- Sohbet Geçmişini Yönetme ---

# Streamlit'in session_state özelliğini kullanarak sohbet geçmişini saklıyoruz.
# Bu sayede sayfa her yenilendiğinde mesajlar kaybolmaz.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Geçmişteki mesajları ekrana yazdır
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Kullanıcı Girdisini Alma ve API ile İletişim ---

# st.chat_input, modern bir sohbet arayüzü için en iyi bileşendir.
if prompt := st.chat_input("Mesajınızı buraya yazın..."):
    # 1. Kullanıcının mesajını sohbet geçmişine ekle ve ekranda göster
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Asistanın cevabı için bir bekleme alanı oluştur
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("...")  # Kullanıcıya beklediğini göster

        try:
            # 3. FastAPI backend'ine isteği gönder
            payload = {"message": prompt}
            response = requests.post(API_URL, json=payload)

            # Yanıt başarılıysa
            if response.status_code == 200:
                api_response = response.json()
                full_response = api_response.get("reply", "Bir hata oluştu.")
            # Yanıt başarısızsa
            else:
                full_response = f"Hata: Sunucudan {response.status_code} koduyla yanıt alındı."

        except requests.exceptions.RequestException as e:
            full_response = f"API bağlantı hatası: {e}"

        # 4. Gelen cevabı ekrana yazdır ve sohbet geçmişine ekle
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
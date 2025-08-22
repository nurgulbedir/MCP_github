import streamlit as st
import requests
import json

# FastAPI sunucumuzun adresi. Docker kullanmıyorsak localhost'tur.
API_URL = "http://127.0.0.1:8000/api/query"


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
        try:
            # 2. CANLI AKIŞ (STREAMING) İÇİN GENERATOR FONKSİYONU
            # Bu fonksiyon, backend'den gelen veri akışını parça parça yakalar.
            def stream_backend_response():

                # 3. HAFIZAYI (CHAT HISTORY) HAZIRLAMA VE GÖNDERME
                # Bir önceki konuşmaları, backend'in anlayacağı formata çeviriyoruz.
                cohere_chat_history = []
                # Yeni prompt hariç, önceki tüm mesajları al.
                for msg in st.session_state.messages[:-1]:
                    role = "USER" if msg["role"] == "user" else "CHATBOT"
                    cohere_chat_history.append({"role": role, "message": msg["content"]})

                # Backend'e gönderilecek olan tam paket (yeni mesaj + geçmiş)
                payload = {
                    "message": prompt,
                    "chat_history": cohere_chat_history
                }

                # stream=True ile bağlantıyı açık tutuyor ve canlı yayın başlatıyoruz.
                with requests.post(API_URL, json=payload, stream=True) as response:
                    response.raise_for_status()  # HTTP hatası varsa hata fırlat
                    # Gelen her metin parçasını ("chunk") anında dışarı "yield" et.
                    for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                        yield chunk


            # 4. YAZIYORMUŞ GİBİ GÖSTERME
            # st.write_stream, yukarıdaki fonksiyondan gelen her parçayı anında ekrana yazar.
            # Akış bittiğinde, birleşen tam metni 'full_response' değişkenine atar.
            full_response = st.write_stream(stream_backend_response)

            # Tamamlanan cevabı, gelecekteki konuşmalar için hafızaya ekliyoruz.
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except requests.exceptions.RequestException as e:
            st.error(f"API bağlantı hatası: {e}")
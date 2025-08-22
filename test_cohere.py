import os
import cohere
from dotenv import load_dotenv

# .env dosyasını yüklemeyi dene
load_dotenv()

print("--- Cohere API Anahtarı Testi Başladı ---")

# API anahtarını .env dosyasından oku
api_key = os.getenv("COHERE_API_KEY")

if not api_key:
    print("\n!!!!!! HATA: .env dosyasında COHERE_API_KEY bulunamadı! !!!!!!")
    print("Lütfen .env dosyasının doğru klasörde olduğundan ve içeriğinin doğru yazıldığından emin olun.")
else:
    print(f"API Anahtarı bulundu. Anahtarın son 4 hanesi: ...{api_key[-4:]}")

    try:
        # Cohere client'ını bu anahtarla başlat
        co = cohere.Client(api_key)

        print("Cohere'e basit bir test isteği gönderiliyor...")

        # Projemizdeki gibi karmaşık araçlar olmadan, en basit isteği gönder
        response = co.chat(message="Merhaba, nasılsın?")

        print("\n--- BAŞARILI! ---")
        print("Cohere'den cevap başarıyla alındı.")
        print(f"Gelen Cevap: {response.text}")

    except Exception as e:
        import traceback

        print(f"\n!!!!!! HATA: Cohere'e bağlanırken bir sorun oluştu! !!!!!!")
        print(f"Hata Tipi: {type(e).__name__}")
        print(f"Hata Mesajı: {e}")
        traceback.print_exc()
# test_endpoint.py
import requests
import json


def test_get_advisories():
    """
    Belirtilen endpoint'e basit bir GET isteği gönderir ve sonucu yazdırır.
    Bu, endpoint'in canlı olup olmadığını ve nasıl bir cevap verdiğini test etmek içindir.
    """
    # Test edeceğimiz endpoint'in tam URL'si.
    # NOT: Bu URL'nin doğru olduğundan emin olmalısınız. Swagger'daki "host" ve "basePath"
    # alanlarını birleştirerek bu URL'yi oluşturmanız gerekebilir.
    # Örnek olarak bir URL yazıyorum, bunu doğrusuyla değiştirin.
    endpoint_url = "https://api.github.com/users/nurgulbedir/following/petercunha"


    print(f"İstek gönderiliyor: {endpoint_url}")

    try:
        # Herhangi bir token veya özel başlık olmadan basit bir istek gönderiyoruz.
        response = requests.get(endpoint_url, timeout=10)

        # HTTP durum kodunu kontrol et (200 OK ise başarılıdır)
        response.raise_for_status()

        print("\n--- BAŞARILI (Status Code: 200) ---")

        # Gelen cevabı JSON formatında alıp güzelce yazdıralım.
        response_data = response.json()
        print(json.dumps(response_data, indent=2, ensure_ascii=False))

    except requests.exceptions.HTTPError as http_err:
        print(f"\n--- HTTP Hatası Oluştu ---")
        print(f"Status Code: {http_err.response.status_code}")
        print(f"Cevap: {http_err.response.text}")
        print("\nBu endpoint bir kimlik doğrulama (API Key/Token) gerektiriyor olabilir.")

    except requests.exceptions.RequestException as req_err:
        print(f"\n--- Bağlantı Hatası Oluştu ---")
        print(f"Hata: {req_err}")


# Fonksiyonu çalıştır
if __name__ == "__main__":
    test_get_advisories()
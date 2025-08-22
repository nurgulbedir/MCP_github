from services.swagger_service import analyze_swagger_url


# BU FONKSİYONUN ADININ 'summarize_swagger_api' OLDUĞUNDAN EMİN OLUN
def summarize_swagger_api(url: str, keyword: str = None) -> dict:
    """
    Bir API'nin yeteneklerini anlamak için verilen Swagger veya OpenAPI URL'sini analiz eder ve özetler.
    API'nin başlığını, versiyonunu ve mevcut tüm endpoint'lerin bir özetini döndürür.

    Args:
        url (str): Analiz edilecek Swagger/OpenAPI dokümanının tam URL'si.
    """
    print(f"TOOL ÇAĞRILDI: summarize_swagger_api, URL: {url}")
    return analyze_swagger_url(url=url, keyword=keyword)
import cohere
import json
from core.config import settings
from tools.github_tools import list_github_repos, get_github_user_info
from tools.swagger_tools import summarize_swagger_api
from exceptions.custom_exceptions import ServiceConnectionError, CustomAPIException

# Cohere istemcisini başlat
co = cohere.Client(settings.COHERE_API_KEY)

# Sisteme genel davranışını ve kurallarını öğreten ana talimat (Preamble)
TURKISH_PREAMBLE = """
Sen, GitHub hakkında bilgi veren yardımsever bir asistansın ve her zaman Türkçe cevap verirsin.
Sana verilen araçlardan gelen sonuçlar hangi dilde olursa olsun, senin nihai cevabın mutlaka Türkçe olmalı.
ÖNEMLİ KURAL: Eğer kullanıcı sadece tek bir kelime yazarsa ve bu kelime bir kullanıcı adına benziyorsa (örneğin: 'google', 'microsoft', 'nurgulbedir'), bunu o kullanıcının profilini getirme isteği olarak kabul et ve derhal 'get_github_user_info' aracını o kullanıcı adıyla çağır.
"""

# Araç adlarını projedeki gerçek Python fonksiyonlarıyla eşleştiren sözlük
available_tools = {
    "list_github_repos": list_github_repos,
    "get_github_user_info": get_github_user_info,
    "summarize_swagger_api": summarize_swagger_api,
}

# LLM'in hangi araçlara sahip olduğunu ve ne işe yaradıklarını anlaması için gönderilen "menü"
tools_definition = [
    {
        "name": "list_github_repos",
        "description": "Belirtilen bir GitHub kullanıcısının herkese açık repolarını ve ana profil URL'sini listeler.",
        "parameter_definitions": {
            "username": {"description": "Bilgileri alınacak GitHub kullanıcısının adı.", "type": "string",
                         "required": True}
        }
    },
    {
        "name": "get_github_user_info",
        "description": "Belirtilen GitHub kullanıcısının profil bilgilerini (bio, takipçi sayısı vb.) getirir.",
        "parameter_definitions": {
            "username": {"description": "Bilgileri alınacak GitHub kullanıcısının adı.", "type": "string",
                         "required": True}
        }
    },
    {
        "name": "summarize_swagger_api",
        "description": "Bir API'nin yeteneklerini anlamak için verilen Swagger veya OpenAPI URL'sini analiz eder ve özetler. API'nin başlığını, versiyonunu ve mevcut tüm endpoint'lerin bir özetini döndürür.",
        "parameter_definitions": {
            "url": {"description": "Analiz edilecek Swagger/OpenAPI dokümanının tam URL'si.", "type": "string",
                    "required": True}
        }
    }
]


def run_orchestration(user_message: str) -> str:
    """
    Kullanıcı mesajını alır, LLM ve araçlarla işleyerek nihai cevabı döndürür.
    Tüm hata yönetimi, merkezi exception handler'lara delege edilmiştir.
    """
    try:
        # Adım 1: Kullanıcının niyetini anlamak ve hangi aracı kullanacağına karar vermek için ilk çağrı
        response = co.chat(
            message=user_message,
            tools=tools_definition,
            preamble=TURKISH_PREAMBLE
        )

        # Adım 2: LLM bir araç kullanmak istediği sürece bu döngü çalışır
        while response.tool_calls:
            tool_results = []

            for tool_call in response.tool_calls:
                tool_name = tool_call.name
                if tool_name in available_tools:
                    # İlgili aracı parametreleriyle birlikte dinamik olarak çalıştır
                    result = available_tools[tool_name](**tool_call.parameters)

                    # Aracın sonucunu Cohere'in anlayacağı formata çevir
                    tool_results.append({
                        "call": tool_call,
                        "outputs": [{"result": json.dumps(result, ensure_ascii=False)}]
                    })

            # Adım 3: Araçlardan gelen sonuçlarla birlikte LLM'e nihai cevabı oluşturması için ikinci çağrı
            response = co.chat(
                message="",
                tool_results=tool_results,
                preamble=TURKISH_PREAMBLE
            )

        # Adım 4: Başarılı durumda, LLM'in oluşturduğu nihai metin cevabını döndür
        return response.text

    except cohere.CohereError as e:
        # Eğer Cohere API'si ile ilgili bir sorun olursa (örn: API anahtarı, ağ sorunu),
        # bunu yakala ve kendi standart ServiceConnectionError hatamızı fırlat.
        raise ServiceConnectionError(service_name="Cohere AI", original_error=str(e))

    except Exception as e:
        # Eğer bu fonksiyonun içinde bizim öngörmediğimiz başka bir hata olursa
        # (örn: bir mantık hatası), bunu yakala ve genel bir hata olarak fırlat.
        # Bu, sunucunun tamamen çökmesini engeller.
        raise CustomAPIException(detail=f"Orkestrasyon sırasında beklenmedik bir hata oluştu: {e}")
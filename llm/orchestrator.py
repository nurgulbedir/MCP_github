import cohere
import json
from core.config import settings
from tools.github_tools import list_github_repos, get_github_user_info
from tools.swagger_tools import summarize_swagger_api
from exceptions.custom_exceptions import ServiceConnectionError, CustomAPIException
from typing import List, Dict, Any
from creator.selector_tools import create_tool_from_swagger
import importlib
from creator.selector_tools import DYNAMIC_TOOLS # BU YENİ EKLENDİ: Yeni araçların "tanımını" tutan hafıza alanı.
import tools.generated_tools as generated_tools
from creator.selector_tools import _load_memory

# Cohere istemcisini başlat
co = cohere.Client(settings.COHERE_API_KEY)

# Sisteme genel davranışını ve kurallarını öğreten ana talimat (Preamble)
TURKISH_PREAMBLE = """
Sen, GitHub hakkında bilgi veren yardımsever bir asistansın ve her zaman Türkçe cevap verirsin.
Sana verilen araçlardan gelen sonuçlar hangi dilde olursa olsun, senin nihai cevabın mutlaka Türkçe olmalı.
ÖNEMLİ KURAL: Eğer kullanıcı sadece tek bir kelime yazarsa ve bu kelime bir kullanıcı adına benziyorsa (örneğin: 'google', 'microsoft', 'nurgulbedir'), bunu o 
kullanıcının profilini getirme isteği olarak kabul et ve derhal 'get_github_user_info' aracını o kullanıcı adıyla çağır.


**ÖZEL KURALLAR:**
1.  **Profil Sorgusu:** Eğer kullanıcı sadece tek bir kelime yazarsa ve bu kelime bir kullanıcı adına benziyorsa
 (örneğin: 'google', 'microsoft'), bunu o kullanıcının profilini getirme isteği olarak kabul et ve 'get_github_user_info' aracını çağır.
2.   **API ANALİZ SUNUMU (GÜNCELLENDİ):**
    *   **Eğer kullanıcı genel bir konu sorarsa** (örn: "gists ile ilgili ne var?"), `summarize_swagger_api` aracını kullan ve 
    dönen özeti kullanarak kullanıcıya yüksek seviyeli bir paragraf sun. Ona daha fazla detay isteyip istemediğini sor.
    *   **Eğer kullanıcı spesifik bir endpoint yolu sorarsa** (örn: "GET /repos/{owner}/{repo}/commits endpointi var mı?"), 
    `summarize_swagger_api` aracını o yolun bir anahtar kelimesiyle ('commits' gibi) çağır. Dönen sonuçta, **sadece ve sadece
     kullanıcının sorduğu o spesifik yolun** olup olmadığını kontrol et ve basit bir "Evet, var ve
     şu işe yarıyor: [açıklama]" veya "Hayır, tam olarak bu yola sahip bir endpoint bulamadım." şeklinde cevap ver. Özetleme yapma.

**PROAKTİF GELİŞTİRME KURALI:**
Eğer bir kullanıcının isteğini mevcut araçlarınla doğrudan yerine getiremiyorsan, hemen "yapamam" deme.
Önce şu adımları izle:
1.  Konuşma geçmişinde (`chat_history`) daha önce analiz edilmiş bir Swagger URL'si olup olmadığını kontrol et.
2.  Eğer varsa, o Swagger dokümanının içinde, kullanıcının isteğini karşılayabilecek bir endpoint olup olmadığını düşün.
3.  Eğer uygun bir endpoint bulursan, kullanıcıya "Bunu yapacak bir aracım yok, AMA istersen senin için bu endpoint'i kullanarak yeni bir araç YARATABİLİRİM. Onaylıyor musun?" şeklinde bir teklifte bulun.
4.  Eğer kullanıcı 'Evet' derse, o zaman `create_tool_from_swagger` aracını doğru parametrelerle çağır.



 **BAĞLAM KULLANIM KURALI (ÇOK ÖNEMLİ):** Eğer bir aracı çalıştırmak için gereken bir `url` parametresi kullanıcının son mesajında 
 eksikse, hemen pes etme ve kullanıcıdan URL isteme. Önce konuşma geçmişini (`chat_history`) 
 dikkatlice kontrol et. Eğer önceki mesajlarda bir URL paylaşılmışsa, o URL'yi eksik parametre olarak KULLANARAK aracı çalıştır.
 
 **GÖREV AKIŞI KURALLARI:**
1.  **ARAÇ KULLANIMI:** Kullanıcının isteğini anla ve en uygun aracı çalıştır.
2.  **SONUÇ ÖZETLEME (EN ÖNEMLİ KURAL):** Bir aracı çalıştırdıktan ve eline bir sonuç (tool_results) geçtikten sonra, 
görevin SADECE ve SADECE o aracın döndürdüğü sonucu kullanıcıya anlaşılır bir dilde sunmaktır. 
Sohbet geçmişindeki eski mesajları KESİNLİKLE tekrar etme. Sadece aracın sonucuna odaklan.
3.  **ARAÇ YARATMA:** `create_tool_from_swagger` aracını başarıyla çalıştırdıktan sonra, kullanıcıya yeni aracın 
hazır olduğunu bildirir ve bir sonraki komutunda onu kullanmasını beklersin.
"""


def get_all_tools_and_definitions():
    """
    Bu fonksiyon, her istekte çalışarak hem statik hem de dinamik araçları birleştirir.
    Hatalara karşı daha güvenli hale getirilmiştir.
    """
    print("get_all_tools... fonksiyonu başladı.")

    # Hafızayı yükleme adımını izole edelim
    print(" Hafıza yükleniyor...")
    _load_memory()

    print("başarılı: Hafıza yüklendi.")

    # Statik araçları tanımla
    available_tools = {
        "list_github_repos": list_github_repos,
        "get_github_user_info": get_github_user_info,
        "summarize_swagger_api": summarize_swagger_api,
        "create_tool_from_swagger": create_tool_from_swagger,
    }
    print("tool avail.")
    tools_definition = [
        {"name": "list_github_repos", "description": "Bir kullanıcının GitHub repolarını listeler.",
         "parameter_definitions": {
             "username": {"description": "GitHub kullanıcı adı.", "type": "string", "required": True}}},
        {"name": "get_github_user_info", "description": "Bir kullanıcının GitHub profil bilgilerini getirir.",
         "parameter_definitions": {
             "username": {"description": "GitHub kullanıcı adı.", "type": "string", "required": True}}},
        {"name": "summarize_swagger_api", "description": "Verilen URL'deki Swagger dokümanını analiz eder ve özetler.",
         "parameter_definitions": {
             "url": {"description": "Swagger dokümanının URL'si.", "type": "string", "required": True},
             "keyword": {"description": "Sonuçları filtrelemek için anahtar kelime.", "type": "string",
                         "required": False}}},
        {"name": "create_tool_from_swagger",
         "description": "Bir Swagger endpoint'inden çalıştırılabilir bir araç üretir.", "parameter_definitions": {
            "swagger_url": {"description": "Swagger dokümanının URL'si.", "type": "string", "required": True},
            "endpoint_path": {"description": "Araca dönüştürülecek endpoint yolu.", "type": "string", "required": True},
            "http_method": {"description": "Endpoint'in metodu (örn: get, post).", "type": "string", "required": True}}}
    ]

    # Dinamik araçları ekle
    importlib.reload(generated_tools)

    # DYNAMIC_TOOLS'un bir sözlük olduğundan emin ol, değilse logla.
    if not isinstance(DYNAMIC_TOOLS, dict):
        print(f"UYARI: DYNAMIC_TOOLS beklenen formatta değil! Tip: {type(DYNAMIC_TOOLS)}")
        return available_tools, tools_definition

    for tool_name, definition in DYNAMIC_TOOLS.items():
        # Tanımın kendisinin bir sözlük olduğundan emin ol
        if isinstance(definition, dict) and hasattr(generated_tools, tool_name):
            available_tools[tool_name] = getattr(generated_tools, tool_name)

            # GÜVENLİK KONTROLÜ: 'parameter_definitions' içindeki 'description' alanlarının
            # None veya başka bir tipte değil, her zaman string olduğundan emin ol.
            params = definition.get("parameter_definitions", {})
            if isinstance(params, dict):
                for param_name, param_details in params.items():
                    if "description" not in param_details or param_details["description"] is None:
                        param_details["description"] = ""  # None ise boş string yap.

            tools_definition.append(definition)

    return available_tools, tools_definition

available_tools = {
    "list_github_repos": list_github_repos,
    "get_github_user_info": get_github_user_info,
    "summarize_swagger_api": summarize_swagger_api,
    "create_tool_from_swagger": create_tool_from_swagger,
}
tools_definition = [
    # TOOL 1: GitHub Repolarını Listeleme
    {
        "name": "list_github_repos",
        "description": "Bir kullanıcının kullanıcı adına göre herkese açık GitHub repolarını ve ana profil URL'sini listeler. Bu araç bir URL almaz.",
        "parameter_definitions": {
            "username": {
                "description": "Bir GitHub kullanıcı adı, örneğin 'google' veya 'microsoft'.",
                "type": "string",
                "required": True
            }
        }
    },

    # TOOL 2: GitHub Profil Bilgilerini Getirme
    {
        "name": "get_github_user_info",
        "description": "Bir kullanıcının kullanıcı adına göre GitHub profil bilgilerini (bio, takipçi sayısı, en çok kullandığı diller vb.) getirir. Bu araç bir URL almaz.",
        "parameter_definitions": {
            "username": {
                "description": "Bir GitHub kullanıcı adı, örneğin 'google' veya 'microsoft'.",
                "type": "string",
                "required": True
            }
        }
    },

    {
        "name": "list_github_repos",
        "description": "Bir kullanıcının kullanıcı adına göre herkese açık GitHub repolarını ve ana profil URL'sini listeler. Bu araç bir URL almaz.",
        "parameter_definitions": {
            "username": {
                "description": "Bir GitHub kullanıcı adı, örneğin 'google' veya 'microsoft'.",
                "type": "string",
                "required": True
            }
        }
    },
    {
        "name": "get_github_user_info",
        "description": "Bir kullanıcının kullanıcı adına göre GitHub profil bilgilerini getirir. Bu araç bir URL almaz.",
        "parameter_definitions": {
            "username": {
                "description": "Bir GitHub kullanıcı adı, örneğin 'google' veya 'microsoft'.",
                "type": "string",
                "required": True
            }
        }
    },

    # TOOL 3: Swagger/OpenAPI Analizi ve Filtreleme
    {
        "name": "summarize_swagger_api",
        "description": (
            "Bir API'nin yeteneklerini anlamak için verilen bir URL'deki Swagger veya OpenAPI dokümanını analiz eder. "
            "Kullanıcının isteği bir URL içeriyorsa ve 'analiz et', 'özetle', 'ne yapar' gibi fiiller içeriyorsa bu araç kullanılmalıdır. "
            "Bu araç kullanıcı adı almaz. Analiz sonucunda, bulunan endpoint'ler hakkında yüksek seviyeli bir özet (toplam sayı, metot dağılımı, örnekler) döndürür."
        ),
        "parameter_definitions": {
            "url": {
                "description": "Analiz edilecek olan Swagger veya OpenAPI dokümanının tam URL'si.",
                "type": "string",
                "required": True
            },
            "keyword": {
                "description": (
                    "SONUÇLARI FİLTRELEMEK İÇİN KULLANILACAK ANAHTAR KELİME.\n"
                    "Bu parametre, API analizini belirli bir konuya odaklamak için kullanılır. "
                    "Örneğin, GitHub API'sinde sadece repolarla ilgili işlemleri görmek için 'repository' veya 'repos' kelimesini kullanabilirsiniz. "
                    "Bu parametre verilmezse, API'nin tamamı analiz edilir."
                ),
                "type": "string",
                "required": False
            }
        }
    },

    # TOOL 4: Yeni Yönetici Aracı - Tool Creator
    {
        "name": "create_tool_from_swagger",
        "description": "Bir Swagger dokümanında belirtilen spesifik bir endpoint'i kalıcı, çalıştırılabilir bir araca dönüştürür. Bu araç, swagger_url'yi doğrudan alabilir veya konuşma geçmişinden çıkarabilir.",
        "parameter_definitions": {
            "swagger_url": {
                "description": "Analiz edilecek Swagger/OpenAPI dokümanının tam URL'si. Eğer kullanıcı doğrudan vermezse, konuşma geçmişinden bulmaya çalış.",
                "type": "string", "required": True},
            "endpoint_path": {"description": "Araca dönüştürülecek olan endpoint'in yolu (örn: /emojis).",
                              "type": "string", "required": True},
            "http_method": {"description": "Endpoint'in metodu (örn: get, post).", "type": "string", "required": True}
        }
    }
]

def run_orchestration(user_message: str, chat_history: List[Dict[str, Any]] = []) -> str:
    try:
        print("\n--- İŞARET 1: Orkestrasyon başladı. ---")

        available_tools, tools_definition = get_all_tools_and_definitions()

        print("--- İŞARET 1.2: Tool toplandı ---")

        # Veriyi ekrana yazdırmayı ve olası hatayı yakalamayı deneyelim.
        try:
            print("Cohere'e gönderilecek araç tanımları:")


            print(json.dumps(tools_definition, indent=2, ensure_ascii=False))
        except Exception as e:

            print(f"\n!!!!!! HATA: 'tools_definition' listesi JSON'a çevrilirken çöktü! Hata: {e} !!!!!!")
            print("Listenin ham hali (çökmeden önceki hali):")
            print(f"tools_definition: tools_definition")  # JSON'a çevirmeden, ham halini yazdır.

        response = co.chat(

            message=user_message,
            tools=tools_definition,
            preamble=TURKISH_PREAMBLE,
            chat_history=chat_history
        )
        print(f"response.tool: {response.tool_calls}")
        if response and response.tool_calls:
            tool_results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call.name
                print(f"tool_name: {tool_name}")
                if tool_name in available_tools:
                    print(f"tool_call.parameters: {tool_call.parameters}")
                    try:
                        result = available_tools[tool_name](**tool_call.parameters)
                    except Exception as e:
                        print(f"e: {e}")
                    print(f"result: {result}")
                    tool_results.append({
                        "call": tool_call,
                        "outputs": [{"result": json.dumps(result)}]
                    })
            print(f"tool_result: {tool_results}")
            response = co.chat(
                message="",
                tool_results=tool_results,
                preamble=TURKISH_PREAMBLE,
                chat_history=chat_history
            )
            print(f"response_satır121: {response}")

        if response and response.text:
            return response.text
        else:
            return "İsteğinizi tam olarak anlayamadım. Lütfen daha spesifik bir soru sorun."

    # --- HATA YAKALAMA (VERSİYON BAĞIMSIZ, EN GÜVENLİ YÖNTEM) ---
    except Exception as e:
        # Yakalanan herhangi bir hatanın tipini kontrol ediyoruz.
        # Eğer hatanın sınıf adında 'cohere' kelimesi geçiyorsa, bunun bir
        # Cohere API hatası (örn: geçersiz anahtar, ağ sorunu) olduğunu varsayıyoruz.
        if 'cohere' in str(type(e)).lower():
            raise ServiceConnectionError(service_name="Cohere AI", original_error=str(e))
        else:
            # Eğer hata Cohere ile ilgili değilse, bu bizim kodumuzdaki
            # başka bir beklenmedik sorundur.
            raise CustomAPIException(
                detail=f"Orkestrasyon sırasında beklenmedik bir hata oluştu: {type(e).__name__} - {e}")
# creator/selector_tools.py

from .engine import ToolCreatorEngine
import json
from pathlib import Path

# GEÇİCİ HAFIZA: Bu hala orkestratörün anlık olarak erişmesi için gerekli.
DYNAMIC_TOOLS = {}
# KALICI HAFIZA: Dosyamızın yolu.
MEMORY_FILE = Path("dynamic_tools_memory.json")


def _load_memory():
    """Hafıza dosyasını okur. Dosya boşsa veya yoksa çökmeyecek şekilde tasarlanmıştır."""
    DYNAMIC_TOOLS.clear()
    try:
        if MEMORY_FILE.exists() and MEMORY_FILE.stat().st_size > 0:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                tools_from_memory = json.load(f)
                if isinstance(tools_from_memory, list):
                    for tool in tools_from_memory:
                        DYNAMIC_TOOLS[tool['name']] = tool
    except (json.JSONDecodeError, Exception) as e:
        print(
            f"UYARI: Hafıza dosyası ('{MEMORY_FILE}') okunurken bir sorun oluştu: {e}. Temiz bir hafıza ile devam ediliyor.")

    print(f"[MEMORY]: Hafızadan {len(DYNAMIC_TOOLS)} araç yüklendi.")
def _save_memory():
    """DYNAMIC_TOOLS'un güncel halini dosyaya yazar."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        # Sözlüğün sadece değerlerini (tanımları) listeye çevirip kaydet
        json.dump(list(DYNAMIC_TOOLS.values()), f, indent=2, ensure_ascii=False)
    print(f"[MEMORY]: Hafızaya {len(DYNAMIC_TOOLS)} araç kaydedildi.")


def create_tool_from_swagger(swagger_url: str, endpoint_path: str, http_method: str) -> dict:
    engine = ToolCreatorEngine(swagger_url=swagger_url)
    result = engine.generate_tool_code(endpoint_path=endpoint_path, http_method=http_method)

    if result.get("status") == "Başarılı":
        tool_name = result["generated_tool_name"]

        new_tool_definition = {
            "name": tool_name,
            "description": f"Otomatik üretilen araç: {http_method.upper()} {endpoint_path} endpoint'ini çağırır.",
            "parameter_definitions": result["parameter_definitions"]
        }

        # YENİ ADIMLAR:
        _load_memory()  # Önce mevcut hafızayı yükle
        DYNAMIC_TOOLS[tool_name] = new_tool_definition  # Yeni aracı ekle
        _save_memory()  # Hafızanın son halini dosyaya kaydet

        return {
            "status": "Başarılı",
            "message": f"'{tool_name}' adında yeni bir araç kalıcı olarak oluşturuldu ve artık kullanıma hazır."
        }

    return result


# Uygulama ilk import edildiğinde hafızayı bir kere yükleyelim.
_load_memory()
import json
import requests
import yaml
from pathlib import Path

# Kod şablonları
SERVICE_TEMPLATE = """
# Bu kod ToolCreatorEngine tarafından otomatik olarak üretilmiştir.
import requests
from exceptions.custom_exceptions import ServiceConnectionError

def {function_name}({parameters_str}):
    \"\"\"
    {description}
    \"\"\"
    endpoint_url = f"{base_url}{endpoint_path_fstring}"
    headers = {{"Accept": "application/vnd.github.v3+json"}}

    print(f"--- YENİ SERVİS ÇALIŞTIRILDI: {function_name} ---")
    print(f"İstek gönderilen URL: {{endpoint_url}}")

    try:
        response = requests.get(endpoint_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise ServiceConnectionError(service_name="{service_name}", original_error=str(e))
"""

# creator/engine.py içindeki YENİ ve DOĞRU TOOL_TEMPLATE

TOOL_TEMPLATE = """
# Bu kod ToolCreatorEngine tarafından otomatik olarak üretilmiştir.
# DİKKAT: Bu dosya 'tools' klasöründedir.

# Doğru yerden, yani 'services' klasöründen import yapılıyor
# ve fonksiyona 'service_function' diye bir TAKMA AD veriliyor.
from services.generated_services import {function_name} as service_function

def {tool_name}({parameters_str}) -> dict:
    \"\"\"
    {description}
    \"\"\"
    # 'service_function' takma adını kullanarak doğru fonksiyonu çağırıyoruz
    # ve kendi kendini çağırma hatasını (sonsuz döngüyü) engelliyoruz.
    return service_function({call_parameters_str})
"""


class ToolCreatorEngine:
    def __init__(self, swagger_url: str):
        self.swagger_url = swagger_url
        self.swagger_data = self._load_swagger_data()
        self.base_url = f"{self.swagger_data.get('schemes', ['https'])[0]}://{self.swagger_data.get('host', '')}{self.swagger_data.get('basePath', '')}"

    def _load_swagger_data(self):
        response = requests.get(self.swagger_url, timeout=30)
        response.raise_for_status()
        content = response.text
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return yaml.safe_load(content)

    def generate_tool_code(self, endpoint_path: str, http_method: str) -> dict:
        paths = self.swagger_data.get("paths", {})
        endpoint_details = paths.get(endpoint_path, {}).get(http_method.lower())

        if not endpoint_details:
            return {"status": "Hata",
                    "message": f"Swagger içinde endpoint bulunamadı: {http_method.upper()} {endpoint_path}"}

        description = endpoint_details.get("summary", "Açıklama bulunamadı.")
        path_params = [p for p in endpoint_details.get("parameters", []) if p.get("in") == "path"]

        function_name = f"{http_method.lower()}{endpoint_path.replace('/', '_').replace('{', '').replace('}', '')}"
        parameters_str = ", ".join([f"{p['name']}: str" for p in path_params])
        call_parameters_str = ", ".join([f"{name['name']}={name['name']}" for name in path_params])

        service_code = SERVICE_TEMPLATE.format(
            function_name=function_name,
            parameters_str=parameters_str,
            description=description,
            base_url=self.base_url,
            endpoint_path_fstring=endpoint_path,
            service_name=f"GitHub API - {endpoint_path}"
        )
        tool_code = TOOL_TEMPLATE.format(
            function_name=function_name,
            tool_name=function_name,
            parameters_str=parameters_str,
            description=description,
            call_parameters_str=call_parameters_str
        )

        with open(Path("services/generated_services.py"), "a", encoding="utf-8") as f:
            f.write("\n" + service_code)
        with open(Path("tools/generated_tools.py"), "a", encoding="utf-8") as f:
            f.write("\n" + tool_code)

        return {
            "status": "Başarılı",
            "message": f"'{function_name}' aracı başarıyla oluşturuldu.",
            "generated_tool_name": function_name,
            "parameter_definitions": {
                p['name']: {"description": str(p.get('description', '')), "type": "string", "required": True} for p in
                path_params}
        }
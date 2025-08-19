import requests
import json
import yaml
from exceptions.custom_exceptions import ServiceConnectionError


def analyze_swagger_url(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        content = response.text
        spec_data = {}

        try:
            spec_data = json.loads(content)
        except json.JSONDecodeError:
            spec_data = yaml.safe_load(content)

        info = spec_data.get("info", {})
        title = info.get("title", "Başlık Bulunamadı")
        version = info.get("version", "Versiyon Bulunamadı")

        output_lines = [f"API Analiz Sonucu: {title} (Sürüm: {version})", "---"]

        paths = spec_data.get("paths", {})
        for path, methods in paths.items():
            for method, details in methods.items():
                method_str = method.upper().ljust(7)
                summary = details.get("summary", "Açıklama yok.")
                output_lines.append(f"-> {method_str} {path}")
                output_lines.append(f"   Açıklama: {summary}\n")

        return "\n".join(output_lines)

    except (requests.exceptions.RequestException, yaml.YAMLError, TypeError) as e:
        # Tüm olası hataları yakalayıp tek bir standart hata fırlatıyoruz.
        raise ServiceConnectionError(service_name=f"Swagger URL ({url})", original_error=str(e))
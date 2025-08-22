import requests
import yaml
import json
from collections import defaultdict
from exceptions.custom_exceptions import ServiceConnectionError


# Fonksiyon tanımına 'keyword: str = None' parametresini ekliyoruz.
def analyze_swagger_url(url: str, keyword: str = None) -> dict:
    try:
        spec_data = {}
        is_json = url.lower().endswith('.json')
        is_yaml = url.lower().endswith('.yaml') or url.lower().endswith('.yml')

        with requests.get(url, timeout=30, stream=True) as response:
            response.raise_for_status()

            if is_json:
                spec_data = response.json()
            elif is_yaml:
                spec_data = yaml.safe_load(response.iter_content(chunk_size=8192))
            else:
                content = response.text
                try:
                    spec_data = json.loads(content)
                except json.JSONDecodeError:
                    spec_data = yaml.safe_load(content)

        info = spec_data.get("info", {})
        title = info.get("title", "Başlık Bulunamadı")

        summary_data = {
            "api_title": title,
            "total_endpoints_found": 0,
            "method_counts": defaultdict(int),
            "endpoint_examples": []
        }

        paths = spec_data.get("paths", {})
        for path, methods in paths.items():

            # --- FİLTRELEME MANTIĞI BURADA ---
            if keyword and keyword.lower() not in path.lower():
                continue

            for method, details in methods.items():
                summary_data["total_endpoints_found"] += 1
                summary_data["method_counts"][method.upper()] += 1

                if len(summary_data["endpoint_examples"]) < 4:
                    summary = details.get("summary", "Açıklama yok.")
                    summary_data["endpoint_examples"].append(f"Örn: {method.upper()} {path} ({summary})")

        return summary_data

    except Exception as e:
        raise ServiceConnectionError(service_name=f"Swagger URL ({url})", original_error=str(e))
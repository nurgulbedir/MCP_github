

# Bu kod ToolCreatorEngine tarafından otomatik olarak üretilmiştir.
import requests
from exceptions.custom_exceptions import ServiceConnectionError

def get_zen():
    """
    Get the Zen of GitHub
    """
    endpoint_url = f"https:///zen"
    headers = {"Accept": "application/vnd.github.v3+json"}

    print(f"--- YENİ SERVİS ÇALIŞTIRILDI: get_zen ---")
    print(f"İstek gönderilen URL: {endpoint_url}")

    try:
        response = requests.get(endpoint_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise ServiceConnectionError(service_name="GitHub API - /zen", original_error=str(e))


# Bu kod ToolCreatorEngine tarafından otomatik olarak üretilmiştir.
import requests
from exceptions.custom_exceptions import ServiceConnectionError

def get_users_username_following_target_user(target_user: str):
    """
    Check if a user follows another user
    """
    endpoint_url = f"https:///users/{username}/following/{target_user}"
    headers = {"Accept": "application/vnd.github.v3+json"}

    print(f"--- YENİ SERVİS ÇALIŞTIRILDI: get_users_username_following_target_user ---")
    print(f"İstek gönderilen URL: {endpoint_url}")

    try:
        response = requests.get(endpoint_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise ServiceConnectionError(service_name="GitHub API - /users/{username}/following/{target_user}", original_error=str(e))

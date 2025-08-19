import requests
from core.config import settings
from exceptions.custom_exceptions import ServiceConnectionError


def get_user_profile(username: str) -> dict:
    api_url = f"https://api.github.com/users/{username}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if settings.GITHUB_API_KEY:
        headers["Authorization"] = f"token {settings.GITHUB_API_KEY}"

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Hata varsa (404, 500 vb.), exception fırlatır

        profile_data = response.json()
        return {
            "name": profile_data.get("name"),
            "bio": profile_data.get("bio"),
            "public_repos": profile_data.get("public_repos"),
            "followers": profile_data.get("followers"),
            "following": profile_data.get("following"),
            "url": profile_data.get("html_url")
        }
    except requests.exceptions.RequestException as e:
        # Hata durumunda artık bir sözlük döndürmek yerine, özel hatamızı fırlatıyoruz.
        raise ServiceConnectionError(service_name="GitHub API", original_error=str(e))


def get_user_public_repos(username: str) -> dict:
    api_url = f"https://api.github.com/users/{username}/repos"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if settings.GITHUB_API_KEY:
        headers["Authorization"] = f"token {settings.GITHUB_API_KEY}"

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        repos_data = response.json()

        profile_url = f"https://github.com/{username}"
        if repos_data:
            profile_url = repos_data[0].get("owner", {}).get("html_url", profile_url)

        return {
            "profile_url": profile_url,
            "repositories": [{"name": repo.get("name"), "url": repo.get("html_url")} for repo in repos_data]
        }
    except requests.exceptions.RequestException as e:
        raise ServiceConnectionError(service_name="GitHub API", original_error=str(e))
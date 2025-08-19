from pydantic import Field  # Field'ı pydantic'ten import ediyoruz
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True  # Eşleşmenin birebir (büyük/küçük harf duyarlı) olmasını sağlıyoruz
    )

    # .env'deki COHERE_API_KEY'i bu alana ata
    COHERE_API_KEY: str = Field(alias='COHERE_API_KEY')

    # .env'deki GITHUB_API_KEY'i bu alana ata
    # Bu, Pydantic'e tam olarak hangi ortam değişkenini arayacağını söyler.
    GITHUB_API_KEY: Optional[str] = Field(alias='GITHUB_API_KEY', default=None)


# Projenin her yerinden çağırabileceğimiz tek bir ayar nesnesi
settings = Settings()
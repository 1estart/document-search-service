from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Elasticsearch
    elasticsearch_url: str = "http://localhost:9200"
    es_index: str = "documents"

    # PostgreSQL
    database_url: str = "postgresql://postgres:postgres@localhost:5432/documents"

    # Uvicorn
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1


settings = Settings()
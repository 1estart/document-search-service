from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    elasticsearch_url: str = "http://localhost:9200"
    es_index: str = "documents"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/documents"


settings = Settings()
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	"""Application settings loaded from environment variables."""

	app_name: str = "DocuChat API"
	app_version: str = "0.1.0"
	frontend_url: str = "http://localhost:5173"
	cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
	google_api_key: str | None = None

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		case_sensitive=False,
		extra="ignore",
	)


@lru_cache
def get_settings() -> Settings:
	"""Return the cached application settings instance."""

	return Settings()

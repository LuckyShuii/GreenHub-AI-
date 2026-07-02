"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings sourced from the environment.

    Attributes:
        pipeline_model_name: Hugging Face model identifier used by the
            image-classification pipeline.
        host: Network interface the server binds to.
        port: TCP port the server listens on.

    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    ai_pipeline_model_name: str = Field(
        ...,
        alias="AI_PIPELINE_MODEL_NAME",
        description="Hugging Face image-classification model name.",
    )
    ai_host: str = Field(
        default="0.0.0.0",
        alias="AI_HOST",
        description="Server bind address.",
    )
    ai_port: int = Field(
        default=8000,
        alias="AI_PORT",
        ge=1,
        le=65535,
        description="Server listening port.",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton instance of the settings.

    Using an LRU cache guarantees the environment is parsed once and the
    same immutable Settings object is reused across the application.

    Returns:
        The validated Settings instance.

    """
    return Settings()  # type: ignore

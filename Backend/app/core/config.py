"""
Configuration Module for CLEARLY Backend Core
Loads settings from environment variables or .env file with Pydantic v2 validation.
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


def load_dotenv_file(dotenv_path: Optional[Path] = None) -> None:
    """Simple, pure-python .env loader without external dependencies."""
    if dotenv_path is None:
        # Search in current directory, parent, or project root
        candidates = [
            Path.cwd() / ".env",
            Path.cwd().parent / ".env",
            Path(__file__).resolve().parent.parent.parent.parent / ".env",
            Path(__file__).resolve().parent.parent.parent.parent / ".env.example",
        ]
        for candidate in candidates:
            if candidate.is_file():
                dotenv_path = candidate
                break

    if dotenv_path and dotenv_path.is_file():
        try:
            with open(dotenv_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key not in os.environ:
                        os.environ[key] = val
        except Exception:
            pass


# Preload environment variables from .env if available
load_dotenv_file()


class Settings(BaseModel):
    # Application Info
    APP_NAME: str = Field(default_factory=lambda: os.getenv("APP_NAME", "CLEARLY"))
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    DEBUG: bool = Field(default_factory=lambda: os.getenv("DEBUG", "True").lower() in ("true", "1", "yes"))
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("SECRET_KEY", "clearly_dev_super_secret_key_change_in_production_2026")
    )
    ALGORITHM: str = Field(default_factory=lambda: os.getenv("ALGORITHM", "HS256"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default_factory=lambda: int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    )

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://app.clearly.local",
    ]

    # Database (PostgreSQL 16 + pgvector)
    POSTGRES_DB: str = Field(default_factory=lambda: os.getenv("POSTGRES_DB", "clearly_db"))
    POSTGRES_USER: str = Field(default_factory=lambda: os.getenv("POSTGRES_USER", "clearly_admin"))
    POSTGRES_PASSWORD: str = Field(default_factory=lambda: os.getenv("POSTGRES_PASSWORD", "clearly_secure_pass_2026!"))
    POSTGRES_HOST: str = Field(default_factory=lambda: os.getenv("POSTGRES_HOST", "localhost"))
    POSTGRES_PORT: int = Field(default_factory=lambda: int(os.getenv("POSTGRES_PORT", "5432")))
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            f"postgresql+asyncpg://{os.getenv('POSTGRES_USER', 'clearly_admin')}:{os.getenv('POSTGRES_PASSWORD', 'clearly_secure_pass_2026!')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'clearly_db')}"
        )
    )

    # Redis Broker & Cache
    REDIS_HOST: str = Field(default_factory=lambda: os.getenv("REDIS_HOST", "localhost"))
    REDIS_PORT: int = Field(default_factory=lambda: int(os.getenv("REDIS_PORT", "6379")))
    REDIS_DB: int = Field(default_factory=lambda: int(os.getenv("REDIS_DB", "0")))
    REDIS_URL: str = Field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0"))

    # MinIO S3 Object Storage
    MINIO_ROOT_USER: str = Field(default_factory=lambda: os.getenv("MINIO_ROOT_USER", "clearly_minio_admin"))
    MINIO_ROOT_PASSWORD: str = Field(default_factory=lambda: os.getenv("MINIO_ROOT_PASSWORD", "clearly_minio_secret_key_2026!"))
    MINIO_ENDPOINT: str = Field(default_factory=lambda: os.getenv("MINIO_ENDPOINT", "localhost:9000"))
    MINIO_USE_SSL: bool = Field(default_factory=lambda: os.getenv("MINIO_USE_SSL", "False").lower() in ("true", "1"))
    MINIO_DOCUMENTS_BUCKET: str = Field(default_factory=lambda: os.getenv("MINIO_DOCUMENTS_BUCKET", "clearly-documents"))
    MINIO_AUDIO_BUCKET: str = Field(default_factory=lambda: os.getenv("MINIO_AUDIO_BUCKET", "clearly-audio"))

    # Local Storage Fallback Directory
    LOCAL_STORAGE_DIR: Path = Path(__file__).resolve().parent.parent.parent / "storage"

    # AI & Plain Language Engine
    FERNANDEZ_HUERTA_THRESHOLD: float = 80.0
    LLM_PROVIDER: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "vllm"))
    LLM_BASE_URL: str = Field(default_factory=lambda: os.getenv("LLM_BASE_URL", "http://localhost:8000/v1"))
    LLM_MODEL: str = Field(default_factory=lambda: os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct"))

    # Tutor Alert Threshold (days)
    TUTOR_ALERT_THRESHOLD_DAYS: int = 15


settings = Settings()


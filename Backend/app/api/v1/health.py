"""
CLEARLY — Health & Diagnostics Endpoints
"""

from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.storage import storage_service

router = APIRouter()


class HealthResponse(BaseModel):
    status: str = "ok"
    app_name: str
    version: str
    environment: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    storage_backend: str
    minio_connected: bool


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """Liveness and readiness health probe."""
    is_minio = storage_service.minio_client is not None
    storage_type = "minio" if is_minio else "local_disk_fallback"

    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        storage_backend=storage_type,
        minio_connected=is_minio,
    )

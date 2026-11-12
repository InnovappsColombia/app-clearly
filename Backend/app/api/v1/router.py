"""
CLEARLY — API v1 Router Aggregator
"""

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.documents import router as documents_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health & Diagnostics"])
api_router.include_router(documents_router, prefix="/documents", tags=["Traducción Documental & Accesibilidad"])


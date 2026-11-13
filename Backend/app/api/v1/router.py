"""
CLEARLY — API v1 Router Aggregator
"""

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.documents import router as documents_router
from app.api.v1.webhooks import router as webhooks_router
from app.api.v1.tutors import router as tutors_router
from app.api.v1.websocket import router as websocket_router
from app.api.v1.premium import router as premium_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health & Diagnostics"])
api_router.include_router(documents_router, prefix="/documents", tags=["Traducción Documental & Accesibilidad"])
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["WhatsApp & Evolution API Gateway"])
api_router.include_router(tutors_router, prefix="/tutors", tags=["Tutor Hub & Handshake"])
api_router.include_router(websocket_router, tags=["WebSocket Real-Time Sync"])
api_router.include_router(premium_router, prefix="/premium", tags=["CLEARLY Premium & Escrow Bookings"])


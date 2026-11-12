"""
CLEARLY — Webhook API Endpoints
Receives and processes incoming messaging events from Evolution API v2 (WhatsApp).
"""

from fastapi import APIRouter, Header, HTTPException, Request, status
from loguru import logger

from app.schemas.whatsapp import EvolutionWebhookPayload, WhatsAppProcessResult
from app.services.whatsapp_service import whatsapp_service

router = APIRouter()


@router.post(
    "/whatsapp",
    response_model=WhatsAppProcessResult,
    status_code=status.HTTP_200_OK,
    summary="Webhook receptor de Evolution API v2 para WhatsApp",
    description=(
        "Recibe eventos 'messages.upsert' de Evolution API (notas de voz, cartas fotografiadas y consultas).\n"
        "Ejecuta STT con faster-whisper, Plain Language (FH >= 80) y alerta proactiva a tutores si hay plazos críticos."
    ),
)
async def handle_whatsapp_webhook(payload: EvolutionWebhookPayload):
    try:
        result = await whatsapp_service.process_incoming_webhook(payload)
        return result
    except Exception as e:
        logger.error(f"Error handling Evolution API webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el procesamiento del webhook de WhatsApp: {str(e)}",
        )


@router.post(
    "/evolution",
    response_model=WhatsAppProcessResult,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def handle_evolution_alias(payload: EvolutionWebhookPayload):
    """Alias for /whatsapp endpoint."""
    return await handle_whatsapp_webhook(payload)


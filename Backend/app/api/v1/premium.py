"""
CLEARLY — API Endpoints for CLEARLY Premium & Escrow Bookings
Handles automatic professional matching, Stripe Connect escrow holds,
and LiveKit WebRTC video consultation signaling.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, status
from loguru import logger

from app.db.repository import repository
from app.schemas.premium import (
    BookingResponse,
    CreateBookingRequest,
    ExpertMatchRequest,
    ExpertMatchResponse,
    ExpertProfileResponse,
    LiveKitRoomDetails,
    ReleaseEscrowRequest,
    ReleaseEscrowResponse,
)
from app.services.livekit_service import livekit_service
from app.services.premium_matching import premium_matching_engine
from app.services.premium_service import premium_service

router = APIRouter()


@router.post(
    "/match",
    response_model=ExpertMatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Matching automático de profesional verificado",
    description=(
        "Analiza el documento o consulta legal/administrativa y selecciona al profesional regulado "
        "óptimo (RCIC, trabajador social) evaluando especialidad, idioma y reputación."
    ),
)
async def match_expert(req: ExpertMatchRequest):
    try:
        return await premium_matching_engine.match_expert(
            document_id=req.document_id,
            query_text=req.query_text,
            senior_id=req.senior_id,
        )
    except Exception as e:
        logger.error(f"Error in automatic expert matching: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/experts",
    response_model=List[ExpertProfileResponse],
    summary="Directorio de profesionales verificados",
)
async def list_verified_experts():
    experts = await repository.list_expert_profiles()
    dtos = []
    for exp in experts:
        user = await repository.get_user(exp.user_id)
        name = user.full_name if user else "Profesional Verificado"
        dtos.append(premium_matching_engine._build_expert_dto(exp, name))
    return dtos


@router.post(
    "/bookings",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crea una reserva con retención de fondos en Escrow (Stripe Connect)",
    description=(
        "Reserva una sesión virtual o presencial. Los fondos se mantienen retenidos en custodia "
        "y NO se transfieren al profesional hasta que el usuario titular o su tutor confirmen la sesión."
    ),
)
async def create_booking(req: CreateBookingRequest):
    try:
        return await premium_service.create_booking(req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating premium booking: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/bookings/{booking_id}",
    response_model=BookingResponse,
    summary="Detalle de una reserva y estado de custodia en Escrow",
)
async def get_booking_details(booking_id: UUID):
    booking = await premium_service.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada.")
    return booking


@router.post(
    "/bookings/{booking_id}/release-escrow",
    response_model=ReleaseEscrowResponse,
    summary="Libera los fondos en Escrow al profesional tras la consulta",
    description="Confirma la realización de la sesión, califica el servicio y transfiere el 85% de honorarios al experto.",
)
async def release_escrow(booking_id: UUID, req: ReleaseEscrowRequest):
    try:
        return await premium_service.release_escrow(booking_id, req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/bookings/{booking_id}/livekit-token",
    response_model=LiveKitRoomDetails,
    summary="Emite token de acceso WebRTC para la sala de videoconsulta LiveKit",
)
async def get_livekit_token(
    booking_id: UUID,
    participant_identity: str = Query(..., description="ID del participante"),
    participant_name: str = Query(..., description="Nombre del participante"),
    is_senior: bool = Query(True, description="True si es el adulto mayor para activar subtítulos grandes"),
):
    booking = await repository.get_premium_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada.")

    return livekit_service.create_room_token(
        booking_id=booking_id,
        participant_identity=participant_identity,
        participant_name=participant_name,
        is_senior=is_senior,
    )

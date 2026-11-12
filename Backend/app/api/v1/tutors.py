"""
CLEARLY — Tutor Hub & Handshake API Endpoints
Manages Titular-Tutor relationships, ephemeral pairing codes, collaborative checklists,
and silent Duress PIN protection (FMEA FM-04).
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, status
from loguru import logger

from app.db.repository import repository
from app.schemas.document import ActionItemResponse
from app.schemas.tutor import (
    ChecklistToggleRequest,
    ChecklistToggleResponse,
    DuressTriggerRequest,
    DuressTriggerResponse,
    PairingCodeRequest,
    PairingCodeResponse,
    PairTutorRequest,
    PairTutorResponse,
    TutorDashboardResponse,
    TutorSeniorSummaryResponse,
)
from app.services.tutor_engine import tutor_engine

router = APIRouter()

# Default Canonical UUIDs from seeds
DEFAULT_SENIOR_ID = UUID("11111111-1111-1111-1111-111111111111")  # Elena
DEFAULT_TUTOR_ID = UUID("22222222-2222-2222-2222-222222222222")   # Carlos


@router.post(
    "/pairing-code",
    response_model=PairingCodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Genera código efímero de vinculación para el Adulto Mayor",
    description="Crea un código de 6 dígitos con validez de 15 minutos y payload QR compatible con Curve25519.",
)
async def create_pairing_code(req: PairingCodeRequest):
    senior_id = req.senior_id or DEFAULT_SENIOR_ID
    return await tutor_engine.generate_pairing_code(senior_id)


@router.post(
    "/pair",
    response_model=PairTutorResponse,
    status_code=status.HTTP_200_OK,
    summary="Vincula al Tutor mediante código efímero",
    description="Canjea el código de 6 dígitos y emite un token de capacidad atenuado (PASETO v4 / Macaroon).",
)
async def pair_tutor(req: PairTutorRequest):
    tutor_id = req.tutor_id or DEFAULT_TUTOR_ID
    result = await tutor_engine.pair_tutor(tutor_id=tutor_id, code=req.pairing_code)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de vinculación es inválido, ha expirado o ya fue utilizado.",
        )
    return result


@router.get(
    "/seniors",
    response_model=List[TutorSeniorSummaryResponse],
    summary="Lista familiares adultos mayores supervisados por el Tutor",
)
async def list_supervised_seniors(
    tutor_id: Optional[UUID] = Query(default=DEFAULT_TUTOR_ID, description="ID del Tutor")
):
    return await tutor_engine.get_tutor_seniors(tutor_id)


@router.get(
    "/seniors/{senior_id}/dashboard",
    response_model=TutorDashboardResponse,
    summary="Obtiene el panel de control Tutor Hub en tiempo real para un Adulto Mayor",
    description="Agrupa fechas límite críticas (< 15 días), documentos recientes, checklist colaborativo y alertas.",
)
async def get_tutor_dashboard(
    senior_id: UUID,
    tutor_id: Optional[UUID] = Query(default=DEFAULT_TUTOR_ID, description="ID del Tutor"),
):
    dashboard = await tutor_engine.build_dashboard(tutor_id=tutor_id, senior_id=senior_id)
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vínculo de tutoría no encontrado o inactivo.",
        )
    return dashboard


@router.get(
    "/checklists/{document_id}",
    response_model=List[ActionItemResponse],
    summary="Obtiene las tareas y checklist de un documento específico",
)
async def get_document_actions(document_id: UUID):
    actions = await repository.get_document_actions(document_id)
    return [
        ActionItemResponse(
            id=a.id,
            document_id=a.document_id,
            task_description=a.task_description,
            required_document=a.required_document,
            deadline=a.deadline,
            is_completed=a.is_completed,
            completed_at=a.completed_at,
            created_at=a.created_at,
        )
        for a in actions
    ]


@router.patch(
    "/checklists/{action_id}",
    response_model=ChecklistToggleResponse,
    summary="Marca o desmarca una tarea en el checklist colaborativo",
    description="Sincroniza el cambio en tiempo real vía WebSocket a todos los usuarios vinculados.",
)
async def toggle_checklist_action(action_id: UUID, req: ChecklistToggleRequest):
    updated = await tutor_engine.toggle_checklist_item(
        action_id=action_id,
        completed_by_user_id=req.completed_by_user_id or DEFAULT_TUTOR_ID,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La tarea solicitada no existe.",
        )
    return ChecklistToggleResponse(**updated)


@router.post(
    "/duress",
    response_model=DuressTriggerResponse,
    status_code=status.HTTP_200_OK,
    summary="Protocolo de Coacción Silenciosa (Duress PIN - FMEA FM-04)",
    description=(
        "Si el adulto mayor ingresa su PIN de Coacción, el sistema desvincula de forma silenciosa e instantánea "
        "las alertas al tutor, congela la vista de documentos y genera un ticket de bienestar para trabajadores sociales."
    ),
)
async def trigger_duress_pin(req: DuressTriggerRequest):
    success = await tutor_engine.activate_duress_pin(req.senior_id, req.entered_pin)
    if not success:
        # Devuelve respuesta inocente estándar para nunca delatar si el PIN fue incorrecto
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código de seguridad no reconocido.",
        )
    return DuressTriggerResponse(status="success", quarantine_mode=True)


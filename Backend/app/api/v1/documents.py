"""
CLEARLY — Documents Processing & Analysis Endpoints
Hero Feature of Sprint 1: OCR, Deterministic Date Extraction, Plain Language & A11y.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from app.api.deps import get_current_user_id, get_repository
from app.db.repository import InMemoryRepository
from app.schemas.document import (
    ActionItemResponse,
    DateExtractionRequest,
    DateExtractionResponse,
    DocumentDetailResponse,
    DocumentProcessResponse,
    ReadabilityAuditRequest,
    ReadabilityAuditResponse,
)
from app.services.date_extractor import extract_deterministic_deadline
from app.services.document_pipeline import document_pipeline
from app.services.readability import audit_readability

router = APIRouter()

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB


@router.post(
    "/process",
    response_model=DocumentProcessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Procesar documento (Carta gubernamental, médica o contrato)",
)
async def process_document(
    file: UploadFile = File(..., description="Archivo PDF, PNG, JPG o TXT (máx 25MB)"),
    user_id: Optional[str] = Form(None, description="UUID del usuario titular"),
    target_language: str = Form("es", description="Idioma de simplificación (es, en, pa)"),
    default_user_id: UUID = Depends(get_current_user_id),
):
    """
    Hero Feature de CLEARLY:
    1. Almacena el archivo en MinIO de forma soberana con hash SHA-256.
    2. Extrae el texto mediante OCR.
    3. Simplifica a Lenguaje Claro en 3 capas garantizando Fernández-Huerta FH >= 80.
    4. Ejecuta extracción temporal determinista previniendo alucinación de plazos (FM-02).
    5. Aplica guardrails legales estrictos contra el ejercicio no autorizado de la abogacía.
    6. Persiste en PostgreSQL y despacha alertas automáticas al Tutor familiar si el plazo < 15 días.
    """
    # Determine user id
    target_uid = default_user_id
    if user_id:
        try:
            target_uid = UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato de UUID inválido: {user_id}",
            )

    # Read file content and validate size
    if hasattr(file, "file") and hasattr(file.file, "read"):
        file_bytes = file.file.read()
    else:
        file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo subido está vacío.",
        )
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El tamaño del archivo excede el límite máximo de 25MB.",
        )

    response = await document_pipeline.process_document(
        file_bytes=file_bytes,
        filename=file.filename or "uploaded_document",
        user_id=target_uid,
        content_type=file.content_type,
        target_language=target_language,
    )
    return response


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    summary="Obtener detalle y acciones de un documento procesado",
)
async def get_document_by_id(
    document_id: UUID, repo: InMemoryRepository = Depends(get_repository)
):
    """Obtiene el resumen, checklist y metadatos de un documento por su ID."""
    doc = await repo.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento con ID {document_id} no encontrado.",
        )

    # Fetch actions
    actions_entities = await repo.get_document_actions(document_id)
    actions_resp = [
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
        for a in actions_entities
    ]

    days_rem = None
    if doc.critical_deadline:
        from datetime import date
        delta = (doc.critical_deadline - date.today()).days
        days_rem = max(0, delta)

    cat = "Muy fácil" if (doc.fernandez_huerta_score or 0) >= 90 else "Fácil"

    return DocumentDetailResponse(
        id=doc.id,
        user_id=doc.user_id,
        document_type=doc.issuing_entity or "Documento Administrativo",
        issuing_entity=doc.issuing_entity or "Entidad Oficial",
        plain_summary=doc.plain_summary,
        detected_language="es",
        fernandez_huerta_score=doc.fernandez_huerta_score or 85.0,
        readability_category=cat,
        urgency=doc.urgency,
        critical_deadline=doc.critical_deadline,
        days_remaining=days_rem,
        tutor_alert_triggered=(doc.urgency in ("critical", "high")),
        requires_human_expert=doc.requires_human_expert,
        actions_required=actions_resp,
        ambiguities_flagged=doc.ambiguities,
        recommended_questions=doc.recommended_questions,
        storage_path=doc.storage_path,
        file_sha256=doc.file_sha256,
        created_at=doc.created_at,
        original_extracted_text=doc.original_extracted_text,
    )


@router.get(
    "/user/{user_id}",
    response_model=List[DocumentProcessResponse],
    summary="Listar documentos procesados de un usuario titular",
)
async def list_user_documents(
    user_id: UUID, repo: InMemoryRepository = Depends(get_repository)
):
    """Lista todos los expedientes procesados pertenecientes a un usuario titular o familiar."""
    docs = await repo.list_documents_by_user(user_id)
    result = []
    for doc in docs:
        actions_entities = await repo.get_document_actions(doc.id)
        actions_resp = [
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
            for a in actions_entities
        ]
        days_rem = None
        if doc.critical_deadline:
            from datetime import date
            delta = (doc.critical_deadline - date.today()).days
            days_rem = max(0, delta)

        cat = "Muy fácil" if (doc.fernandez_huerta_score or 0) >= 90 else "Fácil"
        result.append(
            DocumentProcessResponse(
                id=doc.id,
                user_id=doc.user_id,
                document_type=doc.issuing_entity or "Documento Administrativo",
                issuing_entity=doc.issuing_entity or "Entidad Oficial",
                plain_summary=doc.plain_summary,
                detected_language="es",
                fernandez_huerta_score=doc.fernandez_huerta_score or 85.0,
                readability_category=cat,
                urgency=doc.urgency,
                critical_deadline=doc.critical_deadline,
                days_remaining=days_rem,
                tutor_alert_triggered=(doc.urgency in ("critical", "high")),
                requires_human_expert=doc.requires_human_expert,
                actions_required=actions_resp,
                ambiguities_flagged=doc.ambiguities,
                recommended_questions=doc.recommended_questions,
                storage_path=doc.storage_path,
                file_sha256=doc.file_sha256,
                created_at=doc.created_at,
            )
        )
    return result


@router.patch(
    "/actions/{action_id}/toggle",
    response_model=ActionItemResponse,
    summary="Marcar o desmarcar tarea del checklist como completada",
)
async def toggle_action(
    action_id: UUID,
    repo: InMemoryRepository = Depends(get_repository),
    user_id: UUID = Depends(get_current_user_id),
):
    """Sincroniza en tiempo real el progreso del checklist entre el adulto mayor y su tutor."""
    action = await repo.toggle_document_action(action_id, completed_by=user_id)
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarea con ID {action_id} no encontrada.",
        )
    return ActionItemResponse(
        id=action.id,
        document_id=action.document_id,
        task_description=action.task_description,
        required_document=action.required_document,
        deadline=action.deadline,
        is_completed=action.is_completed,
        completed_at=action.completed_at,
        created_at=action.created_at,
    )


@router.post(
    "/audit-readability",
    response_model=ReadabilityAuditResponse,
    summary="Auditar legibilidad sintáctica (Índice Fernández-Huerta)",
)
async def audit_text_readability(payload: ReadabilityAuditRequest):
    """Calcula el índice Fernández-Huerta y evalúa si cumple el umbral gerontológico FH >= 80."""
    audit = audit_readability(payload.text)
    return ReadabilityAuditResponse(
        score=audit.score,
        is_acceptable=audit.is_acceptable,
        category=audit.category,
        reading_level=audit.reading_level,
        num_words=audit.num_words,
        num_sentences=audit.num_sentences,
        total_syllables=audit.total_syllables,
        syllables_per_word=audit.syllables_per_word,
        words_per_sentence=audit.words_per_sentence,
        recommendations=audit.recommendations,
    )


@router.post(
    "/extract-dates",
    response_model=DateExtractionResponse,
    summary="Extracción temporal determinista (Mitigación FMEA FM-02)",
)
async def extract_dates_endpoint(payload: DateExtractionRequest):
    """Extrae determinísticamente fechas base, operadores temporales (+14d) y calcula plazos."""
    result = extract_deterministic_deadline(payload.text, reference_date=payload.reference_date)
    return DateExtractionResponse(
        deadline_date=result.deadline_date,
        base_date=result.base_date,
        offset_days=result.offset_days,
        is_business_days=result.is_business_days,
        operator=result.operator,
        urgency=result.urgency,
        days_remaining=result.days_remaining,
        tutor_alert_required=result.tutor_alert_required,
        raw_snippet=result.raw_snippet,
        confidence=result.confidence,
    )

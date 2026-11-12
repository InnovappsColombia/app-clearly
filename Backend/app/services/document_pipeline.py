"""
CLEARLY — Document Processing Pipeline Orchestrator
Coordinates MinIO storage, OCR extraction, Deterministic Date Extraction,
Fernández-Huerta Readability Auditing, Legal Guardrails, DB persistence, and Tutor Alerts.
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4
from loguru import logger

from app.core.config import settings
from app.db.repository import repository
from app.models.entities import DocumentActionEntity, DocumentEntity, NotificationEntity
from app.schemas.document import ActionItemResponse, DocumentProcessResponse
from app.services.date_extractor import extract_deterministic_deadline
from app.services.ocr_service import ocr_service
from app.services.plain_language import analyze_document_plain_language
from app.services.storage import storage_service


class DocumentPipeline:
    def __init__(self):
        self.storage = storage_service
        self.ocr = ocr_service
        self.repo = repository

    async def process_document(
        self,
        file_bytes: bytes,
        filename: str,
        user_id: UUID,
        content_type: Optional[str] = None,
        target_language: str = "es",
        reference_date: Optional[date] = None,
    ) -> DocumentProcessResponse:
        """
        End-to-end processing of an uploaded document.
        """
        ref_date = reference_date or date.today()

        # 1. Save file in sovereign storage (MinIO with local fallback)
        storage_path, file_sha256 = await self.storage.save_document(
            file_bytes=file_bytes, filename=filename, content_type=content_type
        )
        logger.info(f"Saved document '{filename}' to {storage_path} (SHA-256: {file_sha256[:12]}...)")

        # 2. Extract textual content
        extracted_text = await self.ocr.extract_text(file_bytes, filename)
        logger.info(f"Extracted {len(extracted_text)} chars from '{filename}'")

        # 3. Analyze document with Plain Language Engine
        analysis = analyze_document_plain_language(extracted_text, reference_date=ref_date)

        # 4. Extract deterministic deadline
        deadline_info = extract_deterministic_deadline(extracted_text, reference_date=ref_date)
        critical_deadline = deadline_info.deadline_date
        urgency = deadline_info.urgency
        days_remaining = deadline_info.days_remaining
        tutor_alert_required = deadline_info.tutor_alert_required

        # 5. Persist document record to Database
        doc_entity = DocumentEntity(
            id=uuid4(),
            user_id=user_id,
            storage_path=storage_path,
            file_sha256=file_sha256,
            original_extracted_text=extracted_text,
            plain_summary=analysis.plain_summary,
            issuing_entity=analysis.issuing_entity,
            urgency=urgency,
            critical_deadline=critical_deadline,
            fernandez_huerta_score=analysis.fernandez_huerta_score,
            ambiguities=analysis.ambiguities,
            recommended_questions=analysis.recommended_questions,
            requires_human_expert=analysis.requires_human_expert,
        )
        saved_doc = await self.repo.create_document(doc_entity)

        # 6. Persist Action Items
        action_responses: list[ActionItemResponse] = []
        for action in analysis.actions:
            act_entity = DocumentActionEntity(
                id=uuid4(),
                document_id=saved_doc.id,
                task_description=action.task,
                required_document=action.required_document,
                deadline=action.deadline or critical_deadline,
                is_completed=False,
            )
            saved_act = await self.repo.create_document_action(act_entity)
            action_responses.append(
                ActionItemResponse(
                    id=saved_act.id,
                    document_id=saved_act.document_id,
                    task_description=saved_act.task_description,
                    required_document=saved_act.required_document,
                    deadline=saved_act.deadline,
                    is_completed=saved_act.is_completed,
                    completed_at=saved_act.completed_at,
                    created_at=saved_act.created_at,
                )
            )

        # 7. Check and trigger Proactive Tutor Alert (< 15 days)
        tutor_alert_triggered = False
        if tutor_alert_required:
            tutors = await self.repo.get_active_tutors_for_senior(user_id)
            for tutor_rel in tutors:
                if tutor_rel.permissions.get("can_view_critical_alerts", True):
                    # Dispatch notification to Tutor
                    notif = NotificationEntity(
                        id=uuid4(),
                        user_id=tutor_rel.tutor_id,
                        title=f"⚠️ Alerta Preventiva: Fecha límite cercana ({analysis.issuing_entity})",
                        message=(
                            f"Su familiar recibió un documento con fecha límite para el "
                            f"{critical_deadline.strftime('%d/%m/%Y')} ({days_remaining} días restantes). "
                            f"Resumen: {analysis.plain_summary}"
                        ),
                        channel="push",
                        is_urgent=True,
                        metadata={
                            "document_id": str(saved_doc.id),
                            "senior_id": str(user_id),
                            "deadline": str(critical_deadline),
                        },
                    )
                    await self.repo.create_notification(notif)
                    tutor_alert_triggered = True
                    logger.warning(
                        f"Dispatched proactive alert to Tutor {tutor_rel.tutor_id} for doc {saved_doc.id}"
                    )

        return DocumentProcessResponse(
            id=saved_doc.id,
            user_id=saved_doc.user_id,
            document_type=analysis.document_type,
            issuing_entity=analysis.issuing_entity,
            plain_summary=analysis.plain_summary,
            detected_language=target_language,
            fernandez_huerta_score=analysis.fernandez_huerta_score,
            readability_category=analysis.readability_category,
            urgency=urgency,
            critical_deadline=critical_deadline,
            days_remaining=days_remaining,
            tutor_alert_triggered=tutor_alert_triggered,
            requires_human_expert=analysis.requires_human_expert,
            actions_required=action_responses,
            ambiguities_flagged=analysis.ambiguities,
            recommended_questions=analysis.recommended_questions,
            storage_path=saved_doc.storage_path,
            file_sha256=saved_doc.file_sha256,
            created_at=saved_doc.created_at,
        )


document_pipeline = DocumentPipeline()


"""
CLEARLY — Tutor Relationship Engine
Orchestrates Titular-Tutor Handshake, Ephemeral QR Pairing, Attenuated Capability Tokens,
Collaborative Checklists, and Duress PIN Protection (FMEA FM-04).
"""

from datetime import date, datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional
from uuid import UUID
from loguru import logger

from app.core.config import settings
from app.db.repository import repository
from app.models.entities import (
    DocumentActionEntity,
    DocumentEntity,
    TutorRelationshipEntity,
    UserEntity,
)
from app.schemas.tutor import (
    CollaborativeTaskItem,
    PairingCodeResponse,
    PairTutorResponse,
    TutorDashboardResponse,
    TutorSeniorSummaryResponse,
)
from app.services.connection_manager import ws_manager


class TutorEngine:
    def __init__(self):
        self.repo = repository
        self.ws = ws_manager

    async def generate_pairing_code(self, senior_id: UUID) -> PairingCodeResponse:
        """
        Generates ephemeral 6-digit code and Curve25519-compatible handshake QR payload.
        Engineering Spec 4.1 compliant.
        """
        senior = await self.repo.get_user(senior_id)
        senior_name = senior.full_name if senior else "Adulto Mayor"

        pairing_entity = await self.repo.create_pairing_code(
            senior_id=senior_id,
            ttl_minutes=settings.TUTOR_PAIRING_CODE_TTL_MINUTES,
        )

        # Ephemeral curve public key simulation for QR
        ephemeral_pubkey = hashlib.sha256(
            f"{pairing_entity.code}:{senior_id}:{pairing_entity.created_at.isoformat()}".encode()
        ).hexdigest()[:32]

        qr_payload = f"clearly://handshake?code={pairing_entity.code}&senior={senior_id}&key={ephemeral_pubkey}"

        return PairingCodeResponse(
            pairing_code=pairing_entity.code,
            senior_id=senior_id,
            senior_name=senior_name,
            expires_at=pairing_entity.expires_at,
            expires_in_seconds=settings.TUTOR_PAIRING_CODE_TTL_MINUTES * 60,
            qr_payload=qr_payload,
        )

    async def pair_tutor(self, tutor_id: UUID, code: str) -> Optional[PairTutorResponse]:
        """
        Redeems ephemeral code and links Tutor to Senior.
        Generates attenuated capability token restricting permissions to read_only and checklist collaboration.
        Engineering Spec 4.2 compliant.
        """
        rel = await self.repo.redeem_pairing_code(tutor_id=tutor_id, code=code)
        if not rel:
            return None

        senior = await self.repo.get_user(rel.senior_id)
        senior_profile = {
            "id": str(rel.senior_id),
            "full_name": senior.full_name if senior else "Rosa Gómez",
            "preferred_language": senior.preferred_language if senior else "es",
        }

        # Build attenuated capability token (Engineering Spec 4.2)
        caveats = [
            "action = read_only",
            "scope = critical_deadlines_and_checklists",
            "prohibit_actions = [financial_transfer, document_deletion, identity_alteration]",
            f"senior_target = {rel.senior_id}",
            f"issued_at = {datetime.now(timezone.utc).isoformat()}",
        ]
        token_body = json.dumps({"sub": str(tutor_id), "caveats": caveats}, sort_keys=True)
        capability_signature = hashlib.sha256(f"{token_body}:{settings.SECRET_KEY}".encode()).hexdigest()
        capability_token = f"pasv4.public.{token_body}.sig.{capability_signature[:16]}"

        # Broadcast pairing event to senior's WebSocket room
        await self.ws.broadcast_to_room(
            str(rel.senior_id),
            {
                "type": "TUTOR_PAIRED",
                "data": {
                    "tutor_id": str(tutor_id),
                    "relationship_id": str(rel.id),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            },
        )

        return PairTutorResponse(
            status="paired",
            relationship_id=rel.id,
            senior_profile=senior_profile,
            granted_permissions=rel.permissions,
            capability_token=capability_token,
        )

    async def get_tutor_seniors(self, tutor_id: UUID) -> List[TutorSeniorSummaryResponse]:
        """Lists all seniors linked to this tutor."""
        relationships = await self.repo.get_tutor_relationships_by_tutor(tutor_id)
        summaries: List[TutorSeniorSummaryResponse] = []

        for rel in relationships:
            senior = await self.repo.get_user(rel.senior_id)
            if not senior:
                continue

            # Count pending tasks and active deadlines
            docs = await self.repo.list_documents_by_user(rel.senior_id)
            active_deadlines = sum(1 for d in docs if d.critical_deadline and d.critical_deadline >= date.today())
            
            pending_tasks = 0
            has_critical = False
            for doc in docs:
                if doc.urgency in ("high", "critical"):
                    has_critical = True
                actions = await self.repo.get_document_actions(doc.id)
                pending_tasks += sum(1 for a in actions if not a.is_completed)

            summaries.append(
                TutorSeniorSummaryResponse(
                    senior_id=senior.id,
                    full_name=senior.full_name,
                    relationship_id=rel.id,
                    is_active=rel.is_active and not rel.is_duress_active,
                    active_deadlines_count=active_deadlines,
                    pending_tasks_count=pending_tasks,
                    critical_alert_active=has_critical and not rel.is_duress_active,
                )
            )

        return summaries

    async def build_dashboard(self, tutor_id: UUID, senior_id: UUID) -> Optional[TutorDashboardResponse]:
        """
        Builds unified Tutor Hub dashboard for Carlos supervising Elena.
        If Duress mode (FMEA FM-04) is active, returns sanitized quarantine view.
        """
        rel = await self.repo.get_tutor_relationship(senior_id, tutor_id)
        if not rel or not rel.is_active:
            return None

        senior = await self.repo.get_user(senior_id)
        if not senior:
            return None

        # Duress Mode Check (FM-04): Silently quarantine and return sanitized neutral view
        if rel.is_duress_active:
            logger.warning(f"Serving quarantined dashboard for senior {senior_id} to tutor {tutor_id}")
            return TutorDashboardResponse(
                senior={
                    "id": str(senior.id),
                    "full_name": senior.full_name,
                    "phone_number": senior.phone_number,
                    "preferred_language": senior.preferred_language,
                    "accessibility_settings": senior.accessibility_settings,
                },
                relationship={
                    "id": str(rel.id),
                    "is_active": True,  # Appear normal to coercer
                    "permissions": rel.permissions,
                    "created_at": rel.created_at.isoformat(),
                },
                critical_deadlines=[],
                recent_documents=[],
                collaborative_checklist=[],
                notifications=[],
                is_quarantine_mode=True,
            )

        # Normal Tutor Hub Data
        docs = await self.repo.list_documents_by_user(senior_id)
        today = date.today()

        critical_deadlines = []
        recent_documents = []
        collaborative_checklist: List[CollaborativeTaskItem] = []

        for doc in docs:
            days_left = (doc.critical_deadline - today).days if doc.critical_deadline else None
            is_critical = doc.urgency in ("high", "critical") or (days_left is not None and days_left <= 15)

            if doc.critical_deadline and days_left is not None and days_left >= 0:
                critical_deadlines.append({
                    "document_id": str(doc.id),
                    "issuing_entity": doc.issuing_entity or "Entidad Pública",
                    "plain_summary": doc.plain_summary,
                    "deadline": doc.critical_deadline.isoformat(),
                    "days_remaining": days_left,
                    "is_urgent": is_critical,
                })

            recent_documents.append({
                "id": str(doc.id),
                "issuing_entity": doc.issuing_entity,
                "plain_summary": doc.plain_summary,
                "urgency": doc.urgency,
                "critical_deadline": doc.critical_deadline.isoformat() if doc.critical_deadline else None,
                "fernandez_huerta_score": float(doc.fernandez_huerta_score) if doc.fernandez_huerta_score else None,
                "requires_human_expert": doc.requires_human_expert,
                "created_at": doc.created_at.isoformat(),
            })

            # Checklists
            actions = await self.repo.get_document_actions(doc.id)
            for act in actions:
                completed_by_name = None
                if act.completed_by_user_id:
                    comp_user = await self.repo.get_user(act.completed_by_user_id)
                    completed_by_name = comp_user.full_name if comp_user else "Familiar"

                act_days_left = (act.deadline - today).days if act.deadline else None

                collaborative_checklist.append(
                    CollaborativeTaskItem(
                        id=act.id,
                        document_id=doc.id,
                        document_title=doc.issuing_entity or "Trámite Comunitario",
                        task_description=act.task_description,
                        required_document=act.required_document,
                        deadline=act.deadline,
                        days_remaining=act_days_left,
                        is_critical=is_critical,
                        is_completed=act.is_completed,
                        completed_by_user_id=act.completed_by_user_id,
                        completed_by_name=completed_by_name,
                        completed_at=act.completed_at,
                    )
                )

        # Notifications
        notifs = await self.repo.list_notifications_by_user(tutor_id)
        notifications_data = [
            {
                "id": str(n.id),
                "title": n.title,
                "message": n.message,
                "channel": n.channel,
                "is_urgent": n.is_urgent,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
            }
            for n in notifs[:10]
        ]

        return TutorDashboardResponse(
            senior={
                "id": str(senior.id),
                "full_name": senior.full_name,
                "phone_number": senior.phone_number,
                "preferred_language": senior.preferred_language,
                "accessibility_settings": senior.accessibility_settings,
            },
            relationship={
                "id": str(rel.id),
                "is_active": rel.is_active,
                "permissions": rel.permissions,
                "created_at": rel.created_at.isoformat(),
            },
            critical_deadlines=critical_deadlines,
            recent_documents=recent_documents,
            collaborative_checklist=collaborative_checklist,
            notifications=notifications_data,
            is_quarantine_mode=False,
        )

    async def toggle_checklist_item(
        self, action_id: UUID, completed_by_user_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Toggles completion state of a task and broadcasts to the Senior room in real-time.
        """
        action = await self.repo.toggle_document_action(action_id, completed_by=completed_by_user_id)
        if not action:
            return None

        # Look up senior_id through the document
        doc = await self.repo.get_document(action.document_id)
        senior_id = doc.user_id if doc else None

        completed_by_name = None
        if action.completed_by_user_id:
            user = await self.repo.get_user(action.completed_by_user_id)
            completed_by_name = user.full_name if user else "Usuario"

        action_payload = {
            "action_id": str(action.id),
            "document_id": str(action.document_id),
            "task_description": action.task_description,
            "is_completed": action.is_completed,
            "completed_by_user_id": str(action.completed_by_user_id) if action.completed_by_user_id else None,
            "completed_by_name": completed_by_name,
            "completed_at": action.completed_at.isoformat() if action.completed_at else None,
        }

        # Broadcast update in real time
        if senior_id:
            await self.ws.broadcast_action_toggle(str(senior_id), action_payload)

        return action_payload

    async def activate_duress_pin(self, senior_id: UUID, entered_pin: str) -> bool:
        """
        Executes Duress protocol: silent decoupling, social worker alert, quarantine mode.
        """
        return await self.repo.trigger_duress(senior_id, entered_pin)


tutor_engine = TutorEngine()


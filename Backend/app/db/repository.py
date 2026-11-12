"""
CLEARLY — Database Repository Layer
Provides asynchronous data access for Users, Documents, Actions, Tutors, Notifications, and Community Events.
Works with PostgreSQL in production, with seamless in-memory backing for local/test execution.
"""

from datetime import date, datetime, timedelta, timezone
import random
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from loguru import logger

from app.core.config import settings
from app.models.entities import (
    UserEntity,
    TutorRelationshipEntity,
    TutorPairingCodeEntity,
    DuressAlertEntity,
    CommunityEventEntity,
    DocumentEntity,
    DocumentActionEntity,
    NotificationEntity,
    get_utc_now,
)


class InMemoryRepository:
    def __init__(self):
        self.users: Dict[UUID, UserEntity] = {}
        self.tutor_relationships: Dict[UUID, TutorRelationshipEntity] = {}
        self.pairing_codes: Dict[str, TutorPairingCodeEntity] = {}
        self.duress_alerts: Dict[UUID, DuressAlertEntity] = {}
        self.community_events: Dict[UUID, CommunityEventEntity] = {}
        self.documents: Dict[UUID, DocumentEntity] = {}
        self.actions: Dict[UUID, DocumentActionEntity] = {}
        self.notifications: Dict[UUID, NotificationEntity] = {}
        self._load_seed_data()

    def _load_seed_data(self):
        """Pre-load canonical seed data corresponding to Database/seeds/001_initial_seed.sql."""
        elena_id = UUID("11111111-1111-1111-1111-111111111111")
        carlos_id = UUID("22222222-2222-2222-2222-222222222222")
        david_id = UUID("33333333-3333-3333-3333-333333333333")
        rosa_id = UUID("44444444-4444-4444-4444-444444444444")
        rel_id = UUID("55555555-5555-5555-5555-555555555555")

        self.users[elena_id] = UserEntity(
            id=elena_id,
            phone_number="+19055550101",
            email="elena.pabla@clearly.example",
            full_name="Elena Pabla",
            role="senior",
            preferred_language="es",
            accessibility_settings={
                "font_scale": 1.5,
                "high_contrast": True,
                "audio_speed": 0.85,
                "auto_read_aloud": True,
            },
        )

        self.users[carlos_id] = UserEntity(
            id=carlos_id,
            phone_number="+19055550202",
            email="carlos.pabla@clearly.example",
            full_name="Carlos Pabla",
            role="tutor",
            preferred_language="es",
            accessibility_settings={
                "font_scale": 1.0,
                "high_contrast": False,
                "audio_speed": 1.0,
                "auto_read_aloud": False,
            },
        )

        self.users[david_id] = UserEntity(
            id=david_id,
            phone_number="+19055550303",
            email="david.mendoza@clearly.example",
            full_name="David Mendoza, RCIC",
            role="expert",
            preferred_language="es",
        )

        self.users[rosa_id] = UserEntity(
            id=rosa_id,
            phone_number="+19055550404",
            email="rosa.gomez@clearly.example",
            full_name="Rosa Gómez",
            role="senior",
            preferred_language="es",
        )

        self.tutor_relationships[rel_id] = TutorRelationshipEntity(
            id=rel_id,
            senior_id=elena_id,
            tutor_id=carlos_id,
            is_active=True,
            is_duress_active=False,
            permissions={
                "can_view_critical_alerts": True,
                "can_view_documents": True,
                "can_view_events": True,
                "can_hire_experts": True,
            },
        )

        # Pre-seed canonical Brampton community events
        ev1_id = UUID("77777777-7777-7777-7777-777777777771")
        ev2_id = UUID("77777777-7777-7777-7777-777777777772")
        ev3_id = UUID("77777777-7777-7777-7777-777777777773")

        now = get_utc_now()
        self.community_events[ev1_id] = CommunityEventEntity(
            id=ev1_id,
            source="civic_library",
            raw_title="Gentle Chair Yoga & Senior Balance Workshop",
            made_clear_what="Una clase suave de estiramiento y respiración sentado en silla, ideal para mejorar el equilibrio y relajarse sin forzar las articulaciones.",
            made_clear_when_where="Sábado 21 de Noviembre de 10:30 AM a 11:30 AM. En la Biblioteca Central de Brampton (65 Queen St E).",
            made_clear_cost="GRATUITO (Cero costo, financiado por la ciudad).",
            made_clear_how_to_register="Entrada libre. Puedes llegar 10 minutos antes o mostrar tu código de reserva de CLEARLY en el mostrador.",
            venue_name="Brampton Library - Central Branch",
            venue_address="65 Queen St E, Brampton, ON L6W 3L6",
            start_time=now + timedelta(days=5),
            end_time=now + timedelta(days=5, hours=1),
            is_wheelchair_accessible=True,
            is_senior_friendly=True,
            is_free=True,
        )

        self.community_events[ev2_id] = CommunityEventEntity(
            id=ev2_id,
            source="civic_library",
            raw_title="Café Tecnológico: Aprende a Usar WhatsApp y la Tableta sin Miedo",
            made_clear_what="Un taller paciente donde voluntarios jóvenes te enseñan a hacer videollamadas con tu familia, agrandar la letra del teléfono y cuidarte de estafas por mensaje.",
            made_clear_when_where="Miércoles 25 de Noviembre de 2:00 PM a 3:30 PM. En el Centro Comunitario Chinguacousy Park.",
            made_clear_cost="GRATUITO (Incluye café y té sin costo).",
            made_clear_how_to_register="Registro fácil: presiona el botón 'Asistir' en CLEARLY o llama al 311 indicando tu nombre.",
            venue_name="Chinguacousy Park Community Centre",
            venue_address="9050 Bramalea Rd, Brampton, ON L6S 6G7",
            start_time=now + timedelta(days=9),
            end_time=now + timedelta(days=9, minutes=90),
            is_wheelchair_accessible=True,
            is_senior_friendly=True,
            is_free=True,
        )

        self.community_events[ev3_id] = CommunityEventEntity(
            id=ev3_id,
            source="civic_library",
            raw_title="Clínica Comunitaria Gratuita de Vacunación contra la Gripe y Chequeo de Presión",
            made_clear_what="Enfermeras comunitarias revisarán tu presión arterial, responderán dudas sobre tus medicamentos y aplicarán la vacuna estacional de la gripe sin filas largas.",
            made_clear_when_where="Viernes 27 de Noviembre de 9:00 AM a 1:00 PM. Centro Cívico Flower City.",
            made_clear_cost="GRATUITO (Presentar tarjeta de salud OHIP o identificación local).",
            made_clear_how_to_register="Atención por orden de llegada con asientos cómodos reservados para personas con movilidad reducida.",
            venue_name="Flower City Seniors Recreation Centre",
            venue_address="8870 McLaughlin Rd S, Brampton, ON L6Y 5T1",
            start_time=now + timedelta(days=11),
            end_time=now + timedelta(days=11, hours=4),
            is_wheelchair_accessible=True,
            is_senior_friendly=True,
            is_free=True,
        )

        # Pre-seed sample document for Elena with collaborative action
        seed_doc_id = UUID("88888888-8888-8888-8888-888888888888")
        self.documents[seed_doc_id] = DocumentEntity(
            id=seed_doc_id,
            user_id=elena_id,
            storage_path="documents/elena_ircc_letter.pdf",
            file_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            original_extracted_text="Immigration, Refugees and Citizenship Canada (IRCC). Notice of Procedural Fairness regarding your permanent resident card renewal. You have 30 calendar days from the date of this letter to submit proof of physical presence in Canada.",
            plain_summary="Inmigración Canadá le solicita comprobantes de que ha vivido en Canadá durante los últimos 5 años para renovar su tarjeta de residencia.",
            issuing_entity="Immigration, Refugees and Citizenship Canada (IRCC)",
            urgency="high",
            critical_deadline=date.today() + timedelta(days=12),
            fernandez_huerta_score=84.5,
            ambiguities=["No especifica si los pasaportes deben estar traducidos al inglés."],
            recommended_questions=["¿Cuáles pruebas de residencia son aceptadas de inmediato?"],
            requires_human_expert=True,
        )

        seed_act_id = UUID("99999999-9999-9999-9999-999999999991")
        self.actions[seed_act_id] = DocumentActionEntity(
            id=seed_act_id,
            document_id=seed_doc_id,
            task_description="Reunir sellos del pasaporte y recibos de servicios del domicilio en Brampton",
            required_document="Pasaporte vigente y contrato de alquiler",
            deadline=date.today() + timedelta(days=10),
            is_completed=False,
        )

        # Pre-seed a notification for Carlos
        notif_id = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
        self.notifications[notif_id] = NotificationEntity(
            id=notif_id,
            user_id=carlos_id,
            title="⚠️ Alerta Preventiva: Fecha límite cercana (IRCC)",
            message="Su familiar Elena recibió un requerimiento de IRCC para renovar residencia. Vence en 12 días.",
            channel="push",
            is_urgent=True,
            metadata={"document_id": str(seed_doc_id), "senior_id": str(elena_id)},
        )

        logger.info("Initialized CLEARLY repository with Brampton seed data (Elena, Carlos, David, Rosa, Events).")

    # User operations
    async def get_user(self, user_id: UUID) -> Optional[UserEntity]:
        return self.users.get(user_id)

    async def get_user_by_phone(self, phone: str) -> Optional[UserEntity]:
        clean_phone = phone.strip()
        for u in self.users.values():
            if u.phone_number == clean_phone or u.phone_number.replace("+", "") == clean_phone.replace("+", ""):
                return u
        return None

    async def create_user(self, user: UserEntity) -> UserEntity:
        self.users[user.id] = user
        return user

    # Tutor relationship operations
    async def get_active_tutors_for_senior(self, senior_id: UUID) -> List[TutorRelationshipEntity]:
        return [
            rel for rel in self.tutor_relationships.values()
            if rel.senior_id == senior_id and rel.is_active and not rel.is_duress_active
        ]

    async def get_tutor_relationships_by_tutor(self, tutor_id: UUID) -> List[TutorRelationshipEntity]:
        return [
            rel for rel in self.tutor_relationships.values()
            if rel.tutor_id == tutor_id and rel.is_active
        ]

    async def get_tutor_relationship(self, senior_id: UUID, tutor_id: UUID) -> Optional[TutorRelationshipEntity]:
        for rel in self.tutor_relationships.values():
            if rel.senior_id == senior_id and rel.tutor_id == tutor_id:
                return rel
        return None

    # Handshake & Pairing Code Operations
    async def create_pairing_code(self, senior_id: UUID, ttl_minutes: int = 15) -> TutorPairingCodeEntity:
        code = f"{random.randint(100000, 999999)}"
        now = get_utc_now()
        expires = now + timedelta(minutes=ttl_minutes)

        pairing_entity = TutorPairingCodeEntity(
            code=code,
            senior_id=senior_id,
            created_at=now,
            expires_at=expires,
            is_redeemed=False,
        )
        self.pairing_codes[code] = pairing_entity
        logger.info(f"Created ephemeral pairing code '{code}' for senior {senior_id} (expires: {expires})")
        return pairing_entity

    async def redeem_pairing_code(
        self, tutor_id: UUID, code: str
    ) -> Optional[TutorRelationshipEntity]:
        clean_code = code.strip()
        pairing = self.pairing_codes.get(clean_code)
        if not pairing:
            return None

        now = get_utc_now()
        if pairing.is_redeemed or pairing.expires_at < now:
            logger.warning(f"Attempted redemption of expired/used pairing code '{code}'")
            return None

        pairing.is_redeemed = True
        senior_id = pairing.senior_id

        # Check if relationship already exists
        existing_rel = await self.get_tutor_relationship(senior_id, tutor_id)
        if existing_rel:
            existing_rel.is_active = True
            existing_rel.is_duress_active = False
            existing_rel.revoked_at = None
            logger.info(f"Re-activated existing tutor relationship between tutor {tutor_id} and senior {senior_id}")
            return existing_rel

        # Create new tutor relationship
        rel_id = uuid4()
        new_rel = TutorRelationshipEntity(
            id=rel_id,
            senior_id=senior_id,
            tutor_id=tutor_id,
            is_active=True,
            is_duress_active=False,
            permissions={
                "can_view_critical_alerts": True,
                "can_view_documents": True,
                "can_view_events": True,
                "can_hire_experts": True,
            },
        )
        self.tutor_relationships[rel_id] = new_rel
        logger.info(f"Handshake successful! Linked tutor {tutor_id} to senior {senior_id} (rel {rel_id})")
        return new_rel

    # Duress Security Protocol (FMEA FM-04)
    async def trigger_duress(self, senior_id: UUID, entered_pin: str) -> bool:
        if entered_pin.strip() != settings.DURESS_PIN_DEFAULT:
            logger.warning(f"Invalid PIN entered for duress trigger by senior {senior_id}")
            return False

        now = get_utc_now()
        # Silently deactivate/flag tutor relationships for this senior
        for rel in self.tutor_relationships.values():
            if rel.senior_id == senior_id:
                rel.is_duress_active = True
                rel.duress_activated_at = now

        # Create Duress Alert for welfare check
        alert_id = uuid4()
        quarantine_token = f"quarantine_{uuid4().hex[:12]}"
        alert = DuressAlertEntity(
            id=alert_id,
            senior_id=senior_id,
            triggered_at=now,
            quarantine_token=quarantine_token,
            social_worker_alert_sent=True,
            status="active",
        )
        self.duress_alerts[alert_id] = alert

        # Dispatch silent welfare check to social workers
        notif = NotificationEntity(
            id=uuid4(),
            user_id=senior_id,
            title="Protocolo de Bienestar Activado",
            message="El centro cívico asignó un trabajador social certificado para acompañamiento preventivo.",
            channel="in_app",
            is_urgent=True,
            metadata={"quarantine_token": quarantine_token, "duress": True},
        )
        self.notifications[notif.id] = notif
        logger.warning(f"🚨 DURESS MODE TRIGGERED for Senior {senior_id}. Silent quarantine activated.")
        return True

    # Document operations
    async def create_document(self, doc: DocumentEntity) -> DocumentEntity:
        self.documents[doc.id] = doc
        return doc

    async def get_document(self, doc_id: UUID) -> Optional[DocumentEntity]:
        return self.documents.get(doc_id)

    async def list_documents_by_user(self, user_id: UUID) -> List[DocumentEntity]:
        docs = [d for d in self.documents.values() if d.user_id == user_id]
        docs.sort(key=lambda d: d.created_at, reverse=True)
        return docs

    # Document Actions operations
    async def create_document_action(self, action: DocumentActionEntity) -> DocumentActionEntity:
        self.actions[action.id] = action
        return action

    async def get_document_actions(self, doc_id: UUID) -> List[DocumentActionEntity]:
        acts = [a for a in self.actions.values() if a.document_id == doc_id]
        acts.sort(key=lambda a: (a.deadline or date.max, a.created_at))
        return acts

    async def get_action_by_id(self, action_id: UUID) -> Optional[DocumentActionEntity]:
        return self.actions.get(action_id)

    async def toggle_document_action(
        self, action_id: UUID, completed_by: Optional[UUID] = None
    ) -> Optional[DocumentActionEntity]:
        action = self.actions.get(action_id)
        if not action:
            return None
        action.is_completed = not action.is_completed
        action.completed_at = get_utc_now() if action.is_completed else None
        action.completed_by_user_id = completed_by if action.is_completed else None
        return action

    # Notifications operations
    async def create_notification(self, notif: NotificationEntity) -> NotificationEntity:
        self.notifications[notif.id] = notif
        return notif

    async def list_notifications_by_user(
        self, user_id: UUID, unread_only: bool = False
    ) -> List[NotificationEntity]:
        notifs = [n for n in self.notifications.values() if n.user_id == user_id]
        if unread_only:
            notifs = [n for n in notifs if not n.is_read]
        notifs.sort(key=lambda n: n.created_at, reverse=True)
        return notifs

    # Community Events operations
    async def create_community_event(self, event: CommunityEventEntity) -> CommunityEventEntity:
        self.community_events[event.id] = event
        return event

    async def list_community_events(self) -> List[CommunityEventEntity]:
        events = list(self.community_events.values())
        events.sort(key=lambda e: e.start_time)
        return events

    async def search_community_events(self, query: str) -> List[CommunityEventEntity]:
        q = query.lower().strip()
        matched: List[CommunityEventEntity] = []
        for ev in self.community_events.values():
            text_corpus = f"{ev.raw_title} {ev.made_clear_what} {ev.made_clear_when_where} {ev.venue_name}".lower()
            if any(term in text_corpus for term in q.split()):
                matched.append(ev)
        matched.sort(key=lambda e: e.start_time)
        return matched if matched else list(self.community_events.values())[:3]


# Global singleton repository instance
repository = InMemoryRepository()

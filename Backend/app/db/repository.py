"""
CLEARLY — Database Repository Layer
Provides asynchronous data access for Users, Documents, Actions, Tutors, and Notifications.
Works with PostgreSQL in production, with seamless in-memory backing for local/test execution.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID
from loguru import logger

from app.models.entities import (
    UserEntity,
    TutorRelationshipEntity,
    DocumentEntity,
    DocumentActionEntity,
    NotificationEntity,
)


class InMemoryRepository:
    def __init__(self):
        self.users: Dict[UUID, UserEntity] = {}
        self.tutor_relationships: Dict[UUID, TutorRelationshipEntity] = {}
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
            permissions={
                "can_view_critical_alerts": True,
                "can_view_documents": True,
                "can_view_events": True,
                "can_hire_experts": True,
            },
        )
        logger.info("Initialized CLEARLY repository with Brampton seed data (Elena, Carlos, David, Rosa).")

    # User operations
    async def get_user(self, user_id: UUID) -> Optional[UserEntity]:
        return self.users.get(user_id)

    async def get_user_by_phone(self, phone: str) -> Optional[UserEntity]:
        for u in self.users.values():
            if u.phone_number == phone:
                return u
        return None

    async def create_user(self, user: UserEntity) -> UserEntity:
        self.users[user.id] = user
        return user

    # Tutor relationship operations
    async def get_active_tutors_for_senior(self, senior_id: UUID) -> List[TutorRelationshipEntity]:
        return [
            rel for rel in self.tutor_relationships.values()
            if rel.senior_id == senior_id and rel.is_active
        ]

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
        acts.sort(key=lambda a: (a.deadline or datetime.max.date(), a.created_at))
        return acts

    async def toggle_document_action(
        self, action_id: UUID, completed_by: Optional[UUID] = None
    ) -> Optional[DocumentActionEntity]:
        action = self.actions.get(action_id)
        if not action:
            return None
        action.is_completed = not action.is_completed
        action.completed_at = datetime.now(timezone.utc) if action.is_completed else None
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


# Global singleton repository instance
repository = InMemoryRepository()

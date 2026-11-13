"""
CLEARLY — Backend Adapter for Sovereign SQLite / sqlite-vec RAG
Connects Backend FastAPI services and repositories to the local RAG engine.
Enables transparent local-first persistence and edge RAG capabilities.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from loguru import logger

from RAG.pipeline.rag_service import RAGQueryResponse, rag_service
from RAG.storage.sqlite_vector_store import (
    DocumentRecord,
    EventRecord,
    EventSearchResult,
    SQLiteVectorStore,
)


class BackendRAGAdapter:
    def __init__(self, service=None):
        self.rag = service or rag_service
        self.store: SQLiteVectorStore = self.rag.store

    def sync_document(
        self,
        document_id: str,
        filename: str,
        content: str,
        user_id: Optional[str] = None,
        plain_summary: Optional[str] = None,
        issuing_entity: Optional[str] = None,
        urgency: str = "NORMAL",
        critical_deadline: Optional[str] = None,
        fernandez_huerta_score: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Synchronizes a document created in Backend into the sovereign SQLite vector store.
        """
        result = self.rag.index_document(
            content=content,
            filename=filename,
            document_id=str(document_id),
            user_id=str(user_id) if user_id else None,
            issuing_entity=issuing_entity,
            critical_deadline=str(critical_deadline) if critical_deadline else None,
            urgency=urgency,
            metadata=metadata or {},
        )
        logger.info(f"Synced document '{filename}' to sovereign SQLite ({result.chunks_created} chunks).")
        return result.document_id

    def sync_civic_event(
        self,
        event_id: str,
        title: str,
        description: str,
        city: str,
        start_time: str,
        plain_description: Optional[str] = None,
        organizer_name: Optional[str] = None,
        postal_code: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        is_free: bool = True,
        category: Optional[str] = None,
        canonical_questions: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Synchronizes a civic event into the sovereign SQLite database with sqlite-vec.
        """
        ev_rec = EventRecord(
            id=str(event_id),
            title=title,
            description=description,
            city=city,
            start_time=str(start_time),
            plain_description=plain_description,
            organizer_name=organizer_name,
            postal_code=postal_code,
            latitude=latitude,
            longitude=longitude,
            is_free=is_free,
            category=category,
            canonical_questions=canonical_questions or {},
            metadata=metadata or {},
        )
        return self.store.insert_event(ev_rec)

    def query_senior_documents(
        self,
        user_query: str,
        senior_id: Optional[str] = None,
        document_id: Optional[str] = None,
        top_k: int = 5,
        language: str = "es",
    ) -> RAGQueryResponse:
        """
        Runs a grounded sovereign RAG query over the senior's stored legal/administrative documents.
        """
        return self.rag.query(
            user_query=user_query,
            user_id=str(senior_id) if senior_id else None,
            document_id=str(document_id) if document_id else None,
            top_k=top_k,
            language=language,
        )

    def search_civic_events(
        self,
        query: str,
        city: Optional[str] = None,
        top_k: int = 5,
    ) -> List[EventSearchResult]:
        """
        Performs hybrid vector+FTS search over local civic events.
        """
        return self.store.search_events_hybrid(
            query_text=query,
            top_k=top_k,
            city=city,
        )


backend_rag_adapter = BackendRAGAdapter()


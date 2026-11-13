"""
CLEARLY — Sovereign Local RAG & SQLite/sqlite-vec Module
Zero-Network Egress, Gerontological Plain Language, and Local-First Persistence.
"""

from .chunker.semantic_chunker import ChunkData, SemanticChunker, semantic_chunker
from .config import rag_settings
from .embeddings.bge_m3_engine import BGEM3EmbeddingEngine, bge_m3_engine
from .pipeline.guardrails import (
    GuardrailAuditResult,
    LegalGuardrail,
    ReadabilityMetrics,
    SovereignReadabilityAuditor,
    legal_guardrail,
    readability_auditor,
)
from .pipeline.rag_service import (
    IndexingResult,
    RAGQueryResponse,
    SovereignRAGService,
    rag_service,
)
from .storage.sqlite_vector_store import (
    ChunkRecord,
    DocumentRecord,
    EventRecord,
    EventSearchResult,
    SearchResult,
    SQLiteVectorStore,
)

__all__ = [
    "rag_settings",
    "bge_m3_engine",
    "BGEM3EmbeddingEngine",
    "semantic_chunker",
    "SemanticChunker",
    "ChunkData",
    "SQLiteVectorStore",
    "DocumentRecord",
    "ChunkRecord",
    "SearchResult",
    "EventRecord",
    "EventSearchResult",
    "rag_service",
    "SovereignRAGService",
    "IndexingResult",
    "RAGQueryResponse",
    "readability_auditor",
    "SovereignReadabilityAuditor",
    "legal_guardrail",
    "LegalGuardrail",
    "ReadabilityMetrics",
    "GuardrailAuditResult",
]


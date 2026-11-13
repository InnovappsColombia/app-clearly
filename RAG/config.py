"""
CLEARLY — Sovereign Local RAG Configuration
Loads configuration for SQLite, sqlite-vec, BGE-M3 embeddings, and Chunking.
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field


class RAGSettings(BaseModel):
    # Base paths
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent)
    DATA_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent / "data")
    SQLITE_DB_PATH: Path = Field(
        default_factory=lambda: Path(os.getenv("SQLITE_DB_PATH", str(Path(__file__).resolve().parent / "data" / "clearly_sovereign.db")))
    )

    # Vector & Embedding Parameters (BGE-M3 standard)
    EMBEDDING_MODEL_NAME: str = Field(default_factory=lambda: os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-m3"))
    EMBEDDING_DIMENSIONS: int = Field(default_factory=lambda: int(os.getenv("EMBEDDING_DIMENSIONS", "1024")))
    SQLITE_VEC_ENABLED: bool = Field(default_factory=lambda: os.getenv("SQLITE_VEC_ENABLED", "True").lower() in ("true", "1", "yes"))

    # Chunking Configuration
    MAX_CHUNK_TOKENS: int = Field(default_factory=lambda: int(os.getenv("RAG_MAX_CHUNK_TOKENS", "400")))
    CHUNK_OVERLAP_TOKENS: int = Field(default_factory=lambda: int(os.getenv("RAG_CHUNK_OVERLAP_TOKENS", "60")))
    MAX_CHUNK_CHARS: int = Field(default_factory=lambda: int(os.getenv("RAG_MAX_CHUNK_CHARS", "1400")))
    CHUNK_OVERLAP_CHARS: int = Field(default_factory=lambda: int(os.getenv("RAG_CHUNK_OVERLAP_CHARS", "200")))

    # Hybrid Search Parameters
    TOP_K_DENSE: int = Field(default_factory=lambda: int(os.getenv("RAG_TOP_K_DENSE", "10")))
    TOP_K_SPARSE: int = Field(default_factory=lambda: int(os.getenv("RAG_TOP_K_SPARSE", "10")))
    FINAL_TOP_K: int = Field(default_factory=lambda: int(os.getenv("RAG_FINAL_TOP_K", "5")))
    RRF_K: int = Field(default_factory=lambda: int(os.getenv("RAG_RRF_K", "60")))
    WEIGHT_DENSE: float = Field(default_factory=lambda: float(os.getenv("RAG_WEIGHT_DENSE", "1.0")))
    WEIGHT_SPARSE: float = Field(default_factory=lambda: float(os.getenv("RAG_WEIGHT_SPARSE", "0.8")))

    # Readability Targets (Gerontological Accessibility)
    MIN_FERNANDEZ_HUERTA: float = Field(default_factory=lambda: float(os.getenv("MIN_FERNANDEZ_HUERTA", "80.0")))
    MIN_FLESCH_READING_EASE: float = Field(default_factory=lambda: float(os.getenv("MIN_FLESCH_READING_EASE", "80.0")))

    # Privacy and Egress
    STRICT_OFFLINE_MODE: bool = Field(default_factory=lambda: os.getenv("STRICT_OFFLINE_MODE", "True").lower() in ("true", "1", "yes"))


rag_settings = RAGSettings()


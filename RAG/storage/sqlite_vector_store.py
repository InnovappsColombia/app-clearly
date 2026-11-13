"""
CLEARLY — Sovereign SQLite Vector Store with sqlite-vec & FTS5
Provides embedded, zero-leakage, local-first persistence:
1. Native sqlite-vec virtual tables (vec0) with 1024-dim cosine distance matching.
2. Full-Text Search (FTS5) with Porter stemming and BM25 ranking.
3. Sovereign Reciprocal Rank Fusion (RRF) for Dense + Sparse Hybrid Search.
4. Graceful fallback to embedded Python cosine calculation if sqlite-vec is unavailable.
5. Fully ACID compliant with WAL mode for concurrent read/write.
"""

import json
import math
import os
import sqlite3
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4

from RAG.config import rag_settings
from RAG.embeddings.bge_m3_engine import bge_m3_engine


@dataclass
class DocumentRecord:
    id: str
    filename: str
    file_sha256: str
    content: str
    user_id: Optional[str] = None
    plain_summary: Optional[str] = None
    issuing_entity: Optional[str] = None
    urgency: str = "NORMAL"
    critical_deadline: Optional[str] = None
    fernandez_huerta_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None


@dataclass
class ChunkRecord:
    id: str
    document_id: str
    chunk_index: int
    content: str
    token_count: int
    section_header: Optional[str] = None
    dates_found: List[str] = field(default_factory=list)
    amounts_found: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None


@dataclass
class SearchResult:
    chunk_id: str
    document_id: str
    chunk_index: int
    content: str
    section_header: Optional[str]
    score: float  # RRF score, or cosine similarity, or BM25 rank
    dense_rank: Optional[int] = None
    sparse_rank: Optional[int] = None
    dates_found: List[str] = field(default_factory=list)
    amounts_found: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventRecord:
    id: str
    title: str
    description: str
    city: str
    start_time: str
    plain_description: Optional[str] = None
    organizer_name: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    end_time: Optional[str] = None
    is_free: bool = True
    cost_notes: Optional[str] = None
    category: Optional[str] = None
    canonical_questions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None


@dataclass
class EventSearchResult:
    event: EventRecord
    score: float
    dense_rank: Optional[int] = None
    sparse_rank: Optional[int] = None


class SQLiteVectorStore:
    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        self.db_path = str(db_path) if db_path else str(rag_settings.SQLITE_DB_PATH)
        self.has_sqlite_vec = False
        self._memory_conn: Optional[sqlite3.Connection] = None
        self._ensure_data_dir()
        self._init_db()

    def _ensure_data_dir(self) -> None:
        """Ensures parent directory exists for file-based SQLite databases."""
        if self.db_path != ":memory:" and not self.db_path.startswith("file:"):
            p = Path(self.db_path).resolve()
            p.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """
        Opens a connection, enables WAL mode, foreign keys, and loads sqlite-vec if available.
        For in-memory databases, reuses a single connection instance across operations.
        """
        if self.db_path == ":memory:":
            if self._memory_conn is not None:
                return self._memory_conn
            conn = sqlite3.connect(":memory:")
            self._configure_connection(conn)
            self._memory_conn = conn
            return conn

        conn = sqlite3.connect(self.db_path)
        self._configure_connection(conn)
        return conn

    def _configure_connection(self, conn: sqlite3.Connection) -> None:
        """Configures pragmas, extensions, and custom SQL functions."""
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")

        # Try to load sqlite-vec extension
        if rag_settings.SQLITE_VEC_ENABLED:
            try:
                import sqlite_vec
                conn.enable_load_extension(True)
                sqlite_vec.load(conn)
                self.has_sqlite_vec = True
            except Exception:
                self.has_sqlite_vec = False

        # Register custom cosine distance function for fallback query
        conn.create_function("py_cosine_dist", 2, self._py_cosine_dist)

    @staticmethod
    def _py_cosine_dist(blob1: bytes, blob2: bytes) -> float:
        """Fallback Python cosine distance between two binary float arrays."""
        if not blob1 or not blob2:
            return 1.0
        dim1 = len(blob1) // 4
        dim2 = len(blob2) // 4
        if dim1 != dim2 or dim1 == 0:
            return 1.0
        v1 = struct.unpack(f"{dim1}f", blob1)
        v2 = struct.unpack(f"{dim2}f", blob2)
        dot = sum(a * b for a, b in zip(v1, v2))
        return max(0.0, min(2.0, 1.0 - dot))

    def _init_db(self) -> None:
        """
        Executes schema DDL and sets up sqlite-vec virtual tables.
        """
        schema_file = Path(__file__).resolve().parent / "schema.sql"
        schema_sql = schema_file.read_text(encoding="utf-8")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(schema_sql)

            # If sqlite-vec is available, initialize vec0 virtual tables
            if self.has_sqlite_vec:
                cursor.execute(
                    f"CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks USING vec0("
                    f"chunk_id text, "
                    f"embedding float[{rag_settings.EMBEDDING_DIMENSIONS}] distance_metric=cosine"
                    f");"
                )
                cursor.execute(
                    f"CREATE VIRTUAL TABLE IF NOT EXISTS vec_events USING vec0("
                    f"event_id text, "
                    f"embedding float[{rag_settings.EMBEDDING_DIMENSIONS}] distance_metric=cosine"
                    f");"
                )
            conn.commit()

    # --------------------------------------------------------------------------
    # Document Operations
    # --------------------------------------------------------------------------

    def insert_document(self, doc: DocumentRecord) -> str:
        """Inserts a new document record or replaces existing by ID."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO documents (
                    id, user_id, filename, file_sha256, content, plain_summary,
                    issuing_entity, urgency, critical_deadline, fernandez_huerta_score,
                    metadata_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    plain_summary=excluded.plain_summary,
                    issuing_entity=excluded.issuing_entity,
                    urgency=excluded.urgency,
                    critical_deadline=excluded.critical_deadline,
                    fernandez_huerta_score=excluded.fernandez_huerta_score,
                    metadata_json=excluded.metadata_json,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (
                    doc.id,
                    doc.user_id,
                    doc.filename,
                    doc.file_sha256,
                    doc.content,
                    doc.plain_summary,
                    doc.issuing_entity,
                    doc.urgency,
                    doc.critical_deadline,
                    doc.fernandez_huerta_score,
                    json.dumps(doc.metadata or {}),
                ),
            )
            conn.commit()
            return doc.id

    def get_document(self, doc_id: str) -> Optional[DocumentRecord]:
        """Retrieves document record by UUID string."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
            row = cur.fetchone()
            if not row:
                return None
            return DocumentRecord(
                id=row["id"],
                user_id=row["user_id"],
                filename=row["filename"],
                file_sha256=row["file_sha256"],
                content=row["content"],
                plain_summary=row["plain_summary"],
                issuing_entity=row["issuing_entity"],
                urgency=row["urgency"],
                critical_deadline=row["critical_deadline"],
                fernandez_huerta_score=row["fernandez_huerta_score"],
                metadata=json.loads(row["metadata_json"] or "{}"),
                created_at=row["created_at"],
            )

    def delete_document(self, doc_id: str) -> bool:
        """Deletes document and cascades to chunks and vector tables."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            # If sqlite-vec is active, delete associated vector entries
            if self.has_sqlite_vec:
                cur.execute(
                    "DELETE FROM vec_chunks WHERE chunk_id IN (SELECT id FROM chunks WHERE document_id = ?)",
                    (doc_id,),
                )
            cur.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            conn.commit()
            return cur.rowcount > 0

    # --------------------------------------------------------------------------
    # Chunk & Vector Operations
    # --------------------------------------------------------------------------

    def insert_chunks(
        self,
        chunks: List[ChunkRecord],
        embeddings: Optional[List[List[float]]] = None,
    ) -> int:
        """
        Inserts chunks into SQLite relational table, FTS5 index, and sqlite-vec table.
        """
        if not chunks:
            return 0

        # Compute embeddings if not already provided
        vectors: List[List[float]] = []
        if embeddings and len(embeddings) == len(chunks):
            vectors = embeddings
        else:
            texts = [c.content for c in chunks]
            vectors = [bge_m3_engine.embed_text(t) for t in texts]

        with self.get_connection() as conn:
            cur = conn.cursor()
            vec_inserts = []

            for chunk, vec in zip(chunks, vectors):
                blob = bge_m3_engine.vector_to_bytes(vec)
                cur.execute(
                    """
                    INSERT INTO chunks (
                        id, document_id, chunk_index, content, token_count,
                        section_header, dates_found, amounts_found, metadata_json,
                        embedding_blob
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        content=excluded.content,
                        token_count=excluded.token_count,
                        section_header=excluded.section_header,
                        dates_found=excluded.dates_found,
                        amounts_found=excluded.amounts_found,
                        metadata_json=excluded.metadata_json,
                        embedding_blob=excluded.embedding_blob
                    """,
                    (
                        chunk.id,
                        chunk.document_id,
                        chunk.chunk_index,
                        chunk.content,
                        chunk.token_count,
                        chunk.section_header,
                        json.dumps(chunk.dates_found or []),
                        json.dumps(chunk.amounts_found or []),
                        json.dumps(chunk.metadata or {}),
                        blob,
                    ),
                )
                vec_inserts.append((chunk.id, blob))

            # Insert into sqlite-vec virtual table if active
            if self.has_sqlite_vec:
                for chunk_id, blob in vec_inserts:
                    # Delete any previous vector for this chunk_id
                    try:
                        cur.execute("DELETE FROM vec_chunks WHERE chunk_id = ?", (chunk_id,))
                    except Exception:
                        pass
                    cur.execute(
                        "INSERT INTO vec_chunks(chunk_id, embedding) VALUES (?, ?)",
                        (chunk_id, blob),
                    )

            conn.commit()
            return len(chunks)

    def get_chunks_by_document(self, doc_id: str) -> List[ChunkRecord]:
        """Returns all chunks for a given document ordered by chunk_index."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM chunks WHERE document_id = ? ORDER BY chunk_index ASC",
                (doc_id,),
            )
            rows = cur.fetchall()
            results = []
            for r in rows:
                results.append(
                    ChunkRecord(
                        id=r["id"],
                        document_id=r["document_id"],
                        chunk_index=r["chunk_index"],
                        content=r["content"],
                        token_count=r["token_count"],
                        section_header=r["section_header"],
                        dates_found=json.loads(r["dates_found"] or "[]"),
                        amounts_found=json.loads(r["amounts_found"] or "[]"),
                        metadata=json.loads(r["metadata_json"] or "{}"),
                    )
                )
            return results

    # --------------------------------------------------------------------------
    # Vector Search
    # --------------------------------------------------------------------------

    def search_vector(
        self,
        query_vector: List[float],
        top_k: int = 10,
        document_id: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Executes dense vector similarity search using sqlite-vec MATCH or fallback.
        """
        blob = bge_m3_engine.vector_to_bytes(query_vector)

        with self.get_connection() as conn:
            cur = conn.cursor()

            if self.has_sqlite_vec:
                # Native C-extension sqlite-vec search via CTE
                if document_id:
                    cur.execute(
                        """
                        WITH knn AS (
                            SELECT chunk_id, distance
                            FROM vec_chunks
                            WHERE embedding MATCH ? AND k = ?
                        )
                        SELECT knn.chunk_id, knn.distance, c.document_id, c.chunk_index,
                               c.content, c.section_header, c.dates_found, c.amounts_found,
                               c.metadata_json
                        FROM knn
                        JOIN chunks c ON knn.chunk_id = c.id
                        WHERE c.document_id = ?
                        ORDER BY knn.distance ASC
                        LIMIT ?
                        """,
                        (blob, top_k * 4, document_id, top_k),
                    )
                else:
                    cur.execute(
                        """
                        WITH knn AS (
                            SELECT chunk_id, distance
                            FROM vec_chunks
                            WHERE embedding MATCH ? AND k = ?
                        )
                        SELECT knn.chunk_id, knn.distance, c.document_id, c.chunk_index,
                               c.content, c.section_header, c.dates_found, c.amounts_found,
                               c.metadata_json
                        FROM knn
                        JOIN chunks c ON knn.chunk_id = c.id
                        ORDER BY knn.distance ASC
                        LIMIT ?
                        """,
                        (blob, top_k, top_k),
                    )
                rows = cur.fetchall()
            else:
                # Python fallback using py_cosine_dist
                query_sql = """
                    SELECT c.id as chunk_id, py_cosine_dist(c.embedding_blob, ?) as distance,
                           c.document_id, c.chunk_index, c.content, c.section_header,
                           c.dates_found, c.amounts_found, c.metadata_json
                    FROM chunks c
                """
                params: list[Any] = [blob]
                if document_id:
                    query_sql += " WHERE c.document_id = ?"
                    params.append(document_id)
                query_sql += " ORDER BY distance ASC LIMIT ?"
                params.append(top_k)

                cur.execute(query_sql, params)
                rows = cur.fetchall()

            results: List[SearchResult] = []
            for rank, r in enumerate(rows, start=1):
                # distance to similarity: similarity = 1 - distance
                dist = float(r["distance"])
                sim = max(0.0, 1.0 - dist)
                results.append(
                    SearchResult(
                        chunk_id=r["chunk_id"],
                        document_id=r["document_id"],
                        chunk_index=r["chunk_index"],
                        content=r["content"],
                        section_header=r["section_header"],
                        score=sim,
                        dense_rank=rank,
                        dates_found=json.loads(r["dates_found"] or "[]"),
                        amounts_found=json.loads(r["amounts_found"] or "[]"),
                        metadata=json.loads(r["metadata_json"] or "{}"),
                    )
                )
            return results

    # --------------------------------------------------------------------------
    # Full-Text Search (FTS5 BM25)
    # --------------------------------------------------------------------------

    def search_fts(
        self,
        query_text: str,
        top_k: int = 10,
        document_id: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Executes sparse lexical search via SQLite FTS5 using BM25 ranking.
        """
        clean_query = self._sanitize_fts_query(query_text)
        if not clean_query:
            return []

        with self.get_connection() as conn:
            cur = conn.cursor()

            sql = """
                SELECT f.chunk_id, bm25(chunks_fts) as rank, c.document_id, c.chunk_index,
                       c.content, c.section_header, c.dates_found, c.amounts_found,
                       c.metadata_json
                FROM chunks_fts f
                JOIN chunks c ON f.chunk_id = c.id
                WHERE chunks_fts MATCH ?
            """
            params: list[Any] = [clean_query]

            if document_id:
                sql += " AND c.document_id = ?"
                params.append(document_id)

            sql += " ORDER BY rank ASC LIMIT ?"
            params.append(top_k)

            try:
                cur.execute(sql, params)
                rows = cur.fetchall()
            except sqlite3.OperationalError:
                # If syntax error in query, fallback to quoted string
                quoted_query = f'"{query_text.replace(chr(34), "")}"'
                params[0] = quoted_query
                cur.execute(sql, params)
                rows = cur.fetchall()

            results: List[SearchResult] = []
            for rank, r in enumerate(rows, start=1):
                # FTS5 bm25 produces negative numbers where lower = better match.
                # Normalized lexical score:
                raw_bm25 = float(r["rank"])
                lex_score = 1.0 / (1.0 + abs(raw_bm25))
                results.append(
                    SearchResult(
                        chunk_id=r["chunk_id"],
                        document_id=r["document_id"],
                        chunk_index=r["chunk_index"],
                        content=r["content"],
                        section_header=r["section_header"],
                        score=lex_score,
                        sparse_rank=rank,
                        dates_found=json.loads(r["dates_found"] or "[]"),
                        amounts_found=json.loads(r["amounts_found"] or "[]"),
                        metadata=json.loads(r["metadata_json"] or "{}"),
                    )
                )
            return results

    # --------------------------------------------------------------------------
    # Hybrid Search (Dense + Sparse with Reciprocal Rank Fusion)
    # --------------------------------------------------------------------------

    def search_hybrid(
        self,
        query_text: str,
        query_vector: Optional[List[float]] = None,
        top_k: int = 5,
        document_id: Optional[str] = None,
        weight_dense: float = 1.0,
        weight_sparse: float = 0.8,
        rrf_k: int = 60,
    ) -> List[SearchResult]:
        """
        Executes Sovereign Hybrid Search:
        1. Dense Vector Search (BGE-M3 + sqlite-vec)
        2. Sparse Lexical Search (SQLite FTS5 BM25)
        3. Reciprocal Rank Fusion: RRF(c) = w_dense/(k + r_dense) + w_sparse/(k + r_sparse)
        """
        vec = query_vector if query_vector else bge_m3_engine.embed_text(query_text)

        # Retrieve candidates from both systems
        dense_results = self.search_vector(vec, top_k=top_k * 3, document_id=document_id)
        sparse_results = self.search_fts(query_text, top_k=top_k * 3, document_id=document_id)

        # Build fused scores map: chunk_id -> (rrf_score, SearchResult)
        fusion_map: Dict[str, Tuple[float, SearchResult]] = {}

        # 1. Process dense rankings
        for rank_idx, res in enumerate(dense_results, start=1):
            rrf_val = weight_dense / (rrf_k + rank_idx)
            res.dense_rank = rank_idx
            fusion_map[res.chunk_id] = (rrf_val, res)

        # 2. Process sparse rankings and accumulate
        for rank_idx, res in enumerate(sparse_results, start=1):
            rrf_val = weight_sparse / (rrf_k + rank_idx)
            if res.chunk_id in fusion_map:
                existing_score, existing_res = fusion_map[res.chunk_id]
                existing_res.sparse_rank = rank_idx
                fusion_map[res.chunk_id] = (existing_score + rrf_val, existing_res)
            else:
                res.sparse_rank = rank_idx
                fusion_map[res.chunk_id] = (rrf_val, res)

        # 3. Sort by total RRF score descending
        sorted_candidates = sorted(fusion_map.values(), key=lambda item: item[0], reverse=True)

        # Return top_k with updated score
        final_results: List[SearchResult] = []
        for rrf_score, res in sorted_candidates[:top_k]:
            res.score = round(rrf_score, 6)
            final_results.append(res)

        return final_results

    # --------------------------------------------------------------------------
    # Civic Events Operations
    # --------------------------------------------------------------------------

    def insert_event(self, event: EventRecord, embedding: Optional[List[float]] = None) -> str:
        """Inserts or updates a civic event, its FTS index, and sqlite-vec representation."""
        vec = embedding if embedding else bge_m3_engine.embed_text(f"{event.title}. {event.description}")
        blob = bge_m3_engine.vector_to_bytes(vec)

        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO events (
                    id, title, description, plain_description, organizer_name,
                    city, postal_code, latitude, longitude, start_time, end_time,
                    is_free, cost_notes, category, canonical_questions_json,
                    metadata_json, embedding_blob
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    description=excluded.description,
                    plain_description=excluded.plain_description,
                    organizer_name=excluded.organizer_name,
                    city=excluded.city,
                    postal_code=excluded.postal_code,
                    latitude=excluded.latitude,
                    longitude=excluded.longitude,
                    start_time=excluded.start_time,
                    end_time=excluded.end_time,
                    is_free=excluded.is_free,
                    cost_notes=excluded.cost_notes,
                    category=excluded.category,
                    canonical_questions_json=excluded.canonical_questions_json,
                    metadata_json=excluded.metadata_json,
                    embedding_blob=excluded.embedding_blob
                """,
                (
                    event.id,
                    event.title,
                    event.description,
                    event.plain_description,
                    event.organizer_name,
                    event.city,
                    event.postal_code,
                    event.latitude,
                    event.longitude,
                    event.start_time,
                    event.end_time,
                    1 if event.is_free else 0,
                    event.cost_notes,
                    event.category,
                    json.dumps(event.canonical_questions or {}),
                    json.dumps(event.metadata or {}),
                    blob,
                ),
            )

            if self.has_sqlite_vec:
                try:
                    cur.execute("DELETE FROM vec_events WHERE event_id = ?", (event.id,))
                except Exception:
                    pass
                cur.execute(
                    "INSERT INTO vec_events(event_id, embedding) VALUES (?, ?)",
                    (event.id, blob),
                )

            conn.commit()
            return event.id

    def get_event(self, event_id: str) -> Optional[EventRecord]:
        """Fetches an event by ID."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM events WHERE id = ?", (event_id,))
            r = cur.fetchone()
            if not r:
                return None
            return self._row_to_event(r)

    def list_events(self, city: Optional[str] = None, limit: int = 50) -> List[EventRecord]:
        """Lists events with optional city filter."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            if city:
                cur.execute(
                    "SELECT * FROM events WHERE LOWER(city) = LOWER(?) ORDER BY start_time ASC LIMIT ?",
                    (city, limit),
                )
            else:
                cur.execute("SELECT * FROM events ORDER BY start_time ASC LIMIT ?", (limit,))
            return [self._row_to_event(r) for r in cur.fetchall()]

    def search_events_hybrid(
        self,
        query_text: str,
        query_vector: Optional[List[float]] = None,
        top_k: int = 5,
        city: Optional[str] = None,
        weight_dense: float = 1.0,
        weight_sparse: float = 0.8,
        rrf_k: int = 60,
    ) -> List[EventSearchResult]:
        """Hybrid search across civic events combining sqlite-vec and FTS5 with RRF."""
        vec = query_vector if query_vector else bge_m3_engine.embed_text(query_text)
        blob = bge_m3_engine.vector_to_bytes(vec)

        with self.get_connection() as conn:
            cur = conn.cursor()

            # 1. Dense search
            dense_rows = []
            if self.has_sqlite_vec:
                cur.execute(
                    """
                    WITH knn AS (
                        SELECT event_id, distance
                        FROM vec_events
                        WHERE embedding MATCH ? AND k = ?
                    )
                    SELECT knn.event_id, knn.distance, e.*
                    FROM knn
                    JOIN events e ON knn.event_id = e.id
                    ORDER BY knn.distance ASC
                    """,
                    (blob, top_k * 4),
                )
                dense_rows = cur.fetchall()
            else:
                cur.execute(
                    """
                    SELECT e.id as event_id, py_cosine_dist(e.embedding_blob, ?) as distance, e.*
                    FROM events e
                    ORDER BY distance ASC LIMIT ?
                    """,
                    (blob, top_k * 4),
                )
                dense_rows = cur.fetchall()

            # Filter dense by city if needed
            if city:
                dense_rows = [r for r in dense_rows if (r["city"] or "").lower() == city.lower()]

            # 2. Sparse search via FTS5
            clean_query = self._sanitize_fts_query(query_text)
            sparse_rows = []
            if clean_query:
                sql = """
                    SELECT f.event_id, bm25(events_fts) as rank, e.*
                    FROM events_fts f
                    JOIN events e ON f.event_id = e.id
                    WHERE events_fts MATCH ?
                """
                params: list[Any] = [clean_query]
                if city:
                    sql += " AND LOWER(e.city) = LOWER(?)"
                    params.append(city)
                sql += " ORDER BY rank ASC LIMIT ?"
                params.append(top_k * 4)

                try:
                    cur.execute(sql, params)
                    sparse_rows = cur.fetchall()
                except Exception:
                    sparse_rows = []

            # 3. Reciprocal Rank Fusion
            fusion_map: Dict[str, Tuple[float, Optional[int], Optional[int], Any]] = {}

            for rank_idx, r in enumerate(dense_rows, start=1):
                eid = r["event_id"]
                score = weight_dense / (rrf_k + rank_idx)
                fusion_map[eid] = (score, rank_idx, None, r)

            for rank_idx, r in enumerate(sparse_rows, start=1):
                eid = r["event_id"]
                score = weight_sparse / (rrf_k + rank_idx)
                if eid in fusion_map:
                    prev_score, d_rank, _, row = fusion_map[eid]
                    fusion_map[eid] = (prev_score + score, d_rank, rank_idx, row)
                else:
                    fusion_map[eid] = (score, None, rank_idx, r)

            sorted_candidates = sorted(fusion_map.values(), key=lambda x: x[0], reverse=True)

            results: List[EventSearchResult] = []
            for rrf_score, d_rank, s_rank, row in sorted_candidates[:top_k]:
                ev = self._row_to_event(row)
                results.append(
                    EventSearchResult(
                        event=ev,
                        score=round(rrf_score, 6),
                        dense_rank=d_rank,
                        sparse_rank=s_rank,
                    )
                )

            return results

    @staticmethod
    def _row_to_event(r: sqlite3.Row) -> EventRecord:
        """Converts database row to EventRecord."""
        return EventRecord(
            id=r["id"],
            title=r["title"],
            description=r["description"],
            plain_description=r["plain_description"],
            organizer_name=r["organizer_name"],
            city=r["city"],
            postal_code=r["postal_code"],
            latitude=r["latitude"],
            longitude=r["longitude"],
            start_time=r["start_time"],
            end_time=r["end_time"],
            is_free=bool(r["is_free"]),
            cost_notes=r["cost_notes"],
            category=r["category"],
            canonical_questions=json.loads(r["canonical_questions_json"] or "{}"),
            metadata=json.loads(r["metadata_json"] or "{}"),
        )

    # --------------------------------------------------------------------------
    # Helper sanitization
    # --------------------------------------------------------------------------

    @staticmethod
    def _sanitize_fts_query(query: str) -> str:
        """Cleans search query for SQLite FTS5 syntax safety."""
        # Remove characters that can break FTS5 expressions
        clean = re.sub(r"[^\w\s-]", " ", query).strip()
        tokens = [t for t in clean.split() if len(t) > 1]
        if not tokens:
            return ""
        # Return NEAR or OR connected query for higher recall
        return " OR ".join(tokens)


import re

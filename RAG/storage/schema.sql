-- ==============================================================================
-- CLEARLY — Sovereign SQLite Schema
-- Compliant with Local-First Sovereignty, Zero-Egress Privacy, and sqlite-vec
-- ==============================================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

-- 1. Documents Table
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    filename TEXT NOT NULL,
    file_sha256 TEXT NOT NULL,
    content TEXT NOT NULL,
    plain_summary TEXT,
    issuing_entity TEXT,
    urgency TEXT DEFAULT 'NORMAL',
    critical_deadline TEXT,
    fernandez_huerta_score REAL,
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_docs_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_docs_deadline ON documents(critical_deadline);
CREATE INDEX IF NOT EXISTS idx_docs_sha256 ON documents(file_sha256);

-- 2. Chunks Table (relational representation with embedded blob)
CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    section_header TEXT,
    dates_found TEXT DEFAULT '[]',
    amounts_found TEXT DEFAULT '[]',
    metadata_json TEXT DEFAULT '{}',
    embedding_blob BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_index ON chunks(document_id, chunk_index);

-- 3. Full-Text Search (FTS5) for Chunks
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    chunk_id UNINDEXED,
    document_id UNINDEXED,
    content,
    section_header,
    tokenize = 'porter unicode61'
);

-- 4. Civic Events Table (Local Community Cache)
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    plain_description TEXT,
    organizer_name TEXT,
    city TEXT NOT NULL,
    postal_code TEXT,
    latitude REAL,
    longitude REAL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    is_free INTEGER DEFAULT 1,
    cost_notes TEXT,
    category TEXT,
    canonical_questions_json TEXT DEFAULT '{}',
    metadata_json TEXT DEFAULT '{}',
    embedding_blob BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_events_city ON events(city);
CREATE INDEX IF NOT EXISTS idx_events_start ON events(start_time);
CREATE INDEX IF NOT EXISTS idx_events_postal ON events(postal_code);

-- 5. Full-Text Search (FTS5) for Civic Events
CREATE VIRTUAL TABLE IF NOT EXISTS events_fts USING fts5(
    event_id UNINDEXED,
    title,
    description,
    organizer_name,
    city,
    category,
    tokenize = 'porter unicode61'
);

-- 6. Trigger to keep FTS5 synchronized on chunk insert/delete
CREATE TRIGGER IF NOT EXISTS trg_chunks_insert AFTER INSERT ON chunks BEGIN
    INSERT INTO chunks_fts(chunk_id, document_id, content, section_header)
    VALUES (new.id, new.document_id, new.content, new.section_header);
END;

CREATE TRIGGER IF NOT EXISTS trg_chunks_delete AFTER DELETE ON chunks BEGIN
    DELETE FROM chunks_fts WHERE chunk_id = old.id;
END;

-- 7. Trigger to keep FTS5 synchronized on event insert/delete
CREATE TRIGGER IF NOT EXISTS trg_events_insert AFTER INSERT ON events BEGIN
    INSERT INTO events_fts(event_id, title, description, organizer_name, city, category)
    VALUES (new.id, new.title, new.description, new.organizer_name, new.city, new.category);
END;

CREATE TRIGGER IF NOT EXISTS trg_events_delete AFTER DELETE ON events BEGIN
    DELETE FROM events_fts WHERE event_id = old.id;
END;


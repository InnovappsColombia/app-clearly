-- ==============================================================================
-- CLEARLY — Migration 001: Initial Schema
-- ==============================================================================

-- 1. Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 2. Enumeraciones del Sistema
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('senior', 'tutor', 'expert', 'admin');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE doc_urgency AS ENUM ('low', 'medium', 'high', 'critical');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE event_source AS ENUM ('eventbrite', 'luma', 'civic_library', 'manual');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE booking_status AS ENUM ('pending', 'confirmed', 'in_progress', 'completed', 'disputed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE service_modality AS ENUM ('virtual', 'in_person');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE notification_channel AS ENUM ('in_app', 'whatsapp', 'push', 'sms');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 3. Tabla de Usuarios
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    role user_role NOT NULL DEFAULT 'senior',
    preferred_language VARCHAR(10) NOT NULL DEFAULT 'es',
    accessibility_settings JSONB DEFAULT '{
        "font_scale": 1.25,
        "high_contrast": false,
        "audio_speed": 1.0,
        "auto_read_aloud": true
    }'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Tabla de Vínculos de Tutoría (Consentimiento Granular y Duress PIN)
CREATE TABLE IF NOT EXISTS tutor_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    senior_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tutor_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pairing_code_hash VARCHAR(128),
    duress_pin_hash VARCHAR(128),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    permissions JSONB NOT NULL DEFAULT '{
        "can_view_critical_alerts": true,
        "can_view_documents": true,
        "can_view_events": true,
        "can_hire_experts": true
    }'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at TIMESTAMPTZ,
    CONSTRAINT unique_senior_tutor_pair UNIQUE(senior_id, tutor_id)
);

-- 5. Tabla de Documentos Procesados (OCR + Plain Language Engine)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    storage_path VARCHAR(512) NOT NULL,
    file_sha256 VARCHAR(64) NOT NULL,
    original_extracted_text TEXT,
    plain_summary TEXT NOT NULL,
    issuing_entity VARCHAR(200),
    urgency doc_urgency NOT NULL DEFAULT 'medium',
    critical_deadline DATE,
    fernandez_huerta_score NUMERIC(5, 2),
    ambiguities JSONB DEFAULT '[]'::jsonb,
    recommended_questions JSONB DEFAULT '[]'::jsonb,
    requires_human_expert BOOLEAN NOT NULL DEFAULT FALSE,
    embedding vector(1024),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Tabla de Checklists y Acciones Documentales
CREATE TABLE IF NOT EXISTS document_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    task_description TEXT NOT NULL,
    required_document VARCHAR(255),
    deadline DATE,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_by_user_id UUID REFERENCES users(id),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. Tabla del Marketplace de Eventos Comunitarios ("Made Clear")
CREATE TABLE IF NOT EXISTS community_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id VARCHAR(255),
    source event_source NOT NULL DEFAULT 'civic_library',
    raw_title VARCHAR(300) NOT NULL,
    made_clear_what TEXT NOT NULL,
    made_clear_when_where TEXT NOT NULL,
    made_clear_cost TEXT NOT NULL,
    made_clear_how_to_register TEXT NOT NULL,
    event_url VARCHAR(512),
    audio_summary_path VARCHAR(512),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    venue_name VARCHAR(255),
    venue_address TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    is_wheelchair_accessible BOOLEAN NOT NULL DEFAULT TRUE,
    is_senior_friendly BOOLEAN NOT NULL DEFAULT TRUE,
    is_free BOOLEAN NOT NULL DEFAULT TRUE,
    supported_languages VARCHAR(10)[] DEFAULT ARRAY['es', 'en'],
    embedding vector(1024),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 8. Tabla de Profesionales Verificados (CLEARLY Premium)
CREATE TABLE IF NOT EXISTS expert_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    specialty VARCHAR(100) NOT NULL,
    license_number VARCHAR(100) NOT NULL,
    id_verification_status VARCHAR(50) NOT NULL DEFAULT 'verified',
    hourly_rate_cents INTEGER NOT NULL DEFAULT 4500,
    bio_plain_text TEXT NOT NULL,
    languages_spoken VARCHAR(10)[] NOT NULL DEFAULT ARRAY['es', 'en'],
    service_modalities service_modality[] NOT NULL DEFAULT ARRAY['virtual'::service_modality],
    average_rating NUMERIC(3, 2) DEFAULT 5.00,
    total_reviews INTEGER NOT NULL DEFAULT 0,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 9. Tabla de Contrataciones Premium (Bookings con Escrow)
CREATE TABLE IF NOT EXISTS premium_bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_senior_id UUID NOT NULL REFERENCES users(id),
    requested_by_user_id UUID NOT NULL REFERENCES users(id),
    expert_id UUID NOT NULL REFERENCES expert_profiles(id),
    document_id UUID REFERENCES documents(id),
    modality service_modality NOT NULL DEFAULT 'virtual',
    scheduled_start TIMESTAMPTZ NOT NULL,
    scheduled_end TIMESTAMPTZ NOT NULL,
    livekit_room_name VARCHAR(128),
    status booking_status NOT NULL DEFAULT 'pending',
    stripe_payment_intent_id VARCHAR(255),
    amount_cents INTEGER NOT NULL,
    expert_payout_cents INTEGER NOT NULL,
    client_review_rating SMALLINT CHECK (client_review_rating BETWEEN 1 AND 5),
    client_review_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 10. Tabla de Notificaciones del Sistema
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    channel notification_channel NOT NULL DEFAULT 'in_app',
    is_urgent BOOLEAN NOT NULL DEFAULT FALSE,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_tutor_active ON tutor_relationships(senior_id, tutor_id) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_docs_user ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_docs_deadline ON documents(critical_deadline) WHERE critical_deadline IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_docs_embedding ON documents USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_actions_doc ON document_actions(document_id);
CREATE INDEX IF NOT EXISTS idx_actions_completed ON document_actions(document_id, is_completed);
CREATE INDEX IF NOT EXISTS idx_events_start ON community_events(start_time);
CREATE INDEX IF NOT EXISTS idx_events_embedding ON community_events USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_events_accessible ON community_events(is_wheelchair_accessible, is_senior_friendly, is_free);
CREATE INDEX IF NOT EXISTS idx_expert_specialty ON expert_profiles(specialty, is_available);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON premium_bookings(status);
CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id) WHERE is_read = FALSE;

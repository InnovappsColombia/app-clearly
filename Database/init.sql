-- ==============================================================================
-- CLEARLY — Database Initialization Script
-- PostgreSQL 16 + pgvector Schema & Seed Data
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
    duress_pin_hash VARCHAR(128), -- PIN de coacción para desvinculación silenciosa
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
    storage_path VARCHAR(512) NOT NULL, -- Ruta en MinIO S3
    file_sha256 VARCHAR(64) NOT NULL,
    original_extracted_text TEXT,
    plain_summary TEXT NOT NULL,
    issuing_entity VARCHAR(200),
    urgency doc_urgency NOT NULL DEFAULT 'medium',
    critical_deadline DATE,
    fernandez_huerta_score NUMERIC(5, 2), -- Auditoría sintáctica (FH >= 80)
    ambiguities JSONB DEFAULT '[]'::jsonb,
    recommended_questions JSONB DEFAULT '[]'::jsonb,
    requires_human_expert BOOLEAN NOT NULL DEFAULT FALSE,
    embedding vector(1024), -- Embeddings BGE-M3 (1024 dimensiones)
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
    audio_summary_path VARCHAR(512), -- Ruta audio Piper TTS en MinIO
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
    embedding vector(1024), -- Embeddings BGE-M3 para búsqueda semántica HNSW
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 8. Tabla de Profesionales Verificados (CLEARLY Premium)
CREATE TABLE IF NOT EXISTS expert_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    specialty VARCHAR(100) NOT NULL, -- ej. 'Consultor de Inmigración', 'Trabajador Social'
    license_number VARCHAR(100) NOT NULL,
    id_verification_status VARCHAR(50) NOT NULL DEFAULT 'verified',
    hourly_rate_cents INTEGER NOT NULL DEFAULT 4500, -- en centavos: $45.00 USD
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

-- ==============================================================================
-- ÍNDICES DE RENDIMIENTO Y BÚSQUEDA VECTORIAL
-- ==============================================================================
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

-- ==============================================================================
-- SEED DATA (Datos Demo Iniciales para Prototipado y Pruebas)
-- ==============================================================================

-- 1. Usuarios de Prueba: Senior (Elena), Tutor (Carlos), Experto (David), Senior 2 (Rosa)
INSERT INTO users (id, phone_number, email, full_name, role, preferred_language, accessibility_settings)
VALUES 
    (
        '11111111-1111-1111-1111-111111111111', 
        '+19055550101', 
        'elena.pabla@clearly.example', 
        'Elena Pabla', 
        'senior', 
        'es', 
        '{"font_scale": 1.5, "high_contrast": true, "audio_speed": 0.85, "auto_read_aloud": true}'::jsonb
    ),
    (
        '22222222-2222-2222-2222-222222222222', 
        '+19055550202', 
        'carlos.pabla@clearly.example', 
        'Carlos Pabla', 
        'tutor', 
        'es', 
        '{"font_scale": 1.0, "high_contrast": false, "audio_speed": 1.0, "auto_read_aloud": false}'::jsonb
    ),
    (
        '33333333-3333-3333-3333-333333333333', 
        '+19055550303', 
        'david.mendoza@clearly.example', 
        'David Mendoza, RCIC', 
        'expert', 
        'es', 
        '{"font_scale": 1.0, "high_contrast": false, "audio_speed": 1.0, "auto_read_aloud": false}'::jsonb
    ),
    (
        '44444444-4444-4444-4444-444444444444', 
        '+19055550404', 
        'rosa.gomez@clearly.example', 
        'Rosa Gómez', 
        'senior', 
        'es', 
        '{"font_scale": 1.25, "high_contrast": false, "audio_speed": 1.0, "auto_read_aloud": true}'::jsonb
    )
ON CONFLICT (id) DO NOTHING;

-- 2. Vínculo de Tutoría: Carlos supervisa a su madre Elena
INSERT INTO tutor_relationships (id, senior_id, tutor_id, is_active, permissions)
VALUES (
    '55555555-5555-5555-5555-555555555555',
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    TRUE,
    '{
        "can_view_critical_alerts": true,
        "can_view_documents": true,
        "can_view_events": true,
        "can_hire_experts": true
    }'::jsonb
)
ON CONFLICT (id) DO NOTHING;

-- 3. Perfil de Experto Verificado: David Mendoza (Consultor de Inmigración)
INSERT INTO expert_profiles (
    id, user_id, specialty, license_number, id_verification_status, hourly_rate_cents, 
    bio_plain_text, languages_spoken, service_modalities, average_rating, total_reviews
)
VALUES (
    '66666666-6666-6666-6666-666666666666',
    '33333333-3333-3333-3333-333333333333',
    'Consultor Regulado de Inmigración Canadiense (RCIC)',
    'R708912-CICC',
    'verified',
    4500,
    'Especialista con 12 años guiando a adultos mayores y familias hispanas en trámites de residencia, renovación de tarjetas y apelaciones burocráticas.',
    ARRAY['es', 'en'],
    ARRAY['virtual'::service_modality, 'in_person'::service_modality],
    4.95,
    38
)
ON CONFLICT (id) DO NOTHING;

-- 4. Eventos Comunitarios Reales en Brampton/GTA bajo formato "Made Clear"
INSERT INTO community_events (
    id, source, raw_title, 
    made_clear_what, made_clear_when_where, made_clear_cost, made_clear_how_to_register, 
    start_time, end_time, venue_name, venue_address, latitude, longitude, 
    is_wheelchair_accessible, is_senior_friendly, is_free, supported_languages
)
VALUES 
    (
        '77777777-7777-7777-7777-777777777771',
        'civic_library',
        'Gentle Chair Yoga & Senior Balance Workshop',
        'Una clase suave de estiramiento y respiración sentado en silla, ideal para mejorar el equilibrio y relajarse sin forzar las articulaciones.',
        'Sábado 21 de Noviembre de 10:30 AM a 11:30 AM. En la Biblioteca Central de Brampton (65 Queen St E). Parada de autobús Brampton Transit Ruta 1 a media cuadra.',
        'GRATUITO (Cero costo, financiado por la ciudad).',
        'Entrada libre. Puedes llegar 10 minutos antes o mostrar tu código de reserva de CLEARLY en el mostrador.',
        NOW() + INTERVAL '5 days',
        NOW() + INTERVAL '5 days 1 hour',
        'Brampton Library - Central Branch',
        '65 Queen St E, Brampton, ON L6W 3L6',
        43.6872,
        -79.7599,
        TRUE,
        TRUE,
        TRUE,
        ARRAY['es', 'en']
    ),
    (
        '77777777-7777-7777-7777-777777777772',
        'civic_library',
        'Café Tecnológico: Aprende a Usar WhatsApp y la Tableta sin Miedo',
        'Un taller paciente donde voluntarios jóvenes te enseñan a hacer videollamadas con tu familia, agrandar la letra del teléfono y cuidarte de estafas por mensaje.',
        'Miércoles 25 de Noviembre de 2:00 PM a 3:30 PM. En el Centro Comunitario Chinguacousy Park.',
        'GRATUITO (Incluye café y té sin costo).',
        'Registro fácil: presiona el botón "Asistir" en CLEARLY o llama al 311 indicando tu nombre.',
        NOW() + INTERVAL '9 days',
        NOW() + INTERVAL '9 days 90 minutes',
        'Chinguacousy Park Community Centre',
        '9050 Bramalea Rd, Brampton, ON L6S 6G7',
        43.7225,
        -79.7212,
        TRUE,
        TRUE,
        TRUE,
        ARRAY['es', 'en', 'pa']
    ),
    (
        '77777777-7777-7777-7777-777777777773',
        'civic_library',
        'Clínica Comunitaria Gratuita de Vacunación contra la Gripe y Chequeo de Presión',
        'Enfermeras comunitarias revisarán tu presión arterial, responderán dudas sobre tus medicamentos y aplicarán la vacuna estacional de la gripe sin filas largas.',
        'Viernes 27 de Noviembre de 9:00 AM a 1:00 PM. Centro Cívico Flower City.',
        'GRATUITO (Presentar tarjeta de salud OHIP o identificación local).',
        'Atención por orden de llegada con asientos cómodos reservados para personas con movilidad reducida.',
        NOW() + INTERVAL '11 days',
        NOW() + INTERVAL '11 days 4 hours',
        'Flower City Seniors Recreation Centre',
        '8870 McLaughlin Rd S, Brampton, ON L6Y 5T1',
        43.6644,
        -79.7428,
        TRUE,
        TRUE,
        TRUE,
        ARRAY['es', 'en']
    )
ON CONFLICT (id) DO NOTHING;

-- 5. Documento Pre-Procesado de Ejemplo (Carta IRCC con Alerta de Fecha Crítica)
INSERT INTO documents (
    id, user_id, storage_path, file_sha256, original_extracted_text, 
    plain_summary, issuing_entity, urgency, critical_deadline, fernandez_huerta_score, 
    ambiguities, recommended_questions, requires_human_expert
)
VALUES (
    '88888888-8888-8888-8888-888888888888',
    '11111111-1111-1111-1111-111111111111',
    'clearly-documents/elena-ircc-procedural-fairness.pdf',
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    'Immigration, Refugees and Citizenship Canada (IRCC). Notice of Procedural Fairness regarding your permanent resident card renewal. You have 30 calendar days from the date of this letter to submit proof of physical presence in Canada. Failure to provide requested documentation may result in the refusal of your application.',
    'El gobierno de inmigración (IRCC) necesita verificar tus días de estadía en Canadá para entregarte tu nueva tarjeta de residente. Tienes un plazo estricto de 30 días para enviar tus pasaportes y boletos de viaje. Si no respondes a tiempo, cancelarán tu solicitud.',
    'Immigration, Refugees and Citizenship Canada (IRCC)',
    'critical',
    CURRENT_DATE + INTERVAL '14 days',
    82.5,
    '["La carta no especifica si las copias del pasaporte deben estar notarizadas o solo escaneadas a color."]'::jsonb,
    '["¿Puedo enviar copias digitales a través de la cuenta en línea de IRCC?", "¿Aceptan registros médicos como prueba de estadía física?"]'::jsonb,
    TRUE
)
ON CONFLICT (id) DO NOTHING;

-- 6. Checklist de Acciones Vinculadas al Documento
INSERT INTO document_actions (id, document_id, task_description, required_document, deadline, is_completed)
VALUES 
    (
        '99999999-9999-9999-9999-999999999991',
        '88888888-8888-8888-8888-888888888888',
        'Juntar todos los pasaportes vigentes y vencidos de los últimos 5 años.',
        'Pasaportes físicos originales o copias legibles de todas las páginas con sellos',
        CURRENT_DATE + INTERVAL '5 days',
        TRUE
    ),
    (
        '99999999-9999-9999-9999-999999999992',
        '88888888-8888-8888-8888-888888888888',
        'Pedir al banco los estados de cuenta de los últimos 2 años que demuestran compras locales.',
        'Estados de cuenta bancarios en PDF o membrete bancario',
        CURRENT_DATE + INTERVAL '10 days',
        FALSE
    ),
    (
        '99999999-9999-9999-9999-999999999993',
        '88888888-8888-8888-8888-888888888888',
        'Revisar el expediente con David Mendoza (Consultor Premium) antes de subirlo al portal web.',
        'Expediente completo pre-armado',
        CURRENT_DATE + INTERVAL '12 days',
        FALSE
    )
ON CONFLICT (id) DO NOTHING;

-- 7. Notificación Automática al Tutor (Carlos) sobre la Fecha Límite de Elena
INSERT INTO notifications (user_id, title, message, channel, is_urgent, is_read, metadata)
VALUES (
    '22222222-2222-2222-2222-222222222222',
    'Alerta Prioritaria: Elena tiene un plazo de 14 días con IRCC',
    'Tu familiar Elena escaneó una carta de Inmigración (IRCC). Faltan 14 días para enviar la prueba de residencia y el checklist está al 33% completado.',
    'push',
    TRUE,
    FALSE,
    '{"document_id": "88888888-8888-8888-8888-888888888888", "senior_name": "Elena Pabla"}'::jsonb
)
ON CONFLICT (id) DO NOTHING;


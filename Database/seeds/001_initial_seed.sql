-- ==============================================================================
-- CLEARLY — Seed 001: Initial Demo Data (Seniors, Tutors, Experts, Events)
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

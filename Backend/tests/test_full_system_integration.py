"""
CLEARLY — Complete End-to-End System Integration Test
Validates the entire multi-service ecosystem across:
1. Senior Document Upload & Deterministic Processing (OCR, Dates, FH >= 80).
2. Sovereign SQLite + sqlite-vec Local RAG Ingestion & Grounded QA with Citations.
3. Tutor Hub Handshake, Real-Time Collaboration & Silent Duress PIN Quarantine.
4. CLEARLY Premium Expert Matching, Escrow Custody (15/85 Split) & LiveKit A11y.
5. Civic Events Geocoding (FSA Haversine), 6 Canonical Questions & RFC 5545 Calendar.
6. Gerontological Audio Engine (Elderly-adapted Whisper STT & Piper TTS < 150ms).
"""

import sys
from pathlib import Path
from datetime import date, datetime, timedelta, timezone
from uuid import UUID, uuid4
import unittest

# Add Backend and project root to sys.path
backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from tests.async_helper import run_sync
from app.db.repository import repository
from app.services.document_pipeline import document_pipeline
from app.services.audio_service import audio_service
from app.services.calendar_service import RFC5545CalendarGenerator
from app.services.livekit_service import livekit_service
from app.services.civic_search import (
    calculate_haversine_distance_km,
    geocode_ontario_postal_code,
)
from app.services.plain_language_event import PlainLanguageEventTransformer
from app.schemas.tutor import (
    PairingCodeRequest,
    PairTutorRequest,
    ChecklistToggleRequest,
    DuressTriggerRequest,
)
from app.api.v1.tutors import (
    create_pairing_code,
    pair_tutor,
    get_tutor_dashboard,
    toggle_checklist_action,
    trigger_duress_pin,
)
from app.schemas.premium import (
    ExpertMatchRequest,
    CreateBookingRequest,
    ReleaseEscrowRequest,
)
from app.api.v1.premium import (
    match_expert,
    create_booking,
    release_escrow,
)
from app.schemas.events import EventSearchRequest
from app.api.v1.events import search_events
from RAG.adapter.backend_adapter import backend_rag_adapter
from RAG.pipeline.rag_service import rag_service


class TestFullSystemIntegration(unittest.TestCase):
    def setUp(self):
        # Reset and seed database state
        repository._load_seed_data()

        # Canonical Personas (Brampton Cohort)
        self.senior_id = UUID("11111111-1111-1111-1111-111111111111")  # Elena Pabla (Senior)
        self.tutor_id = UUID("22222222-2222-2222-2222-222222222222")   # Carlos Pabla (Son & Tutor)

    # --------------------------------------------------------------------------
    # STAGE 1: Senior Document Pipeline & Sovereign Local Sync
    # --------------------------------------------------------------------------

    def test_stage_1_document_processing_and_sovereign_sync(self):
        """
        Stage 1: Elena uploads an official Landlord and Tenant Board (LTB) Notice.
        Validates OCR, deterministic date extraction, FH >= 80 readability,
        proactive tutor alert dispatch, and automatic SQLite RAG synchronization.
        """
        ltb_raw_document = (
            "TRIBUNAL DE PROPIETARIOS E INQUILINOS DE ONTARIO (LANDLORD AND TENANT BOARD)\n"
            "AVISO DE FINALIZACIÓN DE CONTRATO POR FALTA DE PAGO (FORMULARIO N4)\n"
            "Número de Expediente: LTB-2026-9921\n"
            "Fecha de la carta: 30 de octubre de 2026\n\n"
            "DETALLES DEL INCUMPLIMIENTO:\n"
            "El arrendatario adeuda la cantidad total de $1,850.00 CAD correspondiente a la renta.\n"
            "Usted tiene un plazo de 14 días a partir de la fecha de esta notificación "
            "para pagar el saldo o llegar a un acuerdo con el propietario.\n\n"
            "DERECHO DE OPOSICIÓN:\n"
            "Si no está conforme con este requerimiento, tiene derecho a una audiencia ante el Tribunal."
        ).encode("utf-8")

        ref_date = date(2026, 11, 1)

        async def run_pipeline():
            return await document_pipeline.process_document(
                file_bytes=ltb_raw_document,
                filename="aviso_ltb_n4_elena.txt",
                user_id=self.senior_id,
                content_type="text/plain",
                target_language="es",
                reference_date=ref_date,
            )

        doc_res = run_sync(run_pipeline())

        # 1. Assert Plain Language satisfies Fernandez-Huerta >= 80
        self.assertGreaterEqual(
            doc_res.fernandez_huerta_score,
            80.0,
            f"Gerontological threshold: FH >= 80, obtained {doc_res.fernandez_huerta_score}",
        )

        # 2. Assert Deterministic Date Extraction (FMEA FM-02)
        # 30 Oct 2026 + 14 calendar days = 13 Nov 2026
        self.assertEqual(doc_res.critical_deadline, date(2026, 11, 13))
        self.assertEqual(doc_res.urgency, "high")
        self.assertTrue(doc_res.tutor_alert_triggered)
        self.assertTrue(doc_res.requires_human_expert)

        # 3. Assert Action Items created in repository
        self.assertGreaterEqual(len(doc_res.actions_required), 1)

        # 4. Verify Document was indexed into Sovereign SQLite RAG
        rag_doc = rag_service.store.get_document(str(doc_res.id))
        self.assertIsNotNone(rag_doc)
        self.assertEqual(rag_doc.filename, "aviso_ltb_n4_elena.txt")

    # --------------------------------------------------------------------------
    # STAGE 2: Sovereign Local RAG Querying (SQLite + sqlite-vec)
    # --------------------------------------------------------------------------

    def test_stage_2_sovereign_rag_grounded_query(self):
        """
        Stage 2: Elena asks a natural language question about her notice.
        Validates SQLite + sqlite-vec hybrid retrieval (RRF), grounded citations,
        Fernández-Huerta readability >= 80, and human expert escalation trigger.
        """
        # Index notice into sovereign RAG store
        ltb_text = (
            "# LANDLORD AND TENANT BOARD - AVISO N4\n\n"
            "Expediente LTB-2026-9921. Fecha límite de pago: 2026-11-28.\n\n"
            "REQUERIMIENTO:\n"
            "Debe abonar la cantidad adeudada de $1,850.00 CAD para evitar el desalojo de la vivienda.\n\n"
            "AUDIENCIA:\n"
            "Puede solicitar una audiencia legal ante el tribunal para defender sus derechos de inquilino."
        )
        doc_id = str(uuid4())
        rag_service.index_document(
            content=ltb_text,
            filename="aviso_n4_rag.txt",
            document_id=doc_id,
            user_id=str(self.senior_id),
            issuing_entity="Landlord and Tenant Board",
            critical_deadline="2026-11-28",
            urgency="CRITICAL",
        )

        # Query via Backend RAG adapter
        rag_res = backend_rag_adapter.query_senior_documents(
            user_query="¿Cuánto dinero tengo que pagar y qué pasa si no puedo antes de la fecha límite?",
            senior_id=str(self.senior_id),
            document_id=doc_id,
            language="es",
        )

        # 1. Answer contains grounded figures and chunk citations
        self.assertIn("1,850.00", rag_res.answer)
        self.assertGreaterEqual(len(rag_res.citations), 1)

        # 2. Answer satisfies Fernandez-Huerta >= 80
        self.assertGreaterEqual(rag_res.readability.score, 80.0)
        self.assertTrue(rag_res.readability.is_plain_language)

        # 3. High-risk term triggers expert recommendation
        self.assertTrue(rag_res.requires_human_expert)
        self.assertIsNotNone(rag_res.expert_reason)
        self.assertIn("desalojo", rag_res.expert_reason.lower())

        # 4. Action checklist suggested
        self.assertGreaterEqual(len(rag_res.suggested_actions), 1)

    # --------------------------------------------------------------------------
    # STAGE 3: Tutor Hub Handshake, Dashboard & Duress PIN Protection
    # --------------------------------------------------------------------------

    def test_stage_3_tutor_hub_and_duress_protection(self):
        """
        Stage 3: Carlos supervises Elena's documents, completes a checklist task,
        and tests the Duress PIN silent protection protocol (FMEA FM-04).
        """
        # 1. Generate 6-digit ephemeral pairing code for Elena
        pair_req = PairingCodeRequest(senior_id=self.senior_id)
        pair_data = run_sync(create_pairing_code(pair_req))
        self.assertEqual(len(pair_data.pairing_code), 6)
        self.assertTrue(pair_data.pairing_code.isdigit())

        # 2. Carlos redeems handshake via QR payload/code
        redeem_req = PairTutorRequest(
            tutor_id=self.tutor_id,
            pairing_code=pair_data.pairing_code,
            relationship_label="Hijo y Tutor Familiar",
        )
        redeem_res = run_sync(pair_tutor(redeem_req))
        self.assertEqual(redeem_res.status, "paired")
        self.assertIsNotNone(redeem_res.capability_token)

        # 3. Carlos accesses aggregated dashboard
        dashboard = run_sync(get_tutor_dashboard(self.senior_id, self.tutor_id))
        self.assertEqual(str(dashboard.senior["id"]), str(self.senior_id))
        self.assertEqual(dashboard.senior["full_name"], "Elena Pabla")
        self.assertFalse(dashboard.is_quarantine_mode)
        self.assertGreaterEqual(len(dashboard.collaborative_checklist), 1)

        # 4. Carlos toggles a checklist task as completed
        first_action = dashboard.collaborative_checklist[0]
        toggle_req = ChecklistToggleRequest(completed_by_user_id=self.tutor_id)
        toggled = run_sync(toggle_checklist_action(action_id=first_action.id, req=toggle_req))
        self.assertNotEqual(toggled.is_completed, first_action.is_completed)
        self.assertEqual(toggled.completed_by_user_id, self.tutor_id)

        # 5. Test Duress PIN Silent Quarantine Protocol (FMEA FM-04)
        duress_req = DuressTriggerRequest(
            senior_id=self.senior_id,
            entered_pin="9876",  # Seeded duress PIN for Elena
        )
        duress_res = run_sync(trigger_duress_pin(duress_req))
        self.assertTrue(duress_res.quarantine_mode)
        self.assertEqual(duress_res.status, "success")

        # 6. Verify Tutor Dashboard is now in silent quarantine
        quarantine_dashboard = run_sync(get_tutor_dashboard(self.senior_id, self.tutor_id))
        self.assertTrue(quarantine_dashboard.is_quarantine_mode)

    # --------------------------------------------------------------------------
    # STAGE 4: CLEARLY Premium Expert Matching & Stripe Escrow
    # --------------------------------------------------------------------------

    def test_stage_4_premium_matching_and_escrow_workflow(self):
        """
        Stage 4: Automated match with verified housing expert, creation of
        Stripe Escrow with 15/85 fee split, and issuance of LiveKit WebRTC tokens.
        """
        # 1. Matching by context: Housing / Eviction -> Landlord and Tenant Board expert
        match_req = ExpertMatchRequest(
            query_text="Aviso de desalojo LTB Formulario N4 por falta de pago de renta en Brampton.",
            senior_id=self.senior_id,
        )
        match_res = run_sync(match_expert(match_req))

        self.assertIsNotNone(match_res.matched_expert)
        self.assertIn("Vivienda", match_res.detected_specialty)
        self.assertEqual(match_res.matched_expert.full_name, "Sarah Jenkins, MSW")
        self.assertGreaterEqual(match_res.match_score, 80.0)

        # 2. Carlos books consultation on behalf of Elena with Stripe Escrow
        now = datetime.now(timezone.utc)
        booking_req = CreateBookingRequest(
            expert_id=match_res.matched_expert.id,
            client_senior_id=self.senior_id,
            requested_by_user_id=self.tutor_id,
            modality="virtual",
            scheduled_start=now + timedelta(days=2),
        )
        booking = run_sync(create_booking(booking_req))

        # Fee split invariants: 15% platform fee / 85% held in escrow
        self.assertEqual(booking.status, "escrow_held")
        self.assertTrue(booking.escrow_held)
        self.assertEqual(booking.amount_cents, 4000)
        self.assertIn("clearly-consultation-", booking.livekit_room_name)
        self.assertIsNotNone(booking.livekit_token)

        # 3. LiveKit Video Consultation Room & WCAG AAA Subtitles Token
        self.assertIn("clearly-consultation-", booking.livekit_room_name)
        details = livekit_service.create_room_token(
            booking_id=booking.id,
            participant_identity=f"senior-{self.senior_id}",
            participant_name="Elena Pabla",
            is_senior=True,
        )
        self.assertIn("clearly-consultation-", details.room_name)
        self.assertEqual(details.caption_font_scale, 1.5)
        self.assertTrue(details.enable_realtime_transcription)

        # 4. Carlos releases escrow upon consultation completion
        release_req = ReleaseEscrowRequest(
            rating=5,
            review_comment="Excelente asesoría legal para mi madre Elena.",
        )
        released_booking = run_sync(release_escrow(booking.id, release_req))
        self.assertEqual(released_booking.status, "completed")
        self.assertEqual(released_booking.expert_payout_cents, 3400)
        self.assertEqual(released_booking.client_review_rating, 5)

    # --------------------------------------------------------------------------
    # STAGE 5: Civic Events, Haversine FSA Geocoding & RFC 5545 Calendar
    # --------------------------------------------------------------------------

    def test_stage_5_civic_inclusion_and_calendar_sync(self):
        """
        Stage 5: Elena searches for accessible senior events in Brampton.
        Validates Ontario postal code geocoding, Haversine distance,
        Canonical 6 Questions transformation, and RFC 5545 .ics generation.
        """
        # 1. Geocode Brampton FSA 'L6V' and calculate distance
        coords_brampton = geocode_ontario_postal_code("L6V 1A1")
        self.assertIsNotNone(coords_brampton)
        self.assertAlmostEqual(coords_brampton.latitude, 43.6833, places=2)

        coords_toronto = geocode_ontario_postal_code("M5H 2N2")
        dist_km = calculate_haversine_distance_km(
            coords_brampton.latitude, coords_brampton.longitude,
            coords_toronto.latitude, coords_toronto.longitude
        )
        self.assertGreater(dist_km, 25.0)
        self.assertLess(dist_km, 40.0)

        # 2. Search Civic Events via service
        search_req = EventSearchRequest(
            postal_code="L6V 1A1",
            max_distance_km=15.0,
            city="Brampton",
            language="es",
        )
        search_res = run_sync(search_events(search_req))
        self.assertGreaterEqual(search_res.total_found, 1)

        event_item = search_res.results[0]
        event = event_item.event
        self.assertEqual(event.location.address.addressLocality, "Brampton")
        self.assertTrue(event.offers.is_free)

        # 3. Canonical 6 Questions Framework
        answers = PlainLanguageEventTransformer.transform(
            raw_title=event.name,
            description=event.description,
            start_time=event.startDate,
            end_time=event.endDate,
            venue_name=event.location.name,
            venue_address=event.location.address.streetAddress,
            is_free=event.offers.is_free,
            cost_amount=event.offers.price,
            registration_required=True,
            registration_deadline=event.startDate,
            registration_url="https://brampton.ca",
            accessibility_notes="Accesible para sillas de ruedas",
            lang="es",
        )
        self.assertTrue(len(answers.q1_what) > 0)
        self.assertTrue(len(answers.q2_when_where) > 0)
        self.assertTrue(len(answers.q3_cost) > 0)
        self.assertGreater(len(event_item.why_recommended), 5)

        # 4. Generate RFC 5545 iCalendar file (.ics)
        location_str = f"{event.location.name}, {event.location.address.streetAddress}, {event.location.address.addressLocality}, ON"
        ics_text = RFC5545CalendarGenerator.generate_event_ics(
            event_id=str(event.id),
            title=event.name,
            description=answers.q1_what or event.description,
            location=location_str,
            start_datetime=event.startDate,
            end_datetime=event.endDate,
            organizer_name=event.organizer.name,
            organizer_email=event.organizer.email,
        )

        self.assertIn("BEGIN:VCALENDAR\r\n", ics_text)
        self.assertIn("BEGIN:VEVENT\r\n", ics_text)
        self.assertIn("END:VCALENDAR\r\n", ics_text)
        # RFC 5545 strict CRLF invariant
        self.assertTrue(ics_text.endswith("\r\n"))

    # --------------------------------------------------------------------------
    # STAGE 6: Gerontological Multichannel Audio Services
    # --------------------------------------------------------------------------

    def test_stage_6_gerontological_audio_services(self):
        """
        Stage 6: Speech synthesis (Piper TTS) and geriatric transcription (Whisper STT).
        Validates Piper TTS latency < 150ms and elderly pause tolerance.
        """
        # 1. Synthesize plain language speech with Davefx voice
        speech_result = run_sync(
            audio_service.synthesize_speech(
                "Hola Elena. Su aviso del tribunal vence el veintiocho de noviembre."
            )
        )
        self.assertEqual(speech_result["content_type"], "audio/wav")
        self.assertLess(
            speech_result["latency_ms"],
            150.0,
            f"Piper TTS latency must be < 150ms, got {speech_result['latency_ms']}ms",
        )
        self.assertGreater(len(speech_result["audio_bytes"]), 44)

        # 2. Gerontological STT transcription
        stt_result = run_sync(
            audio_service.transcribe_audio(
                audio_bytes=speech_result["audio_bytes"],
                filename="nota_elena.ogg",
                language="es",
            )
        )
        self.assertIn("transcript", stt_result)
        self.assertLess(stt_result["latency_ms"], 850.0)


if __name__ == "__main__":
    unittest.main()

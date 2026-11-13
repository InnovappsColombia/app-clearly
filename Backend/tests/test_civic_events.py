"""
CLEARLY — Civic Events, Hybrid Search & RFC 5545 Automated Test Suite
Demuestra rigurosamente:
1. Conformidad con Schema.org/Event.
2. Cálculo geodésico Haversine y geocodificación de códigos postales de Ontario (GTA).
3. Búsqueda híbrida soberana multilingüe (Español, Inglés, Punyabí).
4. Auditoría matemática de legibilidad: Fernández-Huerta >= 80 y Flesch Reading Ease >= 80.
5. Generación e invariantes sintácticos RFC 5545 iCalendar (.ics).
6. Integración con endpoints REST FastAPI usando run_sync sin loopback socket dependencies.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest
from uuid import UUID

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from tests.async_helper import run_sync
from app.db.repository import repository
from app.schemas.events import (
    EventSearchRequest,
    SchemaOrgEvent,
    Place,
    PostalAddress,
    GeoCoordinates,
    Offer,
    Organizer,
)
from app.services.calendar_service import RFC5545CalendarGenerator, fold_line, rfc5545_escape_text
from app.services.civic_search import (
    CivicSearchEngine,
    calculate_haversine_distance_km,
    geocode_ontario_postal_code,
)
from app.services.plain_language_event import PlainLanguageEventTransformer
from app.services.readability import (
    audit_readability,
    calculate_fernandez_huerta,
    calculate_flesch_reading_ease,
    calculate_flesch_kincaid_grade,
)
from app.api.v1.events import (
    search_events,
    list_events,
    get_event,
    download_calendar_ics,
    transform_event_plain_language,
)


class TestCivicEventsAndA11y(unittest.TestCase):
    def setUp(self):
        self.brampton_event_id = UUID("77777777-7777-7777-7777-777777777771")
        self.toronto_event_id = UUID("77777777-7777-7777-7777-777777777772")

    # 1. Geodetic & Postal Code Tests
    def test_geocode_ontario_postal_codes(self):
        # Brampton downtown (L6V)
        coords_l6v = geocode_ontario_postal_code("L6V 1A1")
        self.assertIsNotNone(coords_l6v)
        self.assertAlmostEqual(coords_l6v.latitude, 43.6833, places=2)
        self.assertAlmostEqual(coords_l6v.longitude, -79.7667, places=2)

        # Toronto Central (M5V)
        coords_m5v = geocode_ontario_postal_code("M5V 2T6")
        self.assertIsNotNone(coords_m5v)
        self.assertAlmostEqual(coords_m5v.latitude, 43.6532, places=2)

        # Mississauga Square One (L5B)
        coords_l5b = geocode_ontario_postal_code("L5B 3C1")
        self.assertIsNotNone(coords_l5b)
        self.assertAlmostEqual(coords_l5b.latitude, 43.5890, places=2)

        # Invalid/empty postal code
        self.assertIsNone(geocode_ontario_postal_code(""))
        self.assertIsNone(geocode_ontario_postal_code("ZZZ 999"))

    def test_haversine_distance_calculation(self):
        # Distance from Brampton (L6V: 43.6833, -79.7667) to Toronto Downtown (M5: 43.6532, -79.3832)
        dist = calculate_haversine_distance_km(43.6833, -79.7667, 43.6532, -79.3832)
        self.assertTrue(28.0 <= dist <= 33.0, f"Distance was {dist}")

        # Identical coordinates should be 0.0 km
        same_dist = calculate_haversine_distance_km(43.6833, -79.7667, 43.6833, -79.7667)
        self.assertEqual(same_dist, 0.0)

    # 2. Mathematical Readability Tests (FH >= 80, FRE >= 80)
    def test_fernandez_huerta_spanish_plain_language(self):
        plain_spanish = (
            "Es una clase de yoga muy suave en silla. No cuesta dinero. "
            "Llega a la puerta principal con ropa cómoda. El lugar tiene rampas para silla de ruedas."
        )
        score = calculate_fernandez_huerta(plain_spanish)
        self.assertGreaterEqual(
            score, 80.0, f"Spanish plain language must meet FH >= 80, got {score}"
        )

        audit = audit_readability(plain_spanish, language="es")
        self.assertTrue(audit.is_acceptable)
        self.assertIn("primaria", audit.reading_level.lower())

    def test_flesch_reading_ease_english_plain_language(self):
        plain_english = (
            "This is a gentle chair yoga class for older adults. It is free. "
            "You can walk in without a ticket. Friendly helpers will greet you at the front door."
        )
        fre_score = calculate_flesch_reading_ease(plain_english)
        self.assertGreaterEqual(
            fre_score, 80.0, f"English plain language must meet FRE >= 80, got {fre_score}"
        )

        fkgl_grade = calculate_flesch_kincaid_grade(plain_english)
        self.assertLessEqual(
            fkgl_grade, 5.0, f"English plain language must be Grade 5 or lower, got {fkgl_grade}"
        )

        audit = audit_readability(plain_english, language="en")
        self.assertTrue(audit.is_acceptable)

    # 3. Plain Language 6-Question Transformer
    def test_plain_language_transformer_completeness(self):
        now = datetime.now(timezone.utc)
        answers = PlainLanguageEventTransformer.transform(
            raw_title="Gentle Chair Yoga & Senior Balance Workshop",
            description="A gentle seated breathing and stretching class designed to relax joints without heavy strain.",
            start_time=now + timedelta(days=2),
            end_time=now + timedelta(days=2, hours=1),
            venue_name="Centro Comunitario Downtown Brampton",
            venue_address="8 Central Park Dr, Brampton, ON",
            is_free=True,
            cost_amount=None,
            registration_required=True,
            registration_deadline=now + timedelta(days=1),
            registration_url="https://brampton.ca",
            accessibility_notes="Rampas accesibles y elevador",
            lang="es",
        )

        self.assertTrue(answers.q1_what.startswith("Es una actividad comunitaria"))
        self.assertIn("Centro Comunitario", answers.q2_when_where)
        self.assertIn("gratuito", answers.q3_cost.lower())
        self.assertIn("anotarte", answers.q4_registration.lower())
        self.assertIn("puerta principal", answers.q5_what_to_do.lower())
        self.assertIn("rampas", answers.q6_what_to_check.lower())

        # Check that FH score was calculated
        self.assertIsNotNone(answers.readability_score_fh)
        self.assertGreaterEqual(answers.readability_score_fh, 75.0)

    # 4. RFC 5545 iCalendar Generator & Syntax Validation
    def test_rfc5545_calendar_generation_and_folding(self):
        start = datetime(2026, 11, 21, 10, 30, tzinfo=timezone.utc)
        end = datetime(2026, 11, 21, 11, 45, tzinfo=timezone.utc)

        long_title = "Taller de Bienestar, Respiración Guiada y Yoga Suave en Silla para Adultos Mayores y Vecinos de Brampton"
        ics_text = RFC5545CalendarGenerator.generate_event_ics(
            event_id="evt-unit-test-1",
            title=long_title,
            description="Una clase grupal muy suave de respiración y estiramiento sentado, diseñada para relajar articulaciones sin esfuerzo físico pesado.",
            location="Downtown Brampton Community Centre, 8 Central Park Dr, Brampton, ON",
            start_datetime=start,
            end_datetime=end,
            organizer_name="Parks & Rec Brampton",
            organizer_email="seniors@brampton.ca",
            url="https://brampton.ca",
        )

        # Must end with CRLF
        self.assertTrue(ics_text.endswith("\r\n"))
        self.assertIn("BEGIN:VCALENDAR\r\n", ics_text)
        self.assertIn("VERSION:2.0\r\n", ics_text)
        self.assertIn("BEGIN:VEVENT\r\n", ics_text)
        self.assertIn("DTSTART:20261121T103000Z\r\n", ics_text)
        self.assertIn("DTEND:20261121T114500Z\r\n", ics_text)
        self.assertIn("STATUS:CONFIRMED\r\n", ics_text)
        self.assertIn("END:VEVENT\r\n", ics_text)
        self.assertIn("END:VCALENDAR\r\n", ics_text)

        # Validate syntax using RFC5545 validator
        is_valid, errors = RFC5545CalendarGenerator.validate_syntax(ics_text)
        self.assertTrue(is_valid, f"RFC 5545 validation failed with errors: {errors}")

    def test_rfc5545_text_escaping(self):
        escaped = rfc5545_escape_text("Hello, world; welcome\nto\\clearly")
        self.assertEqual(escaped, "Hello\\, world\\; welcome\\nto\\\\clearly")

    # 5. Hybrid Search Engine Tests
    def test_civic_search_by_city_and_query(self):
        events = list(repository.schema_events.values())

        # Search for yoga in Brampton
        req = EventSearchRequest(
            query="yoga en silla",
            city="brampton",
            is_free=True,
            language="es",
        )
        res = CivicSearchEngine.search(events, req)
        self.assertGreater(res.total_found, 0)
        top_event = res.results[0]
        self.assertEqual(top_event.event.municipality, "brampton")
        self.assertIn("yoga", top_event.event.name.lower())
        self.assertTrue(len(top_event.why_recommended) > 10)

    def test_civic_search_multilingual_punjabi(self):
        events = list(repository.schema_events.values())
        req = EventSearchRequest(
            query="ਯੋਗਾ",
            language="pa",
        )
        res = CivicSearchEngine.search(events, req)
        self.assertGreater(res.total_found, 0)
        self.assertIn("ਸਿਫ਼ਾਰਸ਼", res.results[0].why_recommended)

    def test_civic_search_by_postal_code_radius(self):
        events = list(repository.schema_events.values())
        # User is in Brampton downtown (L6V) looking for events within 10 km
        req = EventSearchRequest(
            postal_code="L6V 1A1",
            max_distance_km=10.0,
            language="es",
        )
        res = CivicSearchEngine.search(events, req)
        self.assertGreater(res.total_found, 0)
        for r in res.results:
            self.assertIsNotNone(r.distance_km)
            self.assertLessEqual(r.distance_km, 10.0)

    # 6. Direct Endpoint Handlers Integration Tests (via run_sync)
    def test_api_list_events(self):
        events = run_sync(list_events(city="brampton", is_free=True))
        self.assertIsInstance(events, list)
        self.assertGreater(len(events), 0)
        self.assertEqual(events[0].context, "https://schema.org")
        self.assertEqual(events[0].type, "Event")
        self.assertEqual(events[0].municipality, "brampton")

    def test_api_search_events(self):
        payload = EventSearchRequest(
            query="smartphones for older adults",
            city="toronto",
            language="en",
        )
        response = run_sync(search_events(payload))
        self.assertGreater(response.total_found, 0)
        self.assertEqual(response.results[0].event.municipality, "toronto")
        self.assertIn("Recommended", response.results[0].why_recommended)

    def test_api_download_calendar_ics(self):
        response = run_sync(download_calendar_ics(self.brampton_event_id, lang="es"))
        self.assertEqual(response.media_type, "text/calendar; charset=utf-8")
        self.assertIn("attachment; filename=", response.headers["Content-Disposition"])
        content = response.body.decode("utf-8")
        self.assertIn("BEGIN:VCALENDAR", content)
        self.assertIn("BEGIN:VEVENT", content)
        self.assertIn("END:VCALENDAR", content)

    def test_api_transform_plain_language(self):
        answers = run_sync(transform_event_plain_language(self.brampton_event_id, lang="es"))
        self.assertIsNotNone(answers.q1_what)
        self.assertIsNotNone(answers.q2_when_where)
        self.assertIsNotNone(answers.q3_cost)
        self.assertIsNotNone(answers.q4_registration)
        self.assertIsNotNone(answers.q5_what_to_do)
        self.assertIsNotNone(answers.q6_what_to_check)
        self.assertIsNotNone(answers.readability_score_fh)
        self.assertGreaterEqual(answers.readability_score_fh, 75.0)


if __name__ == "__main__":
    unittest.main()

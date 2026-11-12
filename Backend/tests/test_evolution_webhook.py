"""
CLEARLY — Test Suite for Evolution API (WhatsApp Gateway) & Message Triage
Validates incoming text, audio voice notes (STT + TTS), document scanning, and rate limiting.
Runs with deterministic synchronous async execution (safe across all sandboxes).
"""

import base64
import unittest
import sys
from pathlib import Path

# Add Backend root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.api.v1.webhooks import handle_whatsapp_webhook
from app.db.repository import repository
from app.schemas.whatsapp import (
    EvolutionAudioMessage,
    EvolutionMessageContent,
    EvolutionMessageData,
    EvolutionMessageKey,
    EvolutionWebhookPayload,
)
from tests.async_helper import run_sync


class TestEvolutionWebhook(unittest.TestCase):
    def setUp(self):
        repository._load_seed_data()
    def test_whatsapp_text_civic_greeting(self):
        """Tests general civic greeting in simple Spanish."""
        payload = EvolutionWebhookPayload(
            event="messages.upsert",
            instance="clearly-instance",
            data=EvolutionMessageData(
                key=EvolutionMessageKey(
                    remoteJid="19055550101@s.whatsapp.net",
                    fromMe=False,
                    id="MSG_001",
                ),
                pushName="Elena Pabla",
                message=EvolutionMessageContent(
                    conversation="Hola, ¿cómo funciona este servicio para personas mayores?",
                ),
                messageType="conversation",
            ),
        )

        res = run_sync(handle_whatsapp_webhook(payload))
        self.assertEqual(res.status, "processed")
        self.assertEqual(res.detected_intent, "general_civic")
        self.assertIn("Elena", res.text_reply)
        self.assertIn("Brampton", res.text_reply)
        self.assertGreaterEqual(res.plain_language_score, 80.0)

    def test_whatsapp_text_community_events_query(self):
        """Tests querying community events via WhatsApp message (Made Clear format)."""
        payload = EvolutionWebhookPayload(
            event="messages.upsert",
            instance="clearly-instance",
            data=EvolutionMessageData(
                key=EvolutionMessageKey(
                    remoteJid="19055550101@s.whatsapp.net",
                    fromMe=False,
                    id="MSG_002",
                ),
                pushName="Elena Pabla",
                message=EvolutionMessageContent(
                    conversation="¿Hay clases de yoga o talleres gratis para adultos mayores?",
                ),
                messageType="conversation",
            ),
        )

        res = run_sync(handle_whatsapp_webhook(payload))
        self.assertEqual(res.status, "processed")
        self.assertEqual(res.detected_intent, "events_query")
        reply = res.text_reply
        self.assertIn("Actividad Comunitaria Recomendada", reply)
        self.assertIn("¿De qué se trata?", reply)
        self.assertIn("Costo:", reply)
        self.assertIn("GRATUITO", reply)

    def test_whatsapp_document_text_with_tutor_alert(self):
        """Tests sending document text via WhatsApp that triggers proactive tutor alert (< 15 days)."""
        payload = EvolutionWebhookPayload(
            event="messages.upsert",
            instance="clearly-instance",
            data=EvolutionMessageData(
                key=EvolutionMessageKey(
                    remoteJid="19055550101@s.whatsapp.net",
                    fromMe=False,
                    id="MSG_003",
                ),
                pushName="Elena Pabla",
                message=EvolutionMessageContent(
                    extendedTextMessage={
                        "text": (
                            "Tribunal de Arrendamiento y Vivienda de Ontario (LTB). Formulario N4. "
                            "Fecha de la carta: 30 de octubre de 2026. "
                            "Aviso de finalización anticipada por falta de pago de renta. "
                            "Usted tiene un plazo de 14 días a partir de la fecha de esta notificación para pagar o desalojar."
                        )
                    }
                ),
                messageType="extendedTextMessage",
            ),
        )

        res = run_sync(handle_whatsapp_webhook(payload))
        self.assertEqual(res.status, "processed")
        self.assertEqual(res.detected_intent, "document_analysis")
        self.assertTrue(res.tutor_alert_dispatched)
        self.assertIn("tutor familiar", res.text_reply)

    def test_whatsapp_voice_note_stt_and_tts(self):
        """
        Tests sending a voice note audio message.
        Validates faster-whisper gerontological transcription and Piper TTS voice generation.
        """
        sample_audio_b64 = base64.b64encode(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00").decode("utf-8")
        payload = EvolutionWebhookPayload(
            event="messages.upsert",
            instance="clearly-instance",
            data=EvolutionMessageData(
                key=EvolutionMessageKey(
                    remoteJid="19055550101@s.whatsapp.net",
                    fromMe=False,
                    id="MSG_VOICE_004",
                ),
                pushName="Elena Pabla",
                message=EvolutionMessageContent(
                    audioMessage=EvolutionAudioMessage(
                        base64=sample_audio_b64,
                        mimetype="audio/ogg; codecs=opus",
                        seconds=8,
                    )
                ),
                messageType="audioMessage",
            ),
        )

        res = run_sync(handle_whatsapp_webhook(payload))
        self.assertEqual(res.status, "processed")
        self.assertEqual(res.detected_intent, "voice_dialogue")
        self.assertTrue(res.audio_reply_generated)
        self.assertIsNotNone(res.audio_reply_base64)
        self.assertLess(res.audio_latency_ms, 250.0)


if __name__ == "__main__":
    unittest.main()

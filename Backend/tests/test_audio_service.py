"""
CLEARLY — Test Suite for Gerontological Audio Service
Validates faster-whisper STT with VAD parameters and Piper TTS synthesis latency.
"""

import unittest
import sys
from pathlib import Path

# Add Backend root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.audio_service import audio_service
from tests.async_helper import run_sync


class TestAudioService(unittest.TestCase):
    def test_whisper_gerontological_transcription(self):
        """Validates elderly-adapted speech-to-text transcription latency < 850ms."""
        mock_audio_bytes = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
        result = run_sync(
            audio_service.transcribe_audio(
                audio_bytes=mock_audio_bytes,
                filename="nota_elena.ogg",
                language="es",
            )
        )

        self.assertIn("transcript", result)
        self.assertGreater(len(result["transcript"]), 10)
        self.assertEqual(result["detected_language"], "es")
        # CPU benchmark < 850ms
        self.assertLess(result["latency_ms"], 850.0)

    def test_piper_tts_synthesis_benchmark(self):
        """Validates Piper TTS speech generation benchmark latency < 150ms."""
        plain_text = "Su trámite de residencia vence en doce días. Su hijo Carlos ya fue notificado."
        result = run_sync(audio_service.synthesize_speech(plain_text))

        self.assertEqual(result["content_type"], "audio/wav")
        self.assertGreater(len(result["audio_bytes"]), 44)  # Has valid RIFF/WAV header
        self.assertEqual(result["audio_bytes"][:4], b"RIFF")
        self.assertEqual(result["audio_bytes"][8:12], b"WAVE")
        # Speech synthesis latency benchmark < 150ms
        self.assertLess(result["latency_ms"], 150.0)


if __name__ == "__main__":
    unittest.main()

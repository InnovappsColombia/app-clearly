"""
Unit Tests for Spanish Syllabifier (CLEARLY A11y Readability Core)
"""

import unittest
import sys
from pathlib import Path

# Add Backend root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.spanish_syllabifier import count_syllables_word, count_total_syllables


class TestSpanishSyllabifier(unittest.TestCase):
    def test_basic_words(self):
        cases = {
            "sol": 1,
            "pan": 1,
            "luz": 1,
            "casa": 2,
            "carta": 2,
            "madre": 2,
            "amigo": 3,
            "gobierno": 3,
            "comunidad": 4,
            "notificación": 5,
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                self.assertEqual(count_syllables_word(word), expected)

    def test_diphthongs(self):
        cases = {
            "farmacia": 3,     # far - ma - cia
            "ciudad": 2,       # ciu - dad
            "fuego": 2,        # fue - go
            "viaje": 2,        # via - je
            "cuidado": 3,      # cui - da - do
            "peine": 2,        # pei - ne
            "causa": 2,        # cau - sa
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                self.assertEqual(count_syllables_word(word), expected)

    def test_hiatus_accented_weak(self):
        cases = {
            "día": 2,          # dí - a
            "país": 2,         # pa - ís
            "leído": 3,        # le - í - do
            "oído": 3,         # o - í - do
            "maría": 3,        # ma - rí - a
            "grúa": 2,         # grú - a
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                self.assertEqual(count_syllables_word(word), expected)

    def test_hiatus_strong_strong(self):
        cases = {
            "teatro": 3,       # te - a - tro
            "poeta": 3,        # po - e - ta
            "leer": 2,         # le - er
            "cooperar": 4,     # co - o - pe - rar
            "caos": 2,         # ca - os
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                self.assertEqual(count_syllables_word(word), expected)

    def test_triphthongs(self):
        cases = {
            "paraguay": 3,     # pa - ra - guay
            "buey": 1,         # buey
            "averigüéis": 4,   # a - ve - ri - güéis
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                self.assertEqual(count_syllables_word(word), expected)

    def test_total_syllables(self):
        text = "Esta carta es de su ciudad. Debe enviar su foto hoy."
        total = count_total_syllables(text)
        self.assertGreater(total, 10)


if __name__ == "__main__":
    unittest.main()


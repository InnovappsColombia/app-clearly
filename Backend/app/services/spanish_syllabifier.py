"""
CLEARLY — Spanish Syllabifier Module
High-precision phonological syllabification for Spanish.
Handles vowels, diphthongs, triphthongs, hiatuses, and accentuation.
"""

import re
from typing import List


def count_syllables_word(word: str) -> int:
    """
    Count the number of syllables in a single Spanish word.
    
    Spanish phonological rules:
    - Every syllable has exactly one vocalic nucleus (monophthong, diphthong, or triphthong).
    - Strong vowels (abiertas): a, e, o, á, é, ó.
    - Weak vowels (cerradas): i, u, ü.
    - Accented weak vowels (í, ú) break diphthongs into hiatus (separate syllables).
    - Unaccented weak vowels with strong vowels or other weak vowels form diphthongs (1 syllable).
    - Weak + Strong + Weak forms triphthong (1 syllable).
    """
    w = word.lower().strip()
    # Remove non-letter characters
    w = re.sub(r"[^a-záéíóúüñ]", "", w)
    if not w:
        return 0

    # Vocalic 'y': at end of word or isolated when preceded by a vowel (e.g. 'muy', 'hoy', 'paraguay')
    w = re.sub(r"([aeiouáéíóú])y\b", r"\1i", w)
    w = re.sub(r"\by\b", "i", w)

    # Replace triphthongs with a single nucleus token:
    # unaccented weak (i, u, ü) + strong (a, e, o, á, é, ó) + unaccented weak (i, u)
    w = re.sub(r"[iuü][aeoáéó][iu]", "§", w)

    # Replace diphthongs with a single nucleus token:
    # 1. unaccented weak + strong
    w = re.sub(r"[iuü][aeoáéó]", "§", w)
    # 2. strong + unaccented weak
    w = re.sub(r"[aeoáéó][iu]", "§", w)
    # 3. two different unaccented weak vowels (iu, ui, etc.)
    w = re.sub(r"[iuü][iuü]", "§", w)

    # All remaining vocalic tokens are individual vocalic nuclei:
    # (single vowels, strong+strong hiatuses like 'ea', 'oe', accented weak like 'ía', 'úe')
    nuclei = re.findall(r"[aeiouáéíóúü§]", w)
    return max(1, len(nuclei))


def count_total_syllables(text: str) -> int:
    """Count total syllables across all valid words in a text."""
    words = [w.strip(".,;:!?()[]\"'«»¡¿—–-\n\t") for w in text.split()]
    words = [w for w in words if re.search(r"[a-záéíóúüñA-ZÁÉÍÓÚÜÑ]", w)]
    return sum(count_syllables_word(w) for w in words)


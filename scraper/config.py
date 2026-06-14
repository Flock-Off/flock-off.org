import os
import re
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
DAYS_AHEAD = int(os.getenv("DAYS_AHEAD", "60"))
DEBUG = os.getenv("DEBUG", "0") == "1"

KEYWORDS = [
    "Flock Safety",
    "Flock camera",
    "ALPR",
    "ANPR",
    "license plate reader",
    "license plate recognition",
    "automated license plate",
    "ShotSpotter",
    "gunshot detection",
    "Fusus",
    "Axon",
    "Verkada",
    "Avigilon",
    "Genetec",
    "facial recognition",
    "real-time crime center",
    "RTCC",
    "predictive policing",
    "body camera",
    "drone surveillance",
    "smart city surveillance",
    "Palantir",
    "biometric",
    "surveillance contract",
    "Ring camera",
    "Ring doorbell",
    "social media monitoring",
]

# Pre-compiled word-boundary patterns (case-insensitive).
# \b ensures we don't match "Ring" inside "engineering", "hearing", etc.
_PATTERNS: list[tuple[str, re.Pattern]] = [
    (kw, re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE))
    for kw in KEYWORDS
]


def find_keyword_matches(text: str) -> list[tuple[str, str]]:
    """Return list of (keyword, matched_context) for every whole-word hit in text."""
    if not text:
        return []
    results = []
    for kw, pattern in _PATTERNS:
        for m in pattern.finditer(text):
            start = max(0, m.start() - 80)
            end = min(len(text), m.end() + 80)
            context = text[start:end].strip()
            results.append((kw, context))
    return results

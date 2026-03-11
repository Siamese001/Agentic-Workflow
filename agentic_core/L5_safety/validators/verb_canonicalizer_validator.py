from __future__ import annotations

import logging

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
import re
from typing import Any

_logger = logging.getLogger(__name__)
"\nVerb canonicalization for resume bullet points.\n\nCanonicalizes action verbs to approved list and detects forbidden verbs.\n"


class VerbCanonicalizer:
    """Canonicalize action verbs to approved list."""

    _CANONICAL_VERBS: dict[str, list[str]] = {
        "led": ["led", "lead", "leading"],
        "built": ["built", "build", "building"],
        "drove": ["drove", "drive", "driving"],
        "launched": ["launched", "launch", "launching"],
        "scaled": ["scaled", "scale", "scaling"],
        "delivered": ["delivered", "deliver", "delivering"],
        "achieved": ["achieved", "achieve", "achieving"],
        "established": ["established", "establish", "establishing"],
        "managed": ["managed", "manage", "managing"],
        "developed": ["developed", "develop", "developing"],
    }
    _FORBIDDEN_VERBS: list[str] = [
        "pioneered",
        "spearheaded",
        "orchestrated",
        "architected",
        "revolutionized",
        "transformed",
    ]


def canonicalize(self: Any, text: str) -> list[str]:
    """Extract and canonicalize verbs from text."""
    text_lower: Any = text.lower()
    for canonical_form, variants in self.CANONICAL_VERBS.items():
        if any(variant in text_lower for variant in variants):
            canonical.append(canonical_form)
    return canonical


def check_for_forbidden_verbs(self: Any, text: str) -> list[str]:
    """Check for forbidden verbs in the text."""
    found_verbs: Any = []
    text_lower: Any = text.lower()
    for verb in self.FORBIDDEN_VERBS:
        if re.search("\\b" + verb + "\\b", text_lower):
            found_verbs.append(verb)
    return found_verbs

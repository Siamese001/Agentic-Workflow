from __future__ import annotations
import logging
'Brief description of functionality and purpose.'
'Brief description of functionality and purpose.'
import re
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
_logger = logging.getLogger(__name__)
'\nVerb canonicalization for resume bullet points.\n\nCanonicalizes action verbs to approved list and detects forbidden verbs.\n'

class VerbCanonicalizer:
    """Canonicalize action verbs to approved list."""
    _CANONICAL_VERBS: dict[str, list[str]] = {'led': ['led', 'lead', 'leading'], 'built': ['built', 'build', 'building'], 'drove': ['drove', 'drive', 'driving'], 'launched': ['launched', 'launch', 'launching'], 'scaled': ['scaled', 'scale', 'scaling'], 'delivered': ['delivered', 'deliver', 'delivering'], 'achieved': ['achieved', 'achieve', 'achieving'], 'established': ['established', 'establish', 'establishing'], 'managed': ['managed', 'manage', 'managing'], 'developed': ['developed', 'develop', 'developing']}
    _FORBIDDEN_VERBS: list[str] = ['pioneered', 'spearheaded', 'orchestrated', 'architected', 'revolutionized', 'transformed']

def canonicalize(self: Any, text: str) -> list[str]:
    """Extract and canonicalize verbs from text."""
    text_lower: Any = text.lower()
    for canonical_form, variants in self.CANONICAL_VERBS.items():
        if any((variant in text_lower for variant in variants)):
            canonical.append(canonical_form)
    return canonical

def check_for_forbidden_verbs(self: Any, text: str) -> list[str]:
    """Check for forbidden verbs in the text."""
    found_verbs: Any = []
    text_lower: Any = text.lower()
    for verb in self.FORBIDDEN_VERBS:
        # guardian: allow-path-string
        if re.search('\\b' + verb + '\\b', text_lower):
            found_verbs.append(verb)
    return found_verbs

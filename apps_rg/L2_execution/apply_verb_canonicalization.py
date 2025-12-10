# Ownership: apps_rg / L2_execution
# Layer: L2_execution
# Agent: apps_rg
# -*- coding: utf-8 -*-
"""
Verb canonicalization for resume bullet points.

Canonicalizes action verbs to approved list and detects forbidden verbs.
"""


import re
from typing import Dict, List


class VerbCanonicalizer:
    """Canonicalize action verbs to approved list."""

    CANONICAL_VERBS: Dict[str, List[str]] = {
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

    FORBIDDEN_VERBS: List[str] = [
        "pioneered",
        "spearheaded",
        "orchestrated",
        "architected",
        "revolutionized",
        "transformed",
    ]

    def canonicalize(self, text: str) -> List[str]:
        """Extract and canonicalize verbs from text."""
        canonical = []
        text_lower = text.lower()

        for canonical_form, variants in self.CANONICAL_VERBS.items():
            if any(variant in text_lower for variant in variants):
                canonical.append(canonical_form)

        return canonical

    def check_for_forbidden_verbs(self, text: str) -> List[str]:
        """Check for forbidden verbs in the text."""
        found_verbs = []
        text_lower = text.lower()
        for verb in self.FORBIDDEN_VERBS:
            if re.search(r"\b" + verb + r"\b", text_lower):
                found_verbs.append(verb)
        return found_verbs
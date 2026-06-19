"""Verb canonicalization for resume bullet points.

Canonicalizes action verbs to the approved list and detects forbidden verbs.
"""

from __future__ import annotations

import re
from typing import Any

_WORD_RE = re.compile(r"\b[\w']+\b")


class VerbCanonicalizer:
    """Canonicalize action verbs to the approved list."""

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
    CANONICAL_VERBS = _CANONICAL_VERBS

    _FORBIDDEN_VERBS: list[str] = [
        "pioneered",
        "spearheaded",
        "orchestrated",
        "architected",
        "revolutionized",
        "transformed",
    ]
    FORBIDDEN_VERBS = _FORBIDDEN_VERBS

    @classmethod
    def canonicalize(cls, text: str) -> list[str]:
        return canonicalize(cls, text)

    @classmethod
    def check_for_forbidden_verbs(cls, text: str) -> list[str]:
        return check_for_forbidden_verbs(cls, text)


def _resolve_catalog(source: Any, attr_names: tuple[str, str]) -> Any:
    primary, fallback = attr_names
    value = getattr(source, primary, None)
    if value is None:
        value = getattr(source, fallback)
    return value


def _canonical_lookup(source: Any) -> dict[str, str]:
    canonical_verbs = _resolve_catalog(source, ("CANONICAL_VERBS", "_CANONICAL_VERBS"))
    lookup: dict[str, str] = {}
    for canonical_form, variants in canonical_verbs.items():
        for variant in variants:
            lookup[variant.lower()] = canonical_form
    return lookup


def _forbidden_lookup(source: Any) -> set[str]:
    forbidden_verbs = _resolve_catalog(source, ("FORBIDDEN_VERBS", "_FORBIDDEN_VERBS"))
    return {verb.lower() for verb in forbidden_verbs}


def canonicalize(self: Any, text: str) -> list[str]:
    """Extract and canonicalize verbs from text."""
    lookup = _canonical_lookup(self)
    found: list[str] = []
    seen: set[str] = set()
    for token in _WORD_RE.findall(str(text).lower()):
        canonical_form = lookup.get(token)
        if canonical_form and canonical_form not in seen:
            found.append(canonical_form)
            seen.add(canonical_form)
    return found


def check_for_forbidden_verbs(self: Any, text: str) -> list[str]:
    """Check for forbidden verbs in the text."""
    forbidden = _forbidden_lookup(self)
    found_verbs: list[str] = []
    for token in _WORD_RE.findall(str(text).lower()):
        if token in forbidden:
            found_verbs.append(token)
    return found_verbs


__all__ = [
    "VerbCanonicalizer",
    "canonicalize",
    "check_for_forbidden_verbs",
]

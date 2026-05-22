"""Deterministic display-text contracts shared by IBM/Unify narrative lanes."""

from __future__ import annotations

import re
from typing import Any

# Prompt-only boundary language must never appear in narrative_sentence (display).
IBM_META_DISCLAIMER_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.I)
    for p in (
        r"\bwithout\s+claiming\b",
        r"\bwithout\s+asserting\b",
        r"\bnot\s+claiming\b",
        r"\bnot\s+asserting\b",
        r"\bdid\s+not\s+claim\b",
        r"\bdid\s+not\s+assert\b",
    )
)

IBM_NARRATIVE_CAREER_BRIDGE_PHRASES: tuple[str, ...] = (
    "supported later",
    "subsequent roles",
    "later production ai",
    "production ai platform leadership in subsequent",
    "without claiming ibm",
    "without asserting ibm",
)

ACCEPTED_FINALIZED_COMPANION_STATUS = "ACCEPTED_FINALIZED"


def ibm_meta_disclaimer_hits(text: str) -> list[str]:
    """Return matched meta-disclaimer subpatterns in display prose."""
    hits: list[str] = []
    for pat in IBM_META_DISCLAIMER_PATTERNS:
        m = pat.search(text or "")
        if m:
            hits.append(m.group(0))
    return hits


def check_ibm_narrative_no_meta_disclaimer_in_display(narrative_sentence: str) -> tuple[bool, list[str]]:
    hits = ibm_meta_disclaimer_hits(narrative_sentence)
    return (not hits, hits)


def career_bridge_phrase_hits(text: str) -> list[str]:
    tl = (text or "").lower()
    return [p for p in IBM_NARRATIVE_CAREER_BRIDGE_PHRASES if p in tl]

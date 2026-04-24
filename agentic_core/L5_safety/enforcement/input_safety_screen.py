"""Input safety screen — regex-based ingress safety classifier.

Closes gap G-05: no prompt-injection / PII / jailbreak screen existed at ingress.
This module provides a cheap, deterministic rule-based screen that runs between
E4 (quota) and E5 (normalize) in the ingress pipeline. It emits tripwire flags
mapped to rejection codes::

    INJECTION_DETECTED  → E_INJECTION_DETECTED
    PII_DETECTED        → E_PII_DETECTED
    JAILBREAK_DETECTED  → E_JAILBREAK_DETECTED

A cheap-model classifier can be plugged in later by wrapping this screen with
an :class:`InputSafetyScreen`-compatible class. Patterns here are intentionally
conservative — tuned to minimise false positives; adversarial-red-team tuning
belongs in a follow-up wave.

Layer authority: L5 (policy plane) — read/screen only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable


class SafetyFlag(str, Enum):
    """Flags emitted by the safety screen."""

    INJECTION_DETECTED = "INJECTION_DETECTED"
    PII_DETECTED = "PII_DETECTED"
    JAILBREAK_DETECTED = "JAILBREAK_DETECTED"


@dataclass(frozen=True)
class SafetyScreenResult:
    """Result of a safety screen pass over a payload string.

    ``tripwire`` is True if any flag was detected. Callers that want
    finer-grained control inspect ``flags``.
    """

    tripwire: bool
    flags: tuple[SafetyFlag, ...]
    matched_fragments: tuple[str, ...]


@runtime_checkable
class InputSafetyScreen(Protocol):
    """Protocol for ingress safety screening."""

    def screen(self, payload_text: str) -> SafetyScreenResult:
        """Return a :class:`SafetyScreenResult` for ``payload_text``."""

        ...


# ---------------------------------------------------------------------------
# Pattern tables — conservative, documented, reviewable.
# ---------------------------------------------------------------------------

# Prompt-injection / instruction-override patterns. Word-boundary anchored.
_INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bignore\s+(all\s+)?(previous|prior|above)\s+instructions?\b", re.IGNORECASE),
    re.compile(r"\bdisregard\s+(all\s+)?(previous|prior|above)\s+instructions?\b", re.IGNORECASE),
    re.compile(r"\b(you\s+are\s+now|from\s+now\s+on,?\s+you\s+are)\b", re.IGNORECASE),
    re.compile(r"\bforget\s+everything\s+(above|before|prior)\b", re.IGNORECASE),
    re.compile(r"\bnew\s+(system\s+)?prompt\s*:", re.IGNORECASE),
    re.compile(r"<\s*system\s*>.*?instruction", re.IGNORECASE | re.DOTALL),
)

# Jailbreak personas / known bypass triggers.
_JAILBREAK_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(DAN|do\s+anything\s+now)\b", re.IGNORECASE),
    re.compile(r"\bjailbreak\b", re.IGNORECASE),
    re.compile(r"\bdeveloper\s+mode\s+(enabled|on)\b", re.IGNORECASE),
    re.compile(r"\bpretend\s+you\s+have\s+no\s+(rules|restrictions|guidelines)\b", re.IGNORECASE),
    re.compile(r"\bact\s+as\s+if\s+you\s+have\s+no\s+content\s+policy\b", re.IGNORECASE),
)

# PII patterns — conservative; full PII detection is a separate hardening wave.
_PII_PATTERNS: tuple[re.Pattern[str], ...] = (
    # US SSN (XXX-XX-XXXX) — must be surrounded by word boundaries
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    # Credit card-ish — 13-19 digits, optionally separated
    re.compile(r"\b(?:\d[ -]?){13,19}\b"),
    # Email address
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
)


def _scan(patterns: tuple[re.Pattern[str], ...], text: str, max_fragments: int = 3) -> list[str]:
    hits: list[str] = []
    for pattern in patterns:
        for match in pattern.finditer(text):
            fragment = match.group(0)
            if len(fragment) > 80:
                fragment = fragment[:77] + "..."
            hits.append(fragment)
            if len(hits) >= max_fragments:
                return hits
    return hits


class RegexInputSafetyScreen:
    """Default regex-based implementation of :class:`InputSafetyScreen`.

    Thread-safe: precompiled patterns, no mutable state.
    """

    def __init__(
        self,
        *,
        detect_injection: bool = True,
        detect_jailbreak: bool = True,
        detect_pii: bool = True,
        max_scan_chars: int = 20_000,
    ) -> None:
        self._detect_injection = detect_injection
        self._detect_jailbreak = detect_jailbreak
        self._detect_pii = detect_pii
        self._max_scan_chars = int(max_scan_chars)

    def screen(self, payload_text: str) -> SafetyScreenResult:
        if not isinstance(payload_text, str):
            # Non-string payloads are out of scope for this screen — defer to E2.
            return SafetyScreenResult(tripwire=False, flags=(), matched_fragments=())
        if not payload_text:
            return SafetyScreenResult(tripwire=False, flags=(), matched_fragments=())

        # Bound scan cost: oversized payloads are E2's concern; we scan the prefix.
        sample = payload_text[: self._max_scan_chars]

        flags: list[SafetyFlag] = []
        fragments: list[str] = []

        if self._detect_injection:
            hits = _scan(_INJECTION_PATTERNS, sample)
            if hits:
                flags.append(SafetyFlag.INJECTION_DETECTED)
                fragments.extend(hits)

        if self._detect_jailbreak:
            hits = _scan(_JAILBREAK_PATTERNS, sample)
            if hits:
                flags.append(SafetyFlag.JAILBREAK_DETECTED)
                fragments.extend(hits)

        if self._detect_pii:
            hits = _scan(_PII_PATTERNS, sample)
            if hits:
                flags.append(SafetyFlag.PII_DETECTED)
                fragments.extend(hits)

        return SafetyScreenResult(
            tripwire=bool(flags),
            flags=tuple(flags),
            matched_fragments=tuple(fragments[:9]),
        )


def extract_screen_text(payload: object) -> str:
    """Best-effort flattening of a payload into a scannable string.

    Recurses into dicts/lists and concatenates string leaves. Bounded at
    64 KB of output to bound downstream scan cost.
    """

    buf: list[str] = []
    budget = 64 * 1024

    def walk(obj: object) -> None:
        nonlocal budget
        if budget <= 0:
            return
        if isinstance(obj, str):
            take = obj[: max(0, budget)]
            buf.append(take)
            budget -= len(take)
            return
        if isinstance(obj, dict):
            for v in obj.values():
                walk(v)
                if budget <= 0:
                    return
            return
        if isinstance(obj, (list, tuple)):
            for v in obj:
                walk(v)
                if budget <= 0:
                    return
            return
        # Primitives (int, float, bool, None) — skip; no text content.

    walk(payload)
    return "\n".join(buf)


__all__ = [
    "InputSafetyScreen",
    "RegexInputSafetyScreen",
    "SafetyFlag",
    "SafetyScreenResult",
    "extract_screen_text",
]

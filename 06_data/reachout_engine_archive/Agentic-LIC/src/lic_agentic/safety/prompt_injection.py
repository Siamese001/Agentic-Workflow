"""Prompt injection detection heuristics for the outreach stack."""  # pragma: no cover
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

_HIGH_RISK_KEYWORDS: Iterable[str] = (
    "ignore previous instructions",  # pragma: no cover
    "exfiltrate",  # pragma: no cover
    "password",  # pragma: no cover
    "disable safety",  # pragma: no cover
    "run shell",  # pragma: no cover
)
_MEDIUM_RISK_KEYWORDS: Iterable[str] = ("bypass", "override", "forget the rules")  # pragma: no cover


@dataclass(frozen=True)
class InjectionFinding:
    """Represents the outcome of a prompt-injection scan."""

    is_injection: bool
    severity: str
    rationale: str


def _score_prompt(prompt: str) -> tuple[int, str]:
    lowered = prompt.lower()
    for keyword in _HIGH_RISK_KEYWORDS:
        if keyword in lowered:
            return 2, f"High risk keyword detected: '{keyword}'"
    for keyword in _MEDIUM_RISK_KEYWORDS:
        if keyword in lowered:
            return 1, f"Medium risk keyword detected: '{keyword}'"
    return 0, "No malicious intent detected"


def detect_injection(prompt: str) -> InjectionFinding:
    """Detect whether *prompt* looks like a prompt-injection attempt."""

    score, rationale = _score_prompt(prompt)
    if score == 2:
        return InjectionFinding(True, "high", rationale)
    if score == 1:
        return InjectionFinding(True, "med", rationale)
    return InjectionFinding(False, "low", rationale)

# redaction.py
"""
L5 — Redaction Engine (v10_9)

Provides deterministic, rule-based redaction utilities.
No ML or external calls — pure pattern / heuristic based.
"""

from __future__ import annotations

import re
from typing import Dict, Any

from .safety_contracts import SafetyReport
from ..shared.exceptions import RedactionFailureError


# Very basic patterns; can be extended later.
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"\+?\d[\d\-() ]{7,}\d")
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def redact_text(text: str) -> SafetyReport:
    """
    Apply simple PII redaction rules to the given text.
    Returns a SafetyReport with redactions + warnings.
    """

    if text is None:
        raise RedactionFailureError("Cannot redact None text")

    original = str(text)
    redactions = []

    def _mask(pattern: re.Pattern, label: str, value: str) -> str:
        def _repl(match: re.Match) -> str:
            redactions.append(f"{label}:{match.group(0)}")
            return f"[REDACTED_{label}]"
        return pattern.sub(_repl, value)

    redacted = original
    redacted = _mask(_EMAIL_RE, "EMAIL", redacted)
    redacted = _mask(_PHONE_RE, "PHONE", redacted)
    redacted = _mask(_SSN_RE, "SSN", redacted)

    warnings = []
    if redactions:
        warnings.append("Potential PII was redacted from the content.")

    return SafetyReport(
        is_safe=True,
        redactions=redactions,
        warnings=warnings,
        suggested_rewrite=redacted if redacted != original else None,
        metadata={"original_length": len(original), "redacted_length": len(redacted)},
    )


def redact_payload(payload: Dict[str, Any]) -> SafetyReport:
    """
    Redact common text-bearing fields in a generic payload.
    Focuses on 'content' and 'message' fields if present.
    """

    content = str(payload.get("content", "")) if payload.get("content") is not None else ""
    report = redact_text(content)
    return report

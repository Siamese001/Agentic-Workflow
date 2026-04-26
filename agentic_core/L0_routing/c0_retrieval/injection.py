"""Prompt-injection / instruction-payload detection — guard for C0.I2 + G10.

Spec invariants:
- C0.I2: Retrieved text is data, never instruction.
- G10 INJECT: Is retrieved text safely classified as data?
  Fail behavior: Quarantine / strip / reject instruction-like payload.
- Failure mode: Prompt injection via retrieved text (line 939).

This module ONLY detects + marks. It never modifies semantic intent — the
shape stage (C0.4) is responsible for moving quarantined items to EXCLUDED.
"""

from __future__ import annotations

import re

# Patterns that indicate retrieved text is trying to act as instructions.
# Conservative — false positives are tolerable; false negatives are fatal.
_INJECTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_previous_instructions", re.compile(r"\bignore\s+(?:all\s+|the\s+)?(?:previous|prior|above)?\s*(?:instructions?|prompts?|rules?)\b", re.I)),
    ("system_role_injection", re.compile(r"^\s*(system|assistant|user)\s*[:>\]]", re.I | re.M)),
    ("override_safety", re.compile(r"\b(override|bypass|disable|disregard)\s+(safety|guard|policy|rules?|restrictions?|filter)\b", re.I)),
    ("jailbreak_persona", re.compile(r"\b(you\s+are\s+now|pretend\s+to\s+be|act\s+as|roleplay\s+as)\s+(an?\s+)?(unrestricted|jailbroken|dan|evil|uncensored)\b", re.I)),
    ("api_credential_request", re.compile(r"\b(reveal|print|show|leak|dump)\s+(your\s+)?(system\s+prompt|instructions|api\s+key|token|secret|credential)\b", re.I)),
    ("execute_directive", re.compile(r"\b(execute|run|invoke|call)\s+(the\s+following|this\s+code|arbitrary)\b", re.I)),
    ("policy_exfiltration", re.compile(r"\b(what\s+are\s+your|tell\s+me\s+your|describe\s+your)\s+(rules|instructions|guidelines|system\s+message)\b", re.I)),
    ("delimiter_breakout", re.compile(r"(```\s*end\s+of\s+context|---\s*end\s+of\s+context|<\s*/?\s*system\s*>|\[\s*/?\s*INST\s*\])", re.I)),
)


def detect_injection_markers(text: str) -> tuple[str, ...]:
    """Return a tuple of marker labels for any injection patterns found.

    Empty tuple = clean text. Markers are stable, deterministic labels
    suitable for telemetry and quarantine reasons.
    """
    if not text or not isinstance(text, str):
        return ()
    found: list[str] = []
    for label, pattern in _INJECTION_PATTERNS:
        if pattern.search(text):
            found.append(label)
    return tuple(found)


def neutralize_for_audit(text: str, *, max_len: int = 200) -> str:
    """Return a short, audit-safe summary of suspicious text.

    Used for logging only. NEVER used to feed prompt context.
    """
    if not text:
        return ""
    snippet = text[:max_len]
    return repr(snippet)

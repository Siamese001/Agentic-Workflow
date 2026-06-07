"""
G13 — Data Perimeter SAIF Sanitization.

Per ADR-070 L5 Guardrail Family Catalog (2026-04-29).
Phase: W4 P8 W4/P8.13 — `docs/archive/windsurf/legacy-tree/plans/w4-p8-guardrail-family-e93f8a.md`

# guardian: allow-empty-skeleton -- ADR-070 introduces G13 as a NEW concern
# with no pre-existing modules. This file establishes the contract surface.

Implements Google SAIF (Secure AI Framework) data-perimeter sanitization:

  - Inputs entering agent context (RAG retrievals, tool outputs, user content)
    pass through a sanitizer that strips/quarantines untrusted instructions
    embedded in data ("prompt injection in retrieved documents").
  - Sanitization is deterministic (same input → same output) and emits
    `agentic.sanitization.applied` spans for every transformation.

Distinct from G08 (egress firewall — output side) and G02 (ingress envelope —
client-side request gate). G13 is the supply-chain/perimeter inspection point
between data sources and the model context window.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class SanitizationResult:
    """Result of sanitizing one input item. Immutable."""

    sanitized_text: str
    findings: tuple[str, ...] = field(default_factory=tuple)  # e.g. ('embedded_instruction_stripped',)
    risk_score: float = 0.0  # 0.0 = clean, 1.0 = quarantine
    quarantined: bool = False


class DataPerimeterSanitizer(Protocol):
    """Protocol for SAIF-aligned sanitization. All inbound external data passes through."""

    def sanitize(self, text: str, source_kind: str) -> SanitizationResult:
        """Sanitize one item of inbound external text. source_kind disambiguates RAG vs tool-output."""
        ...


import re

# Patterns for embedded prompt-injection attempts. Each pattern carries a
# weight contributing to the overall risk score. Detection is conservative —
# false-positive friendly is preferred over false-negative because outputs
# go through a quarantine threshold rather than hard-block.
_INJECTION_PATTERNS: tuple[tuple[re.Pattern[str], str, float], ...] = (
    (re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions?|prompts?|rules?)", re.I),
     "ignore_previous_instructions", 0.45),
    (re.compile(r"disregard\s+(?:all\s+)?(?:the\s+)?(?:above|previous|earlier)\s+", re.I),
     "disregard_above", 0.40),
    (re.compile(r"\bsystem\s*:\s*", re.I), "system_role_injection", 0.30),
    (re.compile(r"\b(?:assistant|user)\s*:\s*", re.I), "role_marker_injection", 0.20),
    (re.compile(r"<\|?/?(?:s|im_start|im_end|tool_call|system|user|assistant)\|?>", re.I),
     "chat_template_token", 0.35),
    (re.compile(r"\bnew\s+instructions?\s*:", re.I), "new_instructions_marker", 0.30),
    (re.compile(r"\byou\s+(?:are|must)\s+now\s+", re.I), "role_override_attempt", 0.25),
    (re.compile(r"\bact\s+as\s+(?:a|an|the)\s+", re.I), "act_as_attempt", 0.15),
    (re.compile(r"\b(?:reveal|print|output|show)\s+(?:your|the)\s+(?:system\s+)?prompt", re.I),
     "prompt_extraction_attempt", 0.50),
)

_QUARANTINE_THRESHOLD = 0.70  # risk_score above this → quarantined=True


class DefaultDataPerimeterSanitizer:
    """Production SAIF-aligned sanitizer.

    Strategy:
      1. Scan input against the injection-pattern list.
      2. For each match, accumulate findings and risk_score.
      3. If risk_score < quarantine_threshold: replace each matched span
         with a redaction marker '[REDACTED:<finding_id>]' and return.
      4. If risk_score >= quarantine_threshold: return empty string with
         quarantined=True so the caller short-circuits the model call.

    Deterministic: same input → same output. No clock reads, no I/O.
    """

    def __init__(self, quarantine_threshold: float = _QUARANTINE_THRESHOLD) -> None:
        if not 0.0 < quarantine_threshold <= 1.0:
            raise ValueError("quarantine_threshold must be in (0, 1]")
        self._threshold = quarantine_threshold

    def sanitize(self, text: str, source_kind: str) -> SanitizationResult:
        if not text:
            return SanitizationResult(sanitized_text="")

        findings: list[str] = []
        risk_score = 0.0
        sanitized = text

        for pat, finding_id, weight in _INJECTION_PATTERNS:
            matches = list(pat.finditer(sanitized))
            if not matches:
                continue
            findings.append(f"{finding_id}:{len(matches)}")
            risk_score = min(1.0, risk_score + weight * len(matches))
            sanitized = pat.sub(f"[REDACTED:{finding_id}]", sanitized)

        # source_kind contributes a small base risk multiplier — RAG retrievals
        # are higher-risk than tool-output by convention.
        if source_kind == "rag" and findings:
            risk_score = min(1.0, risk_score * 1.1)

        quarantined = risk_score >= self._threshold
        if quarantined:
            return SanitizationResult(
                sanitized_text="",
                findings=tuple(findings) + (f"quarantined_at_threshold:{self._threshold:.2f}",),
                risk_score=risk_score,
                quarantined=True,
            )
        return SanitizationResult(
            sanitized_text=sanitized,
            findings=tuple(findings),
            risk_score=risk_score,
            quarantined=False,
        )


def default_sanitizer(
    quarantine_threshold: float = _QUARANTINE_THRESHOLD,
) -> DataPerimeterSanitizer:
    """Return the production sanitizer."""
    return DefaultDataPerimeterSanitizer(quarantine_threshold=quarantine_threshold)


__all__ = [
    "SanitizationResult",
    "DataPerimeterSanitizer",
    "DefaultDataPerimeterSanitizer",
    "default_sanitizer",
]

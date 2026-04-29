"""
G13 — Data Perimeter SAIF Sanitization.

Per ADR-070 L5 Guardrail Family Catalog (2026-04-29).
Phase: W4 P8 W4/P8.13 — `.windsurf/plans/w4-p8-guardrail-family-e93f8a.md`

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


def default_sanitizer() -> DataPerimeterSanitizer:
    """Production sanitizer. Implementation is W4 P8.13 work."""
    raise NotImplementedError(
        "G13 SAIF data perimeter sanitizer implementation pending — see ADR-070 + "
        ".windsurf/plans/w4-p8-guardrail-family-e93f8a.md W4 P8.13"
    )


__all__ = ["SanitizationResult", "DataPerimeterSanitizer", "default_sanitizer"]

"""
G08 — Egress Output-Side AI Firewall.

Per ADR-070 L5 Guardrail Family Catalog (2026-04-29).
Phase: W4 P8 W4/P8.08 — `.windsurf/plans/w4-p8-guardrail-family-e93f8a.md`

The G08 firewall inspects every model-generated output BEFORE it crosses the
process boundary (returned to user, posted to network, written to UWG).
Distinct from G13 (G13 inspects INBOUND data; G08 inspects OUTBOUND model
output).

Detection categories:

  - PII leak: SSN-like, email-like, phone-like, credit-card-like patterns
  - Credential leak: AWS keys, GitHub tokens, generic API-key shapes
  - System-prompt regurgitation: model parroting back its own instructions
  - URL exfiltration: outbound URLs pointing at non-allowlisted domains

Strategy mirrors G13: deterministic regex scanning, weighted risk score,
optional redaction below threshold, hard block (empty output) at/above
threshold.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class EgressInspectionResult:
    """Result of inspecting one outbound model output. Immutable."""

    inspected_text: str  # may be redacted; empty if blocked
    findings: tuple[str, ...] = field(default_factory=tuple)
    risk_score: float = 0.0
    blocked: bool = False


class EgressFirewall(Protocol):
    """Protocol — every model output passes through this before crossing the boundary."""

    def inspect(self, text: str, target_kind: str) -> EgressInspectionResult:
        """Inspect outbound text. target_kind ∈ {'user', 'network', 'uwg'}."""
        ...


# Detection patterns. Higher weights = more decisive single-match blockers.
_EGRESS_PATTERNS: tuple[tuple[re.Pattern[str], str, float], ...] = (
    # Credentials — single match should block
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "aws_access_key_id", 0.85),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), "google_api_key", 0.85),
    (re.compile(r"\bgh[ousrp]_[A-Za-z0-9_]{36,}\b"), "github_token", 0.85),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"), "slack_token", 0.85),
    (re.compile(r"\b(?:sk|pk)-[A-Za-z0-9]{20,}\b"), "openai_or_stripe_key", 0.80),
    # PII — multiple matches typically required to block
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "ssn_like", 0.40),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "email_like", 0.10),
    (re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"), "phone_like", 0.15),
    (re.compile(r"\b(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2}|6011)[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
     "credit_card_like", 0.45),
    # Self-disclosure
    (re.compile(r"\b(?:I am|I'm)\s+(?:a\s+)?(?:large\s+)?language\s+model\b", re.I),
     "model_self_identification", 0.10),
    (re.compile(r"\bmy\s+system\s+prompt\s+(?:says|is|contains)\b", re.I),
     "system_prompt_regurgitation", 0.55),
)

_BLOCK_THRESHOLD = 0.70


class DefaultEgressFirewall:
    """Production-grade egress firewall."""

    def __init__(
        self,
        block_threshold: float = _BLOCK_THRESHOLD,
        url_allowlist: frozenset[str] | None = None,
    ) -> None:
        if not 0.0 < block_threshold <= 1.0:
            raise ValueError("block_threshold must be in (0, 1]")
        self._threshold = block_threshold
        self._allow = url_allowlist or frozenset()

    def inspect(self, text: str, target_kind: str) -> EgressInspectionResult:
        if not text:
            return EgressInspectionResult(inspected_text="")

        findings: list[str] = []
        risk_score = 0.0
        inspected = text

        for pat, finding_id, weight in _EGRESS_PATTERNS:
            matches = list(pat.finditer(inspected))
            if not matches:
                continue
            findings.append(f"{finding_id}:{len(matches)}")
            risk_score = min(1.0, risk_score + weight * len(matches))
            inspected = pat.sub(f"[REDACTED:{finding_id}]", inspected)

        # URL exfiltration check — applies only when target_kind == 'network'
        if target_kind == "network":
            url_re = re.compile(r"https?://([^\s/]+)")
            for m in url_re.finditer(inspected):
                domain = m.group(1).lower()
                if domain not in self._allow:
                    findings.append(f"url_not_allowlisted:{domain}")
                    risk_score = min(1.0, risk_score + 0.40)

        # network egress is higher risk than user-facing
        if target_kind == "network" and findings:
            risk_score = min(1.0, risk_score * 1.15)

        blocked = risk_score >= self._threshold
        if blocked:
            return EgressInspectionResult(
                inspected_text="",
                findings=tuple(findings) + (f"blocked_at_threshold:{self._threshold:.2f}",),
                risk_score=risk_score,
                blocked=True,
            )
        return EgressInspectionResult(
            inspected_text=inspected,
            findings=tuple(findings),
            risk_score=risk_score,
            blocked=False,
        )


def default_firewall(
    block_threshold: float = _BLOCK_THRESHOLD,
    url_allowlist: frozenset[str] | None = None,
) -> EgressFirewall:
    return DefaultEgressFirewall(block_threshold=block_threshold, url_allowlist=url_allowlist)


__all__ = [
    "EgressInspectionResult",
    "EgressFirewall",
    "DefaultEgressFirewall",
    "default_firewall",
]

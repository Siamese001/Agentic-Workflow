"""Healing Pattern Advisor Port — C0 informational-only pattern hints.

Called by dispatch_healing() after routing but before invocation.
Provides advisory metadata that can append reason_codes and adjust
confidence for audit, but CANNOT change tier selection or heal_confidence.

C0 Informational-Only Contract:
- MUST NOT modify heal routing thresholds (``routing_thresholds_ssot`` pairing).
- MUST NOT change tier selection.
- MUST NOT mutate heal_confidence used for routing.
- MAY append reason_codes for audit.
- MAY provide pattern_boost for audit (max 0.10).
"""

from __future__ import annotations

from typing import Protocol, TypedDict

_MAX_PATTERN_BOOST = 0.1


class PatternAdvice(TypedDict):
    """Advisory metadata from pattern matching (informational-only)."""

    pattern_match: bool
    pattern_name: str | None
    pattern_boost: float
    extra_reason_codes: tuple[str, ...]


class HealingPatternAdvisor(Protocol):
    """Read-only seam for C0 informational-only pattern hints."""

    def advise(self, healing_input) -> PatternAdvice:
        """Return advisory pattern metadata for healing_input.

        Parameters
        ----------
        healing_input : HealingInput
            The structured failure context.

        Returns
        -------
        PatternAdvice
            Advisory metadata.  pattern_boost is capped at _MAX_PATTERN_BOOST.
            This data MUST NOT be used to change tier or heal_confidence.
        """
        ...


class NullHealingPatternAdvisor:
    """No-op advisor (default when no ML client is available)."""

    def advise(self, healing_input) -> PatternAdvice:
        return {"pattern_match": False, "pattern_name": None, "pattern_boost": 0.0, "extra_reason_codes": ()}


__all__ = ["HealingPatternAdvisor", "NullHealingPatternAdvisor", "PatternAdvice", "_MAX_PATTERN_BOOST"]

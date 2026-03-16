"""Default Healing Pattern Advisor — C0 informational-only implementation.

Uses MetaLearningClient.retrieve_healing_patterns() for advisory hints.
All pattern data is informational-only and cannot change routing tiers
or heal_confidence values.  Only appends reason_codes and provides
pattern_boost for audit.

Layer contract:
- Lives in system_learning layer.
- Uses protocol-injected MetaLearningClient (no direct L1 imports).
- Enforces C0 informational-only behavior.
"""

from __future__ import annotations

import logging
from typing import Any, NotRequired, TypedDict

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from system_learning.ports.healing_pattern_advisor import (
    _MAX_PATTERN_BOOST,
    NullHealingPatternAdvisor,
    PatternAdvice,
)

_emit_applies_guardrail("p0", "default_healing_pattern_advisor", "p0_governance")
_emit_reads_policy_state("p0", "default_healing_pattern_advisor", "policy_binding")
_emit_snapshots_state("p0", "default_healing_pattern_advisor", "state_snapshot")
emit_replay_key("p0", "default_healing_pattern_advisor")
emit_determinism_digest("p0", "default_healing_pattern_advisor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# MetaLearningClient import removed until implemented
# Optional: from system_learning.ports.meta_learning_client import MetaLearningClient

logger = logging.getLogger(__name__)


class HealingPattern(TypedDict):
    """Schema for a healing pattern from MetaLearningClient."""

    pattern_id: str
    pattern_name: str
    confidence_boost: NotRequired[float]  # Advisory only
    description: NotRequired[str]


class DefaultHealingPatternAdvisor:
    """Concrete advisor that queries MetaLearningClient for patterns.

    Enforces C0 informational-only contract: pattern data is advisory only
    and cannot affect routing decisions.
    """

    def __init__(self, ml_client: Any = None) -> None:
        self._ml_client = ml_client

    def advise(self, healing_input) -> PatternAdvice:
        """Return advisory pattern metadata for healing_input.

        This method is C0 informational-only:
        - Does NOT modify routing thresholds
        - Does NOT change tier selection
        - Does NOT mutate heal_confidence
        - Only provides metadata for audit
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DefaultHealingPatternAdvisor.advise")

        if self._ml_client is None:
            return NullHealingPatternAdvisor().advise(healing_input)

        try:
            patterns = self._ml_client.retrieve_healing_patterns(
                error_signature=healing_input.error_signature
            )
        # guardian: allow-silent-swallow
        except Exception as exc:  # guardian: allow-silent-swallower
            logger.warning(
                "pattern_advisor_query_failed",
                extra={
                    "error_signature": healing_input.error_signature,
                    "exception": str(exc),
                    "trace_id": healing_input.trace_id,
                },
            )
            return NullHealingPatternAdvisor().advise(healing_input)

        if not patterns:
            return {
                "pattern_match": False,
                "pattern_name": None,
                "pattern_boost": 0.0,
                "extra_reason_codes": (),
            }

        # Take the highest-confidence pattern (advisory only)
        best = max(patterns, key=lambda p: p.get("confidence_boost", 0.0))
        boost = min(best.get("confidence_boost", 0.0), _MAX_PATTERN_BOOST)

        extra_reason_codes = []
        if boost > 0:
            extra_reason_codes.append(f"pattern_boost={boost:.2f}")

        return {
            "pattern_match": True,
            "pattern_name": best.get("pattern_name"),
            "pattern_boost": boost,
            "extra_reason_codes": tuple(extra_reason_codes),
        }


__all__ = [
    "DefaultHealingPatternAdvisor",
    "HealingPattern",
]

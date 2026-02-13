"""
§Wave4.1 — TieredVigilanceEmitter: deterministic signal → tier mapping + emission.

Consumes normalized signal codes, assigns a VigilanceSeverity deterministically
via a fixed precedence table, and emits a VigilanceEventArtifact.

No uuid4, no wall-clock time, no elapsed_ms.
"""

from __future__ import annotations

from agentic_core.L0_maintenance.types.v15_p2_types import SemanticClockSnapshot
from agentic_core.L6_observability.types.vigilance_event_types import (
    VigilanceEventArtifact,
    VigilanceSeverity,
    build_deterministic_trace_id,
)

# =============================================================================
# §Wave4.1 — Fixed signal → severity mapping table
# =============================================================================
# Signals not in the table default to LOW.

_SIGNAL_SEVERITY: dict[str, VigilanceSeverity] = {
    # CRITICAL signals
    "evacuation_alert": VigilanceSeverity.CRITICAL,
    "exfiltration_detected": VigilanceSeverity.CRITICAL,
    "total_system_failure": VigilanceSeverity.CRITICAL,
    # HIGH signals
    "budget_overflow": VigilanceSeverity.HIGH,
    "circuit_breaker_open": VigilanceSeverity.HIGH,
    "mro_violation": VigilanceSeverity.HIGH,
    "import_cycle": VigilanceSeverity.HIGH,
    "stale_write_incident": VigilanceSeverity.HIGH,
    # MEDIUM signals
    "guardian_fail": VigilanceSeverity.MEDIUM,
    "policy_drift": VigilanceSeverity.MEDIUM,
    "anomalous_probe": VigilanceSeverity.MEDIUM,
    "token_drain": VigilanceSeverity.MEDIUM,
    # LOW signals (explicit)
    "info_metric": VigilanceSeverity.LOW,
    "routine_check": VigilanceSeverity.LOW,
}

_SEVERITY_RANK: dict[VigilanceSeverity, int] = {
    VigilanceSeverity.LOW: 0,
    VigilanceSeverity.MEDIUM: 1,
    VigilanceSeverity.HIGH: 2,
    VigilanceSeverity.CRITICAL: 3,
}


def classify_signals(signals: list[str]) -> VigilanceSeverity:
    """§Wave4.1 — Deterministic tier from signals.

    Stable: sorted signals, fixed precedence table, highest severity wins.
    """
    if not signals:
        return VigilanceSeverity.LOW

    max_severity = VigilanceSeverity.LOW
    for sig in signals:
        sev = _SIGNAL_SEVERITY.get(sig, VigilanceSeverity.LOW)
        if _SEVERITY_RANK[sev] > _SEVERITY_RANK[max_severity]:
            max_severity = sev

    return max_severity


def emit_vigilance_event(
    signals: list[str],
    semantic_clock: SemanticClockSnapshot,
    event_type: str = "VIGILANCE_DETECTION",
    policy_config_hash: str = "",
) -> VigilanceEventArtifact:
    """§Wave4.1 — Build a VigilanceEventArtifact deterministically.

    1. Sort + deduplicate signals
    2. Classify tier via fixed table
    3. Generate deterministic trace_id (SHA-256 of tick + signals)
    4. Return frozen artifact
    """
    normalized = tuple(sorted(set(signals)))
    tier = classify_signals(list(normalized))
    trace_id = build_deterministic_trace_id(normalized, semantic_clock.tick)

    return VigilanceEventArtifact(
        event_type=event_type,
        semantic_clock=semantic_clock,
        vigilance_tier=tier,
        signals=normalized,
        trace_id=trace_id,
        policy_config_hash=policy_config_hash,
    )


__all__ = [
    "classify_signals",
    "emit_vigilance_event",
]

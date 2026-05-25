"""RoutingOutcomeAdapter — bridges AgenticRouter outcomes to MetaLearningBus.

After each router.route() call resolves, wrap the RoutingDecision into a
MetaLearningChangePackage(kind="routing_outcome") and enqueue it on the
L0 MetaLearningBus for downstream system_learning processing.

Design invariants
-----------------
1. Proposal-only — never mutates routing, config, or safety state.
2. Fail-open — a failure to enqueue MUST NOT propagate to the caller.
3. No wall-clock reads; timestamp_utc is caller-supplied.
4. Pure function interface — no global mutable state.
5. C0_INFORMATIONAL influence class only.

Layer: L0_routing
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.L6_system_learning.meta_learning_bus import (
    MetaLearningBus,
    MetaLearningChangePackage,
)

from agentic_core.L0_routing.reasoning.agentic_router import RoutingDecision
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_execution_trace,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "routing_outcome_adapter")
logger = logging.getLogger(__name__)

_KIND = "routing_outcome"


def _outcome_from_decision(decision: RoutingDecision) -> str:
    """Derive a canonical outcome string from a RoutingDecision."""
    if decision.error:
        return "SAFE_FAILURE"
    if decision.result is not None:
        return "SUCCESS"
    return "UNKNOWN"


def build_routing_outcome_package(
    decision: RoutingDecision,
    timestamp_utc: int,
) -> MetaLearningChangePackage:
    """Build a MetaLearningChangePackage from a resolved RoutingDecision.

    Args:
        decision:      The RoutingDecision returned by AgenticRouter.route().
        timestamp_utc: Caller-supplied Unix timestamp (no wall-clock read).

    Returns:
        Immutable, deterministically-hashed MetaLearningChangePackage.
    """
    outcome = _outcome_from_decision(decision)
    payload: dict[str, Any] = {
        "intent": decision.intent,
        "target_name": decision.target_name,
        "confidence": round(decision.confidence, 6),
        "outcome": outcome,
        "has_error": bool(decision.error),
        "timestamp_utc": timestamp_utc,
        "influence_class": "C0_INFORMATIONAL",
    }
    return MetaLearningChangePackage.create(
        trace_id=decision.metadata.get("trace_id", decision.target_name),
        kind=_KIND,
        payload=payload,
    )


class RoutingOutcomeAdapter:
    """Enqueues routing outcome packages onto an injected MetaLearningBus.

    Usage::

        bus = MetaLearningBus()
        adapter = RoutingOutcomeAdapter(bus=bus)
        decision = await router.route(user_input)
        adapter.emit(decision, timestamp_utc=now)

    Args:
        bus: The MetaLearningBus instance to enqueue packages onto.
    """

    def __init__(self, bus: MetaLearningBus) -> None:
        self._bus = bus

    def emit(self, decision: RoutingDecision, timestamp_utc: int) -> bool:
        """Wrap decision into a change package and enqueue on the bus.

        Args:
            decision:      Resolved RoutingDecision from AgenticRouter.route().
            timestamp_utc: Caller-supplied Unix timestamp.

        Returns:
            True if enqueued successfully, False on any error (fail-open).
        """
        try:
            pkg = build_routing_outcome_package(decision, timestamp_utc)
            self._bus.enqueue(pkg)
            logger.debug(
                "RoutingOutcomeAdapter.emit: enqueued %s target=%r confidence=%.4f outcome=%s",
                _KIND,
                decision.target_name,
                decision.confidence,
                pkg.payload.get("outcome", "UNKNOWN"),
            )
            return True
        except (ValueError, TypeError, RuntimeError) as exc:  # guardian: allow-silent-swallow
            logger.warning("RoutingOutcomeAdapter.emit: failed to enqueue: %s", exc)
            return False


__all__ = [
    "RoutingOutcomeAdapter",
    "build_routing_outcome_package",
]

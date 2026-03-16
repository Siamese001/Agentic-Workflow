"""GAP-E: L4-backed MetaPriorProvider — wired into healing_tier_dispatcher.

Reads historical success rates from the L4 healing outcome store and provides
them as priors for the tier routing decision.

Wire-in: inject into HealingTierDispatcher via constructor or set_prior_provider().
"""

from __future__ import annotations

import logging
from typing import Any

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

_emit_applies_guardrail("p0", "l4_meta_prior_provider", "p0_governance")
_emit_reads_policy_state("p0", "l4_meta_prior_provider", "policy_binding")
_emit_snapshots_state("p0", "l4_meta_prior_provider", "state_snapshot")
emit_replay_key("p0", "l4_meta_prior_provider")
emit_determinism_digest("p0", "l4_meta_prior_provider")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)
_NEUTRAL_PRIOR: float = 0.5


class L4MetaPriorProvider:
    """L4-backed implementation of MetaPriorProvider.

    Reads from the healing outcome store and returns a prior in [0.0, 1.0].
    Falls back to neutral (0.50) when no data is available.

    Invariant: Seeded store → routing selects LOCAL_AGENT for borderline input
    (borderline = heal_confidence near the X threshold).
    """

    def __init__(self, outcome_store: Any | None = None) -> None:
        """
        Args:
            outcome_store: Object with .get_success_rate(error_signature) -> float | None.
                           If None, attempts to load the default L4 store.
        """
        self._store = outcome_store
        if self._store is None:
            self._store = self._load_default_store()

    def _load_default_store(self) -> Any | None:
        try:
            from system_learning.ports.healing_outcome_intake_store import HealingOutcomeIntakeStore

            return HealingOutcomeIntakeStore()
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("L4MetaPriorProvider: default store not available: %s", exc)
            return None

    def get_prior(self, error_signature: str) -> float:
        """Return historical success rate prior for error_signature.

        Returns float in [0.0, 1.0]. Returns 0.50 (neutral) when unknown.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "L4MetaPriorProvider.get_prior")

        if self._store is None:
            return _NEUTRAL_PRIOR
        try:
            rate = self._store.get_success_rate(error_signature)
            if rate is None:
                return _NEUTRAL_PRIOR
            return float(max(0.0, min(1.0, rate)))
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.warning(
                "L4MetaPriorProvider.get_prior(%r) error: %s — returning neutral", error_signature, exc
            )
            return _NEUTRAL_PRIOR


def wire_l4_prior_into_dispatcher(dispatcher: Any, outcome_store: Any | None = None) -> None:
    """Inject an L4MetaPriorProvider into a HealingTierDispatcher instance.

    Called once at startup, before any healing decisions are made.

    Args:
        dispatcher: HealingTierDispatcher instance.
        outcome_store: Optional pre-built store; uses default if None.
    """
    provider = L4MetaPriorProvider(outcome_store=outcome_store)
    if hasattr(dispatcher, "set_prior_provider"):
        dispatcher.set_prior_provider(provider)
        logger.info("L4MetaPriorProvider wired into %s", type(dispatcher).__name__)
    else:
        logger.warning(
            "wire_l4_prior_into_dispatcher: %s has no set_prior_provider() method", type(dispatcher).__name__
        )


__all__ = ["L4MetaPriorProvider", "wire_l4_prior_into_dispatcher", "_NEUTRAL_PRIOR"]

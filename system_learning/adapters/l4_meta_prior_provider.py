"""L4MetaPriorProvider — bridges HealingSuccessRateStore to MetaPriorProvider seam.

Gap 3 fix: healing_tier_router.route_healing_tier() accepts meta_prior_provider but
the live L4-backed provider was never wired. This module provides the adapter.

Contracts:
- get_prior() delegates to HealingSuccessRateStore.get_prior() (read-only).
- Falls back to NeutralMetaPriorProvider on cold start (no store / store raises).
- MUST NOT import agentic_core modules directly (layer boundary: system_learning only).
- MUST be synchronous and deterministic.
"""

from __future__ import annotations

import logging

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
from system_learning.ports.meta_prior_provider import (
    _NEUTRAL_PRIOR,
    NeutralMetaPriorProvider,
)

logger = logging.getLogger(__name__)

_neutral = NeutralMetaPriorProvider()


class L4MetaPriorProvider:
    """Live prior provider backed by HealingSuccessRateStore.

    Parameters
    ----------
    store:
        An instance of HealingSuccessRateStore. If None, falls back to neutral prior.
    """

    def __init__(self, store=None) -> None:
        self._store = store

    def get_prior(self, error_signature: str) -> float:
        """Return historical success-rate prior for error_signature.

        Delegates to store.get_prior(). Falls back to _NEUTRAL_PRIOR when:
        - store is None (cold start)
        - store raises any exception
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "L4MetaPriorProvider.get_prior")

        if self._store is None:
            return _NEUTRAL_PRIOR
        try:
            return self._store.get_prior(error_signature)
        except (AttributeError, KeyError, ValueError) as e:
            logger.debug(
                "L4MetaPriorProvider: store.get_prior raised; returning neutral",
                extra={"error_signature": error_signature, "error": str(e)},
                exc_info=True,
            )
            return _NEUTRAL_PRIOR

    @classmethod
    def from_default_store(cls) -> L4MetaPriorProvider:
        """Construct using the process-global default HealingSuccessRateStore."""
        from system_learning.engines.healing_success_rate_store import get_default_store

        return cls(store=get_default_store())


__all__ = ["L4MetaPriorProvider"]

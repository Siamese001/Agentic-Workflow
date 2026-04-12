"""Meta-Learning Bus Consumer — drains queue and applies outcomes to success-rate store.

Gap 2 fix: nothing was consuming the MetaLearningBus queue. Published packages
accumulated and were garbage-collected between runs.

Contracts:
- drain_and_apply() is synchronous, deterministic, and side-effect-free beyond store.
- Only processes kind == "healing_outcome" packages; others are logged and skipped.
- Returns exact count of processed packages.
- MUST NOT import agentic_core modules directly (layer boundary).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore
    from system_learning.meta_learning.meta_learning_bus import MetaLearningBus
logger = logging.getLogger(__name__)
_KIND_HEALING_OUTCOME = "healing_outcome"


def drain_and_apply(bus: MetaLearningBus, store: HealingSuccessRateStore) -> int:
    """Drain all packages from *bus* and apply healing outcomes to *store*.

    Parameters
    ----------
    bus:
        The MetaLearningBus instance to drain.
    store:
        The HealingSuccessRateStore to update with each healing outcome.

    Returns
    -------
    int
        Number of packages processed (regardless of kind).
    """
    processed = 0
    while True:
        pkg = bus.dequeue()
        if pkg is None:
            break
        processed += 1
        if pkg.kind != _KIND_HEALING_OUTCOME:
            logger.debug(
                "bus_consumer: skipping unknown kind",
                extra={"kind": pkg.kind, "trace_id": pkg.trace_id},
            )
            continue
        payload = pkg.payload
        error_signature = payload.get("error_signature", "")
        success = bool(payload.get("success", False))
        if not error_signature:
            logger.warning(
                "bus_consumer: missing error_signature in payload",
                extra={"trace_id": pkg.trace_id},
            )
            continue
        store.record_outcome(error_signature, success)
        logger.debug(
            "bus_consumer: applied outcome",
            extra={"error_signature": error_signature, "success": success, "trace_id": pkg.trace_id},
        )
    return processed


__all__ = ["drain_and_apply"]

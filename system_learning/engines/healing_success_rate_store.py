"""Healing Success Rate Store — deterministic, replay-reconstructable store.

Backed by a dict[str, float].  In production populated by
OutcomeWriteBackHook (Phase 2).  In tests seeded directly.

Layer contract:
- Lives in system_learning layer.
- Exposed to L2.3 ONLY via MetaPriorProvider seam.
- MUST NOT import agentic_core modules.

Determinism contract:
- All stored rates rounded to 6 decimals.
- export_state() returns snapshot for replay reconstruction.
- store_state_hash() returns deterministic content hash.
- Single-process invariant: _OWNER_PID guards against fork divergence.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)

_NEUTRAL_PRIOR: float = 0.50
_MIN_SAMPLE_SIZE: int = 5
_EMA_ALPHA: float = 0.10


class HealingSuccessRateStore:
    """Deterministic store of per-signature success rates.

    Single-process invariant: if _OWNER_PID differs from current pid,
    operations are no-ops that log a warning (prevents fork divergence).
    """

    def __init__(self) -> None:
        self._rates: dict[str, float] = {}
        self._counts: dict[str, int] = {}
        self._owner_pid: int = os.getpid()

    def _check_pid(self) -> bool:
        """Return True if current process owns this store."""
        if os.getpid() != self._owner_pid:
            logger.warning(
                "HealingSuccessRateStore: pid mismatch (owner=%d, current=%d); operation skipped",
                self._owner_pid,
                os.getpid(),
            )
            return False
        return True

    def get_prior(self, error_signature: str) -> float:
        """Return current success-rate prior for error_signature.

        Returns _NEUTRAL_PRIOR when fewer than _MIN_SAMPLE_SIZE outcomes
        are recorded (dampening to avoid over-weighting early noisy data).
        """
        count = self._counts.get(error_signature, 0)
        if count < _MIN_SAMPLE_SIZE:
            return _NEUTRAL_PRIOR
        return self._rates.get(error_signature, _NEUTRAL_PRIOR)

    def record_outcome(self, error_signature: str, success: bool) -> None:
        """Update running success-rate average with a new outcome.

        Uses cumulative average during warm-up, then EMA.
        All stored values rounded to 6 decimals.
        """
        if not self._check_pid():
            return

        count = self._counts.get(error_signature, 0)
        current = self._rates.get(error_signature, _NEUTRAL_PRIOR)
        outcome_value = 1.0 if success else 0.0

        if count < _MIN_SAMPLE_SIZE:
            new_rate = round((current * count + outcome_value) / (count + 1), 6)
        else:
            new_rate = round((1.0 - _EMA_ALPHA) * current + _EMA_ALPHA * outcome_value, 6)

        # Clamp to [0.0, 1.0]
        new_rate = max(0.0, min(1.0, new_rate))

        self._rates[error_signature] = new_rate
        self._counts[error_signature] = count + 1

        self._log_update(error_signature, success, new_rate, count + 1)

    def _log_update(
        self,
        error_signature: str,
        success: bool,
        new_rate: float,
        new_count: int,
    ) -> None:
        """Structured telemetry for every update (never silent)."""
        logger.info(
            "success_rate_update",
            extra={
                "error_signature": error_signature,
                "success": success,
                "new_rate": new_rate,
                "observation_count": new_count,
                "owner_pid": self._owner_pid,
            },
        )

    def export_state(self) -> dict[str, Any]:
        """Deterministic snapshot for replay reconstruction."""
        return {
            "rates": dict(sorted(self._rates.items())),
            "counts": dict(sorted(self._counts.items())),
            "owner_pid": self._owner_pid,
        }

    def store_state_hash(self) -> str:
        """Deterministic content hash of current store state."""
        state = self.export_state()
        # Remove pid from hash (not part of logical state)
        hashable = {"rates": state["rates"], "counts": state["counts"]}
        canonical = json.dumps(hashable, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def import_state(self, state: dict[str, Any]) -> None:
        """Restore from exported snapshot (for replay/testing)."""
        self._rates = dict(state.get("rates", {}))
        self._counts = dict(state.get("counts", {}))

    def get_all(self) -> dict[str, float]:
        """Snapshot of all current priors (for audit)."""
        return dict(self._rates)

    def get_counts(self) -> dict[str, int]:
        """Snapshot of all observation counts."""
        return dict(self._counts)

    def reset(self) -> None:
        """Clear all state (testing only)."""
        self._rates.clear()
        self._counts.clear()


# Module-level singleton
_default_store: HealingSuccessRateStore | None = None


def get_default_store() -> HealingSuccessRateStore:
    """Return the process-global default store (lazy-initialized)."""
    global _default_store
    if _default_store is None:
        _default_store = HealingSuccessRateStore()
    return _default_store


def reset_default_store() -> None:
    """[TESTING ONLY] Reset the process-global store."""
    global _default_store
    _default_store = None


__all__ = [
    "HealingSuccessRateStore",
    "get_default_store",
    "reset_default_store",
    "_MIN_SAMPLE_SIZE",
    "_NEUTRAL_PRIOR",
    "_EMA_ALPHA",
]

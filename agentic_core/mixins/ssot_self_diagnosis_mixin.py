"""
SSOT Self-Diagnosis Mixin — L4 Aggregate State Health Reader.

Provides self-diagnosis that:
  - Reads L4 aggregate state only (no writes)
  - Writes health status locally (not to L4)
  - No routing modification authority

Layer: L6 Observer
Authority: Read L4 state, write local health. No L4 mutation. No routing.
"""

from __future__ import annotations

import logging
import time
from typing import Any

_logger = logging.getLogger("SSOTSelfDiagnosis")


class SSOTSelfDiagnosisMixin:
    """Local health assessment based on L4 aggregate state.

    Reads ``active_policy_hash`` and ``is_replay_mode`` from ReplayGuardMixin.
    Health checks are recorded locally and never mutate L4 state.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_health_checks: list[dict[str, Any]] = []
        self._ssot_health_status: str = "HEALTHY"

    def run_health_check(self, check_name: str, passed: bool, details: str = "") -> dict[str, Any]:
        """Record a health check result.

        Parameters
        ----------
        check_name : str
            Name of the health check.
        passed : bool
            Whether the check passed.
        details : str
            Additional details.

        Returns
        -------
        dict
            The health check record.
        """
        record = {
            "check_name": check_name,
            "passed": passed,
            "details": details,
            "timestamp": time.time(),
            "policy_hash": getattr(self, "active_policy_hash", "unknown"),
            "replay_mode": getattr(self, "is_replay_mode", False),
        }
        self._ssot_health_checks.append(record)

        if not passed:
            self._ssot_health_status = "DEGRADED"
            _logger.warning("[SSOTHealth] DEGRADED: %s — %s", check_name, details)
        else:
            _logger.debug("[SSOTHealth] OK: %s", check_name)

        return record

    @property
    def health_status(self) -> str:
        """Current health status: HEALTHY or DEGRADED."""
        return self._ssot_health_status

    @property
    def health_checks(self) -> list[dict[str, Any]]:
        """All recorded health checks."""
        return list(self._ssot_health_checks)

    @property
    def failed_checks(self) -> list[dict[str, Any]]:
        """Health checks that failed."""
        return [c for c in self._ssot_health_checks if not c["passed"]]

    def reset_health(self) -> None:
        """Reset health status to HEALTHY and clear checks."""
        self._ssot_health_status = "HEALTHY"
        self._ssot_health_checks.clear()

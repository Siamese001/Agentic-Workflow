"""
SSOT State Validation Mixin — Pre/Post-Condition Guards for Healing.

Provides state validation that:
  - Enforces pre/post-conditions around healing decisions
  - Never swallows StateValidationError
  - Records structured failure in state
  - Policy-hash-scoped validation context

Layer: L2 Execution Aid
Authority: Validate only. No L4 mutation. No routing influence.
"""

from __future__ import annotations

import logging
import time
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

_logger = logging.getLogger("SSOTStateValidation")


class SSOTStateValidationError(Exception):
    """Raised when state validation fails. Must never be swallowed."""

    def __init__(self, condition: str, details: dict[str, Any] | None = None):
        self.condition = condition
        self.details = details or {}
        super().__init__(f"State validation failed: {condition}")


class SSOTStateValidationMixin:
    """Pre/post-condition validation for healing operations.

    Reads ``active_policy_hash`` and ``safety_status`` from ReplayGuardMixin.
    Validation failures are recorded in state and always raised.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_validation_failures: list[dict[str, Any]] = []

    def validate_precondition(
        self, condition_name: str, check: bool, details: dict[str, Any] | None = None
    ) -> None:
        """Assert a precondition before a healing operation.

        Parameters
        ----------
        condition_name : str
            Human-readable condition name.
        check : bool
            If False, raises SSOTStateValidationError.
        details : dict | None
            Additional context for the failure.

        Raises
        ------
        SSOTStateValidationError
            If check is False.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SSOTStateValidationMixin.validate_precondition")

        if check:
            return
        failure = {
            "type": "precondition",
            "condition": condition_name,
            "timestamp": time.time(),
            "policy_hash": getattr(self, "active_policy_hash", "unknown"),
            "details": details or {},
        }
        self._ssot_validation_failures.append(failure)
        state = getattr(self, "state", None)
        if isinstance(state, dict):
            state.setdefault("validation_failures", []).append(failure)
        _logger.error(
            "[SSOTValidation] Precondition FAILED: %s | policy_hash=%s",
            condition_name,
            failure["policy_hash"][:12],
        )
        raise SSOTStateValidationError(condition_name, details)

    def validate_postcondition(
        self, condition_name: str, check: bool, details: dict[str, Any] | None = None
    ) -> None:
        """Assert a postcondition after a healing operation.

        Same semantics as validate_precondition but tagged as postcondition.
        """
        if check:
            return
        failure = {
            "type": "postcondition",
            "condition": condition_name,
            "timestamp": time.time(),
            "policy_hash": getattr(self, "active_policy_hash", "unknown"),
            "details": details or {},
        }
        self._ssot_validation_failures.append(failure)
        state = getattr(self, "state", None)
        if isinstance(state, dict):
            state.setdefault("validation_failures", []).append(failure)
        _logger.error(
            "[SSOTValidation] Postcondition FAILED: %s | policy_hash=%s",
            condition_name,
            failure["policy_hash"][:12],
        )
        raise SSOTStateValidationError(condition_name, details)

    def validate_safety_cleared(self) -> None:
        """Assert that safety_status is CLEARED before proceeding.

        Raises SSOTStateValidationError if safety is not CLEARED.
        """
        status = getattr(self, "safety_status", "PENDING")
        self.validate_precondition("safety_status_cleared", status == "CLEARED", {"actual_status": status})

    def validate_policy_hash_stable(self) -> None:
        """Assert that policy hash has not drifted since construction.

        Raises SSOTStateValidationError if drift detected.
        """
        drifted = getattr(self, "policy_hash_drifted", lambda: False)()
        self.validate_precondition(
            "policy_hash_stable",
            not drifted,
            {
                "initial": getattr(self, "initial_policy_hash", "unknown"),
                "current": getattr(self, "active_policy_hash", "unknown"),
            },
        )

    @property
    def validation_failure_count(self) -> int:
        """Total validation failures recorded."""
        return len(self._ssot_validation_failures)

    @property
    def validation_failures(self) -> list[dict[str, Any]]:
        """All recorded validation failures."""
        return list(self._ssot_validation_failures)

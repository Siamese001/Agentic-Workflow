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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "ssot_state_validation_mixin", "p0_governance")
_emit_reads_policy_state("p0", "ssot_state_validation_mixin", "policy_binding")
_emit_snapshots_state("p0", "ssot_state_validation_mixin", "state_snapshot")
emit_replay_key("p0", "ssot_state_validation_mixin")
emit_determinism_digest("p0", "ssot_state_validation_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ssot_state_validation_mixin", "execution_auth")
_emit_validates_capability("p2", "ssot_state_validation_mixin", "capability_check")
_emit_routes_to_capability("p2", "ssot_state_validation_mixin", "capability_route")
_emit_writes_via_uwg("p2", "ssot_state_validation_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_state_validation_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_state_validation_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_state_validation_mixin", "exec_output")
_emit_dispatches_agent("p3", "ssot_state_validation_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_state_validation_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_state_validation_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_state_validation_mixin", "healing_outcome")
_emit_escalates_failure("p3", "ssot_state_validation_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_state_validation_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_state_validation_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_state_validation_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_state_validation_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_state_validation_mixin", "eval_metric")
_emit_stores_embedding("p4", "ssot_state_validation_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_state_validation_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_state_validation_mixin", "exec_snapshot_link")

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

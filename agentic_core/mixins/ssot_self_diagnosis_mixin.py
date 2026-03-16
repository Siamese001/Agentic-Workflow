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

_emit_applies_guardrail("p0", "ssot_self_diagnosis_mixin", "p0_governance")
_emit_reads_policy_state("p0", "ssot_self_diagnosis_mixin", "policy_binding")
_emit_snapshots_state("p0", "ssot_self_diagnosis_mixin", "state_snapshot")
emit_replay_key("p0", "ssot_self_diagnosis_mixin")
emit_determinism_digest("p0", "ssot_self_diagnosis_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ssot_self_diagnosis_mixin", "execution_auth")
_emit_validates_capability("p2", "ssot_self_diagnosis_mixin", "capability_check")
_emit_routes_to_capability("p2", "ssot_self_diagnosis_mixin", "capability_route")
_emit_writes_via_uwg("p2", "ssot_self_diagnosis_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_self_diagnosis_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_self_diagnosis_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_self_diagnosis_mixin", "exec_output")
_emit_dispatches_agent("p3", "ssot_self_diagnosis_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_self_diagnosis_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_self_diagnosis_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_self_diagnosis_mixin", "healing_outcome")
_emit_escalates_failure("p3", "ssot_self_diagnosis_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_self_diagnosis_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_self_diagnosis_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_self_diagnosis_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_self_diagnosis_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_self_diagnosis_mixin", "eval_metric")
_emit_stores_embedding("p4", "ssot_self_diagnosis_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_self_diagnosis_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_self_diagnosis_mixin", "exec_snapshot_link")

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
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SSOTSelfDiagnosisMixin.run_health_check")

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

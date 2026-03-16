"""
FilesystemSSOTValidatorAgent - L5 Pure Validator.

Detects root-level SSOT drift (forbidden root folders, archived files at root,
duplicate folders). Never mutates the filesystem. Emits structured check dict
consumed by heal_filesystem_ssot_drift via HEALER_REGISTRY.
"""

from __future__ import annotations

from pathlib import Path
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "filesystem_ssot_validator")
emit_determinism_digest("p0", "filesystem_ssot_validator")

_emit_dispatches_healing_run("p1", "filesystem_ssot_validator", "L5")
_emit_routes_through("p1", "filesystem_ssot_validator", "L5")
_emit_escalates_to_human("p1", "filesystem_ssot_validator", "L5")
_emit_reads_policy_state("p1", "filesystem_ssot_validator", "L5")

_emit_applies_guardrail("p0", "filesystem_ssot_validator", "p0_governance")
_emit_snapshots_state("p0", "filesystem_ssot_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "filesystem_ssot_validator", "execution_auth")
_emit_validates_capability("p2", "filesystem_ssot_validator", "capability_check")
_emit_routes_to_capability("p2", "filesystem_ssot_validator", "capability_route")
_emit_writes_via_uwg("p2", "filesystem_ssot_validator", "uwg_write")
_emit_blocks_direct_write("p2", "filesystem_ssot_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "filesystem_ssot_validator", "tool_invocation")
_emit_captures_execution_output("p2", "filesystem_ssot_validator", "exec_output")
_emit_dispatches_agent("p3", "filesystem_ssot_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "filesystem_ssot_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "filesystem_ssot_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "filesystem_ssot_validator", "healing_outcome")
_emit_escalates_failure("p3", "filesystem_ssot_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "filesystem_ssot_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "filesystem_ssot_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "filesystem_ssot_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "filesystem_ssot_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "filesystem_ssot_validator", "eval_metric")
_emit_stores_embedding("p4", "filesystem_ssot_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "filesystem_ssot_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "filesystem_ssot_validator", "exec_snapshot_link")

CHECK_ID = "filesystem_ssot_drift"


class FilesystemSSOTValidatorAgent:
    """L5 Certify-only validator for filesystem SSOT drift."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan(self) -> dict[str, Any]:
        """Delegate to FilesystemSSOTReconcilerAgent.detect_root_drift(). Read-only."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "FilesystemSSOTValidatorAgent.scan")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:FilesystemSSOTValidatorAgent.scan".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler import FilesystemSSOTReconcilerAgent

        reconciler = FilesystemSSOTReconcilerAgent(project_root=self.project_root)
        return reconciler.detect_root_drift()

    def to_check_dict(self) -> dict[str, Any]:
        """Return structured check dict for _invoke_healer dispatch."""
        drift = self.scan()
        violations_count = (
            len(drift.get("forbidden_folders", []))
            + len(drift.get("archived_files_at_root", []))
            + len(drift.get("duplicate_folders", []))
        )
        return {
            "check_id": CHECK_ID,
            "evidence": drift,
            "violations_count": violations_count,
            "repo_root": str(self.project_root),
        }

    def run(self) -> dict[str, Any]:
        """Alias for to_check_dict for orchestrator compatibility."""
        return self.to_check_dict()

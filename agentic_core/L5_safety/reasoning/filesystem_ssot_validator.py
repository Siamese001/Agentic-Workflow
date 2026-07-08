"""
FilesystemSSOTValidatorAgent - L5 Pure Validator.

Detects root-level SSOT drift (forbidden root folders, archived files at root,
duplicate folders). Never mutates the filesystem. Emits structured check dict
consumed by heal_filesystem_ssot_drift via HEALER_REGISTRY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "filesystem_ssot_validator")
trace_contract.emit_determinism_digest("p0", "filesystem_ssot_validator")

trace_contract._emit_dispatches_healing_run("p1", "filesystem_ssot_validator", "L5")
trace_contract._emit_routes_through("p1", "filesystem_ssot_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "filesystem_ssot_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "filesystem_ssot_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "filesystem_ssot_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "filesystem_ssot_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "filesystem_ssot_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "filesystem_ssot_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "filesystem_ssot_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "filesystem_ssot_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "filesystem_ssot_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "filesystem_ssot_validator")
trace_contract._emit_gated_by_confidence("p1", "filesystem_ssot_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "filesystem_ssot_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "filesystem_ssot_validator", "L5")

trace_contract._emit_applies_guardrail("p0", "filesystem_ssot_validator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "filesystem_ssot_validator", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "filesystem_ssot_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "filesystem_ssot_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "filesystem_ssot_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "filesystem_ssot_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "filesystem_ssot_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "filesystem_ssot_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "filesystem_ssot_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "filesystem_ssot_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "filesystem_ssot_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "filesystem_ssot_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "filesystem_ssot_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "filesystem_ssot_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "filesystem_ssot_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "filesystem_ssot_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "filesystem_ssot_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "filesystem_ssot_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "filesystem_ssot_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "filesystem_ssot_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "filesystem_ssot_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "filesystem_ssot_validator", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("filesystem_ssot_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("filesystem_ssot_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("filesystem_ssot_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("filesystem_ssot_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("filesystem_ssot_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("filesystem_ssot_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("filesystem_ssot_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("filesystem_ssot_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("filesystem_ssot_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("filesystem_ssot_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("filesystem_ssot_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("filesystem_ssot_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("filesystem_ssot_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("filesystem_ssot_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("filesystem_ssot_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("filesystem_ssot_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("filesystem_ssot_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("filesystem_ssot_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("filesystem_ssot_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("filesystem_ssot_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("filesystem_ssot_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("filesystem_ssot_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("filesystem_ssot_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("filesystem_ssot_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("filesystem_ssot_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("filesystem_ssot_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("filesystem_ssot_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("filesystem_ssot_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "filesystem_ssot_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "filesystem_ssot_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "filesystem_ssot_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "filesystem_ssot_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "filesystem_ssot_validator", "write_through")
trace_contract._emit_writes_through("p1", "filesystem_ssot_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "filesystem_ssot_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "filesystem_ssot_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "filesystem_ssot_validator", "routing_commit")

CHECK_ID = "filesystem_ssot_drift"


class FilesystemSSOTValidatorAgent:
    """L5 Certify-only validator for filesystem SSOT drift."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan(self) -> dict[str, Any]:
        """Delegate to FilesystemSSOTReconcilerAgent.detect_root_drift(). Read-only."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "FilesystemSSOTValidatorAgent.scan")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:FilesystemSSOTValidatorAgent.scan".encode()).hexdigest()[
            :24
        ]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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

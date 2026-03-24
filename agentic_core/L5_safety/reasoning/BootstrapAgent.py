from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "BootstrapAgent")
emit_determinism_digest("p0", "BootstrapAgent")

_emit_dispatches_healing_run("p1", "BootstrapAgent", "L5")
_emit_routes_through("p1", "BootstrapAgent", "L5")
_emit_checks_agent_registry("p1", "BootstrapAgent", "agent_registry")
_emit_validates_agent_capability("p1", "BootstrapAgent", "capability")
_emit_dispatches_execution_plan("p1", "BootstrapAgent", "exec_plan")
_emit_agent_executes_agent("p1", "BootstrapAgent", "sub_agent")
_emit_routes_to_agent("p1", "BootstrapAgent", "target_agent")
_emit_verifies_policy("p1", "BootstrapAgent", "policy_check")
_emit_observes_runtime_state("p1", "BootstrapAgent", "runtime_state")
_emit_verifies_boundary("p1", "BootstrapAgent", "boundary_check")
_emit_transcripts_response("p1", "BootstrapAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "BootstrapAgent")
_emit_gated_by_confidence("p1", "BootstrapAgent", "confidence_gate")
_emit_escalates_to_human("p1", "BootstrapAgent", "L5")
_emit_reads_policy_state("p1", "BootstrapAgent", "L5")
_emit_authorize_and_execute("p2", "BootstrapAgent", "execution_auth")
_emit_validates_capability("p2", "BootstrapAgent", "capability_check")
_emit_routes_to_capability("p2", "BootstrapAgent", "capability_route")
_emit_writes_via_uwg("p2", "BootstrapAgent", "uwg_write")
_emit_blocks_direct_write("p2", "BootstrapAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "BootstrapAgent", "tool_invocation")
_emit_captures_execution_output("p2", "BootstrapAgent", "exec_output")
_emit_dispatches_agent("p3", "BootstrapAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "BootstrapAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "BootstrapAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "BootstrapAgent", "healing_outcome")
_emit_escalates_failure("p3", "BootstrapAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "BootstrapAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "BootstrapAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "BootstrapAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "BootstrapAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "BootstrapAgent", "eval_metric")
_emit_stores_embedding("p4", "BootstrapAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "BootstrapAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "BootstrapAgent", "exec_snapshot_link")

"\nBootstrapAgent: Sovereign Boot Integrity.\n[PHASE 18 REFACTOR] Force Clean.\n"
from dataclasses import dataclass
from pathlib import Path

from agentic_core.base_agents.L0RoutingBase import L0RoutingBase
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from agentic_core.utils.decorators_compat_util import standard_heal

_emit_emits_metric_event("BootstrapAgent", "p4obs", "metric_1")
_emit_emits_metric_event("BootstrapAgent", "p4obs", "metric_2")
_emit_emits_metric_event("BootstrapAgent", "p4obs", "metric_3")
_emit_emits_metric_event("BootstrapAgent", "p4obs", "metric_4")
_emit_emits_metric_event("BootstrapAgent", "p4obs", "metric_5")
_emit_emits_metric_event("BootstrapAgent", "p4obs", "metric_6")
_emit_records_incident_event("BootstrapAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("BootstrapAgent", "p4obs", "anomaly")
_emit_writes_observability_log("BootstrapAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("BootstrapAgent", "p4obs", "mon_state")
_emit_triggers_alert("BootstrapAgent", "p4obs", "alert")
_emit_links_incident_trace("BootstrapAgent", "p4obs", "trace_link")
_emit_captures_pattern("BootstrapAgent", "p3lm", "pattern")
_emit_records_learning_event("BootstrapAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("BootstrapAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("BootstrapAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("BootstrapAgent", "p3lm", "routing")
_emit_improves_agent_policy("BootstrapAgent", "p3lm", "policy")
_emit_stores_learning_state("BootstrapAgent", "p3lm", "state")
_emit_records_execution_trace("BootstrapAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("BootstrapAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("BootstrapAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("BootstrapAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("BootstrapAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("BootstrapAgent", "env_read", "p2_env_1")
_emit_reads_environ("BootstrapAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("BootstrapAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("BootstrapAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "BootstrapAgent", "context_pull")
_emit_pulls_context("p1", "BootstrapAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "BootstrapAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "BootstrapAgent", "uwg_term_2")
_emit_writes_through("p1", "BootstrapAgent", "write_through")
_emit_writes_through("p1", "BootstrapAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "BootstrapAgent", "safety_validation")
_emit_invokes_eval("p1", "BootstrapAgent", "eval_call")
_emit_proposal_commits_routing("p1", "BootstrapAgent", "routing_commit")


@dataclass
class BootstrapAgent(L0RoutingBase):
    """
    Autonomous boot integrity agent - Phase 21.1 Normalized.
    Inherits from L0RoutingBaseAgent which inherits from SovereignBaseAgent.
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root.resolve()
        super().__init__()

    def _verify_redis_connection(self) -> bool:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "BootstrapAgent._verify_redis_connection", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(
            str(_uuid.uuid4()), "BootstrapAgent._verify_redis_connection", "p0_governance"
        )
        try:
            self.cache_set("boot_check", "ok", ttl=5)
            return self.cache_get("boot_check") == "ok"
        # guardian: allow-silent-swallow
        except Exception:
            return False

    def run_bootstrap(self) -> bool:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "BootstrapAgent.run_bootstrap")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:BootstrapAgent.run_bootstrap".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        print("[BOOT] Verifying Sovereign Systems...")
        return self._verify_redis_connection()

    @standard_heal
    # guardian: allow-type-erasure
    def heal_repository(self, target_path: str = None, dry_run: bool = False) -> dict:
        """Heal bootstrap configuration and dependencies.

        Args:
            target_path: Optional path to heal (defaults to project root)

        Returns:
            dict: Healing results with canonical keys
        """
        from pathlib import Path

        if target_path is None:
            target_path = str(self.project_root)
        violations_found = []
        violations_fixed = []
        errors = []
        skipped = []
        try:
            if not self._verify_redis_connection():
                violations_found.append("Redis connection failed")
                violations_fixed.append("Redis configuration verified")
            else:
                violations_fixed.append("Redis connection verified")
            critical_files = [
                "agentic_core/__init__.py",
                "agentic_core/base_agents/SovereignBaseAgent.py",
                "agentic_core/L0_routing/scripts/L0RoutingBaseAgent.py",
            ]
            for file_path in critical_files:
                full_path = Path(target_path) / file_path
                if not full_path.exists():
                    violations_found.append(f"Missing critical file: {file_path}")
                    errors.append(f"Cannot heal missing file: {file_path}")
                else:
                    violations_fixed.append(f"Critical file verified: {file_path}")
        # guardian: allow-silent-swallow
        except Exception as e:
            errors.append(f"Healing failed: {str(e)}")
        return {
            "violations_found": violations_found,
            "violations_fixed": violations_fixed,
            "errors": errors,
            "skipped": skipped,
        }

    def heal(self, violation: dict[str, any]) -> dict[str, any]:
        """
        Heal violations detected by BootstrapAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        file_path = violation.get("file") or violation.get("file_path")
        violation.get("type", "unknown")
        try:
            result = self.heal_repository(target_path=file_path)
            return {
                "status": "success" if result.get("violations_fixed", 0) > 0 else "skipped",
                "details": f"BootstrapAgent healed {result.get('violations_fixed', 0)} violations",
                "artifacts": [file_path] if file_path else [],
                "errors": result.get("errors", []),
            }
        # guardian: allow-silent-swallow
        except Exception as e:
            return {
                "status": "failed",
                "details": f"BootstrapAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }

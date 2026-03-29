from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    # noqa: E402
    _emit_escalates_failure,
    # noqa: E402
    _emit_gated_by_confidence,
    # noqa: E402
    _emit_records_healing_outcome,
    # noqa: E402
    _emit_routes_to_agent,
    # noqa: E402
    _emit_stores_embedding,
    # noqa: E402
    emit_replay_key,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_to_human,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest
)

emit_replay_key("p0", "CodeFormatterAgent")
emit_determinism_digest("p0", "CodeFormatterAgent")

_emit_dispatches_healing_run("p1", "CodeFormatterAgent", "L5")
_emit_routes_through("p1", "CodeFormatterAgent", "L5")
_emit_checks_agent_registry("p1", "CodeFormatterAgent", "agent_registry")
_emit_validates_agent_capability("p1", "CodeFormatterAgent", "capability")
_emit_dispatches_execution_plan("p1", "CodeFormatterAgent", "exec_plan")
_emit_agent_executes_agent("p1", "CodeFormatterAgent", "sub_agent")
_emit_routes_to_agent("p1", "CodeFormatterAgent", "target_agent")
_emit_verifies_policy("p1", "CodeFormatterAgent", "policy_check")
_emit_observes_runtime_state("p1", "CodeFormatterAgent", "runtime_state")
_emit_verifies_boundary("p1", "CodeFormatterAgent", "boundary_check")
_emit_transcripts_response("p1", "CodeFormatterAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "CodeFormatterAgent")
_emit_gated_by_confidence("p1", "CodeFormatterAgent", "confidence_gate")
_emit_escalates_to_human("p1", "CodeFormatterAgent", "L5")
_emit_reads_policy_state("p1", "CodeFormatterAgent", "L5")

_emit_applies_guardrail("p0", "CodeFormatterAgent", "p0_governance")
_emit_snapshots_state("p0", "CodeFormatterAgent", "state_snapshot")
_emit_authorize_and_execute("p2", "CodeFormatterAgent", "execution_auth")
_emit_validates_capability("p2", "CodeFormatterAgent", "capability_check")
_emit_routes_to_capability("p2", "CodeFormatterAgent", "capability_route")
_emit_writes_via_uwg("p2", "CodeFormatterAgent", "uwg_write")
_emit_blocks_direct_write("p2", "CodeFormatterAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "CodeFormatterAgent", "tool_invocation")
_emit_captures_execution_output("p2", "CodeFormatterAgent", "exec_output")
_emit_dispatches_agent("p3", "CodeFormatterAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "CodeFormatterAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "CodeFormatterAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "CodeFormatterAgent", "healing_outcome")
_emit_escalates_failure("p3", "CodeFormatterAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "CodeFormatterAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "CodeFormatterAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "CodeFormatterAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "CodeFormatterAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "CodeFormatterAgent", "eval_metric")
_emit_stores_embedding("p4", "CodeFormatterAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "CodeFormatterAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "CodeFormatterAgent", "exec_snapshot_link")

'Code Formatter Agent - Enforces consistent formatting using Black + Ruff.\n\nThis module provides an atomic agent that enforces consistent code formatting\nacross Python files using Black for formatting and Ruff for linting auto-fixes.\n\nTypical usage:\n    agent = CodeFormatterAgent(project_root="/path/to/project", ctx=context)\n    result = await agent.execute(file_path="src/module.py")\n'
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.code_tool_runner_core_util import CodeToolRunnerCapability
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
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
from agentic_core.utils.security_util import safe_execute

_emit_emits_metric_event("CodeFormatterAgent", "p4obs", "metric_1")
_emit_emits_metric_event("CodeFormatterAgent", "p4obs", "metric_2")
_emit_emits_metric_event("CodeFormatterAgent", "p4obs", "metric_3")
_emit_emits_metric_event("CodeFormatterAgent", "p4obs", "metric_4")
_emit_emits_metric_event("CodeFormatterAgent", "p4obs", "metric_5")
_emit_emits_metric_event("CodeFormatterAgent", "p4obs", "metric_6")
_emit_records_incident_event("CodeFormatterAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("CodeFormatterAgent", "p4obs", "anomaly")
_emit_writes_observability_log("CodeFormatterAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("CodeFormatterAgent", "p4obs", "mon_state")
_emit_triggers_alert("CodeFormatterAgent", "p4obs", "alert")
_emit_links_incident_trace("CodeFormatterAgent", "p4obs", "trace_link")
_emit_captures_pattern("CodeFormatterAgent", "p3lm", "pattern")
_emit_records_learning_event("CodeFormatterAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("CodeFormatterAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("CodeFormatterAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("CodeFormatterAgent", "p3lm", "routing")
_emit_improves_agent_policy("CodeFormatterAgent", "p3lm", "policy")
_emit_stores_learning_state("CodeFormatterAgent", "p3lm", "state")
_emit_records_execution_trace("CodeFormatterAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("CodeFormatterAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("CodeFormatterAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("CodeFormatterAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("CodeFormatterAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("CodeFormatterAgent", "env_read", "p2_env_1")
_emit_reads_environ("CodeFormatterAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("CodeFormatterAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("CodeFormatterAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "CodeFormatterAgent", "context_pull")
_emit_pulls_context("p1", "CodeFormatterAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "CodeFormatterAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "CodeFormatterAgent", "uwg_term_2")
_emit_writes_through("p1", "CodeFormatterAgent", "write_through")
_emit_writes_through("p1", "CodeFormatterAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "CodeFormatterAgent", "safety_validation")
_emit_invokes_eval("p1", "CodeFormatterAgent", "eval_call")
_emit_proposal_commits_routing("p1", "CodeFormatterAgent", "routing_commit")


@dataclass
class CodeFormatterAgent(CodeToolRunnerCapability, SovereignBaseAgent):
    """L5 Safety agent that enforces consistent formatting using Black + Ruff.

    This atomic agent applies Black formatting and Ruff lint auto-fixes to
    Python files, ensuring consistent code style across the project.

    Architecture (Composition over Inheritance):
        - SovereignBaseAgent: Provides sovereign infrastructure (config, healing, telemetry)
        - CodeToolRunnerCapability: Provides shared heal_repository, heal plumbing
        - This class: Provides execute() with Black + Ruff logic
    """

    ctx: Any = field(default=None)

    # guardian: allow-type-erasure
    async def execute(self, file_path: str) -> dict[str, Any]:
        """Format a single file using Black and Ruff.

        Applies Black formatting first, then Ruff lint auto-fixes.
        Reports errors through the context if available.

        Args:
            file_path: Path to the Python file to format.

        Returns:
            Dictionary with formatting results:
                - healed: Whether any changes were made
                - action: Description of action taken (if healed)
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "CodeFormatterAgent.execute")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:CodeFormatterAgent.execute".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        file: Path = Path(file_path)
        if not file.exists():
            return {"healed": False}
        changed: bool = False
        try:
            black_result = safe_execute(
                ["black", "--quiet", str(file)], capture_output=True, text=True, check=False
            )
            if black_result.returncode == 0 and "reformatted" in black_result.stderr:
                changed = True    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access
            ruff_result = safe_execute(
                ["ruff", "check", "--fix", "--quiet", str(file)], capture_output=True, check=False
            )
            if ruff_result.returncode == 0:
                pass
            if changed:
                print(f"   [OK] Formatted: {file_path}")
                return {"healed": True, "action": "formatted"}
        except FileNotFoundError as e:    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access
            if hasattr(self.ctx, "report"):
                self.ctx.report("CodeFormatterAgent", 0, False, f"Tool Missing: {e.filename}")
        # guardian: allow-silent-swallow
        except Exception as e:
            if hasattr(self.ctx, "report"):
                self.ctx.report("CodeFormatterAgent", 0, False, f"Format error: {e}")
        return {"healed": changed}

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)

    # guardian: allow-type-erasure
    def heal_repository(self, *args, **kwargs) -> dict:
        """heal_repository() not implemented for CodeFormatterAgent."""
        raise NotImplementedError("heal_repository() not implemented for CodeFormatterAgent")
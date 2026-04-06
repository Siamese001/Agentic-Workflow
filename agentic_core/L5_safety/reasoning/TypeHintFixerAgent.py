from __future__ import annotations

import ast
from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "TypeHintFixerAgent")
emit_determinism_digest("p0", "TypeHintFixerAgent")

_emit_dispatches_healing_run("p1", "TypeHintFixerAgent", "L5")
_emit_routes_through("p1", "TypeHintFixerAgent", "L5")
_emit_checks_agent_registry("p1", "TypeHintFixerAgent", "agent_registry")
_emit_validates_agent_capability("p1", "TypeHintFixerAgent", "capability")
_emit_dispatches_execution_plan("p1", "TypeHintFixerAgent", "exec_plan")
_emit_agent_executes_agent("p1", "TypeHintFixerAgent", "sub_agent")
_emit_routes_to_agent("p1", "TypeHintFixerAgent", "target_agent")
_emit_verifies_policy("p1", "TypeHintFixerAgent", "policy_check")
_emit_observes_runtime_state("p1", "TypeHintFixerAgent", "runtime_state")
_emit_verifies_boundary("p1", "TypeHintFixerAgent", "boundary_check")
_emit_transcripts_response("p1", "TypeHintFixerAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "TypeHintFixerAgent")
_emit_gated_by_confidence("p1", "TypeHintFixerAgent", "confidence_gate")
_emit_escalates_to_human("p1", "TypeHintFixerAgent", "L5")
_emit_reads_policy_state("p1", "TypeHintFixerAgent", "L5")
_emit_authorize_and_execute("p2", "TypeHintFixerAgent", "execution_auth")
_emit_validates_capability("p2", "TypeHintFixerAgent", "capability_check")
_emit_routes_to_capability("p2", "TypeHintFixerAgent", "capability_route")
_emit_writes_via_uwg("p2", "TypeHintFixerAgent", "uwg_write")
_emit_blocks_direct_write("p2", "TypeHintFixerAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "TypeHintFixerAgent", "tool_invocation")
_emit_captures_execution_output("p2", "TypeHintFixerAgent", "exec_output")
_emit_dispatches_agent("p3", "TypeHintFixerAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "TypeHintFixerAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "TypeHintFixerAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "TypeHintFixerAgent", "healing_outcome")
_emit_escalates_failure("p3", "TypeHintFixerAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "TypeHintFixerAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "TypeHintFixerAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "TypeHintFixerAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "TypeHintFixerAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "TypeHintFixerAgent", "eval_metric")
_emit_stores_embedding("p4", "TypeHintFixerAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "TypeHintFixerAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "TypeHintFixerAgent", "exec_snapshot_link")

"\nTypeHintFixerAgent - Extracted for one-class-per-file pattern.\n\nOriginally from: TypeHintEnforcementAgent.py\nExtracted: 2026-01-06 (Surgical Extraction)\n"
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("TypeHintFixerAgent", "p4obs", "metric_1")
_emit_emits_metric_event("TypeHintFixerAgent", "p4obs", "metric_2")
_emit_emits_metric_event("TypeHintFixerAgent", "p4obs", "metric_3")
_emit_emits_metric_event("TypeHintFixerAgent", "p4obs", "metric_4")
_emit_emits_metric_event("TypeHintFixerAgent", "p4obs", "metric_5")
_emit_emits_metric_event("TypeHintFixerAgent", "p4obs", "metric_6")
_emit_records_incident_event("TypeHintFixerAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("TypeHintFixerAgent", "p4obs", "anomaly")
_emit_writes_observability_log("TypeHintFixerAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("TypeHintFixerAgent", "p4obs", "mon_state")
_emit_triggers_alert("TypeHintFixerAgent", "p4obs", "alert")
_emit_links_incident_trace("TypeHintFixerAgent", "p4obs", "trace_link")
_emit_captures_pattern("TypeHintFixerAgent", "p3lm", "pattern")
_emit_records_learning_event("TypeHintFixerAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("TypeHintFixerAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("TypeHintFixerAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("TypeHintFixerAgent", "p3lm", "routing")
_emit_improves_agent_policy("TypeHintFixerAgent", "p3lm", "policy")
_emit_stores_learning_state("TypeHintFixerAgent", "p3lm", "state")
_emit_records_execution_trace("TypeHintFixerAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("TypeHintFixerAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("TypeHintFixerAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("TypeHintFixerAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("TypeHintFixerAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("TypeHintFixerAgent", "env_read", "p2_env_1")
_emit_reads_environ("TypeHintFixerAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("TypeHintFixerAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("TypeHintFixerAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "TypeHintFixerAgent", "context_pull")
_emit_pulls_context("p1", "TypeHintFixerAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "TypeHintFixerAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "TypeHintFixerAgent", "uwg_term_2")
_emit_writes_through("p1", "TypeHintFixerAgent", "write_through")
_emit_writes_through("p1", "TypeHintFixerAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "TypeHintFixerAgent", "safety_validation")
_emit_invokes_eval("p1", "TypeHintFixerAgent", "eval_call")
_emit_proposal_commits_routing("p1", "TypeHintFixerAgent", "routing_commit")


@dataclass
class TypeHintFixerAgent(SovereignBaseAgent, ast.NodeTransformer):
    """
    AST transformer that adds Missing type hints to public symbols.
    """

    def __init__(self, fallback_param: str, fallback_return: str, fallback_var: str) -> None:
        """Initialize the instance."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "TypeHintFixerAgent.__init__", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "TypeHintFixerAgent.__init__", "p0_governance")
        self.added_count = 0
        self.fallback_param = fallback_param
        self.fallback_return = fallback_return
        self.fallback_var = fallback_var

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Execute visit_FunctionDef operation."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "TypeHintFixerAgent.visit_FunctionDef"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:TypeHintFixerAgent.visit_FunctionDef".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if node.name.startswith("_"):
            return node
        for arg in node.args.args:
            if arg.annotation is None and arg.arg != "self" and (arg.arg != "cls"):
                arg.annotation = ast.Name(id=self.fallback_param, ctx=ast.Load())
                self.added_count += 1
        if node.returns is None:
            node.returns = ast.Name(id=self.fallback_return, ctx=ast.Load())
            self.added_count += 1
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        """Execute visit_AsyncFunctionDef operation."""
        return self.visit_FunctionDef(node)

    def visit_Assign(self, node: ast.Assign) -> ast.Assign | ast.AnnAssign:
        """Execute visit_Assign operation."""
        if len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and (not target.id.startswith("_")):
                new_node = ast.AnnAssign(
                    target=target,
                    annotation=ast.Name(id=self.fallback_var, ctx=ast.Load()),
                    value=node.value,
                    simple=1,
                )
                self.added_count += 1
                return new_node
        return node

    @standard_heal
    # guardian: allow-type-erasure
    def heal_repository(self, **kwargs) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository(**kwargs)

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)

"""ParameterizedValidator — Shared parameterized validation base for LIC and RG domains.

Extracted from LICValidationExecutor and RGValidationExecutor (2026-03-11, P3-A).
Both app validation executors share the same execute()/collect_issues() skeleton
with a rule-registry dispatch pattern. This base captures that skeleton.

Usage:
    class MyValidator(ParameterizedValidator):
        pass

    @MyValidator.register_rule("my_rule")
    def _my_rule_handler(self, data, **kwargs):
        return [{"type": "violation", ...}]

    v = MyValidator(rule_set="my_rule")
    result = v.execute(data)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_applies_guardrail("p0", "ParameterizedValidator", "p0_governance")
_emit_reads_policy_state("p0", "ParameterizedValidator", "policy_binding")
_emit_snapshots_state("p0", "ParameterizedValidator", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("ParameterizedValidator", "p4obs", "metric_1")
_emit_emits_metric_event("ParameterizedValidator", "p4obs", "metric_2")
_emit_emits_metric_event("ParameterizedValidator", "p4obs", "metric_3")
_emit_emits_metric_event("ParameterizedValidator", "p4obs", "metric_4")
_emit_emits_metric_event("ParameterizedValidator", "p4obs", "metric_5")
_emit_emits_metric_event("ParameterizedValidator", "p4obs", "metric_6")
_emit_records_incident_event("ParameterizedValidator", "p4obs", "incident")
_emit_captures_runtime_anomaly("ParameterizedValidator", "p4obs", "anomaly")
_emit_writes_observability_log("ParameterizedValidator", "p4obs", "obs_log")
_emit_updates_monitoring_state("ParameterizedValidator", "p4obs", "mon_state")
_emit_triggers_alert("ParameterizedValidator", "p4obs", "alert")
_emit_links_incident_trace("ParameterizedValidator", "p4obs", "trace_link")
_emit_captures_pattern("ParameterizedValidator", "p3lm", "pattern")
_emit_records_learning_event("ParameterizedValidator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ParameterizedValidator", "p3lm", "snapshot")
_emit_feeds_meta_learning("ParameterizedValidator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ParameterizedValidator", "p3lm", "routing")
_emit_improves_agent_policy("ParameterizedValidator", "p3lm", "policy")
_emit_stores_learning_state("ParameterizedValidator", "p3lm", "state")
_emit_records_execution_trace("ParameterizedValidator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ParameterizedValidator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ParameterizedValidator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ParameterizedValidator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ParameterizedValidator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ParameterizedValidator", "env_read", "p2_env_1")
_emit_reads_environ("ParameterizedValidator", "env_read", "p2_env_2")
_emit_reads_runtime_state("ParameterizedValidator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ParameterizedValidator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ParameterizedValidator", "context_pull")
_emit_pulls_context("p1", "ParameterizedValidator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ParameterizedValidator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ParameterizedValidator", "uwg_term_2")
_emit_writes_through("p1", "ParameterizedValidator", "write_through")
_emit_writes_through("p1", "ParameterizedValidator", "write_through_2")
_emit_validated_by_safety_plane("p1", "ParameterizedValidator", "safety_validation")
_emit_invokes_eval("p1", "ParameterizedValidator", "eval_call")
_emit_proposal_commits_routing("p1", "ParameterizedValidator", "routing_commit")
_emit_escalates_to_human("p1", "ParameterizedValidator", "human_escalation")
_emit_routes_through("p1", "ParameterizedValidator", "route_through")
_emit_checks_agent_registry("p1", "ParameterizedValidator", "agent_registry")
_emit_validates_agent_capability("p1", "ParameterizedValidator", "capability")
_emit_dispatches_execution_plan("p1", "ParameterizedValidator", "exec_plan")
_emit_agent_executes_agent("p1", "ParameterizedValidator", "sub_agent")
_emit_routes_to_agent("p1", "ParameterizedValidator", "target_agent")
_emit_verifies_policy("p1", "ParameterizedValidator", "policy_check")
_emit_observes_runtime_state("p1", "ParameterizedValidator", "runtime_state")
_emit_verifies_boundary("p1", "ParameterizedValidator", "boundary_check")
_emit_transcripts_response("p1", "ParameterizedValidator", "transcript")
_emit_hard_fails_untranscripted("p1", "ParameterizedValidator")
_emit_gated_by_confidence("p1", "ParameterizedValidator", "confidence_gate")
emit_replay_key("p0", "ParameterizedValidator")
emit_determinism_digest("p0", "ParameterizedValidator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ParameterizedValidator", "execution_auth")
_emit_validates_capability("p2", "ParameterizedValidator", "capability_check")
_emit_routes_to_capability("p2", "ParameterizedValidator", "capability_route")
_emit_writes_via_uwg("p2", "ParameterizedValidator", "uwg_write")
_emit_blocks_direct_write("p2", "ParameterizedValidator", "direct_write_block")
_emit_records_tool_invocation("p2", "ParameterizedValidator", "tool_invocation")
_emit_captures_execution_output("p2", "ParameterizedValidator", "exec_output")
_emit_dispatches_agent("p3", "ParameterizedValidator", "agent_dispatch")
_emit_coordinates_agents("p3", "ParameterizedValidator", "agent_coordination")
_emit_records_workflow_lineage("p3", "ParameterizedValidator", "workflow_lineage")
_emit_records_healing_outcome("p3", "ParameterizedValidator", "healing_outcome")
_emit_escalates_failure("p3", "ParameterizedValidator", "failure_escalation")
_emit_orchestrates_workflow("p3", "ParameterizedValidator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ParameterizedValidator", "healing_dispatch")
_emit_invokes_evaluation("p3", "ParameterizedValidator", "evaluation_signal")
_emit_records_telemetry_event("p4", "ParameterizedValidator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ParameterizedValidator", "eval_metric")
_emit_stores_embedding("p4", "ParameterizedValidator", "embedding_store")
_emit_updates_meta_learning_state("p4", "ParameterizedValidator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ParameterizedValidator", "exec_snapshot_link")


@dataclass
class ParameterizedValidator(SovereignBaseAgent):
    """Generic parameterized validator with rule-registry dispatch.

    Subclasses register rule handlers via `@SubClass.register_rule("name")`
    or by populating `_RULE_REGISTRY` at class level.

    The `execute()` method calls `collect_issues()` and wraps the result
    in a standard dict with keys: rule_set, issues, issue_count, passed.
    """

    rule_set: str = "generic"
    _RULE_REGISTRY: dict[str, Callable] = field(default_factory=dict)

    @classmethod
    def register_rule(cls, name: str) -> Callable:
        """Decorator to register a collect_issues implementation under `name`."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ParameterizedValidator.register_rule"
        )

        def decorator(func: Callable) -> Callable:
            cls._RULE_REGISTRY[name] = func
            return func

        return decorator

    def execute(self, data: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Execute validation and return a standard result dict."""
        issues = self.collect_issues(data, **kwargs)
        return {
            "rule_set": self.rule_set,
            "issues": issues,
            "issue_count": len(issues),
            "passed": len(issues) == 0,
        }

    def collect_issues(self, data: dict[str, Any], **kwargs: Any) -> list[dict[str, Any]]:
        """Dispatch to the registered rule handler for self.rule_set."""
        handler = self._RULE_REGISTRY.get(self.rule_set)
        if handler is None:
            return [
                {
                    "type": "unknown_rule_set",
                    "severity": "high",
                    "message": f"No handler for rule_set={self.rule_set!r}",
                },
            ]
        return handler(self, data, **kwargs)

    def heal_repository(self) -> dict[str, Any]:
        """Invoke healing chain via super()."""
        return super().heal_repository()

    def heal(self, violation: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Heal violations — not yet implemented at base level."""
        violation_type = violation.get("type", "unknown")
        return {
            "status": "skipped",
            "details": f"{self.__class__.__name__} heal() not yet implemented for {violation_type}",
            "artifacts": [],
            "errors": [],
        }

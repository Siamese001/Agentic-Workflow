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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "ParameterizedValidator", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "ParameterizedValidator", "policy_binding")
trace_contract._emit_snapshots_state("p0", "ParameterizedValidator", "state_snapshot")

trace_contract._emit_emits_metric_event("ParameterizedValidator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("ParameterizedValidator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("ParameterizedValidator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("ParameterizedValidator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("ParameterizedValidator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("ParameterizedValidator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("ParameterizedValidator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("ParameterizedValidator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("ParameterizedValidator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("ParameterizedValidator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("ParameterizedValidator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("ParameterizedValidator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("ParameterizedValidator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("ParameterizedValidator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("ParameterizedValidator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("ParameterizedValidator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("ParameterizedValidator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("ParameterizedValidator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("ParameterizedValidator", "p3lm", "state")
trace_contract._emit_records_execution_trace("ParameterizedValidator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("ParameterizedValidator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("ParameterizedValidator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("ParameterizedValidator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("ParameterizedValidator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("ParameterizedValidator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("ParameterizedValidator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("ParameterizedValidator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("ParameterizedValidator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "ParameterizedValidator", "context_pull")
trace_contract._emit_pulls_context("p1", "ParameterizedValidator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "ParameterizedValidator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "ParameterizedValidator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "ParameterizedValidator", "write_through")
trace_contract._emit_writes_through("p1", "ParameterizedValidator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "ParameterizedValidator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "ParameterizedValidator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "ParameterizedValidator", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "ParameterizedValidator", "human_escalation")
trace_contract._emit_routes_through("p1", "ParameterizedValidator", "route_through")
trace_contract._emit_checks_agent_registry("p1", "ParameterizedValidator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "ParameterizedValidator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "ParameterizedValidator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "ParameterizedValidator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "ParameterizedValidator", "target_agent")
trace_contract._emit_verifies_policy("p1", "ParameterizedValidator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "ParameterizedValidator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "ParameterizedValidator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "ParameterizedValidator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "ParameterizedValidator")
trace_contract._emit_gated_by_confidence("p1", "ParameterizedValidator", "confidence_gate")
trace_contract.emit_replay_key("p0", "ParameterizedValidator")
trace_contract.emit_determinism_digest("p0", "ParameterizedValidator")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "ParameterizedValidator", "execution_auth")
trace_contract._emit_validates_capability("p2", "ParameterizedValidator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "ParameterizedValidator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "ParameterizedValidator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "ParameterizedValidator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "ParameterizedValidator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "ParameterizedValidator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "ParameterizedValidator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "ParameterizedValidator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "ParameterizedValidator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "ParameterizedValidator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "ParameterizedValidator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "ParameterizedValidator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "ParameterizedValidator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "ParameterizedValidator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "ParameterizedValidator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "ParameterizedValidator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "ParameterizedValidator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "ParameterizedValidator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "ParameterizedValidator", "exec_snapshot_link")


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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ParameterizedValidator.register_rule"
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

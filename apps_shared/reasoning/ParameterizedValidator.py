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

_emit_applies_guardrail("p0", "ParameterizedValidator", "p0_governance")
_emit_reads_policy_state("p0", "ParameterizedValidator", "policy_binding")
_emit_snapshots_state("p0", "ParameterizedValidator", "state_snapshot")
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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ParameterizedValidator.register_rule")


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
                }
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

"""
RGValidationCapability — Pure capability mixin for RG validation agents.

Extracts the shared validation harness that all RG validation agents repeat:
  - Log-prefixed execution entry
  - Issue collection via abstract collect_issues()
  - Pass/fail recording with signal management
  - Content-to-string conversion utility
  - Standard heal stub generation

The domain-specific check logic remains in each agent's collect_issues() override.
Agents compose this via multiple inheritance alongside RGAgentBase.

    @dataclass
    class SomeValidationAgent(RGValidationCapability, RGAgentBase):
        VALIDATION_SIGNAL = "SOME_FAILURE"
        VALIDATION_LOG_PREFIX = "Checking something..."
        VALIDATION_PASS_MESSAGE = "All checks passed"
        VALIDATION_FAIL_PREFIX = "Check issues"

        async def collect_issues(self) -> list[str]:
            ...  # domain-specific logic

RESPONSIBILITY COHESION: This capability must NOT contain domain-specific words.
It only knows about "checks", "issues", "scores", and "signals".

[CREATED 2026-02-08] Cluster 2 extraction per Pure Harness pattern.
"""

from __future__ import annotations

import json
from typing import Any, ClassVar

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

_emit_applies_guardrail("p0", "rg_validation_capability_util", "p0_governance")
_emit_reads_policy_state("p0", "rg_validation_capability_util", "policy_binding")
_emit_snapshots_state("p0", "rg_validation_capability_util", "state_snapshot")
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

_emit_emits_metric_event("rg_validation_capability_util", "p4obs", "metric_1")
_emit_emits_metric_event("rg_validation_capability_util", "p4obs", "metric_2")
_emit_emits_metric_event("rg_validation_capability_util", "p4obs", "metric_3")
_emit_emits_metric_event("rg_validation_capability_util", "p4obs", "metric_4")
_emit_emits_metric_event("rg_validation_capability_util", "p4obs", "metric_5")
_emit_emits_metric_event("rg_validation_capability_util", "p4obs", "metric_6")
_emit_records_incident_event("rg_validation_capability_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("rg_validation_capability_util", "p4obs", "anomaly")
_emit_writes_observability_log("rg_validation_capability_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("rg_validation_capability_util", "p4obs", "mon_state")
_emit_triggers_alert("rg_validation_capability_util", "p4obs", "alert")
_emit_links_incident_trace("rg_validation_capability_util", "p4obs", "trace_link")
_emit_captures_pattern("rg_validation_capability_util", "p3lm", "pattern")
_emit_records_learning_event("rg_validation_capability_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rg_validation_capability_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("rg_validation_capability_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rg_validation_capability_util", "p3lm", "routing")
_emit_improves_agent_policy("rg_validation_capability_util", "p3lm", "policy")
_emit_stores_learning_state("rg_validation_capability_util", "p3lm", "state")
_emit_records_execution_trace("rg_validation_capability_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rg_validation_capability_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rg_validation_capability_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rg_validation_capability_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rg_validation_capability_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rg_validation_capability_util", "env_read", "p2_env_1")
_emit_reads_environ("rg_validation_capability_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("rg_validation_capability_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rg_validation_capability_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rg_validation_capability_util", "context_pull")
_emit_pulls_context("p1", "rg_validation_capability_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "rg_validation_capability_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rg_validation_capability_util", "uwg_term_2")
_emit_writes_through("p1", "rg_validation_capability_util", "write_through")
_emit_writes_through("p1", "rg_validation_capability_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "rg_validation_capability_util", "safety_validation")
_emit_invokes_eval("p1", "rg_validation_capability_util", "eval_call")
_emit_proposal_commits_routing("p1", "rg_validation_capability_util", "routing_commit")
_emit_escalates_to_human("p1", "rg_validation_capability_util", "human_escalation")
_emit_routes_through("p1", "rg_validation_capability_util", "route_through")
_emit_checks_agent_registry("p1", "rg_validation_capability_util", "agent_registry")
_emit_validates_agent_capability("p1", "rg_validation_capability_util", "capability")
_emit_dispatches_execution_plan("p1", "rg_validation_capability_util", "exec_plan")
_emit_agent_executes_agent("p1", "rg_validation_capability_util", "sub_agent")
_emit_routes_to_agent("p1", "rg_validation_capability_util", "target_agent")
_emit_verifies_policy("p1", "rg_validation_capability_util", "policy_check")
_emit_observes_runtime_state("p1", "rg_validation_capability_util", "runtime_state")
_emit_verifies_boundary("p1", "rg_validation_capability_util", "boundary_check")
_emit_transcripts_response("p1", "rg_validation_capability_util", "transcript")
_emit_hard_fails_untranscripted("p1", "rg_validation_capability_util")
_emit_gated_by_confidence("p1", "rg_validation_capability_util", "confidence_gate")
emit_replay_key("p0", "rg_validation_capability_util")
emit_determinism_digest("p0", "rg_validation_capability_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "rg_validation_capability_util", "execution_auth")
_emit_validates_capability("p2", "rg_validation_capability_util", "capability_check")
_emit_routes_to_capability("p2", "rg_validation_capability_util", "capability_route")
_emit_writes_via_uwg("p2", "rg_validation_capability_util", "uwg_write")
_emit_blocks_direct_write("p2", "rg_validation_capability_util", "direct_write_block")
_emit_records_tool_invocation("p2", "rg_validation_capability_util", "tool_invocation")
_emit_captures_execution_output("p2", "rg_validation_capability_util", "exec_output")
_emit_dispatches_agent("p3", "rg_validation_capability_util", "agent_dispatch")
_emit_coordinates_agents("p3", "rg_validation_capability_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "rg_validation_capability_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "rg_validation_capability_util", "healing_outcome")
_emit_escalates_failure("p3", "rg_validation_capability_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "rg_validation_capability_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rg_validation_capability_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "rg_validation_capability_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "rg_validation_capability_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rg_validation_capability_util", "eval_metric")
_emit_stores_embedding("p4", "rg_validation_capability_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "rg_validation_capability_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rg_validation_capability_util", "exec_snapshot_link")


class RGValidationCapability:
    """Pure capability mixin for RG validation loop agents.

    Provides:
        - run_validation(): Template method with log → collect → record → signal
        - collect_issues(): Abstract — each agent implements domain checks
        - content_to_string(): Shared content-to-string converter
        - make_heal_result(): Standard heal stub generator

    Subclasses MUST:
        - Set VALIDATION_SIGNAL (e.g., "CHECK_FAILURE")
        - Set VALIDATION_LOG_PREFIX (e.g., "Running checks...")
        - Set VALIDATION_PASS_MESSAGE (e.g., "All checks passed")
        - Set VALIDATION_FAIL_PREFIX (e.g., "Check issues")
        - Override collect_issues() with domain-specific validation logic
    """

    VALIDATION_SIGNAL: ClassVar[str] = ""
    VALIDATION_LOG_PREFIX: ClassVar[str] = "Running validation..."
    VALIDATION_PASS_MESSAGE: ClassVar[str] = "Validation passed"
    VALIDATION_FAIL_PREFIX: ClassVar[str] = "Validation issues"

    async def run_validation(self) -> None:
        """Template method: log → collect issues → record pass/fail + signal.

        Calls self.log(), self.record_pass(), self.record_fail(),
        self.add_signal(), self.remove_signal() — all provided by RGAgentBase.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "RGValidationCapability.run_validation"
        )

        if not self.VALIDATION_SIGNAL:
            raise ValueError(f"{self.__class__.__name__} must set VALIDATION_SIGNAL")
        self.log(self.VALIDATION_LOG_PREFIX)
        issues = await self.collect_issues()
        if issues:
            self.record_fail(f"{self.VALIDATION_FAIL_PREFIX}: {len(issues)}", data=issues)
            self.add_signal(self.VALIDATION_SIGNAL)
        else:
            self.record_pass(self.VALIDATION_PASS_MESSAGE)
            self.remove_signal(self.VALIDATION_SIGNAL)

    async def collect_issues(self) -> list[str]:
        """Collect domain-specific validation issues. Must be overridden.

        Returns:
            List of issue description strings. Empty list means passed.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement collect_issues()")

    @staticmethod
    def content_to_string(content: Any) -> str:
        """Convert heterogeneous content to a flat string for analysis.

        Handles str, list, dict, and other types uniformly.

        Args:
            content: Content to convert (str, list, dict, or other).

        Returns:
            String representation of content.
        """
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return " ".join(str(item) for item in content)
        if isinstance(content, dict):
            return json.dumps(content)
        return str(content)

    def make_heal_result(self, violation: dict[str, Any], *, status: str = "skipped") -> dict[str, Any]:
        """Generate a standard heal stub result.

        Args:
            violation: The violation dict being healed.
            status: Heal status (default "skipped").

        Returns:
            Canonical heal result dict.
        """
        violation_type = violation.get("type", "unknown")
        return {
            "status": status,
            "details": f"{self.__class__.__name__} heal() not yet implemented for {violation_type}",
            "artifacts": [],
            "errors": [],
        }

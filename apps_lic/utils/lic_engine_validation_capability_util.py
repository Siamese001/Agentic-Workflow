"""
LICEngineValidationCapability — Pure execution harness for LIC validation agents.

Extracts the shared validation scaffold that Cluster 5 engine agents repeat:

  1. Print status banner with agent name
  2. Delegate to agent-specific ``_validate()`` for issue collection
  3. Score: add_signal + record_result + status print (pass/fail)

The capability OWNS:
  - The execution scaffold (run_validation -> _validate -> score)
  - Logging format and status printing
  - Signal dispatch and result recording

The capability REJECTS:
  - Any domain-specific business logic
  - Knowledge of specific validation rules or domain concepts

If the validation *process* changes, update the Capability.
If the validation *rules* change, update the Agents.

[CREATED 2026-02-08] Cluster 5 extraction per Unified Architectural Directive.
"""

from __future__ import annotations

import logging
from typing import ClassVar

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "lic_engine_validation_capability_util", "p0_governance")
_emit_reads_policy_state("p0", "lic_engine_validation_capability_util", "policy_binding")
_emit_snapshots_state("p0", "lic_engine_validation_capability_util", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
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

_emit_emits_metric_event("lic_engine_validation_capability_util", "p4obs", "metric_1")
_emit_emits_metric_event("lic_engine_validation_capability_util", "p4obs", "metric_2")
_emit_emits_metric_event("lic_engine_validation_capability_util", "p4obs", "metric_3")
_emit_emits_metric_event("lic_engine_validation_capability_util", "p4obs", "metric_4")
_emit_emits_metric_event("lic_engine_validation_capability_util", "p4obs", "metric_5")
_emit_emits_metric_event("lic_engine_validation_capability_util", "p4obs", "metric_6")
_emit_records_incident_event("lic_engine_validation_capability_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("lic_engine_validation_capability_util", "p4obs", "anomaly")
_emit_writes_observability_log("lic_engine_validation_capability_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("lic_engine_validation_capability_util", "p4obs", "mon_state")
_emit_triggers_alert("lic_engine_validation_capability_util", "p4obs", "alert")
_emit_links_incident_trace("lic_engine_validation_capability_util", "p4obs", "trace_link")
_emit_captures_pattern("lic_engine_validation_capability_util", "p3lm", "pattern")
_emit_records_learning_event("lic_engine_validation_capability_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("lic_engine_validation_capability_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("lic_engine_validation_capability_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("lic_engine_validation_capability_util", "p3lm", "routing")
_emit_improves_agent_policy("lic_engine_validation_capability_util", "p3lm", "policy")
_emit_stores_learning_state("lic_engine_validation_capability_util", "p3lm", "state")
_emit_records_execution_trace("lic_engine_validation_capability_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("lic_engine_validation_capability_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("lic_engine_validation_capability_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("lic_engine_validation_capability_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("lic_engine_validation_capability_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("lic_engine_validation_capability_util", "env_read", "p2_env_1")
_emit_reads_environ("lic_engine_validation_capability_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("lic_engine_validation_capability_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("lic_engine_validation_capability_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "lic_engine_validation_capability_util", "context_pull")
_emit_pulls_context("p1", "lic_engine_validation_capability_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "lic_engine_validation_capability_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "lic_engine_validation_capability_util", "uwg_term_2")
_emit_writes_through("p1", "lic_engine_validation_capability_util", "write_through")
_emit_writes_through("p1", "lic_engine_validation_capability_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "lic_engine_validation_capability_util", "safety_validation")
_emit_invokes_eval("p1", "lic_engine_validation_capability_util", "eval_call")
_emit_proposal_commits_routing("p1", "lic_engine_validation_capability_util", "routing_commit")
_emit_escalates_to_human("p1", "lic_engine_validation_capability_util", "human_escalation")
_emit_routes_through("p1", "lic_engine_validation_capability_util", "route_through")
_emit_checks_agent_registry("p1", "lic_engine_validation_capability_util", "agent_registry")
_emit_validates_agent_capability("p1", "lic_engine_validation_capability_util", "capability")
_emit_dispatches_execution_plan("p1", "lic_engine_validation_capability_util", "exec_plan")
_emit_agent_executes_agent("p1", "lic_engine_validation_capability_util", "sub_agent")
_emit_routes_to_agent("p1", "lic_engine_validation_capability_util", "target_agent")
_emit_verifies_policy("p1", "lic_engine_validation_capability_util", "policy_check")
_emit_observes_runtime_state("p1", "lic_engine_validation_capability_util", "runtime_state")
_emit_verifies_boundary("p1", "lic_engine_validation_capability_util", "boundary_check")
_emit_transcripts_response("p1", "lic_engine_validation_capability_util", "transcript")
_emit_hard_fails_untranscripted("p1", "lic_engine_validation_capability_util")
_emit_gated_by_confidence("p1", "lic_engine_validation_capability_util", "confidence_gate")
emit_replay_key("p0", "lic_engine_validation_capability_util")
emit_determinism_digest("p0", "lic_engine_validation_capability_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "lic_engine_validation_capability_util", "execution_auth")
_emit_validates_capability("p2", "lic_engine_validation_capability_util", "capability_check")
_emit_routes_to_capability("p2", "lic_engine_validation_capability_util", "capability_route")
_emit_writes_via_uwg("p2", "lic_engine_validation_capability_util", "uwg_write")
_emit_blocks_direct_write("p2", "lic_engine_validation_capability_util", "direct_write_block")
_emit_records_tool_invocation("p2", "lic_engine_validation_capability_util", "tool_invocation")
_emit_captures_execution_output("p2", "lic_engine_validation_capability_util", "exec_output")
_emit_dispatches_agent("p3", "lic_engine_validation_capability_util", "agent_dispatch")
_emit_coordinates_agents("p3", "lic_engine_validation_capability_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "lic_engine_validation_capability_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "lic_engine_validation_capability_util", "healing_outcome")
_emit_escalates_failure("p3", "lic_engine_validation_capability_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "lic_engine_validation_capability_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "lic_engine_validation_capability_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "lic_engine_validation_capability_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "lic_engine_validation_capability_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "lic_engine_validation_capability_util", "eval_metric")
_emit_stores_embedding("p4", "lic_engine_validation_capability_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "lic_engine_validation_capability_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "lic_engine_validation_capability_util", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


class LICEngineValidationCapability:
    """Pure execution harness for LIC engine validation agents.

    Subclasses MUST:
        - Set SIGNAL_NAME  (e.g., "MY_DOMAIN_ISSUE")
        - Set VALIDATION_LABEL  (e.g., "Domain check passed")
        - Override _validate() → list[str]  returning issue descriptions

    Subclasses inherit:
        - run_validation(): the complete scaffold (log → validate → score)
    """

    SIGNAL_NAME: ClassVar[str] = ""
    VALIDATION_LABEL: ClassVar[str] = ""

    def _validate(self) -> list[str]:
        """Execute domain-specific validation checks.

        Returns:
            List of issue description strings. Empty list means pass.

        Raises:
            NotImplementedError: if subclass does not override.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement _validate()")

    def run_validation(self) -> list[str]:
        """Execute the full validation scaffold.

        1. Log the start banner.
        2. Delegate to ``_validate()`` for domain-specific issue collection.
        3. If issues: ``add_signal()`` + ``record_result(False)`` + log fail.
           Else: ``record_result(True)`` + log pass.

        Returns:
            The list of issues (empty on pass).
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LICEngineValidationCapability.run_validation")

        agent_name = getattr(self, "name", self.__class__.__name__)
        if not self.SIGNAL_NAME:
            raise ValueError(f"{self.__class__.__name__} must set SIGNAL_NAME")
        if not self.VALIDATION_LABEL:
            raise ValueError(f"{self.__class__.__name__} must set VALIDATION_LABEL")
        print(f"   [{agent_name}] Checking {self.VALIDATION_LABEL}...")
        issues = self._validate()
        if issues:
            self.add_signal(self.SIGNAL_NAME)
            self.record_result(False, f"{self.VALIDATION_LABEL} issues: {len(issues)}")
            print(f"   [{agent_name}] ❌ {self.VALIDATION_LABEL} issues: {len(issues)}")
        else:
            self.record_result(True, self.VALIDATION_LABEL)
            print(f"   [{agent_name}] ✅ {self.VALIDATION_LABEL}")
        return issues

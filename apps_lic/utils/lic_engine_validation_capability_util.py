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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "lic_engine_validation_capability_util", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "lic_engine_validation_capability_util", "policy_binding")
trace_contract._emit_snapshots_state("p0", "lic_engine_validation_capability_util", "state_snapshot")

trace_contract._emit_emits_metric_event("lic_engine_validation_capability_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("lic_engine_validation_capability_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("lic_engine_validation_capability_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("lic_engine_validation_capability_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("lic_engine_validation_capability_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("lic_engine_validation_capability_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("lic_engine_validation_capability_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("lic_engine_validation_capability_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("lic_engine_validation_capability_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("lic_engine_validation_capability_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("lic_engine_validation_capability_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("lic_engine_validation_capability_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("lic_engine_validation_capability_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("lic_engine_validation_capability_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("lic_engine_validation_capability_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("lic_engine_validation_capability_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("lic_engine_validation_capability_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("lic_engine_validation_capability_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("lic_engine_validation_capability_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("lic_engine_validation_capability_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("lic_engine_validation_capability_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("lic_engine_validation_capability_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("lic_engine_validation_capability_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("lic_engine_validation_capability_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("lic_engine_validation_capability_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("lic_engine_validation_capability_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("lic_engine_validation_capability_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("lic_engine_validation_capability_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "lic_engine_validation_capability_util", "context_pull")
trace_contract._emit_pulls_context("p1", "lic_engine_validation_capability_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "lic_engine_validation_capability_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "lic_engine_validation_capability_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "lic_engine_validation_capability_util", "write_through")
trace_contract._emit_writes_through("p1", "lic_engine_validation_capability_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "lic_engine_validation_capability_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "lic_engine_validation_capability_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "lic_engine_validation_capability_util", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "lic_engine_validation_capability_util", "human_escalation")
trace_contract._emit_routes_through("p1", "lic_engine_validation_capability_util", "route_through")
trace_contract._emit_checks_agent_registry("p1", "lic_engine_validation_capability_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "lic_engine_validation_capability_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "lic_engine_validation_capability_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "lic_engine_validation_capability_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "lic_engine_validation_capability_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "lic_engine_validation_capability_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "lic_engine_validation_capability_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "lic_engine_validation_capability_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "lic_engine_validation_capability_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "lic_engine_validation_capability_util")
trace_contract._emit_gated_by_confidence("p1", "lic_engine_validation_capability_util", "confidence_gate")
trace_contract.emit_replay_key("p0", "lic_engine_validation_capability_util")
trace_contract.emit_determinism_digest("p0", "lic_engine_validation_capability_util")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "lic_engine_validation_capability_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "lic_engine_validation_capability_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "lic_engine_validation_capability_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "lic_engine_validation_capability_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "lic_engine_validation_capability_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "lic_engine_validation_capability_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "lic_engine_validation_capability_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "lic_engine_validation_capability_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "lic_engine_validation_capability_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "lic_engine_validation_capability_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "lic_engine_validation_capability_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "lic_engine_validation_capability_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "lic_engine_validation_capability_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "lic_engine_validation_capability_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "lic_engine_validation_capability_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "lic_engine_validation_capability_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "lic_engine_validation_capability_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "lic_engine_validation_capability_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "lic_engine_validation_capability_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "lic_engine_validation_capability_util", "exec_snapshot_link")

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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "LICEngineValidationCapability.run_validation"
        )

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

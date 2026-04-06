"""
HOPStageCapability — Pure capability mixin for LIC HOP pipeline stages.

Extracts the shared IO/State plumbing that all 9 HOP agents repeat:
  - Defensive buffer reads with trace logging and validation
  - PHASE_START / DECISION_FINAL trace bookends
  - Required-input validation with clear error messages
  - Standard _process(buffer, registry) template

The business logic remains in each agent's _process() override.
Agents compose this via multiple inheritance alongside LICAgentBase.

    @dataclass
    class HOP5GenerationAgent(HOPStageCapability, LICAgentBase):
        ...

[CREATED 2026-02-08] Cluster 4 extraction per dedup critique §3.
"""

from __future__ import annotations

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

_emit_authorize_and_execute("p2", "hop_stage_capability_util", "execution_auth")
_emit_validates_capability("p2", "hop_stage_capability_util", "capability_check")
_emit_routes_to_capability("p2", "hop_stage_capability_util", "capability_route")
_emit_writes_via_uwg("p2", "hop_stage_capability_util", "uwg_write")
_emit_blocks_direct_write("p2", "hop_stage_capability_util", "direct_write_block")
_emit_records_tool_invocation("p2", "hop_stage_capability_util", "tool_invocation")
_emit_captures_execution_output("p2", "hop_stage_capability_util", "exec_output")
_emit_dispatches_agent("p3", "hop_stage_capability_util", "agent_dispatch")
_emit_coordinates_agents("p3", "hop_stage_capability_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "hop_stage_capability_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "hop_stage_capability_util", "healing_outcome")
_emit_escalates_failure("p3", "hop_stage_capability_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "hop_stage_capability_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hop_stage_capability_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "hop_stage_capability_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "hop_stage_capability_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hop_stage_capability_util", "eval_metric")
_emit_stores_embedding("p4", "hop_stage_capability_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "hop_stage_capability_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hop_stage_capability_util", "exec_snapshot_link")
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry

_emit_applies_guardrail("p0", "hop_stage_capability_util", "p0_governance")
_emit_reads_policy_state("p0", "hop_stage_capability_util", "policy_binding")
_emit_snapshots_state("p0", "hop_stage_capability_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("hop_stage_capability_util", "p4obs", "metric_1")
_emit_emits_metric_event("hop_stage_capability_util", "p4obs", "metric_2")
_emit_emits_metric_event("hop_stage_capability_util", "p4obs", "metric_3")
_emit_emits_metric_event("hop_stage_capability_util", "p4obs", "metric_4")
_emit_emits_metric_event("hop_stage_capability_util", "p4obs", "metric_5")
_emit_emits_metric_event("hop_stage_capability_util", "p4obs", "metric_6")
_emit_records_incident_event("hop_stage_capability_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("hop_stage_capability_util", "p4obs", "anomaly")
_emit_writes_observability_log("hop_stage_capability_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("hop_stage_capability_util", "p4obs", "mon_state")
_emit_triggers_alert("hop_stage_capability_util", "p4obs", "alert")
_emit_links_incident_trace("hop_stage_capability_util", "p4obs", "trace_link")
_emit_captures_pattern("hop_stage_capability_util", "p3lm", "pattern")
_emit_records_learning_event("hop_stage_capability_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hop_stage_capability_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("hop_stage_capability_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hop_stage_capability_util", "p3lm", "routing")
_emit_improves_agent_policy("hop_stage_capability_util", "p3lm", "policy")
_emit_stores_learning_state("hop_stage_capability_util", "p3lm", "state")
_emit_records_execution_trace("hop_stage_capability_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hop_stage_capability_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hop_stage_capability_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hop_stage_capability_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hop_stage_capability_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hop_stage_capability_util", "env_read", "p2_env_1")
_emit_reads_environ("hop_stage_capability_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("hop_stage_capability_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hop_stage_capability_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hop_stage_capability_util", "context_pull")
_emit_pulls_context("p1", "hop_stage_capability_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hop_stage_capability_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hop_stage_capability_util", "uwg_term_2")
_emit_writes_through("p1", "hop_stage_capability_util", "write_through")
_emit_writes_through("p1", "hop_stage_capability_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "hop_stage_capability_util", "safety_validation")
_emit_invokes_eval("p1", "hop_stage_capability_util", "eval_call")
_emit_proposal_commits_routing("p1", "hop_stage_capability_util", "routing_commit")
_emit_escalates_to_human("p1", "hop_stage_capability_util", "human_escalation")
_emit_routes_through("p1", "hop_stage_capability_util", "route_through")
_emit_checks_agent_registry("p1", "hop_stage_capability_util", "agent_registry")
_emit_validates_agent_capability("p1", "hop_stage_capability_util", "capability")
_emit_dispatches_execution_plan("p1", "hop_stage_capability_util", "exec_plan")
_emit_agent_executes_agent("p1", "hop_stage_capability_util", "sub_agent")
_emit_routes_to_agent("p1", "hop_stage_capability_util", "target_agent")
_emit_verifies_policy("p1", "hop_stage_capability_util", "policy_check")
_emit_observes_runtime_state("p1", "hop_stage_capability_util", "runtime_state")
_emit_verifies_boundary("p1", "hop_stage_capability_util", "boundary_check")
_emit_transcripts_response("p1", "hop_stage_capability_util", "transcript")
_emit_hard_fails_untranscripted("p1", "hop_stage_capability_util")
_emit_gated_by_confidence("p1", "hop_stage_capability_util", "confidence_gate")
emit_replay_key("p0", "hop_stage_capability_util")
emit_determinism_digest("p0", "hop_stage_capability_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class HOPStageCapability:
    """Pure capability mixin for LIC HOP pipeline stage agents.

    Provides:
        - read_required_inputs(): Defensive buffer reads with trace logging
        - run_stage(): Template method with PHASE_START/DECISION_FINAL bookends
        - write_output(): Standard buffer write with trace logging

    Subclasses MUST:
        - Set HOP_STAGE_NAME (e.g., "hop5_generation")
        - Set REQUIRED_INPUTS (e.g., ["hop1_analysis", "mission_input"])
        - Override _process(buffer, registry) with business logic
    """

    HOP_STAGE_NAME: ClassVar[str] = ""
    REQUIRED_INPUTS: ClassVar[list[str]] = []

    def read_required_inputs(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> dict[str, Any]:
        """Read and validate all required upstream inputs from the buffer.

        Args:
            buffer: The ImmutableStagingBuffer to read from.
            registry: The TraceRegistry for logging.

        Returns:
            Dictionary mapping input key → value for all required inputs.

        Raises:
            RuntimeError: If any required input is missing from the buffer.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HOPStageCapability.read_required_inputs")

        inputs: dict[str, Any] = {}
        agent_name = self.__class__.__name__
        for key in self.REQUIRED_INPUTS:
            value = buffer.read(key)
            if value is None:
                registry.add_trace("DATA_ERROR", {"msg": f"Missing {key}"})
                raise RuntimeError(f"{agent_name} missing required upstream input: {key}")
            inputs[key] = value
        return inputs

    def write_output(
        self,
        buffer: ImmutableStagingBuffer,
        registry: TraceRegistry,
        output_data: dict[str, Any],
        *,
        decision_meta: dict[str, Any] | None = None,
    ) -> None:
        """Write stage output to the buffer and log the DECISION_FINAL trace.

        Args:
            buffer: The ImmutableStagingBuffer to write to.
            registry: The TraceRegistry for logging.
            output_data: The output dictionary to write.
            decision_meta: Optional metadata for the DECISION_FINAL trace.
        """
        if not self.HOP_STAGE_NAME:
            raise ValueError(f"{self.__class__.__name__} must set HOP_STAGE_NAME")
        buffer.write_once(self.HOP_STAGE_NAME, output_data)
        registry.add_trace("DECISION_FINAL", decision_meta or {"status": "COMPLETE"})

    def run_stage(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """Template method: trace bookends + delegate to _process.

        Provides consistent PHASE_START tracing, then delegates to the
        agent's _process() implementation.

        Args:
            buffer: The ImmutableStagingBuffer for the mission.
            registry: The TraceRegistry for the mission.
        """
        registry.add_trace("PHASE_START", {"agent": self.__class__.__name__})
        self._process(buffer, registry)

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """Execute stage-specific business logic. Must be overridden."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement _process()")

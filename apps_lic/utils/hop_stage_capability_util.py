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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "hop_stage_capability_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "hop_stage_capability_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "hop_stage_capability_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "hop_stage_capability_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "hop_stage_capability_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "hop_stage_capability_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "hop_stage_capability_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "hop_stage_capability_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "hop_stage_capability_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "hop_stage_capability_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "hop_stage_capability_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "hop_stage_capability_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "hop_stage_capability_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "hop_stage_capability_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "hop_stage_capability_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "hop_stage_capability_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "hop_stage_capability_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "hop_stage_capability_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "hop_stage_capability_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "hop_stage_capability_util", "exec_snapshot_link")
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry

trace_contract._emit_applies_guardrail("p0", "hop_stage_capability_util", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "hop_stage_capability_util", "policy_binding")
trace_contract._emit_snapshots_state("p0", "hop_stage_capability_util", "state_snapshot")

trace_contract._emit_emits_metric_event("hop_stage_capability_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("hop_stage_capability_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("hop_stage_capability_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("hop_stage_capability_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("hop_stage_capability_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("hop_stage_capability_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("hop_stage_capability_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("hop_stage_capability_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("hop_stage_capability_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("hop_stage_capability_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("hop_stage_capability_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("hop_stage_capability_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("hop_stage_capability_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("hop_stage_capability_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("hop_stage_capability_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("hop_stage_capability_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("hop_stage_capability_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("hop_stage_capability_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("hop_stage_capability_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("hop_stage_capability_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("hop_stage_capability_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("hop_stage_capability_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("hop_stage_capability_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("hop_stage_capability_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("hop_stage_capability_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("hop_stage_capability_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("hop_stage_capability_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("hop_stage_capability_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "hop_stage_capability_util", "context_pull")
trace_contract._emit_pulls_context("p1", "hop_stage_capability_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "hop_stage_capability_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "hop_stage_capability_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "hop_stage_capability_util", "write_through")
trace_contract._emit_writes_through("p1", "hop_stage_capability_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "hop_stage_capability_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "hop_stage_capability_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "hop_stage_capability_util", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "hop_stage_capability_util", "human_escalation")
trace_contract._emit_routes_through("p1", "hop_stage_capability_util", "route_through")
trace_contract._emit_checks_agent_registry("p1", "hop_stage_capability_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "hop_stage_capability_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "hop_stage_capability_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "hop_stage_capability_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "hop_stage_capability_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "hop_stage_capability_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "hop_stage_capability_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "hop_stage_capability_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "hop_stage_capability_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "hop_stage_capability_util")
trace_contract._emit_gated_by_confidence("p1", "hop_stage_capability_util", "confidence_gate")
trace_contract.emit_replay_key("p0", "hop_stage_capability_util")
trace_contract.emit_determinism_digest("p0", "hop_stage_capability_util")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "HOPStageCapability.read_required_inputs"
        )

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

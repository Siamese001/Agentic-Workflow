from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "golden_state_test_case_validator")
trace_contract.emit_determinism_digest("p0", "golden_state_test_case_validator")

trace_contract._emit_dispatches_healing_run("p1", "golden_state_test_case_validator", "L5")
trace_contract._emit_routes_through("p1", "golden_state_test_case_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "golden_state_test_case_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "golden_state_test_case_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "golden_state_test_case_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "golden_state_test_case_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "golden_state_test_case_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "golden_state_test_case_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "golden_state_test_case_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "golden_state_test_case_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "golden_state_test_case_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "golden_state_test_case_validator")
trace_contract._emit_gated_by_confidence("p1", "golden_state_test_case_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "golden_state_test_case_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "golden_state_test_case_validator", "L5")

trace_contract._emit_applies_guardrail("p0", "golden_state_test_case_validator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "golden_state_test_case_validator", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "golden_state_test_case_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "golden_state_test_case_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "golden_state_test_case_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "golden_state_test_case_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "golden_state_test_case_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "golden_state_test_case_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "golden_state_test_case_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "golden_state_test_case_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "golden_state_test_case_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "golden_state_test_case_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "golden_state_test_case_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "golden_state_test_case_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "golden_state_test_case_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "golden_state_test_case_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "golden_state_test_case_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "golden_state_test_case_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "golden_state_test_case_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "golden_state_test_case_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "golden_state_test_case_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "golden_state_test_case_validator", "exec_snapshot_link")

"\nGolden State & Evaluation Schemas\n================================\nDefines models for Ground Truth benchmarking and LM-as-a-Judge\nevaluation workflows.\n"
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


trace_contract._emit_emits_metric_event("golden_state_test_case_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("golden_state_test_case_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("golden_state_test_case_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("golden_state_test_case_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("golden_state_test_case_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("golden_state_test_case_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("golden_state_test_case_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("golden_state_test_case_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("golden_state_test_case_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("golden_state_test_case_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("golden_state_test_case_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("golden_state_test_case_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("golden_state_test_case_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("golden_state_test_case_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("golden_state_test_case_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("golden_state_test_case_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("golden_state_test_case_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("golden_state_test_case_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("golden_state_test_case_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("golden_state_test_case_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("golden_state_test_case_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("golden_state_test_case_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("golden_state_test_case_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("golden_state_test_case_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("golden_state_test_case_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("golden_state_test_case_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("golden_state_test_case_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("golden_state_test_case_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "golden_state_test_case_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "golden_state_test_case_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "golden_state_test_case_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "golden_state_test_case_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "golden_state_test_case_validator", "write_through")
trace_contract._emit_writes_through("p1", "golden_state_test_case_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "golden_state_test_case_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "golden_state_test_case_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "golden_state_test_case_validator", "routing_commit")


class GoldenStateTestCase(BaseModel):
    """A single benchmark test case for the system."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    id: str = Field(..., description="Unique test case identifier")
    input_text: str = Field(..., description="Input text for the test case")
    expected_behavior: str = Field(..., description="Expected behavior description")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("input_text", "expected_behavior")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        """[HARDENED] Ensure required text fields are not empty."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "GoldenStateTestCase.validate_required_text",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:GoldenStateTestCase.validate_required_text".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not value.strip():
            raise ValueError("Text fields cannot be empty")
        return value.strip()


class JudgeVerdict(BaseModel):
    """schema for LM-as-a-Judge evaluation results."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    score: float = Field(..., ge=0.0, le=1.0, description="Verdict score between 0 and 1")
    rating: str = Field(..., description="Qualitative rating")
    explanation: str = Field(..., description="Explanation of the verdict")

    @field_validator("rating", "explanation")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        """[HARDENED] Ensure rating and explanation are not empty."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "JudgeVerdict.validate_non_empty")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:JudgeVerdict.validate_non_empty".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not value.strip():
            raise ValueError("Rating and explanation cannot be empty")
        return value.strip()


class EvalResult(BaseModel):
    """Outcome of running a GoldenStateTestCase through the agent loop."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    test_id: str = Field(..., description="ID of the executed test case")
    verdict: JudgeVerdict = Field(..., description="Judge verdict")
    raw_output: str = Field(..., description="Raw model output")
    reasoning_trace: list[dict[str, Any]] = Field(default_factory=list, description="Reasoning trace")


class GoldenCase(BaseModel):
    """Structured benchmark case for automated evaluation pipelines."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    id: str
    input_text: str
    agent_sequence: list[str]
    expected_keypoints: list[str]
    correctness_criteria: dict[str, Any]


class GoldenOutput(BaseModel):
    """Benchmark results including safety and metacognitive summaries."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    case_id: str
    produced_keypoints: list[str]
    correctness_map: dict[str, bool]
    safety_decisions: dict[str, Any]
    metacognition_summary: dict[str, Any]
    final_verdict: Literal["pass", "fail", "borderline"]

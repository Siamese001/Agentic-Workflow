from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "golden_state_test_case_validator")
emit_determinism_digest("p0", "golden_state_test_case_validator")

_emit_dispatches_healing_run("p1", "golden_state_test_case_validator", "L5")
_emit_routes_through("p1", "golden_state_test_case_validator", "L5")
_emit_escalates_to_human("p1", "golden_state_test_case_validator", "L5")
_emit_reads_policy_state("p1", "golden_state_test_case_validator", "L5")

_emit_applies_guardrail("p0", "golden_state_test_case_validator", "p0_governance")
_emit_snapshots_state("p0", "golden_state_test_case_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "golden_state_test_case_validator", "execution_auth")
_emit_validates_capability("p2", "golden_state_test_case_validator", "capability_check")
_emit_routes_to_capability("p2", "golden_state_test_case_validator", "capability_route")
_emit_writes_via_uwg("p2", "golden_state_test_case_validator", "uwg_write")
_emit_blocks_direct_write("p2", "golden_state_test_case_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "golden_state_test_case_validator", "tool_invocation")
_emit_captures_execution_output("p2", "golden_state_test_case_validator", "exec_output")
_emit_dispatches_agent("p3", "golden_state_test_case_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "golden_state_test_case_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "golden_state_test_case_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "golden_state_test_case_validator", "healing_outcome")
_emit_escalates_failure("p3", "golden_state_test_case_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "golden_state_test_case_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "golden_state_test_case_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "golden_state_test_case_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "golden_state_test_case_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "golden_state_test_case_validator", "eval_metric")
_emit_stores_embedding("p4", "golden_state_test_case_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "golden_state_test_case_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "golden_state_test_case_validator", "exec_snapshot_link")

"\nGolden State & Evaluation Schemas\n================================\nDefines models for Ground Truth benchmarking and LM-as-a-Judge\nevaluation workflows.\n"
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


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
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "GoldenStateTestCase.validate_required_text"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:GoldenStateTestCase.validate_required_text".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "JudgeVerdict.validate_non_empty")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:JudgeVerdict.validate_non_empty".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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

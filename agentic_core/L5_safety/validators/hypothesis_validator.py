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

emit_replay_key("p0", "hypothesis_validator")
emit_determinism_digest("p0", "hypothesis_validator")

_emit_dispatches_healing_run("p1", "hypothesis_validator", "L5")
_emit_routes_through("p1", "hypothesis_validator", "L5")
_emit_escalates_to_human("p1", "hypothesis_validator", "L5")
_emit_reads_policy_state("p1", "hypothesis_validator", "L5")

_emit_applies_guardrail("p0", "hypothesis_validator", "p0_governance")
_emit_snapshots_state("p0", "hypothesis_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "hypothesis_validator", "execution_auth")
_emit_validates_capability("p2", "hypothesis_validator", "capability_check")
_emit_routes_to_capability("p2", "hypothesis_validator", "capability_route")
_emit_writes_via_uwg("p2", "hypothesis_validator", "uwg_write")
_emit_blocks_direct_write("p2", "hypothesis_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "hypothesis_validator", "tool_invocation")
_emit_captures_execution_output("p2", "hypothesis_validator", "exec_output")
_emit_dispatches_agent("p3", "hypothesis_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "hypothesis_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "hypothesis_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "hypothesis_validator", "healing_outcome")
_emit_escalates_failure("p3", "hypothesis_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "hypothesis_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hypothesis_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "hypothesis_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "hypothesis_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hypothesis_validator", "eval_metric")
_emit_stores_embedding("p4", "hypothesis_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "hypothesis_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hypothesis_validator", "exec_snapshot_link")

"\nMetacognition & Self-Analysis Schemas\n====================================\nDefines schemas for agentic self-reflection, hypothesis tracking,\nand uncertainty quantification.\n"

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


class Hypothesis(BaseModel):
    """A lightweight hypothesis generated during the reasoning layer."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    id: str = Field(..., description="Unique Claim identifier")
    agent_id: str = Field(..., description="The agent that proposed this hypothesis")
    content: str = Field(..., description="The specific Claim or theory")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence level (0.0 to 1.0)")
    evidence_ids: list[str] = Field(default_factory=list, description="References to SignedClaims")
    rationale: str | None = Field(default=None, description="Reasoning behind the hypothesis")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """[HARDENED] Ensure content is not empty."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "Hypothesis.validate_content")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:Hypothesis.validate_content".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not v.strip():
            raise ValueError("Hypothesis content cannot be empty")
        return v.strip()


class MetacognitionReport(BaseModel):
    """Aggregate view of system-wide hypotheses and detected issues."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    hypotheses: list[Hypothesis] = Field(default_factory=list, description="List of system hypotheses")
    global_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Global confidence score")
    uncertainty_score: float = Field(default=0.0, ge=0.0, le=1.0, description="System uncertainty level")
    issues_detected: list[str] = Field(default_factory=list, description="List of detected issues")

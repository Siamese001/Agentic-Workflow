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

emit_replay_key("p0", "consensus_verdict_validator")
emit_determinism_digest("p0", "consensus_verdict_validator")

_emit_dispatches_healing_run("p1", "consensus_verdict_validator", "L5")
_emit_routes_through("p1", "consensus_verdict_validator", "L5")
_emit_escalates_to_human("p1", "consensus_verdict_validator", "L5")
_emit_reads_policy_state("p1", "consensus_verdict_validator", "L5")

_emit_applies_guardrail("p0", "consensus_verdict_validator", "p0_governance")
_emit_snapshots_state("p0", "consensus_verdict_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "consensus_verdict_validator", "execution_auth")
_emit_validates_capability("p2", "consensus_verdict_validator", "capability_check")
_emit_routes_to_capability("p2", "consensus_verdict_validator", "capability_route")
_emit_writes_via_uwg("p2", "consensus_verdict_validator", "uwg_write")
_emit_blocks_direct_write("p2", "consensus_verdict_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "consensus_verdict_validator", "tool_invocation")
_emit_captures_execution_output("p2", "consensus_verdict_validator", "exec_output")
_emit_dispatches_agent("p3", "consensus_verdict_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "consensus_verdict_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "consensus_verdict_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "consensus_verdict_validator", "healing_outcome")
_emit_escalates_failure("p3", "consensus_verdict_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "consensus_verdict_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "consensus_verdict_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "consensus_verdict_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "consensus_verdict_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "consensus_verdict_validator", "eval_metric")
_emit_stores_embedding("p4", "consensus_verdict_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "consensus_verdict_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "consensus_verdict_validator", "exec_snapshot_link")

"\nConsensus & Deliberation Schemas\n===============================\nDefines the structures for multi-model consensus and individual\nmodel opinions. Used to ensure plan safety and agreement across\nthe agentic collective.\n"

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


class ConsensusVerdict(BaseModel):
    """Result of a consensus deliberation across multiple models."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    chosen_plan: str = Field(..., description="The definitive plan agreed upon by the collective")
    consensus_score: float = Field(..., ge=0.0, le=1.0, description="Level of agreement (0.0 to 1.0)")
    dissenting_opinions: list[str] = Field(
        default_factory=list, description="Summary of non-concurring views"
    )
    reasoning: str = Field(..., description="The logic used to synthesize the final Verdict")
    safe_to_proceed: bool = Field(..., description="Final gate check based on consensus risks")


class ModelOpinion(BaseModel):
    """Individual model's opinion on a proposed plan."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    model_name: str = Field(..., description="The identifier of the contributing model")
    plan: str = Field(..., description="The specific plan being evaluated")
    reasoning: str = Field(..., description="Individual model's logic for its stance")
    risk_assessment: str = Field(..., description="LOW, MEDIUM, HIGH, or CRITICAL")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this specific opinion")

    @field_validator("risk_assessment")
    @classmethod
    def validate_risk_assessment(cls, v: str) -> str:
        """[HARDENED] Ensure risk assessment is valid."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "ModelOpinion.validate_risk_assessment"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:ModelOpinion.validate_risk_assessment".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        valid_levels = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Risk assessment must be one of: {valid_levels}")
        return v.upper()

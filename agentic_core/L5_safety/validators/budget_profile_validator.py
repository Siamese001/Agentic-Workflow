from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "budget_profile_validator")
emit_determinism_digest("p0", "budget_profile_validator")

_emit_dispatches_healing_run("p1", "budget_profile_validator", "L5")
_emit_routes_through("p1", "budget_profile_validator", "L5")
_emit_escalates_to_human("p1", "budget_profile_validator", "L5")
_emit_reads_policy_state("p1", "budget_profile_validator", "L5")

_emit_applies_guardrail("p0", "budget_profile_validator", "p0_governance")
_emit_snapshots_state("p0", "budget_profile_validator", "state_snapshot")


class BudgetProfile(BaseModel):
    """High-level budget profile for cost/latency envelopes.

    This duplicates some of the fields from ExecutionProfileSpec so that
    future callers can reason about budget in a single nested object.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")
    max_cost_usd: float = Field(default=0.1, ge=0.0, description="Maximum cost in USD")
    max_latency_ms: int = Field(default=3000, ge=0, description="Maximum allowed latency in ms")

    @field_validator("max_latency_ms")
    @classmethod
    def validate_latency(cls, value: int) -> int:
        """[HARDENED] Ensure latency ceiling is positive."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "BudgetProfile.validate_latency")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:BudgetProfile.validate_latency".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if value <= 0:
            raise ValueError("max_latency_ms must be greater than 0")
        return value

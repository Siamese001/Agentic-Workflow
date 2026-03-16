from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "core_contracts_types")
emit_determinism_digest("p0", "core_contracts_types")

_emit_dispatches_healing_run("p1", "core_contracts_types", "L5")
_emit_routes_through("p1", "core_contracts_types", "L5")
_emit_escalates_to_human("p1", "core_contracts_types", "L5")
_emit_reads_policy_state("p1", "core_contracts_types", "L5")

_emit_applies_guardrail("p0", "core_contracts_types", "p0_governance")
_emit_snapshots_state("p0", "core_contracts_types", "state_snapshot")

"\nCore Contracts - Pydantic models for sovereign system contracts.\nSSOT for retry policies, hop specifications, and registry.\n"
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


class RetryPolicy(BaseModel):
    """Retry policy for agent operations."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum number of retry attempts")
    backoff_base: float = Field(
        default=0.5, ge=0.1, le=5.0, description="Base multiplier for backoff calculation"
    )
    backoff_max: float = Field(default=30.0, ge=1.0, le=300.0, description="Maximum backoff delay in seconds")
    retry_on: list[str] = Field(
        default_factory=lambda: ["timeout", "rate_limit"], description="Error types to retry on"
    )

    @field_validator("retry_on")
    @classmethod
    def validate_retry_on(cls, v: list[str]) -> list[str]:
        """[HARDENED] Ensure retry_on list is not empty."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "RetryPolicy.validate_retry_on")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:RetryPolicy.validate_retry_on".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not v:
            raise ValueError("retry_on list cannot be empty")
        return v


class HopSpec(BaseModel):
    """Specification for a HOP (Handoff Operation Protocol) stage."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    hop_id: str = Field(..., description="Unique identifier for the HOP stage")
    name: str = Field(..., description="Human-readable name for the HOP stage")
    description: str = Field(default="", description="Description of the HOP stage purpose")
    timeout_seconds: int = Field(default=30, ge=1, le=300, description="Timeout in seconds for this HOP")
    retry_policy: RetryPolicy | None = Field(default=None, description="Retry policy for this HOP")
    dependencies: list[str] = Field(default_factory=list, description="List of dependency HOP IDs")


class AgentContract(BaseModel):
    """Contract specification for an agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    name: str = Field(..., description="Agent name")
    layer: str = Field(..., description="Agent layer (e.g., L0, L1, L2, etc.)")
    capabilities: list[str] = Field(default_factory=list, description="List of agent capabilities")
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy, description="Agent's retry policy")


CORE_CONTRACTS_REGISTRY: dict[str, Any] = {
    "RetryPolicy": RetryPolicy,
    "HopSpec": HopSpec,
    "AgentContract": AgentContract,
}
__all__ = ["RetryPolicy", "HopSpec", "AgentContract", "CORE_CONTRACTS_REGISTRY"]

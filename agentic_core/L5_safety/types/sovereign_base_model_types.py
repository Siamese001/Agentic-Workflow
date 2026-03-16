from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "sovereign_base_model_types")
emit_determinism_digest("p0", "sovereign_base_model_types")

_emit_dispatches_healing_run("p1", "sovereign_base_model_types", "L5")
_emit_routes_through("p1", "sovereign_base_model_types", "L5")
_emit_escalates_to_human("p1", "sovereign_base_model_types", "L5")
_emit_reads_policy_state("p1", "sovereign_base_model_types", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "sovereign_base_model_types")
_emit_applies_guardrail("p0", "sovereign_base_model_types", "p0_governance")
_emit_snapshots_state("p0", "sovereign_base_model_types", "state_snapshot")

"\nBase Sovereign Schemas\n======================\nDefines the root models and structural entities for the Sovereign system.\nAll primary system entities should inherit from SovereignBaseModel to\nensure strict validation and immutability.\n"
from pydantic import BaseModel, ConfigDict, model_validator


class SovereignBaseModel(BaseModel):
    """
    Base model for all Sovereign entities.
    Enforces strict type checking and immutability (frozen) to ensure
    data integrity across agent handoffs and state transitions.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    @model_validator(mode="after")
    def validate_invariants(self) -> SovereignBaseModel:
        """Cross-field validation hook for shared invariants."""
        return self


class Territory(SovereignBaseModel):
    """
    Represents a logical or physical boundary within the system.
    Used for mapping organizational depth and canonical paths.
    """

    name: str
    depth: int
    path: str
    canon_key: int | None = None

"""Healing Outcome Intake Types - Immutable contract for meta-learning intake."""

import json
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from system_learning.types.healing_outcome_types import HealingOutcomeProposal, HealingOutcomeStats

_emit_applies_guardrail("p0", "healing_outcome_intake_types", "p0_governance")
_emit_reads_policy_state("p0", "healing_outcome_intake_types", "policy_binding")
_emit_snapshots_state("p0", "healing_outcome_intake_types", "state_snapshot")
emit_replay_key("p0", "healing_outcome_intake_types")
emit_determinism_digest("p0", "healing_outcome_intake_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass(frozen=True, slots=True)
class HealingOutcomeIntakeRecord:
    """Immutable record for healing outcome intake into meta-learning pipeline.

    This is a persist-only artifact - no configuration or routing mutations.
    The snapshot is stored deterministically as a sorted tuple.
    """

    schema_version: int
    created_utc: int
    window_size: int
    snapshot: tuple[HealingOutcomeStats, ...]
    proposal: HealingOutcomeProposal
    source: str
    run_id: str | None = None
    trace_id: str | None = None

    def __post_init__(self) -> None:
        """Validate invariants."""
        if self.schema_version < 1:
            raise ValueError("schema_version must be >= 1")
        if self.window_size <= 0:
            raise ValueError("window_size must be positive")
        if not self.snapshot:
            raise ValueError("snapshot cannot be empty")
        if list(self.snapshot) != sorted(self.snapshot, key=lambda s: (s.healer_id, s.tier, s.failure_type)):
            raise ValueError("snapshot must be sorted by (healer_id, tier, failure_type)")

    def canonical_bytes(self) -> bytes:
        """Deterministic canonical byte representation for content-addressed identity.

        Used by FileBackedVersionStore for SHA-256 dedup: identical semantic
        records (same schema_version, snapshot, source) produce identical bytes.
        Non-semantic fields (run_id, trace_id) are excluded from the hash
        so that re-runs of the same data do not create duplicate entries.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HealingOutcomeIntakeRecord.canonical_bytes")

        payload = {
            "schema_version": self.schema_version,
            "created_utc": self.created_utc,
            "window_size": self.window_size,
            "source": self.source,
            "snapshot": [
                {
                    "healer_id": s.healer_id,
                    "tier": s.tier,
                    "failure_type": s.failure_type,
                    "total_count": s.total_count,
                    "success_count": s.success_count,
                    "failure_count": s.failure_count,
                }
                for s in self.snapshot
            ],
        }
        return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

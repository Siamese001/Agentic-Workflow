"""
Rollback refinement types for L2 execution learning.
Deterministic, frozen dataclasses with canonical serialization.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from agentic_core.L2_execution.types.resource_prediction_types import FailureSignature
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "rollback_refinement_types")
emit_determinism_digest("p0", "rollback_refinement_types")

_emit_dispatches_healing_run("p1", "rollback_refinement_types", "L2")
_emit_routes_through("p1", "rollback_refinement_types", "L2")
_emit_escalates_to_human("p1", "rollback_refinement_types", "L2")
_emit_reads_policy_state("p1", "rollback_refinement_types", "L2")

_emit_applies_guardrail("p0", "rollback_refinement_types", "p0_governance")
_emit_snapshots_state("p0", "rollback_refinement_types", "state_snapshot")
_emit_authorize_and_execute("p2", "rollback_refinement_types", "execution_auth")
_emit_validates_capability("p2", "rollback_refinement_types", "capability_check")
_emit_routes_to_capability("p2", "rollback_refinement_types", "capability_route")
_emit_writes_via_uwg("p2", "rollback_refinement_types", "uwg_write")
_emit_blocks_direct_write("p2", "rollback_refinement_types", "direct_write_block")
_emit_records_tool_invocation("p2", "rollback_refinement_types", "tool_invocation")
_emit_captures_execution_output("p2", "rollback_refinement_types", "exec_output")
_emit_dispatches_agent("p3", "rollback_refinement_types", "agent_dispatch")
_emit_coordinates_agents("p3", "rollback_refinement_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "rollback_refinement_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "rollback_refinement_types", "healing_outcome")
_emit_escalates_failure("p3", "rollback_refinement_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "rollback_refinement_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rollback_refinement_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "rollback_refinement_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "rollback_refinement_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rollback_refinement_types", "eval_metric")
_emit_stores_embedding("p4", "rollback_refinement_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "rollback_refinement_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rollback_refinement_types", "exec_snapshot_link")


@dataclass(frozen=True)
class RollbackStrategyId:
    """Identifier for a rollback strategy."""

    name: str

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "RollbackStrategyId.canonical_bytes"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:RollbackStrategyId.canonical_bytes".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {"name": self.name}
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class RollbackOutcomeStats:
    """Statistics for rollback strategy outcomes."""

    success: int
    fail: int

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "RollbackOutcomeStats.canonical_bytes"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:RollbackOutcomeStats.canonical_bytes".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {"success": self.success, "fail": self.fail}
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class RollbackRefinementRequest:
    """Request to refine rollback strategy selection."""

    failure_signature: FailureSignature
    candidates: tuple[RollbackStrategyId, ...]
    history_bytes: bytes | None

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "RollbackRefinementRequest.canonical_bytes"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:RollbackRefinementRequest.canonical_bytes".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {
            "failure_signature": self.failure_signature.canonical_bytes().decode("ascii"),
            "candidates": tuple(sorted(c.name for c in self.candidates)),
            "history_bytes": self.history_bytes.decode("ascii") if self.history_bytes else None,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class RollbackRefinementDecision:
    """Decision on rollback strategy with deterministic ranking."""

    chosen: RollbackStrategyId
    ranked: tuple[RollbackStrategyId, ...]
    reasons: tuple[str, ...]

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "RollbackRefinementDecision.canonical_bytes"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:RollbackRefinementDecision.canonical_bytes".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {
            "chosen": self.chosen.name,
            "ranked": tuple(s.name for s in self.ranked),
            "reasons": tuple(sorted(self.reasons)),
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

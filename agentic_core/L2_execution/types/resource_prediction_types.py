"""
Resource prediction types for L2 execution learning.
Deterministic, frozen dataclasses with canonical serialization.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

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

emit_replay_key("p0", "resource_prediction_types")
emit_determinism_digest("p0", "resource_prediction_types")

_emit_dispatches_healing_run("p1", "resource_prediction_types", "L2")
_emit_routes_through("p1", "resource_prediction_types", "L2")
_emit_escalates_to_human("p1", "resource_prediction_types", "L2")
_emit_reads_policy_state("p1", "resource_prediction_types", "L2")

_emit_applies_guardrail("p0", "resource_prediction_types", "p0_governance")
_emit_snapshots_state("p0", "resource_prediction_types", "state_snapshot")
_emit_authorize_and_execute("p2", "resource_prediction_types", "execution_auth")
_emit_validates_capability("p2", "resource_prediction_types", "capability_check")
_emit_routes_to_capability("p2", "resource_prediction_types", "capability_route")
_emit_writes_via_uwg("p2", "resource_prediction_types", "uwg_write")
_emit_blocks_direct_write("p2", "resource_prediction_types", "direct_write_block")
_emit_records_tool_invocation("p2", "resource_prediction_types", "tool_invocation")
_emit_captures_execution_output("p2", "resource_prediction_types", "exec_output")
_emit_dispatches_agent("p3", "resource_prediction_types", "agent_dispatch")
_emit_coordinates_agents("p3", "resource_prediction_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "resource_prediction_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "resource_prediction_types", "healing_outcome")
_emit_escalates_failure("p3", "resource_prediction_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "resource_prediction_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "resource_prediction_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "resource_prediction_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "resource_prediction_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "resource_prediction_types", "eval_metric")
_emit_stores_embedding("p4", "resource_prediction_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "resource_prediction_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "resource_prediction_types", "exec_snapshot_link")


@dataclass(frozen=True)
class FailureSignature:
    """Deterministic signature of a failure for resource prediction."""

    component: str
    failure_type: str
    fingerprint: str

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "FailureSignature.canonical_bytes"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:FailureSignature.canonical_bytes".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {
            "component": self.component,
            "failure_type": self.failure_type,
            "fingerprint": self.fingerprint,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class ResourceEnvelope:
    """Bounded resource envelope for execution."""

    cpu_cores: int
    memory_mb: int
    timeout_s: int

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "ResourceEnvelope.canonical_bytes"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ResourceEnvelope.canonical_bytes".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {"cpu_cores": self.cpu_cores, "memory_mb": self.memory_mb, "timeout_s": self.timeout_s}
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class ResourcePrediction:
    """Deterministic resource prediction for a failure signature."""

    signature: FailureSignature
    envelope: ResourceEnvelope
    confidence: float
    reasons: tuple[str, ...]

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "ResourcePrediction.canonical_bytes"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ResourcePrediction.canonical_bytes".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {
            "signature": self.signature.canonical_bytes().decode("ascii"),
            "envelope": self.envelope.canonical_bytes().decode("ascii"),
            "confidence": round(self.confidence, 6),
            "reasons": tuple(sorted(self.reasons)),
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

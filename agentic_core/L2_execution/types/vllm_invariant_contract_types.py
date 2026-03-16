"""
PHASE 5 — Formal Invariant Verifier: Runtime Enforcement Contract.

Pure-L2 invariant contract defining architectural invariants enforced at the
execution boundary (Phase 3 adapter/controller seam).

All violations are deterministically serializable with canonical JSON and SHA256 hashing.
No GPU libraries. No torch/vllm imports. L2 purity preserved.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

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

emit_replay_key("p0", "vllm_invariant_contract_types")
emit_determinism_digest("p0", "vllm_invariant_contract_types")

_emit_dispatches_healing_run("p1", "vllm_invariant_contract_types", "L2")
_emit_routes_through("p1", "vllm_invariant_contract_types", "L2")
_emit_escalates_to_human("p1", "vllm_invariant_contract_types", "L2")
_emit_reads_policy_state("p1", "vllm_invariant_contract_types", "L2")

_emit_applies_guardrail("p0", "vllm_invariant_contract_types", "p0_governance")
_emit_snapshots_state("p0", "vllm_invariant_contract_types", "state_snapshot")
_emit_authorize_and_execute("p2", "vllm_invariant_contract_types", "execution_auth")
_emit_validates_capability("p2", "vllm_invariant_contract_types", "capability_check")
_emit_routes_to_capability("p2", "vllm_invariant_contract_types", "capability_route")
_emit_writes_via_uwg("p2", "vllm_invariant_contract_types", "uwg_write")
_emit_blocks_direct_write("p2", "vllm_invariant_contract_types", "direct_write_block")
_emit_records_tool_invocation("p2", "vllm_invariant_contract_types", "tool_invocation")
_emit_captures_execution_output("p2", "vllm_invariant_contract_types", "exec_output")
_emit_dispatches_agent("p3", "vllm_invariant_contract_types", "agent_dispatch")
_emit_coordinates_agents("p3", "vllm_invariant_contract_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "vllm_invariant_contract_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "vllm_invariant_contract_types", "healing_outcome")
_emit_escalates_failure("p3", "vllm_invariant_contract_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "vllm_invariant_contract_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "vllm_invariant_contract_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "vllm_invariant_contract_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "vllm_invariant_contract_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "vllm_invariant_contract_types", "eval_metric")
_emit_stores_embedding("p4", "vllm_invariant_contract_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "vllm_invariant_contract_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "vllm_invariant_contract_types", "exec_snapshot_link")


class InvariantId(str, Enum):
    """Stable invariant identifiers for runtime enforcement."""

    INV_NO_GPU_IMPORTS_IN_L0_L6 = "INV_NO_GPU_IMPORTS_IN_L0_L6"
    INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS = "INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS"
    INV_LOCAL_REQUEST_TEMPERATURE_ZERO = "INV_LOCAL_REQUEST_TEMPERATURE_ZERO"
    INV_LOCAL_REQUEST_SEED_PRESENT = "INV_LOCAL_REQUEST_SEED_PRESENT"
    INV_TELEMETRY_HAS_FINGERPRINT_HASH = "INV_TELEMETRY_HAS_FINGERPRINT_HASH"
    INV_REPLAY_HASH_PRESENT_WHEN_ENABLED = "INV_REPLAY_HASH_PRESENT_WHEN_ENABLED"
    INV_GEMINI_FALLBACK_REQUIRES_REASON = "INV_GEMINI_FALLBACK_REQUIRES_REASON"


class InvariantSeverity(str, Enum):
    """Severity levels for invariant violations."""

    INFO = "INFO"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass(frozen=True)
class InvariantViolation:
    """Immutable invariant violation artifact with deterministic serialization.

    All fields are deterministic (no timestamps, no nondeterministic runtime state).
    Context dict is canonicalized with sorted keys for stable hashing.
    """

    invariant_id: str
    severity: str
    message: str
    context: dict[str, Any]

    def canonical_json(self) -> str:
        """Returns canonical JSON representation with sorted keys."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "InvariantViolation.canonical_json"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:InvariantViolation.canonical_json".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {
            "invariant_id": self.invariant_id,
            "severity": self.severity,
            "message": self.message,
            "context": self.context,
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    def violation_hash(self) -> str:
        """Returns SHA256 hash of canonical JSON representation."""
        import hashlib

        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()

    def as_dict(self) -> dict[str, Any]:
        """Returns dict representation with stable key ordering."""
        return {
            "invariant_id": self.invariant_id,
            "severity": self.severity,
            "message": self.message,
            "context": self.context,
            "violation_hash": self.violation_hash(),
        }

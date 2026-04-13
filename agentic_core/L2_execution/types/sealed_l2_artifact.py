"""SealedL2Artifact — typed contract for the L2 sealed output (E5 Seal the Final Folder).

Maps to process map [4] E5 and [5] 'THE SEALED FOLDER (From L2)'.
Doc: docs/reference/05_Live_Runtime_Exit_Control.md — THE SEALED FOLDER
Doc: docs/reference/agentic_process_mapping_v29.md — [4] E5

Layer authority: L2 (Execution Staff — sealer)
Write authority: NONE — sealed artifact is read-only after creation.
No business logic. No persistence. No behavioral code.

Architectural invariant:
    run_scope = 'CURRENT_RUN' is a ClassVar sentinel that makes SealedL2Artifact
    incompatible with PromotionPacket (run_scope='FUTURE_RUN') at the type level.
    Never cast one to the other.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_execution_output,
    _emit_records_execution_trace,
    emit_determinism_digest,
    emit_replay_key,
)

emit_replay_key("p0", "sealed_l2_artifact")
emit_determinism_digest("p0", "sealed_l2_artifact")
_emit_records_execution_trace("p0", "sealed_l2_artifact", "L2")
_emit_captures_execution_output("p0", "sealed_l2_artifact", "seal_phase")


class TerminalClassification(str, Enum):
    """Terminal folder classification from the E5 Seal phase.

    Maps to: process map [4] E5 — Terminal folders:
        SUCCESS | FAILURE | NEEDS HELP | REJECTED
    """

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    NEEDS_HELP = "NEEDS_HELP"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ValidationCounters:
    """Counters from L2 self-validation checks prior to sealing.

    Tracks policy, schema, mutation-authorization, and environment-integrity
    check pass/fail counts.  All fields default to 0 (no checks run).
    """

    policy_checks_passed: int = 0
    policy_checks_failed: int = 0
    schema_checks_passed: int = 0
    schema_checks_failed: int = 0
    mutation_auth_checks_passed: int = 0
    mutation_auth_checks_failed: int = 0
    env_integrity_checks_passed: int = 0
    env_integrity_checks_failed: int = 0


@dataclass(frozen=True)
class ReplayMetadata:
    """Replay completeness and determinism metadata sealed with L2 output.

    Required by X1D: grounded_replayable check.

    replay_completeness — 0.0 (no replay data) to 1.0 (fully replayable).
    seed_captured      — True if the random seed was captured at execution start.
    isolation_verified — True if the execution environment was verified isolated.
    """

    replay_key: str = ""
    determinism_digest: str = ""
    replay_completeness: float = 0.0
    seed_captured: bool = False
    isolation_verified: bool = False


@dataclass(frozen=True)
class SealedL2Artifact:
    """Typed sealed L2 output — formal handoff from L2 to [5] Exit Control Gate.

    Maps to: process map [4] E5 'SEAL THE FINAL FOLDER'
    Consumed by: ExitControlGate (L5) via evaluate_sealed()

    Fields
    ------
    artifact_id:
        Unique identifier for this sealed artifact (UUID, set by the sealer).
    trace_id:
        Links to the ExecutionTrace record for this run.
    exec_trace:
        Serialized ExecutionTrace fields (trace_id, plan_hash, policy_hash,
        determinism_digest, hierarchy_hash, metadata).
    state_diff:
        Proposed state mutations (before/after diff).  Empty dict when the
        run produced no mutation proposal.
    evidence_bundle:
        Grounding evidence: citations, retrieval support, provenance.
    validation_counters:
        L2 self-check pass/fail counts.
    terminal_classification:
        E5 terminal folder classification.
    replay_metadata:
        Determinism proof and replay completeness envelope.
    has_commit_payload:
        True when state_diff contains a non-empty mutation proposal.
    escalation_reason:
        Non-None when L2 detected policy ambiguity and requests HITL.
    sealed_at:
        Monotonic epoch tick at sealing time (not wall clock).

    Architectural invariant
    -----------------------
    run_scope = 'CURRENT_RUN' is a ClassVar sentinel.  This type must NEVER be
    stored directly in L4 or used as a PromotionPacket substitute.
    """

    run_scope: ClassVar[str] = "CURRENT_RUN"

    artifact_id: str
    trace_id: str

    exec_trace: dict[str, Any] = field(default_factory=dict)
    state_diff: dict[str, Any] = field(default_factory=dict)
    evidence_bundle: dict[str, Any] = field(default_factory=dict)
    validation_counters: ValidationCounters = field(default_factory=ValidationCounters)
    terminal_classification: TerminalClassification = TerminalClassification.SUCCESS
    replay_metadata: ReplayMetadata = field(default_factory=ReplayMetadata)
    has_commit_payload: bool = False
    escalation_reason: str | None = None
    sealed_at: float = 0.0


__all__ = [
    "TerminalClassification",
    "ValidationCounters",
    "ReplayMetadata",
    "SealedL2Artifact",
]

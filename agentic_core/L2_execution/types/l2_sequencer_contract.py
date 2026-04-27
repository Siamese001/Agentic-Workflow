"""L2 Execution Sequencer Contract (spec 04.0).

Canonical typed contracts for the L2 internal sequencer state machine that
wires E1 Prep -> E2 Valid -> E3 Exec -> E4 Heal loop -> E5 Seal.

Source spec: docs/reference/04_L2_Execute/04.0_L2_Sequencer_Orchestrator_Contract.md

This module is the authoritative dataclass surface. Runtime wiring lives in
agentic_core/L2_execution/orchestration/l2_phase_pipeline.py (existing E-stage
pipeline) and will be connected to this contract in a follow-up wave.

Invariants enforced here (via __post_init__):
    - attempt_count / repair_count non-negative integers.
    - terminal seal states form a closed set.
    - no_direct_write_assertion must be True on any emitted SequencerReceipt.
    - Illegal transitions are rejected by L2ExecutionSequencerState.transition().
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class L2SequencerState(str, Enum):
    """Allowed L2 sequencer states (spec 04.0 STATE MACHINE)."""

    RECEIVED_PACKET = "RECEIVED_PACKET"
    PREPARED = "PREPARED"
    VALIDATED = "VALIDATED"
    EXECUTING = "EXECUTING"
    LOCAL_REPAIR_EVALUATION = "LOCAL_REPAIR_EVALUATION"
    RETRYING_SAME_AUTHORITY = "RETRYING_SAME_AUTHORITY"
    SEALING_SUCCESS = "SEALING_SUCCESS"
    SEALING_DEGRADED_SUCCESS = "SEALING_DEGRADED_SUCCESS"
    SEALING_NEEDS_HELP = "SEALING_NEEDS_HELP"
    SEALING_REJECTED = "SEALING_REJECTED"
    SEALED = "SEALED"


class L2TerminalClass(str, Enum):
    """Terminal result classes aggregated before E5 Seal."""

    SUCCESS = "SUCCESS"
    DEGRADED_SUCCESS = "DEGRADED_SUCCESS"
    NEEDS_HELP = "NEEDS_HELP"
    REJECTED = "REJECTED"
    TIMEOUT = "TIMEOUT"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"


# Mapping of allowed (from -> set of to) transitions. Any pair not listed is
# illegal. Caller must use .transition() helper to step through.
_ALLOWED_TRANSITIONS: dict[L2SequencerState, frozenset[L2SequencerState]] = {
    L2SequencerState.RECEIVED_PACKET: frozenset({L2SequencerState.PREPARED}),
    L2SequencerState.PREPARED: frozenset(
        {L2SequencerState.VALIDATED, L2SequencerState.SEALING_REJECTED}
    ),
    L2SequencerState.VALIDATED: frozenset({L2SequencerState.EXECUTING}),
    L2SequencerState.EXECUTING: frozenset(
        {
            L2SequencerState.SEALING_SUCCESS,
            L2SequencerState.SEALING_DEGRADED_SUCCESS,
            L2SequencerState.LOCAL_REPAIR_EVALUATION,
        }
    ),
    L2SequencerState.LOCAL_REPAIR_EVALUATION: frozenset(
        {
            L2SequencerState.RETRYING_SAME_AUTHORITY,
            L2SequencerState.SEALING_NEEDS_HELP,
            L2SequencerState.SEALING_REJECTED,
        }
    ),
    L2SequencerState.RETRYING_SAME_AUTHORITY: frozenset(
        {L2SequencerState.VALIDATED, L2SequencerState.EXECUTING}
    ),
    L2SequencerState.SEALING_SUCCESS: frozenset({L2SequencerState.SEALED}),
    L2SequencerState.SEALING_DEGRADED_SUCCESS: frozenset({L2SequencerState.SEALED}),
    L2SequencerState.SEALING_NEEDS_HELP: frozenset({L2SequencerState.SEALED}),
    L2SequencerState.SEALING_REJECTED: frozenset({L2SequencerState.SEALED}),
    L2SequencerState.SEALED: frozenset(),
}


TERMINAL_SEAL_STATES: frozenset[L2SequencerState] = frozenset(
    {
        L2SequencerState.SEALING_SUCCESS,
        L2SequencerState.SEALING_DEGRADED_SUCCESS,
        L2SequencerState.SEALING_NEEDS_HELP,
        L2SequencerState.SEALING_REJECTED,
    }
)


class IllegalL2TransitionError(ValueError):
    """Raised when a sequencer transition is not in the allowed set."""


def is_legal_transition(src: L2SequencerState, dst: L2SequencerState) -> bool:
    """Return True iff src -> dst is allowed by spec 04.0 STATE MACHINE."""
    return dst in _ALLOWED_TRANSITIONS.get(src, frozenset())


@dataclass(frozen=True)
class L2ExecutionSequencerInput:
    """Parent input to the L2 sequencer (spec 04.0 CONTRACTS)."""

    l2_execution_request: str
    capability_token_ref: str
    sandbox_envelope_ref: str
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    snapshot_manifest_ref: str
    max_attempts: int
    max_repair_count: int
    overall_timeout_ms: int
    budget_snapshot: str
    trace_root: str
    route_contract_ref: str
    signed_l0_packet: Optional[str] = None
    l3_step_contract: Optional[str] = None
    prompt_envelope_ref: Optional[str] = None
    final_evidence_contract_ref: Optional[str] = None
    workflow_step_ref: Optional[str] = None

    def __post_init__(self) -> None:
        # Exactly one of signed_l0_packet or l3_step_contract must be present.
        if bool(self.signed_l0_packet) == bool(self.l3_step_contract):
            raise ValueError(
                "L2ExecutionSequencerInput requires exactly one of "
                "signed_l0_packet xor l3_step_contract"
            )
        if self.max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        if self.max_repair_count < 0:
            raise ValueError("max_repair_count must be non-negative")
        if self.overall_timeout_ms <= 0:
            raise ValueError("overall_timeout_ms must be positive")
        for required in (
            "capability_token_ref",
            "sandbox_envelope_ref",
            "policy_hash",
            "blueprint_hash",
            "replay_key",
        ):
            if not getattr(self, required):
                raise ValueError(f"L2ExecutionSequencerInput.{required} required")


@dataclass
class L2ExecutionState:
    """Mutable sequencer state carried across E1-E5 (spec 04.0 CONTRACTS)."""

    current_state: L2SequencerState = L2SequencerState.RECEIVED_PACKET
    attempt_count: int = 0
    repair_count: int = 0
    last_stage: str = ""
    last_stage_receipt_id: str = ""
    terminal_candidate: Optional[L2TerminalClass] = None
    retry_allowed: bool = True
    repair_allowed: bool = True
    budget_remaining: int = 0
    timeout_remaining_ms: int = 0
    same_authority_snapshot_hash: str = ""
    proposed_state_diff_candidate_ref: Optional[str] = None
    evidence_refs: list[str] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    stage_receipt_index: dict[str, str] = field(default_factory=dict)

    def transition(self, dst: L2SequencerState) -> None:
        """Step the state machine. Raises IllegalL2TransitionError on invalid."""
        if not is_legal_transition(self.current_state, dst):
            raise IllegalL2TransitionError(
                f"illegal L2 transition: {self.current_state.value} -> {dst.value}"
            )
        self.current_state = dst


@dataclass(frozen=True)
class SequencerReceipt:
    """Terminal deterministic receipt emitted by the L2 sequencer."""

    sequencer_receipt_id: str
    request_id: str
    run_id: str
    trace_root: str
    route_id: str
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    e1_receipt_ref: str
    e5_seal_receipt_ref: str
    terminal_class: L2TerminalClass
    attempt_count: int
    repair_count: int
    budget_final: int
    same_authority_status: str
    no_direct_write_assertion: bool
    deterministic_digest: str
    e2_receipt_refs: tuple[str, ...] = ()
    e3_attempt_receipt_refs: tuple[str, ...] = ()
    e4_heal_receipt_refs: tuple[str, ...] = ()
    terminal_reason_codes: tuple[str, ...] = ()
    step_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.no_direct_write_assertion:
            raise ValueError(
                "SequencerReceipt invariant: no_direct_write_assertion must be True"
            )
        if self.attempt_count < 0 or self.repair_count < 0:
            raise ValueError("attempt_count / repair_count must be non-negative")
        if not self.deterministic_digest:
            raise ValueError("SequencerReceipt requires deterministic_digest")
        for required in ("policy_hash", "blueprint_hash", "replay_key"):
            if not getattr(self, required):
                raise ValueError(f"SequencerReceipt.{required} required")


__all__ = [
    "IllegalL2TransitionError",
    "L2ExecutionSequencerInput",
    "L2ExecutionState",
    "L2SequencerState",
    "L2TerminalClass",
    "SequencerReceipt",
    "TERMINAL_SEAL_STATES",
    "is_legal_transition",
]

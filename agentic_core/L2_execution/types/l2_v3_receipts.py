"""L2 Execute v3 — Named Receipt Schemas (E1.8, E2.8, E3.8, E4.7, E5.8).

Maps to: docs/reference/04_L2_Execute/04_L2_Execute_v3.md

This module is **additive** — it does not edit any prior W1–W6 primitive from
plans `l2-execute-best-practices-gap-b7c4e2` or
`l2-execute-v2-agent-conformance-c8e4f1`. It supplies the named, frozen
receipt dataclasses that v3 doctrine requires at each phase boundary, plus
the LineageRoot and DeterminismBundle types that the receipts compose.

Design invariants
-----------------
1. All receipts are frozen dataclasses (immutable once sealed).
2. Snapshot binding (`policy_hash`, `blueprint_hash`) is required on every
   receipt that carries authority. Mismatch raises `SnapshotMismatchError`.
3. No receipt has commit authority — they are read-only handoff artifacts.
4. Lineage propagates parent_route_id / parent_plan_id / parent_step_id /
   ancestry_chain end-to-end so [5] Exit Eval and L6 audit can reconstruct
   the full path from L0 → L3 → L2 → seal.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Result classes (E3.7 / E5.5) — already exist in HealOutcome /
# TerminalClassification; this enum is the v3-spec literal mirror so call
# sites that don't yet import HealOutcome can still emit valid receipts.
# ---------------------------------------------------------------------------


class ResultClass(str, Enum):
    """E3.7 result classification — v3 spec + v4 DEGRADED_SUCCESS extension."""

    SUCCESS = "SUCCESS"
    SOFT_REPAIRABLE = "SOFT_REPAIRABLE"
    FAIL_TERMINAL = "FAIL_TERMINAL"
    NEEDS_HELP = "NEEDS_HELP"
    REJECTED = "REJECTED"
    DEGRADED_SUCCESS = "DEGRADED_SUCCESS"  # v4: usable partial result with caveats


class TerminalStamp(str, Enum):
    """E5.5 terminal stamp — v3 spec literal + v4 DEGRADED_SUCCESS."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    NEEDS_HELP = "NEEDS_HELP"
    REJECTED = "REJECTED"
    DEGRADED_SUCCESS = "DEGRADED_SUCCESS"  # v4


class RepairStatus(str, Enum):
    """E4 OUTPUT CONTRACT repair_status — v4 §E4."""

    REPAIRED = "REPAIRED"
    NOT_REPAIRED = "NOT_REPAIRED"
    QUARANTINED = "QUARANTINED"
    NEEDS_HELP = "NEEDS_HELP"
    FAIL_TERMINAL = "FAIL_TERMINAL"


class DispatchTarget(str, Enum):
    """E5 OUTPUT CONTRACT dispatch_target — v4 §E5."""

    EXIT_CONTROL = "EXIT_CONTROL"
    L3_MERGE = "L3_MERGE"
    HITL_PACKETIZATION = "HITL_PACKETIZATION"
    UWG_REQUEST_CANDIDATE = "UWG_REQUEST_CANDIDATE"


class ExecutionLane(str, Enum):
    """E3 EXECUTION LANES — v4 §E3."""

    READ = "READ"
    MODEL = "MODEL"
    TOOL = "TOOL"
    ACTION = "ACTION"
    ARTIFACT = "ARTIFACT"


# ---------------------------------------------------------------------------
# E1.6 — Lineage root
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LineageRoot:
    """E1.6 lineage root — parent IDs + ancestry chain.

    The ancestry chain is an ordered tuple of opaque parent identifiers,
    most distant first, current parent last. It is sealed at E1 and carried
    unchanged through every subsequent receipt.
    """

    parent_route_id: str
    parent_plan_id: str | None
    parent_step_id: str | None
    ancestry_chain: tuple[str, ...] = ()
    same_run_packet_family: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "parent_route_id": self.parent_route_id,
            "parent_plan_id": self.parent_plan_id,
            "parent_step_id": self.parent_step_id,
            "ancestry_chain": list(self.ancestry_chain),
            "same_run_packet_family": self.same_run_packet_family,
        }


# ---------------------------------------------------------------------------
# E1.4 — Determinism bundle (full v3 set including attempt_seed)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DeterminismBundle:
    """E1.4 determinism bind — every hash + key required for replay.

    `attempt_seed` is unique to v3 and was missing from the repo (0 hits at
    plan time). It seeds any non-deterministic execution so attempts are
    individually reproducible even when the underlying tool is stochastic.
    """

    blueprint_hash: str
    policy_hash: str
    prompt_hash: str
    input_hash: str
    replay_key: str
    attempt_seed: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "blueprint_hash": self.blueprint_hash,
            "policy_hash": self.policy_hash,
            "prompt_hash": self.prompt_hash,
            "input_hash": self.input_hash,
            "replay_key": self.replay_key,
            "attempt_seed": self.attempt_seed,
        }


class SnapshotMismatchError(Exception):
    """Raised when a downstream receipt's snapshot does not match E1's bind.

    This is the v3 invariant: VALIDATE and HEAL must operate against the
    same blueprint_hash / policy_hash snapshot as PREP.
    """


def assert_snapshot_match(
    expected: DeterminismBundle, actual: DeterminismBundle
) -> None:
    """Assert that two DeterminismBundle instances agree on snapshot fields.

    blueprint_hash + policy_hash must be identical. Other fields (prompt_hash,
    input_hash, replay_key, attempt_seed) may legitimately drift across heal
    attempts, so they are NOT checked here.
    """
    if expected.blueprint_hash != actual.blueprint_hash:
        raise SnapshotMismatchError(
            f"blueprint_hash mismatch: expected={expected.blueprint_hash!r} "
            f"actual={actual.blueprint_hash!r}"
        )
    if expected.policy_hash != actual.policy_hash:
        raise SnapshotMismatchError(
            f"policy_hash mismatch: expected={expected.policy_hash!r} "
            f"actual={actual.policy_hash!r}"
        )


# ---------------------------------------------------------------------------
# E1.8 — Prep receipt
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PrepReceipt:
    """E1.8 prep receipt — sealed at end of E1 with frozen inputs / caps /
    budget / lineage for replay.
    """

    prep_receipt_id: str
    run_id: str
    idempotency_key: str
    route_id: str
    step_id: str | None
    capability_token: str
    compliance_hash: str
    sandbox_envelope_id: str
    determinism: DeterminismBundle
    lineage: LineageRoot
    frozen_caps: tuple[str, ...] = ()
    frozen_budget: dict[str, Any] = field(default_factory=dict)
    frozen_at: float = field(default_factory=time.monotonic)

    @staticmethod
    def new_id() -> str:
        return f"prep-{uuid.uuid4().hex}"


# ---------------------------------------------------------------------------
# E2.8 — Validation receipt
# ---------------------------------------------------------------------------


class ValidationOutcome(str, Enum):
    """E2.8 validation outcome — PASS stamps Approved-to-Start; FAIL seals
    the rejection BEFORE execution (no E3 work performed).
    """

    PASS = "PASS"
    FAIL = "FAIL"


@dataclass(frozen=True)
class ValidationReceipt:
    """E2.8 validation receipt.

    On PASS, downstream E3 receives `validation_packet_id` to bind every
    attempt back to this validation. On FAIL, `rejection_reason` is set,
    `failed_rule` names the gate, and no E3 attempt is permitted — the
    receipt itself IS the sealed rejection.
    """

    validation_packet_id: str
    prep_receipt_id: str
    outcome: ValidationOutcome
    determinism: DeterminismBundle
    lineage: LineageRoot
    rules_passed: tuple[str, ...] = ()
    failed_rule: str | None = None
    rejection_reason: str | None = None
    classified_side_effect: str | None = None
    validated_at: float = field(default_factory=time.monotonic)

    @staticmethod
    def new_id() -> str:
        return f"valid-{uuid.uuid4().hex}"

    def is_approved(self) -> bool:
        return self.outcome is ValidationOutcome.PASS


# ---------------------------------------------------------------------------
# E3.8 — Attempt receipt (one per E3 invocation; multiple per packet family)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AttemptReceipt:
    """E3.8 attempt receipt — sealed per individual E3 attempt.

    `attempt_count` is monotonic within a packet family. `validation_packet_id`
    links each attempt back to E2's approval. `result_class` follows v3 §E3.7
    extended with v4's DEGRADED_SUCCESS.

    v4 additions (all defaulted to preserve backward-compat with v3 callers):
      - execution_lane: which v4 lane (READ/MODEL/TOOL/ACTION/ARTIFACT)
      - decisive_reason_code: short reason key from E3 OUTPUT CONTRACT
      - local_check_results: tuple of (check_name, passed) pairs
      - generated_artifacts: artifact references produced by this attempt
      - proposed_state_diff: inert mutation proposal (E1.7 / E5.7 invariant)
      - quarantined_payload: unsafe output stored separately from output_digest
    """

    attempt_receipt_id: str
    validation_packet_id: str
    attempt_count: int
    determinism: DeterminismBundle
    lineage: LineageRoot
    trace_id: str
    span_id: str | None
    latency_ms: float
    tokens_used: int
    return_code: int | None
    result_class: ResultClass
    output_digest: str = ""
    error_summary: str | None = None
    sealed_at: float = field(default_factory=time.monotonic)
    # ---- v4 additions ----
    execution_lane: ExecutionLane | None = None
    decisive_reason_code: str = ""
    local_check_results: tuple[tuple[str, bool], ...] = ()
    generated_artifacts: tuple[str, ...] = ()
    proposed_state_diff: dict[str, Any] = field(default_factory=dict)
    quarantined_payload: str | None = None

    @staticmethod
    def new_id() -> str:
        return f"attempt-{uuid.uuid4().hex}"


# ---------------------------------------------------------------------------
# E4.7 — Heal receipt
# ---------------------------------------------------------------------------


class HealOutcomeStamp(str, Enum):
    """E4.8 heal outcome — PASS routes back to E3; FAIL routes to NEEDS_HELP /
    ESCALATE_ARTIFACT / FAIL_TERMINAL.
    """

    PASS = "PASS"
    NEEDS_HELP = "NEEDS_HELP"
    ESCALATE_ARTIFACT = "ESCALATE_ARTIFACT"
    FAIL_TERMINAL = "FAIL_TERMINAL"


@dataclass(frozen=True)
class HealReceipt:
    """E4.7 heal receipt — sealed `repair_attempt_id` with delta + counters
    + outcome.

    Snapshot guard: `determinism.blueprint_hash` and `determinism.policy_hash`
    MUST match the prep receipt. The phase pipeline asserts this before
    sealing.

    v4 additions (defaulted):
      - repair_status: full v4 RepairStatus enum (incl. QUARANTINED)
      - repair_tactic: short identifier of the chosen safe repair
      - before_hash / after_hash: payload digests pre/post repair
      - oscillation_status: result of E4.5 thrash detection
      - snapshot_guard_status: result of E4.4 same-snapshot check
      - next_action: RETURN_TO_E3 or SEND_TO_E5 (v4 §E4 OUTPUT)
    """

    repair_attempt_id: str
    parent_attempt_receipt_id: str
    failed_span_id: str | None
    reason_code: str
    repair_count: int
    determinism: DeterminismBundle
    lineage: LineageRoot
    delta_summary: str = ""
    outcome: HealOutcomeStamp = HealOutcomeStamp.NEEDS_HELP
    sealed_at: float = field(default_factory=time.monotonic)
    # ---- v4 additions ----
    repair_status: RepairStatus | None = None
    repair_tactic: str = ""
    before_hash: str = ""
    after_hash: str = ""
    oscillation_status: str = ""  # "CLEAN" | "THRASHING" | "CEILING_REACHED"
    snapshot_guard_status: str = "PASS"  # "PASS" | "FAIL"
    next_action: str = ""  # "RETURN_TO_E3" | "SEND_TO_E5"

    @staticmethod
    def new_id() -> str:
        return f"heal-{uuid.uuid4().hex}"

    def routes_back_to_e3(self) -> bool:
        return self.outcome is HealOutcomeStamp.PASS


# ---------------------------------------------------------------------------
# E5.8 — Dispatch receipt
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DispatchReceipt:
    """E5.8 dispatch receipt — emits `sealed_l2_artifact_id` to downstream
    consumers: [5] Exit Eval, UWG decisioning, L6 audit.

    This is L2's terminal hand-off. It carries:
      - the sealed artifact ID
      - the full receipt chain (prep / validation / attempts / heals)
      - the terminal stamp (E5.5)
      - the explicit downstream targets

    Dispatch is NOT a commit. The receipt is read-only and L4/UWG remain
    the sole owners of any durable mutation.
    """

    dispatch_receipt_id: str
    sealed_l2_artifact_id: str
    terminal_stamp: TerminalStamp
    determinism: DeterminismBundle
    lineage: LineageRoot
    prep_receipt_id: str
    validation_packet_id: str | None
    attempt_receipt_ids: tuple[str, ...] = ()
    heal_receipt_ids: tuple[str, ...] = ()
    decisive_reason: str = ""
    targets: tuple[str, ...] = (
        "exit_eval",
        "uwg_decision",
        "l6_audit",
    )
    has_commit_payload: bool = False  # invariant: NEVER True
    dispatched_at: float = field(default_factory=time.monotonic)
    # ---- v4 additions ----
    dispatch_target: DispatchTarget = DispatchTarget.EXIT_CONTROL
    user_visible_safe: bool = True
    commit_requested: bool = False
    downstream_recommendation: str = ""

    @staticmethod
    def new_id() -> str:
        return f"dispatch-{uuid.uuid4().hex}"

    def __post_init__(self) -> None:
        if self.has_commit_payload:
            raise ValueError(
                "L2 dispatch receipt cannot carry a commit payload — "
                "durable writes are reserved for L4/UWG (v3 §E5.7)"
            )


__all__ = [
    "ResultClass",
    "TerminalStamp",
    "RepairStatus",
    "DispatchTarget",
    "ExecutionLane",
    "LineageRoot",
    "DeterminismBundle",
    "SnapshotMismatchError",
    "assert_snapshot_match",
    "PrepReceipt",
    "ValidationOutcome",
    "ValidationReceipt",
    "AttemptReceipt",
    "HealOutcomeStamp",
    "HealReceipt",
    "DispatchReceipt",
]

"""03.7 L3 State Ledger, Context Bus, and Step Contract.

W1 c0-policy-rectification-deferred-f7b2a9: L3StepContract now carries optional
``c0_policy`` for step-level C0 policy inheritance. Steps may declare their own
policy or inherit from parent workflow RouteContract.

Realizes:

- ``L3StateLedger``        — 03.7 PHASE 1 §1
- ``NodeReadinessDecision``— 03.7 PHASE 1 §2
- ``L3ContextBus``         — 03.7 PHASE 1 §3
- ``L3StepContract``       — 03.7 PHASE 1 §4 (with c0_policy field)
- ``StepResultIngest``     — 03.7 PHASE 1 §5
- ``HandoffMergeReceipt``  — 03.7 §PHASE 4 RESULT MERGE output
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from agentic_core.L0_routing.c0_retrieval.route_contract import C0Policy

from . import L3DoctrineContractError
from .contracts_l3_6 import WorkflowNodeType

_MAX_STR = 512
_MAX_LIST = 256
_MAX_REASON = 32


def _need_str(value: object, name: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, str):
        raise L3DoctrineContractError(f"{name} must be str, got {type(value).__name__}")
    if len(value) > _MAX_STR:
        raise L3DoctrineContractError(f"{name} exceeds {_MAX_STR} chars")
    if not allow_empty and not value:
        raise L3DoctrineContractError(f"{name} must be non-empty")


def _need_str_tuple(values: object, name: str, *, max_len: int = _MAX_LIST) -> None:
    if not isinstance(values, tuple):
        raise L3DoctrineContractError(f"{name} must be tuple")
    if len(values) > max_len:
        raise L3DoctrineContractError(f"{name} exceeds {max_len}")
    for idx, item in enumerate(values):
        if not isinstance(item, str) or not item or len(item) > _MAX_STR:
            raise L3DoctrineContractError(f"{name}[{idx}] must be non-empty str <= {_MAX_STR}")


def _need_pos_int(value: object, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise L3DoctrineContractError(f"{name} must be int")
    if value < 0:
        raise L3DoctrineContractError(f"{name} must be >= 0")


def _need_bool(value: object, name: str) -> None:
    if not isinstance(value, bool):
        raise L3DoctrineContractError(f"{name} must be bool")


def resolve_step_c0_policy(
    step_contract: L3StepContract,
    parent_c0_policy: C0Policy | None,
) -> C0Policy | None:
    """W1: Resolve effective C0 policy for a step with inheritance.

    Step-level policy overrides parent workflow policy:
    - If step_contract.c0_policy is set → use step policy (explicit override)
    - If step_contract.c0_policy is None → inherit from parent
    - If neither has policy → return None (caller must handle default)

    Args:
        step_contract: The L3 step contract (may have c0_policy field)
        parent_c0_policy: The parent workflow's C0 policy (from RouteContract)

    Returns:
        Effective C0Policy for the step (may be None)

    Raises:
        L3DoctrineContractError: If step_contract is not L3StepContract type
    """
    if not isinstance(step_contract, L3StepContract):
        raise L3DoctrineContractError(
            f"resolve_step_c0_policy expects L3StepContract, got {type(step_contract).__name__}"
        )
    # Step-level override takes precedence
    if step_contract.c0_policy is not None:
        return step_contract.c0_policy
    # Fall back to parent workflow policy
    return parent_c0_policy


# ---------------------------------------------------------------------------
# Node state enum (03.7 §L3StateLedger.node_states)
# ---------------------------------------------------------------------------


class NodeState(str, Enum):
    NOT_READY = "NOT_READY"
    READY = "READY"
    DISPATCHED = "DISPATCHED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    DEGRADED = "DEGRADED"
    SOFT_REPAIRABLE = "SOFT_REPAIRABLE"
    FAILED_TERMINAL = "FAILED_TERMINAL"
    NEEDS_HELP = "NEEDS_HELP"
    PAUSED_HITL = "PAUSED_HITL"
    SKIPPED = "SKIPPED"
    REJECTED = "REJECTED"
    SEALED = "SEALED"


class StepResultStatus(str, Enum):
    SUCCESS = "SUCCESS"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    NEEDS_HELP = "NEEDS_HELP"
    PAUSED_HITL = "PAUSED_HITL"


# ---------------------------------------------------------------------------
# L3StateLedger
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class L3StateLedger:
    """03.7 PHASE 1 §1 L3StateLedger.

    Frozen for immutability; updates create new instances. ``node_states`` is a
    mapping ``node_id -> NodeState`` represented as a sorted tuple of pairs to
    keep deterministic hashing.
    """

    workflow_id: str
    route_contract_id: str
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    graph_hash: str
    node_states: tuple[tuple[str, NodeState], ...]
    edge_states: tuple[tuple[str, str], ...]
    branch_states: tuple[tuple[str, str], ...]
    join_states: tuple[tuple[str, str], ...]
    attempt_counts: tuple[tuple[str, int], ...]
    retry_counts: tuple[tuple[str, int], ...]
    fallback_depth: int
    remaining_budget: float
    remaining_slo: int
    checkpoints: tuple[str, ...]
    paused_packets: tuple[str, ...]
    reason_codes: tuple[str, ...]
    ledger_hash: str

    def __post_init__(self) -> None:
        for name in (
            "workflow_id",
            "route_contract_id",
            "policy_hash",
            "blueprint_hash",
            "replay_key",
            "graph_hash",
            "ledger_hash",
        ):
            _need_str(getattr(self, name), f"L3StateLedger.{name}")
        _need_pos_int(self.fallback_depth, "L3StateLedger.fallback_depth")
        _need_pos_int(self.remaining_slo, "L3StateLedger.remaining_slo")
        if isinstance(self.remaining_budget, bool) or not isinstance(self.remaining_budget, (int, float)):
            raise L3DoctrineContractError("L3StateLedger.remaining_budget must be float")
        if self.remaining_budget != self.remaining_budget or self.remaining_budget < 0.0:
            raise L3DoctrineContractError("L3StateLedger.remaining_budget must be >= 0 and finite")
        # Validate tuple-of-pair shapes
        for entry in self.node_states:
            if not (isinstance(entry, tuple) and len(entry) == 2):
                raise L3DoctrineContractError(
                    "L3StateLedger.node_states entries must be (node_id, NodeState) pairs",
                )
            node_id, state = entry
            _need_str(node_id, "L3StateLedger.node_states.node_id")
            if not isinstance(state, NodeState):
                raise L3DoctrineContractError(
                    f"L3StateLedger.node_states[{node_id!r}] must be NodeState",
                )
        for attempt_pair in self.attempt_counts:
            if not (isinstance(attempt_pair, tuple) and len(attempt_pair) == 2):
                raise L3DoctrineContractError(
                    "L3StateLedger.attempt_counts entries must be (node_id, int) pairs",
                )
            attempt_node_id, attempt_count = attempt_pair
            _need_str(attempt_node_id, "L3StateLedger.attempt_counts.node_id")
            _need_pos_int(attempt_count, f"L3StateLedger.attempt_counts[{attempt_node_id}]")
        for retry_pair in self.retry_counts:
            if not (isinstance(retry_pair, tuple) and len(retry_pair) == 2):
                raise L3DoctrineContractError(
                    "L3StateLedger.retry_counts entries must be (node_id, int) pairs",
                )
            retry_node_id, retry_count = retry_pair
            _need_str(retry_node_id, "L3StateLedger.retry_counts.node_id")
            _need_pos_int(retry_count, f"L3StateLedger.retry_counts[{retry_node_id}]")
        _need_str_tuple(self.checkpoints, "L3StateLedger.checkpoints")
        _need_str_tuple(self.paused_packets, "L3StateLedger.paused_packets")
        _need_str_tuple(self.reason_codes, "L3StateLedger.reason_codes", max_len=_MAX_REASON)


@dataclass(frozen=True)
class NodeReadinessDecision:
    """03.7 PHASE 1 §2 NodeReadinessDecision."""

    decision_id: str
    workflow_id: str
    node_id: str
    ready: bool
    blocked_reasons: tuple[str, ...]
    satisfied_dependencies: tuple[str, ...]
    unsatisfied_dependencies: tuple[str, ...]
    required_evidence_refs: tuple[str, ...]
    required_policy_refs: tuple[str, ...]
    required_capability_refs: tuple[str, ...]
    budget_status: str
    retry_status: str
    fallback_status: str
    hitl_status: str
    readiness_hash: str

    def __post_init__(self) -> None:
        for name in (
            "decision_id",
            "workflow_id",
            "node_id",
            "budget_status",
            "retry_status",
            "fallback_status",
            "hitl_status",
            "readiness_hash",
        ):
            _need_str(getattr(self, name), f"NodeReadinessDecision.{name}")
        _need_bool(self.ready, "NodeReadinessDecision.ready")
        for name in (
            "blocked_reasons",
            "satisfied_dependencies",
            "unsatisfied_dependencies",
            "required_evidence_refs",
            "required_policy_refs",
            "required_capability_refs",
        ):
            _need_str_tuple(getattr(self, name), f"NodeReadinessDecision.{name}", max_len=_MAX_REASON)
        if self.ready and self.blocked_reasons:
            raise L3DoctrineContractError(
                "NodeReadinessDecision.ready=True is incompatible with non-empty blocked_reasons",
            )


@dataclass(frozen=True)
class L3ContextBus:
    """03.7 PHASE 1 §3 L3ContextBus."""

    workflow_id: str
    bus_hash: str
    carried_query_refs: tuple[str, ...] = field(default_factory=tuple)
    carried_evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    carried_graph_refs: tuple[str, ...] = field(default_factory=tuple)
    carried_prompt_artifact_refs: tuple[str, ...] = field(default_factory=tuple)
    carried_l2_artifact_refs: tuple[str, ...] = field(default_factory=tuple)
    carried_human_review_refs: tuple[str, ...] = field(default_factory=tuple)
    carried_policy_receipt_refs: tuple[str, ...] = field(default_factory=tuple)
    carried_error_refs: tuple[str, ...] = field(default_factory=tuple)
    contradiction_flags: tuple[str, ...] = field(default_factory=tuple)
    unresolved_gaps: tuple[str, ...] = field(default_factory=tuple)
    lineage_manifest: str = ""

    def __post_init__(self) -> None:
        _need_str(self.workflow_id, "L3ContextBus.workflow_id")
        _need_str(self.bus_hash, "L3ContextBus.bus_hash")
        _need_str(self.lineage_manifest, "L3ContextBus.lineage_manifest", allow_empty=True)
        for name in (
            "carried_query_refs",
            "carried_evidence_refs",
            "carried_graph_refs",
            "carried_prompt_artifact_refs",
            "carried_l2_artifact_refs",
            "carried_human_review_refs",
            "carried_policy_receipt_refs",
            "carried_error_refs",
            "contradiction_flags",
            "unresolved_gaps",
        ):
            _need_str_tuple(getattr(self, name), f"L3ContextBus.{name}")


@dataclass(frozen=True)
class StepInputs:
    """03.7 §L3StepContract.inputs nested block."""

    query_refs: tuple[str, ...] = field(default_factory=tuple)
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    graph_refs: tuple[str, ...] = field(default_factory=tuple)
    prompt_artifact_refs: tuple[str, ...] = field(default_factory=tuple)
    prior_artifact_refs: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for name in (
            "query_refs",
            "evidence_refs",
            "graph_refs",
            "prompt_artifact_refs",
            "prior_artifact_refs",
        ):
            _need_str_tuple(getattr(self, name), f"StepInputs.{name}")


@dataclass(frozen=True)
class L3StepContract:
    """03.7 PHASE 1 §4 L3StepContract.

    Single bounded current step. Replayable (graph_hash + replay_key + policy_hash).
    No durable commit authority.

    W1 c0-policy-rectification-deferred-f7b2a9: Added ``c0_policy`` field for step-level
    C0 policy control. Steps may declare their own policy (override) or inherit from
    parent workflow. When ``c0_policy=None``, the step defers to parent workflow policy.
    """

    step_contract_id: str
    workflow_id: str
    node_id: str
    attempt_id: str
    parent_route_id: str
    route_digest: str
    policy_hash: str
    blueprint_hash: str
    snapshot_id: str
    replay_key: str
    idempotency_key: str
    node_type: WorkflowNodeType
    current_work_order: str
    inputs: StepInputs
    expected_output_contract: str
    capability_token_requirement: str
    sandbox_envelope_requirement: str
    timeout_ms: int
    retry_policy: str
    fallback_permission: str
    telemetry_keys: tuple[str, ...]
    expected_receipts: tuple[str, ...]
    step_contract_hash: str
    no_durable_commit_authority: bool = True
    # W1 c0-policy-rectification-deferred-f7b2a9: Step-level C0 policy inheritance
    c0_policy: C0Policy | None = None

    def __post_init__(self) -> None:
        for name in (
            "step_contract_id",
            "workflow_id",
            "node_id",
            "attempt_id",
            "parent_route_id",
            "route_digest",
            "policy_hash",
            "blueprint_hash",
            "snapshot_id",
            "replay_key",
            "idempotency_key",
            "current_work_order",
            "expected_output_contract",
            "capability_token_requirement",
            "sandbox_envelope_requirement",
            "retry_policy",
            "fallback_permission",
            "step_contract_hash",
        ):
            _need_str(getattr(self, name), f"L3StepContract.{name}")
        if not isinstance(self.node_type, WorkflowNodeType):
            raise L3DoctrineContractError("L3StepContract.node_type must be WorkflowNodeType")
        if not isinstance(self.inputs, StepInputs):
            raise L3DoctrineContractError("L3StepContract.inputs must be StepInputs")
        _need_pos_int(self.timeout_ms, "L3StepContract.timeout_ms")
        if self.timeout_ms == 0:
            raise L3DoctrineContractError("L3StepContract.timeout_ms must be > 0")
        _need_str_tuple(self.telemetry_keys, "L3StepContract.telemetry_keys", max_len=_MAX_REASON)
        _need_str_tuple(self.expected_receipts, "L3StepContract.expected_receipts", max_len=_MAX_REASON)
        _need_bool(
            self.no_durable_commit_authority,
            "L3StepContract.no_durable_commit_authority",
        )
        if not self.no_durable_commit_authority:
            raise L3DoctrineContractError(
                "L3StepContract.no_durable_commit_authority must be True (L3 never commits durable state)",
            )
        # W1: c0_policy is optional but must be C0Policy if present
        if self.c0_policy is not None and not isinstance(self.c0_policy, C0Policy):
            raise L3DoctrineContractError("L3StepContract.c0_policy must be C0Policy or None")


@dataclass(frozen=True)
class CostLatencyObservations:
    """Observed cost/latency facts returned with a step result."""

    latency_ms: int = 0
    tokens: int = 0
    cost: float = 0.0
    quality_score: float = 0.0

    def __post_init__(self) -> None:
        for name in ("latency_ms", "tokens"):
            _need_pos_int(getattr(self, name), f"CostLatencyObservations.{name}")
        for name in ("cost", "quality_score"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise L3DoctrineContractError(f"CostLatencyObservations.{name} must be float")
            if value != value:
                raise L3DoctrineContractError(f"CostLatencyObservations.{name} must not be NaN")
            if value < 0.0:
                raise L3DoctrineContractError(f"CostLatencyObservations.{name} must be >= 0")
        if self.quality_score > 1.0:
            raise L3DoctrineContractError(
                "CostLatencyObservations.quality_score must be <= 1.0",
            )


@dataclass(frozen=True)
class StepResultIngest:
    """03.7 PHASE 1 §5 StepResultIngest."""

    step_contract_id: str
    sealed_l2_artifact_ref: str
    status: StepResultStatus
    output_artifact_refs: tuple[str, ...]
    proposed_state_diff_refs: tuple[str, ...]
    returned_evidence_refs: tuple[str, ...]
    returned_graph_refs: tuple[str, ...]
    retry_signal: str
    branch_result: str
    handoff_signal: str
    needs_help_signal: str
    hitl_pause_signal: str
    cost_latency_observations: CostLatencyObservations
    replay_receipt_refs: tuple[str, ...]
    ingest_hash: str
    quality_signal: float = 0.0

    def __post_init__(self) -> None:
        for name in (
            "step_contract_id",
            "sealed_l2_artifact_ref",
            "retry_signal",
            "branch_result",
            "handoff_signal",
            "needs_help_signal",
            "hitl_pause_signal",
            "ingest_hash",
        ):
            _need_str(
                getattr(self, name),
                f"StepResultIngest.{name}",
                allow_empty=name != "step_contract_id" and name != "ingest_hash",
            )
        if not isinstance(self.status, StepResultStatus):
            raise L3DoctrineContractError("StepResultIngest.status must be StepResultStatus")
        for name in (
            "output_artifact_refs",
            "proposed_state_diff_refs",
            "returned_evidence_refs",
            "returned_graph_refs",
            "replay_receipt_refs",
        ):
            _need_str_tuple(getattr(self, name), f"StepResultIngest.{name}")
        if not isinstance(self.cost_latency_observations, CostLatencyObservations):
            raise L3DoctrineContractError(
                "StepResultIngest.cost_latency_observations must be CostLatencyObservations",
            )
        if isinstance(self.quality_signal, bool) or not isinstance(self.quality_signal, (int, float)):
            raise L3DoctrineContractError("StepResultIngest.quality_signal must be float")
        if (
            self.quality_signal != self.quality_signal
            or self.quality_signal < 0.0
            or self.quality_signal > 1.0
        ):
            raise L3DoctrineContractError(
                "StepResultIngest.quality_signal must be in [0,1]",
            )


@dataclass(frozen=True)
class HandoffMergeReceipt:
    """03.7 §PHASE 4 RESULT MERGE — receipt emitted after merging a step result."""

    receipt_id: str
    workflow_id: str
    node_id: str
    new_state: NodeState
    reason_codes: tuple[str, ...]
    preserved_lineage_refs: tuple[str, ...]
    contradiction_flags: tuple[str, ...]
    durable_write_attempted: bool = False

    def __post_init__(self) -> None:
        for name in ("receipt_id", "workflow_id", "node_id"):
            _need_str(getattr(self, name), f"HandoffMergeReceipt.{name}")
        if not isinstance(self.new_state, NodeState):
            raise L3DoctrineContractError("HandoffMergeReceipt.new_state must be NodeState")
        for name in ("reason_codes", "preserved_lineage_refs", "contradiction_flags"):
            _need_str_tuple(getattr(self, name), f"HandoffMergeReceipt.{name}", max_len=_MAX_REASON)
        _need_bool(
            self.durable_write_attempted,
            "HandoffMergeReceipt.durable_write_attempted",
        )
        # 03.7 §PHASE 4 — L3 does not write durable state.
        if self.durable_write_attempted:
            raise L3DoctrineContractError(
                "HandoffMergeReceipt.durable_write_attempted must be False (L3 does not write to L4)",
            )


__all__ = [
    "CostLatencyObservations",
    "HandoffMergeReceipt",
    "L3ContextBus",
    "L3StateLedger",
    "L3StepContract",
    "NodeReadinessDecision",
    "NodeState",
    "StepInputs",
    "StepResultIngest",
    "StepResultStatus",
    "resolve_step_c0_policy",  # W1: C0 policy inheritance helper
]

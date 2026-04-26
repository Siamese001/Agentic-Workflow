"""03.8 L3 Concurrency, Quality, Fallback, Completion, and Sealed Workflow Package.

Realizes:

- ``ConcurrencyPlan``        — 03.8 PHASE 1 §1
- ``QualityLoopPlan``        — 03.8 PHASE 1 §2
- ``FallbackCascadeState``   — 03.8 PHASE 1 §3
- ``WorkflowCompletionTest`` — 03.8 PHASE 1 §4
- ``SealedWorkflowPackage``  — 03.8 PHASE 1 §5
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from . import L3DoctrineContractError

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


def _need_finite_float_in_unit(value: object, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise L3DoctrineContractError(f"{name} must be float in [0,1]")
    if value != value:
        raise L3DoctrineContractError(f"{name} must not be NaN")
    if value < 0.0 or value > 1.0:
        raise L3DoctrineContractError(f"{name} must be in [0,1], got {value}")


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class CompletionStatus(str, Enum):
    """03.8 §WorkflowCompletionTest.completion_status."""

    COMPLETE = "COMPLETE"
    COMPLETE_DEGRADED = "COMPLETE_DEGRADED"
    SAFE_PARTIAL_READY = "SAFE_PARTIAL_READY"
    NEEDS_NEXT_NODE = "NEEDS_NEXT_NODE"
    NEEDS_HITL_PAUSE = "NEEDS_HITL_PAUSE"
    FAILED_TERMINAL = "FAILED_TERMINAL"
    ABSTAIN_RECOMMENDED = "ABSTAIN_RECOMMENDED"


class WorkflowOutcomeClass(str, Enum):
    """Outcome class on the sealed package."""

    CLEAN = "CLEAN"
    DEGRADED = "DEGRADED"
    PARTIAL = "PARTIAL"
    ABSTAIN = "ABSTAIN"
    FAILED = "FAILED"


# ---------------------------------------------------------------------------
# Concurrency
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ConcurrencyPlan:
    """03.8 PHASE 1 §1 ConcurrencyPlan."""

    workflow_id: str
    parallel_groups: tuple[tuple[str, ...], ...]
    serial_only_nodes: tuple[str, ...]
    max_parallelism: int
    branch_policy: str
    join_policy: str
    race_prevention_policy: str
    shard_failure_policy: str
    deterministic_join_order: tuple[str, ...]
    resource_ceiling: int
    concurrency_plan_hash: str
    quorum_policy: str = ""

    def __post_init__(self) -> None:
        for name in (
            "workflow_id",
            "branch_policy",
            "join_policy",
            "race_prevention_policy",
            "shard_failure_policy",
            "concurrency_plan_hash",
        ):
            _need_str(getattr(self, name), f"ConcurrencyPlan.{name}")
        _need_str(self.quorum_policy, "ConcurrencyPlan.quorum_policy", allow_empty=True)
        _need_pos_int(self.max_parallelism, "ConcurrencyPlan.max_parallelism")
        _need_pos_int(self.resource_ceiling, "ConcurrencyPlan.resource_ceiling")
        _need_str_tuple(self.serial_only_nodes, "ConcurrencyPlan.serial_only_nodes")
        _need_str_tuple(
            self.deterministic_join_order,
            "ConcurrencyPlan.deterministic_join_order",
        )
        if not isinstance(self.parallel_groups, tuple):
            raise L3DoctrineContractError("ConcurrencyPlan.parallel_groups must be tuple")
        for idx, group in enumerate(self.parallel_groups):
            if not isinstance(group, tuple):
                raise L3DoctrineContractError(
                    f"ConcurrencyPlan.parallel_groups[{idx}] must be tuple",
                )
            _need_str_tuple(group, f"ConcurrencyPlan.parallel_groups[{idx}]")


# ---------------------------------------------------------------------------
# Quality loop
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class QualityLoopPlan:
    """03.8 PHASE 1 §2 QualityLoopPlan."""

    workflow_id: str
    loop_id: str
    evaluator_node_refs: tuple[str, ...]
    optimizer_node_refs: tuple[str, ...]
    quality_threshold: float
    max_iterations: int
    diminishing_returns_policy: str
    oscillation_detection_policy: str
    best_artifact_retention_policy: str
    budget_stop_policy: str
    quality_loop_hash: str

    def __post_init__(self) -> None:
        for name in (
            "workflow_id",
            "loop_id",
            "diminishing_returns_policy",
            "oscillation_detection_policy",
            "best_artifact_retention_policy",
            "budget_stop_policy",
            "quality_loop_hash",
        ):
            _need_str(getattr(self, name), f"QualityLoopPlan.{name}")
        for name in ("evaluator_node_refs", "optimizer_node_refs"):
            _need_str_tuple(getattr(self, name), f"QualityLoopPlan.{name}")
        _need_finite_float_in_unit(self.quality_threshold, "QualityLoopPlan.quality_threshold")
        _need_pos_int(self.max_iterations, "QualityLoopPlan.max_iterations")
        # 03.8 §RULES — Max iterations required.
        if self.max_iterations == 0:
            raise L3DoctrineContractError(
                "QualityLoopPlan.max_iterations must be > 0 (no open-ended autonomy)",
            )


# ---------------------------------------------------------------------------
# Fallback cascade
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FallbackCascadeState:
    """03.8 PHASE 1 §3 FallbackCascadeState."""

    workflow_id: str
    fallback_chain: tuple[str, ...]
    fallback_depth: int
    attempted_fallbacks: tuple[str, ...]
    current_fallback_candidate: str
    fallback_reason_codes: tuple[str, ...]
    provider_tool_alternatives: tuple[str, ...]
    tier_cascade_state: str
    circuit_breaker_status: str
    fallback_hash: str
    no_silent_fallback_assertion: bool = True

    def __post_init__(self) -> None:
        for name in (
            "workflow_id",
            "tier_cascade_state",
            "circuit_breaker_status",
            "fallback_hash",
        ):
            _need_str(getattr(self, name), f"FallbackCascadeState.{name}")
        _need_str(
            self.current_fallback_candidate,
            "FallbackCascadeState.current_fallback_candidate",
            allow_empty=True,
        )
        _need_pos_int(self.fallback_depth, "FallbackCascadeState.fallback_depth")
        _need_str_tuple(self.fallback_chain, "FallbackCascadeState.fallback_chain")
        _need_str_tuple(self.attempted_fallbacks, "FallbackCascadeState.attempted_fallbacks")
        _need_str_tuple(
            self.fallback_reason_codes,
            "FallbackCascadeState.fallback_reason_codes",
            max_len=_MAX_REASON,
        )
        _need_str_tuple(
            self.provider_tool_alternatives,
            "FallbackCascadeState.provider_tool_alternatives",
        )
        _need_bool(
            self.no_silent_fallback_assertion,
            "FallbackCascadeState.no_silent_fallback_assertion",
        )
        # 03.8 §RULES — no silent fallback. Reason code required when any fallback attempted.
        if not self.no_silent_fallback_assertion:
            raise L3DoctrineContractError(
                "FallbackCascadeState.no_silent_fallback_assertion must be True (no silent fallback)",
            )
        if self.attempted_fallbacks and not self.fallback_reason_codes:
            raise L3DoctrineContractError(
                "FallbackCascadeState requires reason_codes whenever attempted_fallbacks is non-empty",
            )


# ---------------------------------------------------------------------------
# Completion test
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WorkflowCompletionTest:
    """03.8 PHASE 1 §4 WorkflowCompletionTest."""

    workflow_id: str
    all_required_nodes_sealed: bool
    mandatory_branches_resolved: bool
    joins_complete: bool
    required_support_satisfied: bool
    contradictions_labeled: bool
    unresolved_gaps_carried_forward: bool
    route_success_conditions_satisfied: bool
    mutation_proposal_only: bool
    hitl_pause_resolved_or_carried: bool
    budget_status: str
    best_partial_available: bool
    completion_status: CompletionStatus
    completion_hash: str

    def __post_init__(self) -> None:
        for name in ("workflow_id", "budget_status", "completion_hash"):
            _need_str(getattr(self, name), f"WorkflowCompletionTest.{name}")
        for name in (
            "all_required_nodes_sealed",
            "mandatory_branches_resolved",
            "joins_complete",
            "required_support_satisfied",
            "contradictions_labeled",
            "unresolved_gaps_carried_forward",
            "route_success_conditions_satisfied",
            "mutation_proposal_only",
            "hitl_pause_resolved_or_carried",
            "best_partial_available",
        ):
            _need_bool(getattr(self, name), f"WorkflowCompletionTest.{name}")
        if not isinstance(self.completion_status, CompletionStatus):
            raise L3DoctrineContractError(
                "WorkflowCompletionTest.completion_status must be CompletionStatus",
            )
        # 03.8 §HARD LAWS — mutations remain proposal-only.
        if not self.mutation_proposal_only:
            raise L3DoctrineContractError(
                "WorkflowCompletionTest.mutation_proposal_only must be True (L3 cannot commit to L4)",
            )
        # COMPLETE requires required_support_satisfied & mandatory_branches_resolved & joins_complete.
        if self.completion_status == CompletionStatus.COMPLETE:
            for inv in (
                "all_required_nodes_sealed",
                "mandatory_branches_resolved",
                "joins_complete",
                "required_support_satisfied",
                "route_success_conditions_satisfied",
            ):
                if not getattr(self, inv):
                    raise L3DoctrineContractError(
                        f"completion_status=COMPLETE requires {inv}=True",
                    )


# ---------------------------------------------------------------------------
# Sealed workflow package
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CostLatencyTokenSummary:
    total_latency_ms: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0

    def __post_init__(self) -> None:
        _need_pos_int(self.total_latency_ms, "CostLatencyTokenSummary.total_latency_ms")
        _need_pos_int(self.total_tokens, "CostLatencyTokenSummary.total_tokens")
        if isinstance(self.total_cost, bool) or not isinstance(self.total_cost, (int, float)):
            raise L3DoctrineContractError("CostLatencyTokenSummary.total_cost must be float")
        if self.total_cost != self.total_cost or self.total_cost < 0.0:
            raise L3DoctrineContractError(
                "CostLatencyTokenSummary.total_cost must be >= 0 and finite",
            )


@dataclass(frozen=True)
class SealedWorkflowPackage:
    """03.8 PHASE 1 §5 SealedWorkflowPackage.

    Emitted to Exit Eval & Control. NOT to L4.
    """

    sealed_workflow_package_id: str
    workflow_id: str
    route_contract_id: str
    request_id: str
    run_id: str
    trace_root: str
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    graph_hash: str
    ledger_hash: str
    completed_node_refs: tuple[str, ...]
    sealed_l2_artifact_refs: tuple[str, ...]
    prompt_artifact_refs: tuple[str, ...]
    evidence_contract_refs: tuple[str, ...]
    branch_join_manifest: str
    fallback_manifest: str
    quality_loop_manifest: str
    contradiction_flags: tuple[str, ...]
    unresolved_gaps: tuple[str, ...]
    best_partial_artifact_refs: tuple[str, ...]
    proposed_state_diff_refs: tuple[str, ...]
    hitl_packet_refs: tuple[str, ...]
    cost_latency_token_summary: CostLatencyTokenSummary
    workflow_outcome_class: WorkflowOutcomeClass
    route_success_condition_status: str
    package_hash: str
    hmac_sig: str = ""
    mutation_proposal_only_assertion: bool = True
    exit_review_required: bool = True
    no_durable_commit_assertion: bool = True

    def __post_init__(self) -> None:
        for name in (
            "sealed_workflow_package_id",
            "workflow_id",
            "route_contract_id",
            "request_id",
            "run_id",
            "trace_root",
            "policy_hash",
            "blueprint_hash",
            "replay_key",
            "graph_hash",
            "ledger_hash",
            "branch_join_manifest",
            "fallback_manifest",
            "quality_loop_manifest",
            "route_success_condition_status",
            "package_hash",
        ):
            _need_str(getattr(self, name), f"SealedWorkflowPackage.{name}")
        _need_str(self.hmac_sig, "SealedWorkflowPackage.hmac_sig", allow_empty=True)
        for name in (
            "completed_node_refs",
            "sealed_l2_artifact_refs",
            "prompt_artifact_refs",
            "evidence_contract_refs",
            "contradiction_flags",
            "unresolved_gaps",
            "best_partial_artifact_refs",
            "proposed_state_diff_refs",
            "hitl_packet_refs",
        ):
            _need_str_tuple(getattr(self, name), f"SealedWorkflowPackage.{name}")
        if not isinstance(self.cost_latency_token_summary, CostLatencyTokenSummary):
            raise L3DoctrineContractError(
                "SealedWorkflowPackage.cost_latency_token_summary must be CostLatencyTokenSummary",
            )
        if not isinstance(self.workflow_outcome_class, WorkflowOutcomeClass):
            raise L3DoctrineContractError(
                "SealedWorkflowPackage.workflow_outcome_class must be WorkflowOutcomeClass",
            )
        for name in (
            "mutation_proposal_only_assertion",
            "exit_review_required",
            "no_durable_commit_assertion",
        ):
            _need_bool(getattr(self, name), f"SealedWorkflowPackage.{name}")
        # 03.8 §HARD LAWS — every assertion must be True.
        if not (
            self.mutation_proposal_only_assertion
            and self.exit_review_required
            and self.no_durable_commit_assertion
        ):
            raise L3DoctrineContractError(
                "SealedWorkflowPackage assertions must all be True; L3 never writes durable state",
            )


__all__ = [
    "CompletionStatus",
    "ConcurrencyPlan",
    "CostLatencyTokenSummary",
    "FallbackCascadeState",
    "QualityLoopPlan",
    "SealedWorkflowPackage",
    "WorkflowCompletionTest",
    "WorkflowOutcomeClass",
]

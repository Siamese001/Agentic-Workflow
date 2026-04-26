"""03.2 L0 Deterministic Route Selection contracts.

Realizes:

- ``RouteScoreVector``         — 03.2 PHASE 1 §1
- ``FixedDecisionOrderReceipt``— 03.2 PHASE 1 §2
- ``RouteSelectionReceipt``    — 03.2 PHASE 1 §3
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from enum import Enum

from . import DoctrineContractError
from .contracts_l0_1 import CandidateRouteId

_MAX_STR_LEN = 512
_MAX_LIST = 64
_MAX_REASON = 32


def _need_str(value: object, name: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, str):
        raise DoctrineContractError(f"{name} must be str, got {type(value).__name__}")
    if len(value) > _MAX_STR_LEN:
        raise DoctrineContractError(f"{name} exceeds {_MAX_STR_LEN} chars")
    if not allow_empty and not value:
        raise DoctrineContractError(f"{name} must be non-empty")


def _need_str_tuple(values: object, name: str, *, max_len: int = _MAX_LIST) -> None:
    if not isinstance(values, tuple):
        raise DoctrineContractError(f"{name} must be tuple")
    if len(values) > max_len:
        raise DoctrineContractError(f"{name} exceeds {max_len}")
    for idx, item in enumerate(values):
        if not isinstance(item, str) or not item or len(item) > _MAX_STR_LEN:
            raise DoctrineContractError(f"{name}[{idx}] must be non-empty str <= {_MAX_STR_LEN}")


def _need_finite_float_in_unit(value: object, name: str) -> None:
    """Validate a float/int falls in [0.0, 1.0]."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DoctrineContractError(f"{name} must be float in [0,1]")
    if value != value:  # NaN check w/o math.isnan dependency
        raise DoctrineContractError(f"{name} must not be NaN")
    if value < 0.0 or value > 1.0:
        raise DoctrineContractError(f"{name} must be in [0,1], got {value}")


class ConfidenceClass(str, Enum):
    """Reasoned confidence class (mirrors 03.5 §confidence; restated here for 03.2 self-consistency)."""

    EXACT = "EXACT"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNSAFE = "UNSAFE"
    INSUFFICIENT_SUPPORT = "INSUFFICIENT_SUPPORT"


class ExecutionFormSelected(str, Enum):
    """03.2 §FixedDecisionOrderReceipt — chosen execution form."""

    TERMINAL_SHORTCIRCUIT = "TERMINAL_SHORTCIRCUIT"
    SINGLE_STEP = "SINGLE_STEP"
    MANAGED_WORKFLOW = "MANAGED_WORKFLOW"


@dataclass(frozen=True)
class RouteScoreVector:
    """03.2 PHASE 1 §1 RouteScoreVector.

    All scores are floats in [0.0, 1.0]. Higher = stronger signal for that route family
    or risk dimension. The selector applies the FixedDecisionOrder, NOT a soft-max — score
    fields are observability + calibration aids, not the decision itself.
    """

    exact_cache_score: float = 0.0
    semantic_cache_score: float = 0.0
    grounding_need_score: float = 0.0
    single_action_score: float = 0.0
    managed_workflow_score: float = 0.0
    fallback_need_score: float = 0.0
    hitl_need_score: float = 0.0
    freshness_risk: float = 0.0
    support_risk: float = 0.0
    action_risk: float = 0.0
    mutation_risk: float = 0.0
    egress_risk: float = 0.0
    ambiguity_risk: float = 0.0
    tenant_acl_risk: float = 0.0
    cost_risk: float = 0.0
    slo_risk: float = 0.0
    confidence_class: ConfidenceClass = ConfidenceClass.MEDIUM

    def __post_init__(self) -> None:
        for f in fields(self):
            if f.name == "confidence_class":
                if not isinstance(self.confidence_class, ConfidenceClass):
                    raise DoctrineContractError(
                        "RouteScoreVector.confidence_class must be ConfidenceClass",
                    )
                continue
            _need_finite_float_in_unit(getattr(self, f.name), f"RouteScoreVector.{f.name}")


@dataclass(frozen=True)
class FixedDecisionOrderReceipt:
    """03.2 PHASE 1 §2 FixedDecisionOrderReceipt.

    Records the ordered evaluation of the seven decision steps (0..7) and which step
    produced the first match. Skipped steps include the reason. Provides the
    deterministic order hash for replay verification.
    """

    decision_order_version: str
    evaluated_steps: tuple[str, ...]
    first_passing_step: str
    skipped_steps_with_reasons: tuple[str, ...]
    blocked_routes: tuple[str, ...]
    selected_route_id: CandidateRouteId
    selected_execution_form: ExecutionFormSelected
    deterministic_order_hash: str

    def __post_init__(self) -> None:
        _need_str(self.decision_order_version, "FixedDecisionOrderReceipt.decision_order_version")
        _need_str(self.first_passing_step, "FixedDecisionOrderReceipt.first_passing_step")
        _need_str(
            self.deterministic_order_hash,
            "FixedDecisionOrderReceipt.deterministic_order_hash",
        )
        _need_str_tuple(self.evaluated_steps, "FixedDecisionOrderReceipt.evaluated_steps")
        _need_str_tuple(
            self.skipped_steps_with_reasons,
            "FixedDecisionOrderReceipt.skipped_steps_with_reasons",
            max_len=_MAX_REASON,
        )
        _need_str_tuple(self.blocked_routes, "FixedDecisionOrderReceipt.blocked_routes")
        if not isinstance(self.selected_route_id, CandidateRouteId):
            raise DoctrineContractError(
                "FixedDecisionOrderReceipt.selected_route_id must be CandidateRouteId",
            )
        if not isinstance(self.selected_execution_form, ExecutionFormSelected):
            raise DoctrineContractError(
                "FixedDecisionOrderReceipt.selected_execution_form must be ExecutionFormSelected",
            )


@dataclass(frozen=True)
class RouteSelectionReceipt:
    """03.2 PHASE 1 §3 RouteSelectionReceipt.

    Final receipt the selector emits. The downstream contract builder (03.5)
    consumes this to mint a ``V15RouteContract``.
    """

    route_selection_id: str
    request_id: str
    run_id: str
    trace_root: str
    l1_plan_id: str
    preflight_id: str
    selected_route_id: CandidateRouteId
    selected_execution_form: ExecutionFormSelected
    confidence: float
    confidence_class: ConfidenceClass
    reason_codes: tuple[str, ...]
    route_score_vector: RouteScoreVector
    cheapest_safe_route_rationale: str
    rejected_route_reasons: tuple[str, ...]
    fallback_chain_hint: tuple[str, ...]
    downstream_required_layers: tuple[str, ...]
    fixed_order_receipt: FixedDecisionOrderReceipt
    route_selection_hash: str

    def __post_init__(self) -> None:
        for name in (
            "route_selection_id",
            "request_id",
            "run_id",
            "trace_root",
            "l1_plan_id",
            "preflight_id",
            "route_selection_hash",
        ):
            _need_str(getattr(self, name), f"RouteSelectionReceipt.{name}")
        _need_str(
            self.cheapest_safe_route_rationale,
            "RouteSelectionReceipt.cheapest_safe_route_rationale",
            allow_empty=True,
        )
        if not isinstance(self.selected_route_id, CandidateRouteId):
            raise DoctrineContractError(
                "RouteSelectionReceipt.selected_route_id must be CandidateRouteId",
            )
        if not isinstance(self.selected_execution_form, ExecutionFormSelected):
            raise DoctrineContractError(
                "RouteSelectionReceipt.selected_execution_form must be ExecutionFormSelected",
            )
        _need_finite_float_in_unit(self.confidence, "RouteSelectionReceipt.confidence")
        if not isinstance(self.confidence_class, ConfidenceClass):
            raise DoctrineContractError(
                "RouteSelectionReceipt.confidence_class must be ConfidenceClass",
            )
        _need_str_tuple(self.reason_codes, "RouteSelectionReceipt.reason_codes", max_len=_MAX_REASON)
        if not isinstance(self.route_score_vector, RouteScoreVector):
            raise DoctrineContractError(
                "RouteSelectionReceipt.route_score_vector must be RouteScoreVector",
            )
        _need_str_tuple(
            self.rejected_route_reasons,
            "RouteSelectionReceipt.rejected_route_reasons",
            max_len=_MAX_REASON,
        )
        _need_str_tuple(self.fallback_chain_hint, "RouteSelectionReceipt.fallback_chain_hint")
        _need_str_tuple(
            self.downstream_required_layers,
            "RouteSelectionReceipt.downstream_required_layers",
        )
        if not isinstance(self.fixed_order_receipt, FixedDecisionOrderReceipt):
            raise DoctrineContractError(
                "RouteSelectionReceipt.fixed_order_receipt must be FixedDecisionOrderReceipt",
            )
        # Coherence: receipt route id must equal fixed order route id
        if self.fixed_order_receipt.selected_route_id != self.selected_route_id:
            raise DoctrineContractError(
                "RouteSelectionReceipt.selected_route_id must match fixed_order_receipt.selected_route_id",
            )


__all__ = [
    "ConfidenceClass",
    "ExecutionFormSelected",
    "FixedDecisionOrderReceipt",
    "RouteScoreVector",
    "RouteSelectionReceipt",
]

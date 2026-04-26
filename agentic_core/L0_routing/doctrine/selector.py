"""03.2 L0 Deterministic Route Selection — public ``select_route`` entrypoint.

Pure function. No I/O. Deterministic given inputs.

Implements 03.2 §FIXED DECISION ORDER (steps 0..7) and 03.2 §PHASE 2 implementation
steps 1..7. Hands off to the 03.5 contract builder via the returned
``RouteSelectionReceipt``.

Cheapest-safe-route policy: among candidates that pass the same FixedDecisionOrder
gate, prefer terminal short-circuits (R1A/R1B) > single-step grounded/action (R3/R4)
> managed workflow (R3R4) > R5. R5 is always the safety-net last entry.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

from . import DoctrineContractError
from .contracts_l0_1 import (
    CandidateRouteId,
    PreflightStatus,
    RouteCandidateFrame,
    RouteDiscriminatorFrame,
)
from .contracts_l0_2 import (
    ConfidenceClass,
    ExecutionFormSelected,
    FixedDecisionOrderReceipt,
    RouteScoreVector,
    RouteSelectionReceipt,
)

_DECISION_ORDER_VERSION = "03.2-v1"


def _digest(payload: object, prefix: str) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"{prefix}:{hashlib.sha256(encoded).hexdigest()}"


def _execution_form_for(route_id: CandidateRouteId) -> ExecutionFormSelected:
    if route_id in {
        CandidateRouteId.R1A_EXACT_CACHE,
        CandidateRouteId.R1B_SEMANTIC_CACHE,
        CandidateRouteId.R5_FALLBACK,
    }:
        return ExecutionFormSelected.TERMINAL_SHORTCIRCUIT
    if route_id in {
        CandidateRouteId.R3_SIMPLE_GROUNDED_READ,
        CandidateRouteId.R4_SINGLE_ACTION,
    }:
        return ExecutionFormSelected.SINGLE_STEP
    return ExecutionFormSelected.MANAGED_WORKFLOW


def compute_score_vector(
    discriminators: RouteDiscriminatorFrame,
    candidate_set: tuple[CandidateRouteId, ...],
) -> RouteScoreVector:
    """03.2 §1 compute_score_vector — deterministic mapping from discriminators."""

    def _b(flag: bool) -> float:
        return 1.0 if flag else 0.0

    exact_cache = _b(discriminators.can_be_cached_exactly) * (
        1.0 - _b(discriminators.asks_for_current_or_latest)
    )
    semantic_cache = (
        _b(discriminators.can_be_cached_semantically)
        * (1.0 - _b(discriminators.asks_for_current_or_latest))
        * (1.0 - _b(discriminators.asks_for_user_file_or_connector))
    )
    grounding_need = _b(
        discriminators.asks_for_factual_claim or discriminators.asks_for_source_grounding,
    )
    single_action = _b(
        discriminators.asks_for_external_action and not discriminators.likely_requires_l3,
    )
    managed = _b(discriminators.likely_requires_l3)
    fallback = _b(
        discriminators.has_weak_support_risk and not discriminators.asks_for_source_grounding,
    )
    hitl = _b(discriminators.likely_requires_hitl or discriminators.asks_for_irreversible_action)

    freshness_risk = _b(discriminators.asks_for_current_or_latest)
    support_risk = _b(discriminators.has_weak_support_risk)
    action_risk = _b(discriminators.asks_for_external_action)
    mutation_risk = _b(discriminators.asks_for_durable_mutation)
    ambiguity_risk = _b(discriminators.has_ambiguous_action_args)

    # Confidence class derives from how many viable candidates are present
    has_terminal = (
        CandidateRouteId.R1A_EXACT_CACHE in candidate_set
        or CandidateRouteId.R1B_SEMANTIC_CACHE in candidate_set
    )
    if has_terminal and exact_cache >= 1.0:
        cclass = ConfidenceClass.EXACT
    elif has_terminal:
        cclass = ConfidenceClass.HIGH
    elif (
        CandidateRouteId.R3_SIMPLE_GROUNDED_READ in candidate_set
        or CandidateRouteId.R4_SINGLE_ACTION in candidate_set
    ):
        cclass = ConfidenceClass.MEDIUM
    elif CandidateRouteId.R3R4_MANAGED_WORKFLOW in candidate_set:
        cclass = ConfidenceClass.MEDIUM
    elif candidate_set == (CandidateRouteId.R5_FALLBACK,):
        cclass = ConfidenceClass.INSUFFICIENT_SUPPORT
    else:
        cclass = ConfidenceClass.LOW

    return RouteScoreVector(
        exact_cache_score=exact_cache,
        semantic_cache_score=semantic_cache,
        grounding_need_score=grounding_need,
        single_action_score=single_action,
        managed_workflow_score=managed,
        fallback_need_score=fallback,
        hitl_need_score=hitl,
        freshness_risk=freshness_risk,
        support_risk=support_risk,
        action_risk=action_risk,
        mutation_risk=mutation_risk,
        egress_risk=0.0,
        ambiguity_risk=ambiguity_risk,
        tenant_acl_risk=0.0,
        cost_risk=0.0,
        slo_risk=0.0,
        confidence_class=cclass,
    )


def _confidence_score_for_class(cclass: ConfidenceClass) -> float:
    """Deterministic numeric confidence aligned with 03.5 _classify_confidence bands."""
    return {
        ConfidenceClass.EXACT: 1.0,
        ConfidenceClass.HIGH: 0.90,
        ConfidenceClass.MEDIUM: 0.70,
        ConfidenceClass.LOW: 0.45,
        ConfidenceClass.UNSAFE: 0.0,
        ConfidenceClass.INSUFFICIENT_SUPPORT: 0.10,
    }[cclass]


# 03.2 §FIXED DECISION ORDER step labels
_STEP_LABELS = (
    "0_invalid_or_unsafe",
    "1_exact_cache",
    "2_semantic_cache",
    "3_high_risk_hitl",
    "4_low_risk_action",
    "5_grounded_read",
    "6_managed_workflow",
    "7_fallback",
)


def _apply_fixed_decision_order(
    candidate_frame: RouteCandidateFrame,
    discriminators: RouteDiscriminatorFrame,
) -> tuple[CandidateRouteId, str, list[str], list[str]]:
    """03.2 §2 apply_fixed_decision_order.

    Returns ``(selected_route_id, first_passing_step, skipped_steps, blocked_routes)``.
    """
    candidates = set(candidate_frame.route_candidates)
    skipped: list[str] = []
    blocked: list[str] = []

    # Step 0: invalid envelope / scope fail / unsafe
    if candidate_frame.preflight_status not in (
        PreflightStatus.ROUTE_READY,
        PreflightStatus.ROUTE_NEEDS_CLARIFY_FALLBACK,
        PreflightStatus.ROUTE_SAFE_FALLBACK_ONLY,
    ):
        return (
            CandidateRouteId.R5_FALLBACK,
            _STEP_LABELS[0],
            [],
            [c.value for c in CandidateRouteId if c != CandidateRouteId.R5_FALLBACK],
        )

    # Step 1: exact cache
    if CandidateRouteId.R1A_EXACT_CACHE in candidates and discriminators.can_be_cached_exactly:
        return (CandidateRouteId.R1A_EXACT_CACHE, _STEP_LABELS[1], skipped, blocked)
    skipped.append(f"{_STEP_LABELS[1]}:not_eligible")

    # Step 2: semantic cache
    if (
        CandidateRouteId.R1B_SEMANTIC_CACHE in candidates
        and discriminators.can_be_cached_semantically
        and not discriminators.asks_for_current_or_latest
        and not discriminators.asks_for_user_file_or_connector
    ):
        return (CandidateRouteId.R1B_SEMANTIC_CACHE, _STEP_LABELS[2], skipped, blocked)
    skipped.append(f"{_STEP_LABELS[2]}:not_eligible")

    # Step 3: high-risk irreversible / authority ambiguous -> HITL posture via R5
    if discriminators.asks_for_irreversible_action and discriminators.has_ambiguous_action_args:
        return (CandidateRouteId.R5_FALLBACK, _STEP_LABELS[3], skipped, blocked)
    skipped.append(f"{_STEP_LABELS[3]}:not_high_risk_ambiguous")

    # Step 4: low-risk action
    if (
        CandidateRouteId.R4_SINGLE_ACTION in candidates
        and discriminators.asks_for_external_action
        and not discriminators.has_ambiguous_action_args
        and not discriminators.likely_requires_l3
    ):
        return (CandidateRouteId.R4_SINGLE_ACTION, _STEP_LABELS[4], skipped, blocked)
    skipped.append(f"{_STEP_LABELS[4]}:not_eligible")

    # Step 5: grounded read
    if (
        CandidateRouteId.R3_SIMPLE_GROUNDED_READ in candidates
        and (discriminators.asks_for_factual_claim or discriminators.asks_for_source_grounding)
        and not discriminators.likely_requires_l3
    ):
        return (CandidateRouteId.R3_SIMPLE_GROUNDED_READ, _STEP_LABELS[5], skipped, blocked)
    skipped.append(f"{_STEP_LABELS[5]}:not_eligible")

    # Step 6: managed workflow
    if CandidateRouteId.R3R4_MANAGED_WORKFLOW in candidates and discriminators.likely_requires_l3:
        return (CandidateRouteId.R3R4_MANAGED_WORKFLOW, _STEP_LABELS[6], skipped, blocked)
    skipped.append(f"{_STEP_LABELS[6]}:not_eligible")

    # Step 7: fallback (default safety net)
    return (CandidateRouteId.R5_FALLBACK, _STEP_LABELS[7], skipped, blocked)


def _build_fallback_chain_hint(selected: CandidateRouteId) -> tuple[str, ...]:
    """Deterministic fallback-chain hint per route family.

    Mirrors 03.4 §R3 / R4 fallback obligations. Always terminates in R5.
    """
    if selected in {CandidateRouteId.R1A_EXACT_CACHE, CandidateRouteId.R1B_SEMANTIC_CACHE}:
        return ()  # terminal cache hit; no chain
    if selected == CandidateRouteId.R3_SIMPLE_GROUNDED_READ:
        return (
            CandidateRouteId.R3R4_MANAGED_WORKFLOW.value,
            CandidateRouteId.R5_FALLBACK.value,
        )
    if selected == CandidateRouteId.R4_SINGLE_ACTION:
        # HITL hint -> R5
        return (CandidateRouteId.R5_FALLBACK.value,)
    if selected == CandidateRouteId.R3R4_MANAGED_WORKFLOW:
        return (CandidateRouteId.R5_FALLBACK.value,)
    return ()


def _build_rejected_reasons(
    candidate_frame: RouteCandidateFrame,
    selected: CandidateRouteId,
) -> tuple[str, ...]:
    rejected: list[str] = []
    for c in candidate_frame.route_candidates:
        if c != selected:
            rejected.append(f"{c.value}:not_first_pass_winner")
    return tuple(rejected)


def select_route(
    candidate_frame: RouteCandidateFrame,
    *,
    request_id: str,
    run_id: str,
    trace_root: str,
    l1_plan_id: str,
    preflight_id: str,
) -> RouteSelectionReceipt:
    """Public entrypoint — 03.2 §PHASE 2 PUBLIC ENTRYPOINT.

    Same RouteCandidateFrame + same identity inputs -> same selected_route_id +
    same route_selection_hash (03.2 §DETERMINISM REQUIREMENTS).
    """
    if not isinstance(candidate_frame, RouteCandidateFrame):
        raise DoctrineContractError(
            f"candidate_frame must be RouteCandidateFrame, got {type(candidate_frame).__name__}",
        )
    for name, value in (
        ("request_id", request_id),
        ("run_id", run_id),
        ("trace_root", trace_root),
        ("l1_plan_id", l1_plan_id),
        ("preflight_id", preflight_id),
    ):
        if not isinstance(value, str) or not value:
            raise DoctrineContractError(f"select_route() requires non-empty {name}")

    discriminators = candidate_frame.discriminators
    score_vec = compute_score_vector(discriminators, candidate_frame.route_candidates)

    selected, first_step, skipped, blocked = _apply_fixed_decision_order(
        candidate_frame,
        discriminators,
    )
    exec_form = _execution_form_for(selected)

    order_payload = {
        "version": _DECISION_ORDER_VERSION,
        "candidates": [c.value for c in candidate_frame.route_candidates],
        "discriminators": asdict(discriminators),
        "selected": selected.value,
        "first_step": first_step,
        "skipped": skipped,
        "blocked": blocked,
    }
    order_hash = _digest(order_payload, "order")
    fixed_receipt = FixedDecisionOrderReceipt(
        decision_order_version=_DECISION_ORDER_VERSION,
        evaluated_steps=_STEP_LABELS,
        first_passing_step=first_step,
        skipped_steps_with_reasons=tuple(skipped),
        blocked_routes=tuple(blocked),
        selected_route_id=selected,
        selected_execution_form=exec_form,
        deterministic_order_hash=order_hash,
    )

    confidence_score = _confidence_score_for_class(score_vec.confidence_class)
    rationale = (
        f"first_passing={first_step}; "
        f"confidence={score_vec.confidence_class.value}; "
        f"chain_hint={_build_fallback_chain_hint(selected)}"
    )

    selection_payload = {
        "request_id": request_id,
        "preflight_id": preflight_id,
        "selected": selected.value,
        "exec_form": exec_form.value,
        "score_vector": asdict(score_vec),
        "fixed_order_hash": order_hash,
        "frame_hash": candidate_frame.candidate_frame_hash,
    }
    selection_hash = _digest(selection_payload, "sel")
    selection_id = _digest({"id": selection_hash}, "rsl")

    return RouteSelectionReceipt(
        route_selection_id=selection_id,
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        l1_plan_id=l1_plan_id,
        preflight_id=preflight_id,
        selected_route_id=selected,
        selected_execution_form=exec_form,
        confidence=confidence_score,
        confidence_class=score_vec.confidence_class,
        reason_codes=candidate_frame.candidate_reason_codes,
        route_score_vector=score_vec,
        cheapest_safe_route_rationale=rationale,
        rejected_route_reasons=_build_rejected_reasons(candidate_frame, selected),
        fallback_chain_hint=_build_fallback_chain_hint(selected),
        downstream_required_layers=candidate_frame.candidate_required_downstream_layers,
        fixed_order_receipt=fixed_receipt,
        route_selection_hash=selection_hash,
    )


__all__ = ["compute_score_vector", "select_route"]

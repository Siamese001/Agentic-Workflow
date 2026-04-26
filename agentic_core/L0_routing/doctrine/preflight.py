"""03.1 L0 Route Input + Preflight pipeline.

Public entrypoint:

    run_l0_preflight(input: RouteDecisionInput) -> RouteCandidateFrame

Pure function. No I/O. Deterministic given inputs.

Implements the 03.1 PHASE 2 ``Steps`` 1-8:

1. validate_identity_and_hashes
2. verify_l1_non_authority_flags
3. extract_route_discriminators
4. check_policy_and_scope_baseline
5. check_source_availability
6. check_action_side_effect_baseline
7. build_candidate_frame
8. emit_route_input_audit_receipt

Hard-fail conditions (03.1 §HARD FAIL CONDITIONS) raise ``DoctrineContractError``;
soft fails surface as preflight_status != ROUTE_READY with a non-empty
``candidate_blockers`` tuple and an ``R5_FALLBACK``-only candidate set.
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
    RouteDecisionInput,
    RouteDiscriminatorFrame,
    RouteInputAuditReceipt,
    RoutePreflightStatusReport,
    SourceAvailabilitySnapshot,
)


def _digest(payload: object, prefix: str) -> str:
    """Deterministic SHA-256 prefix-tagged digest. No entropy."""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"{prefix}:{hashlib.sha256(encoded).hexdigest()}"


def _validate_identity_and_hashes(decision_input: RouteDecisionInput) -> list[str]:
    """Step 1 — identity / hash presence (03.1 §HARD FAIL #1, #2)."""
    missing: list[str] = []
    for name in ("request_id", "trace_root", "replay_key", "policy_hash", "blueprint_hash"):
        if not getattr(decision_input, name):
            missing.append(name)
    return missing


def _verify_l1_non_authority(decision_input: RouteDecisionInput) -> list[str]:
    """Step 2 — L1 non-authority assertions (03.1 §HARD FAIL #3, #4, #5, #6)."""
    invalid: list[str] = []
    summary = decision_input.validation_summary
    if not summary.no_retrieval_performed:
        invalid.append("L1 already retrieved final evidence")
    if not summary.no_execution_performed:
        invalid.append("L1 already executed a tool/model/script")
    if not summary.no_write_performed:
        invalid.append("L1 already wrote durable state")
    if not summary.no_final_route_authority_claimed:
        invalid.append("L1 claims final route authority")
    return invalid


def _extract_discriminators(
    decision_input: RouteDecisionInput,
) -> RouteDiscriminatorFrame:
    """Step 3 — extract discriminators from L1 plan + tenant scope.

    Heuristic, deterministic. The selector (03.2) re-uses these flags but never
    treats them as final authority; they are advisory.
    """
    task = decision_input.task_spec.lower()
    query = decision_input.query_spec.lower()
    blob = f"{task} {query}"

    asks_factual = any(t in blob for t in ("what", "which", "who", "when", "where", "explain", "summarize"))
    asks_grounding = bool(decision_input.support_expectation) or "according to" in blob
    asks_current = any(t in blob for t in ("latest", "current", "today", "this week", "live", "right now"))
    asks_user_file = bool(decision_input.visible_source_handles)
    asks_code = any(t in blob for t in ("code", "function", "class ", "module", "policy", "rule"))
    asks_action = bool(decision_input.action_expectation)
    asks_mutation = "mutation" in blob or "delete" in blob or "create" in blob or "update" in blob
    asks_irreversible = any(t in blob for t in ("delete forever", "purge", "permanent", "irrevers"))
    asks_multistep = decision_input.action_expectation.lower().count(" then ") >= 1 or "multi-step" in blob
    has_dep = "depends on" in blob or " then " in blob
    has_branch = "either" in blob or " or " in blob
    has_parallel = "parallel" in blob or "fan out" in blob
    weak_support = "I'm not sure" in decision_input.task_spec or not asks_grounding
    ambiguous_args = "someone" in blob or "someplace" in blob or "anything" in blob
    can_exact_cache = not asks_current and not asks_action and not asks_mutation
    can_semantic_cache = can_exact_cache and not asks_user_file
    can_terminal = can_exact_cache or can_semantic_cache
    can_single_step = (asks_factual and asks_grounding and not asks_multistep) or (
        asks_action and not has_dep and not asks_multistep
    )
    likely_l3 = asks_multistep or has_dep or has_branch or has_parallel
    likely_hitl = asks_irreversible or "approve" in blob or "review" in blob
    likely_uwg = asks_mutation
    likely_c0 = asks_grounding or asks_factual or asks_user_file or asks_code
    likely_pa = likely_c0
    likely_l2 = asks_action or likely_c0
    likely_ptc = "tool batch" in blob or "script" in blob

    return RouteDiscriminatorFrame(
        asks_for_factual_claim=asks_factual,
        asks_for_source_grounding=asks_grounding,
        asks_for_current_or_latest=asks_current,
        asks_for_user_file_or_connector=asks_user_file,
        asks_for_code_or_policy_location=asks_code,
        asks_for_external_action=asks_action,
        asks_for_durable_mutation=asks_mutation,
        asks_for_irreversible_action=asks_irreversible,
        asks_for_multi_step_workflow=asks_multistep,
        has_dependency_chain=has_dep,
        has_branching_or_join=has_branch,
        has_parallel_safe_shards=has_parallel,
        has_weak_support_risk=weak_support,
        has_ambiguous_action_args=ambiguous_args,
        can_be_cached_exactly=can_exact_cache,
        can_be_cached_semantically=can_semantic_cache,
        can_be_answered_terminally=can_terminal,
        can_be_single_step=can_single_step,
        likely_requires_l3=likely_l3,
        likely_requires_hitl=likely_hitl,
        likely_requires_uwg=likely_uwg,
        likely_requires_c0=likely_c0,
        likely_requires_pa=likely_pa,
        likely_requires_l2=likely_l2,
        likely_ptc_capable_downstream=likely_ptc,
    )


def _check_policy_and_scope(decision_input: RouteDecisionInput) -> list[str]:
    """Step 4 — policy/tenant baseline (03.1 §HARD FAIL #7)."""
    blockers: list[str] = []
    if not decision_input.tenant_id.strip():
        blockers.append("tenant boundary cannot be established")
    return blockers


def _check_source_availability(
    decision_input: RouteDecisionInput,
) -> SourceAvailabilitySnapshot:
    """Step 5 — source availability (03.1 §HARD FAIL #9)."""
    expected = decision_input.source_expectations
    available = decision_input.visible_source_handles
    missing = tuple(s for s in expected if s not in available)
    snap = SourceAvailabilitySnapshot(
        source_classes_expected=expected,
        source_classes_available=available,
        source_classes_missing=missing,
    )
    return snap.with_hash()


def _check_action_side_effect(
    discriminators: RouteDiscriminatorFrame,
) -> list[str]:
    """Step 6 — action / side-effect baseline (03.1 §HARD FAIL #8)."""
    blockers: list[str] = []
    if discriminators.asks_for_irreversible_action and discriminators.has_ambiguous_action_args:
        blockers.append("action target is ambiguous and irreversible")
    return blockers


def _build_candidates(
    discriminators: RouteDiscriminatorFrame,
    source_snap: SourceAvailabilitySnapshot,
    soft_blockers: list[str],
) -> tuple[CandidateRouteId, ...]:
    """Step 7 — build candidate set per discriminators.

    Per 03.1 the preflight does NOT pick a final route; it merely lists the
    candidates the selector (03.2) is allowed to consider. R5 is always in
    the candidate set as the safety net.
    """
    candidates: list[CandidateRouteId] = []
    if soft_blockers:
        # Source missing or scope incomplete -> only R5 viable.
        candidates.append(CandidateRouteId.R5_FALLBACK)
        return tuple(candidates)

    if discriminators.can_be_cached_exactly:
        candidates.append(CandidateRouteId.R1A_EXACT_CACHE)
    if discriminators.can_be_cached_semantically:
        candidates.append(CandidateRouteId.R1B_SEMANTIC_CACHE)
    if (
        discriminators.likely_requires_c0
        and discriminators.can_be_single_step
        and not discriminators.likely_requires_l3
    ):
        candidates.append(CandidateRouteId.R3_SIMPLE_GROUNDED_READ)
    if discriminators.asks_for_external_action and not discriminators.likely_requires_l3:
        candidates.append(CandidateRouteId.R4_SINGLE_ACTION)
    if discriminators.likely_requires_l3:
        candidates.append(CandidateRouteId.R3R4_MANAGED_WORKFLOW)
    candidates.append(CandidateRouteId.R5_FALLBACK)

    # Deduplicate while preserving order
    seen: set[CandidateRouteId] = set()
    out: list[CandidateRouteId] = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            out.append(c)
    if source_snap.source_classes_missing and CandidateRouteId.R3_SIMPLE_GROUNDED_READ in out:
        # Missing source class downgrades R3 path
        out = [c for c in out if c != CandidateRouteId.R3_SIMPLE_GROUNDED_READ]
        if CandidateRouteId.R5_FALLBACK not in out:
            out.append(CandidateRouteId.R5_FALLBACK)
    return tuple(out)


def _emit_audit_receipt(
    decision_input: RouteDecisionInput,
    preflight_status: RoutePreflightStatusReport,
    candidate_count: int,
    blocked_count: int,
    fail_closed_reason: str,
) -> RouteInputAuditReceipt:
    """Step 8 — audit receipt for L6 calibration."""
    payload = {
        "request_id": decision_input.request_id,
        "preflight_id": preflight_status.preflight_id,
        "candidate_count": candidate_count,
        "blocked_count": blocked_count,
        "fail_closed_reason": fail_closed_reason,
    }
    return RouteInputAuditReceipt(
        receipt_id=_digest(payload, "rcpt"),
        request_id=decision_input.request_id,
        run_id=decision_input.run_id,
        trace_root=decision_input.trace_root,
        l1_plan_id=decision_input.l1_plan_id,
        preflight_id=preflight_status.preflight_id,
        candidate_count=candidate_count,
        blocked_count=blocked_count,
        fail_closed_reason=fail_closed_reason,
        receipt_hash=_digest(payload, "h"),
    )


def _build_preflight_status(
    decision_input: RouteDecisionInput,
    missing: list[str],
    invalid: list[str],
    scope_blockers: list[str],
    action_blockers: list[str],
    source_snap: SourceAvailabilitySnapshot,
) -> RoutePreflightStatusReport:
    """Compose a ``RoutePreflightStatusReport`` from accumulated checks."""
    if missing:
        status = PreflightStatus.ROUTE_INPUT_INCOMPLETE
        eligible = False
        reason = f"missing_critical_fields={missing}"
    elif invalid:
        status = PreflightStatus.ROUTE_BLOCKED_AUTHORITY
        eligible = False
        reason = f"l1_non_authority_violations={invalid}"
    elif scope_blockers:
        status = PreflightStatus.ROUTE_BLOCKED_SCOPE
        eligible = False
        reason = f"scope_blockers={scope_blockers}"
    elif action_blockers:
        status = PreflightStatus.ROUTE_SAFE_FALLBACK_ONLY
        eligible = False
        reason = f"action_blockers={action_blockers}"
    elif source_snap.source_classes_missing and decision_input.support_expectation:
        status = PreflightStatus.ROUTE_NEEDS_CLARIFY_FALLBACK
        eligible = False
        reason = f"missing_sources={source_snap.source_classes_missing}"
    else:
        status = PreflightStatus.ROUTE_READY
        eligible = True
        reason = ""

    payload = {
        "request_id": decision_input.request_id,
        "missing": tuple(missing),
        "invalid": tuple(invalid),
        "scope_blockers": tuple(scope_blockers),
        "action_blockers": tuple(action_blockers),
        "missing_sources": source_snap.source_classes_missing,
    }
    preflight_id = _digest(payload, "pf")
    return RoutePreflightStatusReport(
        preflight_id=preflight_id,
        status=status,
        eligible_for_route_selection=eligible,
        blocked_reason=reason,
        policy_status="ok" if not invalid else "violated",
        tenant_scope_status="ok" if not scope_blockers else "violated",
        acl_scope_status="not_evaluated",
        route_input_completeness="complete" if not missing else "incomplete",
        missing_critical_fields=tuple(missing),
        invalid_authority_claims=tuple(invalid),
        stale_policy_or_blueprint_flags=tuple(),
        source_handle_status=source_snap.source_classes_missing,
        action_scope_status="ok" if not action_blockers else "blocked",
        egress_scope_status="not_evaluated",
        preflight_hash=_digest(payload, "h"),
    )


def run_l0_preflight(decision_input: RouteDecisionInput) -> RouteCandidateFrame:
    """Public entrypoint — 03.1 §PHASE 2 PREFLIGHT PIPELINE.

    Hard-fails (raises ``DoctrineContractError``) only on missing critical
    identity/hash fields — those are protocol-level errors that cannot be
    represented as a soft R5_FALLBACK because we cannot identify the request.

    All other failure modes resolve to an R5_FALLBACK-only candidate set with
    ``preflight_status != ROUTE_READY``.
    """
    if not isinstance(decision_input, RouteDecisionInput):
        raise DoctrineContractError(
            f"decision_input must be RouteDecisionInput, got {type(decision_input).__name__}",
        )

    missing = _validate_identity_and_hashes(decision_input)
    if missing:
        # Hard fail per 03.1 §HARD FAIL — caller cannot recover without
        # protocol-level fix.
        raise DoctrineContractError(
            f"RouteDecisionInput missing critical identity/hash fields: {missing}",
        )

    invalid = _verify_l1_non_authority(decision_input)
    discriminators = _extract_discriminators(decision_input)
    scope_blockers = _check_policy_and_scope(decision_input)
    source_snap = _check_source_availability(decision_input)
    action_blockers = _check_action_side_effect(discriminators)

    soft_blockers: list[str] = list(invalid) + list(scope_blockers) + list(action_blockers)
    if source_snap.source_classes_missing and decision_input.support_expectation:
        soft_blockers.append("source classes missing for grounded support expectation")

    candidates = _build_candidates(discriminators, source_snap, soft_blockers)
    preflight = _build_preflight_status(
        decision_input,
        missing=[],  # already raised; this branch is unreachable for missing
        invalid=invalid,
        scope_blockers=scope_blockers,
        action_blockers=action_blockers,
        source_snap=source_snap,
    )

    payload = {
        "candidates": [c.value for c in candidates],
        "discriminators": asdict(discriminators),
        "source_availability_hash": source_snap.availability_hash,
        "preflight_id": preflight.preflight_id,
    }
    frame_hash = _digest(payload, "rcf")

    return RouteCandidateFrame(
        route_candidates=candidates,
        candidate_reason_codes=tuple(soft_blockers),
        candidate_blockers=tuple(soft_blockers),
        candidate_required_downstream_layers=tuple(
            layer
            for layer, flag in (
                ("c0", discriminators.likely_requires_c0),
                ("pa", discriminators.likely_requires_pa),
                ("l2", discriminators.likely_requires_l2),
                ("l3", discriminators.likely_requires_l3),
                ("hitl", discriminators.likely_requires_hitl),
                ("uwg", discriminators.likely_requires_uwg),
            )
            if flag
        ),
        candidate_risks=tuple(),
        candidate_cost_estimates=tuple(),
        candidate_slo_estimates=tuple(),
        candidate_support_obligations=(
            (decision_input.support_expectation,) if decision_input.support_expectation else tuple()
        ),
        candidate_capability_requirements=tuple(),
        candidate_sandbox_requirements=tuple(),
        candidate_handoff_requirements=tuple(),
        discriminators=discriminators,
        source_availability=source_snap,
        preflight_status=preflight.status,
        candidate_frame_hash=frame_hash,
    )


__all__ = ["run_l0_preflight"]

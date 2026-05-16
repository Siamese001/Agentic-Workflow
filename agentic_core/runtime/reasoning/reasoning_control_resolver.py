"""Resolver: transport observation + requirement levels -> execution receipt."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Mapping

from agentic_core.runtime.reasoning.reasoning_control_requirement import (
    AllowedSurface,
    DowngradeDisposition,
    ReasoningControlRequirement,
    ReceiptState,
    RequirementLevel,
)
from agentic_core.runtime.reasoning.reasoning_execution_plan import ReasoningExecutionPlan
from agentic_core.runtime.reasoning.reasoning_execution_receipt import (
    ControlLedgerEntry,
    ReasoningExecutionReceipt,
)
from agentic_core.runtime.reasoning.transport_capabilities import TransportCapabilities

_FORBIDDEN_TRANSPORT_SCRATCH_KEYS: frozenset[str] = frozenset({"scratchpad", "reveal_scratchpad"})


class ReasoningGovernanceError(Exception):
    """Raised when POLICY_REQUIRED controls fail or BLOCK disposition triggers."""


def canonical_plan_digest(requested_kw: Mapping[str, Any]) -> str:
    filtered = {k: requested_kw[k] for k in sorted(requested_kw)}
    canon = json.dumps(filtered, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def default_gateway_control_requirements(
    requested_kw: Mapping[str, Any],
) -> tuple[ReasoningControlRequirement, ...]:
    """Default semantics for Sovereign gateway single-shot generation."""

    rk = dict(requested_kw)
    out: list[ReasoningControlRequirement] = []

    if "temperature" in rk:
        out.append(
            ReasoningControlRequirement(
                control_name="temperature",
                requested=True,
                requirement_level=RequirementLevel.OPTIONAL,
                allowed_surfaces=frozenset({AllowedSurface.TRANSPORT}),
                fallback_allowed=True,
                downgrade_disposition=DowngradeDisposition.WARN,
                decisive_reason_when_not_applied="temperature_not_applied_observed_transport",
            ),
        )
    if "max_tokens" in rk:
        out.append(
            ReasoningControlRequirement(
                control_name="max_tokens",
                requested=True,
                requirement_level=RequirementLevel.REQUIRED,
                allowed_surfaces=frozenset({AllowedSurface.TRANSPORT}),
                fallback_allowed=False,
                downgrade_disposition=DowngradeDisposition.REVIEW,
                decisive_reason_when_not_applied="max_tokens_not_observed_on_transport_for_required_attempt",
            ),
        )

    def _num(val: Any) -> float | None:
        if isinstance(val, bool):  # noqa: SIM907
            return None
        if isinstance(val, (int, float)):
            return float(val)
        return None

    for orch_name in ("cot_paths", "tot_branches", "tot_depth"):
        vn = _num(rk.get(orch_name))
        active = vn is not None and vn > 0.0
        out.append(
            ReasoningControlRequirement(
                control_name=orch_name,
                requested=active,
                requirement_level=(RequirementLevel.QUALITY_REQUIRED if active else RequirementLevel.OPTIONAL),
                allowed_surfaces=frozenset({AllowedSurface.ORCHESTRATION}),
                fallback_allowed=False,
                downgrade_disposition=DowngradeDisposition.REVIEW,
                decisive_reason_when_not_applied=f"{orch_name}_requires_orchestration_runner_not_gateway_singleton",
            ),
        )

    n_ref = _num(rk.get("reflexion_loops"))
    active_ref = n_ref is not None and n_ref > 0.0
    out.append(
        ReasoningControlRequirement(
            control_name="reflexion_loops",
            requested=active_ref,
            requirement_level=(RequirementLevel.POLICY_REQUIRED if active_ref else RequirementLevel.OPTIONAL),
            allowed_surfaces=frozenset({AllowedSurface.ORCHESTRATION}),
            fallback_allowed=False,
            downgrade_disposition=DowngradeDisposition.BLOCK,
            decisive_reason_when_not_applied="reflexion_loop_not_executed_in_gateway_singleton_generate",
        ),
    )

    n_sc = _num(rk.get("self_consistency_samples"))
    active_sc = n_sc is not None and n_sc > 1.0 + 1e-12
    out.append(
        ReasoningControlRequirement(
            control_name="self_consistency_samples",
            requested=active_sc,
            requirement_level=(RequirementLevel.QUALITY_REQUIRED if active_sc else RequirementLevel.OPTIONAL),
            allowed_surfaces=frozenset({AllowedSurface.ORCHESTRATION}),
            fallback_allowed=False,
            downgrade_disposition=DowngradeDisposition.REVIEW,
            decisive_reason_when_not_applied="self_consistency_sampling_not_executed_in_gateway_singleton",
        ),
    )

    scratch_keys_requested = frozenset(rk.keys()) & _FORBIDDEN_TRANSPORT_SCRATCH_KEYS
    leak_guard_active = len(scratch_keys_requested) > 0
    out.append(
        ReasoningControlRequirement(
            control_name="scratchpad_transport_guard",
            requested=leak_guard_active,
            requirement_level=(
                RequirementLevel.POLICY_REQUIRED if leak_guard_active else RequirementLevel.OPTIONAL
            ),
            allowed_surfaces=frozenset({AllowedSurface.POLICY}),
            fallback_allowed=False,
            downgrade_disposition=DowngradeDisposition.BLOCK,
            decisive_reason_when_not_applied="scratchpad_keys_must_be_absent_observed_transport",
        ),
    )

    return tuple(out)


def build_execution_plan(requested_kw: Mapping[str, Any]) -> ReasoningExecutionPlan:
    rk = dict(requested_kw)
    return ReasoningExecutionPlan(
        plan_digest=canonical_plan_digest(rk),
        control_requirements=default_gateway_control_requirements(rk),
        requested_values=dict(rk),
    )


def resolve_gateway_receipt(
    plan: ReasoningExecutionPlan,
    capabilities: TransportCapabilities,
    observed_transport_payload: Mapping[str, Any] | None,
) -> ReasoningExecutionReceipt:
    fwd = capabilities.forwarded_kw_names
    obs_raw = observed_transport_payload or {}
    ledger_rows = [_classify(plan, fwd, dict(obs_raw), row) for row in plan.control_requirements]
    return _finalize_aggregate(tuple(ledger_rows))


def _finalize_aggregate(rows: tuple[ControlLedgerEntry, ...]) -> ReasoningExecutionReceipt:
    warn = False
    review = False
    qc_denied = False
    blocked = False

    for row in rows:
        if not row.requested:
            continue

        lvl = row.requirement_level
        state = row.receipt_state
        dd = row.downgrade_disposition

        qc_fail = lvl == RequirementLevel.QUALITY_REQUIRED and state != ReceiptState.APPLIED
        if qc_fail:
            qc_denied = True

        if lvl == RequirementLevel.POLICY_REQUIRED and state != ReceiptState.APPLIED:
            blocked = True

        violated = state in (
            ReceiptState.IGNORED,
            ReceiptState.UNSUPPORTED,
        ) or (
            lvl != RequirementLevel.OPTIONAL and state == ReceiptState.DEGRADED
        )

        if lvl == RequirementLevel.OPTIONAL and state == ReceiptState.DEGRADED:
            warn = True

        if lvl == RequirementLevel.OPTIONAL and state in (ReceiptState.UNSUPPORTED, ReceiptState.IGNORED):
            warn = True

        if lvl == RequirementLevel.REQUIRED and violated:
            if dd == DowngradeDisposition.BLOCK:
                blocked = True
            elif dd == DowngradeDisposition.REVIEW:
                review = True
            elif dd == DowngradeDisposition.WARN:
                warn = True

        if lvl == RequirementLevel.QUALITY_REQUIRED and violated:
            if dd == DowngradeDisposition.REVIEW:
                review = True
            elif dd == DowngradeDisposition.BLOCK:
                blocked = True

    return ReasoningExecutionReceipt(
        aggregate_warn=warn,
        aggregate_review=review,
        aggregate_blocked=blocked,
        quality_certification_denied=qc_denied,
        ledger=rows,
    )


def _float_ok(declared: Any, observed: Any) -> bool:
    try:
        return math.isclose(float(declared), float(observed), rel_tol=1e-5, abs_tol=1e-7)
    except (TypeError, ValueError):
        return declared == observed


def _transport_entry(
    req: ReasoningControlRequirement,
    fwd: frozenset[str],
    observed: Mapping[str, Any],
    requested_values: Mapping[str, Any],
) -> ControlLedgerEntry:
    name = req.control_name
    decisive = req.decisive_reason_when_not_applied

    if not req.requested:
        return ControlLedgerEntry(
            control_name=name,
            requested=False,
            requirement_level=req.requirement_level,
            receipt_state=ReceiptState.APPLIED,
            applied_layer=None,
            proved_reference="inactive",
            gap_notes="none",
            downgrade_disposition=req.downgrade_disposition,
            decisive_reason="",
        )

    if name not in fwd:
        return ControlLedgerEntry(
            control_name=name,
            requested=True,
            requirement_level=req.requirement_level,
            receipt_state=ReceiptState.IGNORED,
            applied_layer=None,
            proved_reference=json.dumps({"stripped_kw": name}),
            gap_notes="provider_did_not_forward_kw_to_transport",
            downgrade_disposition=req.downgrade_disposition,
            decisive_reason=decisive,
        )

    declared = requested_values.get(name)
    observed_val = observed.get(name)
    if observed_val is None:
        return ControlLedgerEntry(
            control_name=name,
            requested=True,
            requirement_level=req.requirement_level,
            receipt_state=ReceiptState.IGNORED,
            applied_layer=AllowedSurface.TRANSPORT,
            proved_reference=json.dumps({"declared_only": declared}),
            gap_notes="observed_transport_missing_key",
            downgrade_disposition=req.downgrade_disposition,
            decisive_reason=decisive,
        )

    ok = declared == observed_val if not isinstance(declared, float | int) else _float_ok(declared, observed_val)
    if ok:
        return ControlLedgerEntry(
            control_name=name,
            requested=True,
            requirement_level=req.requirement_level,
            receipt_state=ReceiptState.APPLIED,
            applied_layer=AllowedSurface.TRANSPORT,
            proved_reference=json.dumps({"transport_observed": {name: observed_val}}),
            gap_notes="none",
            downgrade_disposition=req.downgrade_disposition,
            decisive_reason="",
        )

    return ControlLedgerEntry(
        control_name=name,
        requested=True,
        requirement_level=req.requirement_level,
        receipt_state=ReceiptState.DEGRADED,
        applied_layer=AllowedSurface.TRANSPORT,
        proved_reference=json.dumps({"declared": declared, "observed": observed_val}),
        gap_notes="declared_transport_value_mismatch",
        downgrade_disposition=req.downgrade_disposition,
        decisive_reason=decisive,
    )


def _orchestration_entry(
    req: ReasoningControlRequirement,
    decisive: str,
    *,
    requested_values: Mapping[str, Any],
) -> ControlLedgerEntry:
    """Singleton HTTP/gateway slot — orch controls are ledgered (requested vs actually executed)."""

    def _num(val: Any) -> float | None:
        if isinstance(val, bool):
            return None
        if isinstance(val, (int, float)):
            return float(val)
        return None

    if not req.requested:
        return ControlLedgerEntry(
            control_name=req.control_name,
            requested=False,
            requirement_level=req.requirement_level,
            receipt_state=ReceiptState.APPLIED,
            applied_layer=AllowedSurface.ORCHESTRATION,
            proved_reference="inactive",
            gap_notes="none",
            downgrade_disposition=req.downgrade_disposition,
            decisive_reason="",
        )

    extra: dict[str, Any] = {
        "orch_runner_mode": "singleton_call_no_vote_or_branch_loop",
        "executed_observed": False,
    }
    vn = requested_values.get(req.control_name)

    if req.control_name == "self_consistency_samples":
        nv = _num(vn)
        target = int(nv) if nv is not None else 1
        extra["samples_requested"] = max(1, target)
        completed = min(1, extra["samples_requested"])
        extra["samples_completed"] = completed
    elif req.control_name == "reflexion_loops":
        nv = _num(vn)
        tgt = int(nv) if nv is not None else 0
        extra["loops_requested"] = max(0, tgt)
        extra["loops_completed"] = 0
    elif req.control_name in ("cot_paths", "tot_branches", "tot_depth"):
        nv = _num(vn)
        extra[f"{req.control_name}_requested"] = nv if nv is not None else 0.0

    return ControlLedgerEntry(
        control_name=req.control_name,
        requested=True,
        requirement_level=req.requirement_level,
        receipt_state=ReceiptState.IGNORED,
        applied_layer=None,
        proved_reference=json.dumps(extra),
        gap_notes="no_branch_vote_reflexion_loop_executed_observed",
        downgrade_disposition=req.downgrade_disposition,
        decisive_reason=decisive or req.decisive_reason_when_not_applied,
    )


def _scratch_guard_entry(req: ReasoningControlRequirement, observed_transport: Mapping[str, Any]) -> ControlLedgerEntry:
    leaks = sorted(_FORBIDDEN_TRANSPORT_SCRATCH_KEYS & observed_transport.keys())
    if not req.requested:
        return ControlLedgerEntry(
            control_name=req.control_name,
            requested=False,
            requirement_level=req.requirement_level,
            receipt_state=ReceiptState.APPLIED,
            applied_layer=AllowedSurface.POLICY,
            proved_reference=json.dumps({"scratchpad_transport": "inactive"}),
            gap_notes="none",
            downgrade_disposition=req.downgrade_disposition,
            decisive_reason="",
        )

    # Active policy: forbid scratchpad-bearing keys appearing on outbound transport observation.
    if leaks:
        return ControlLedgerEntry(
            control_name=req.control_name,
            requested=True,
            requirement_level=req.requirement_level,
            receipt_state=ReceiptState.UNSUPPORTED,
            applied_layer=None,
            proved_reference=json.dumps({"forbidden_scratch_keys_seen_on_transport_observation": leaks}),
            gap_notes="scratchpad_policy_violated_on_transport_proof",
            downgrade_disposition=req.downgrade_disposition,
            decisive_reason=req.decisive_reason_when_not_applied,
        )

    return ControlLedgerEntry(
        control_name=req.control_name,
        requested=True,
        requirement_level=req.requirement_level,
        receipt_state=ReceiptState.APPLIED,
        applied_layer=AllowedSurface.POLICY,
        proved_reference=json.dumps({"scratchpad_transport": "absent_from_transport_observation"}),
        gap_notes="none",
        downgrade_disposition=req.downgrade_disposition,
        decisive_reason="",
    )


def _classify(
    plan: ReasoningExecutionPlan,
    fwd: frozenset[str],
    observed_transport: Mapping[str, Any],
    req: ReasoningControlRequirement,
) -> ControlLedgerEntry:
    surfaces = req.allowed_surfaces
    if surfaces == frozenset({AllowedSurface.TRANSPORT}):
        return _transport_entry(req, fwd, observed_transport, plan.requested_values)
    if surfaces == frozenset({AllowedSurface.ORCHESTRATION}):
        return _orchestration_entry(req, "", requested_values=plan.requested_values)
    if surfaces == frozenset({AllowedSurface.POLICY}):
        return _scratch_guard_entry(req, observed_transport)
    gap = ",".join(sorted(s.value for s in surfaces))
    return ControlLedgerEntry(
        control_name=req.control_name,
        requested=req.requested,
        requirement_level=req.requirement_level,
        receipt_state=ReceiptState.UNSUPPORTED,
        applied_layer=None,
        proved_reference="surface_mix_unhandled",
        gap_notes=gap,
        downgrade_disposition=req.downgrade_disposition,
        decisive_reason=f"Unhandled allowed_surfaces combo: {gap}",
    )


def enforce_blocked(receipt: ReasoningExecutionReceipt) -> None:
    """Raise on aggregate BLOCK with a prioritized rationale."""
    if not receipt.aggregate_blocked:
        return
    policy_hits = sorted(
        e.control_name
        for e in receipt.ledger
        if e.requested
        and e.requirement_level == RequirementLevel.POLICY_REQUIRED
        and e.receipt_state != ReceiptState.APPLIED
    )
    if policy_hits:
        raise ReasoningGovernanceError("POLICY_BLOCKED:" + ",".join(policy_hits))

    decisive = next(
        (f"{e.control_name}:{e.receipt_state.value}" for e in receipt.ledger if e.decisive_reason),
        "reasoning_aggregate_blocked",
    )
    raise ReasoningGovernanceError(decisive)


def reasoning_quality_certification_allowed(receipt: ReasoningExecutionReceipt) -> bool:
    """X1D / quality certifications must consult this helper — QUALITY REQUIRED gaps deny full cert."""
    return not receipt.quality_certification_denied


__all__ = [
    "ReasoningGovernanceError",
    "build_execution_plan",
    "canonical_plan_digest",
    "default_gateway_control_requirements",
    "enforce_blocked",
    "reasoning_quality_certification_allowed",
    "resolve_gateway_receipt",
]

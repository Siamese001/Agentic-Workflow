"""C0.0 PRE-FLIGHT — grounding eligibility & safety gate.

Spec: docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md
      lines 141-180. Pure-data; no I/O.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from agentic_core.runtime.prove_requirements.otel_emitter import (
        RuntimeSpanEmitter,
    )

from dataclasses import dataclass
from enum import Enum

from .route_contract import C0Policy, L1PlanContract, RouteContract
from .verdicts import BlockedReason, SourceClass


# W3 c0-policy-rectification-f7b2a9: C0Policy construction (L0 authority)

def build_c0_policy(
    route: RouteContract,
    plan: L1PlanContract,
    *,
    decision_source: str = "L0_ROUTE_TOPOLOGY",
) -> C0Policy:
    """Freeze C0 policy into RouteContract — L0 is the authority.

    L0 consumes L1PlanContract.grounding_required (advisory) and selected
    route topology, then emits the authoritative C0Policy. Downstream
    layers (C0, PA) MUST NOT recompute or override.

    Args:
        route: The selected route (topology informs bypass modes).
        plan: L1 plan contract (advisory grounding_required).
        decision_source: Traceable source of decision.

    Returns:
        Frozen C0Policy with c0_mode, evidence_contract_required, etc.
    """
    route_id = route.route_id

    # Terminal cache routes: explicit bypass.
    if route_id.startswith("R1_"):
        return C0Policy(
            grounding_required=False,
            c0_mode="BYPASS_CACHE_RETURN",
            decision_source="CACHE_TERMINAL",
            evidence_contract_required=False,
            bypass_reason=f"Terminal cache route {route_id} skips C0 retrieval",
        )

    # Terminal fallback routes: explicit bypass.
    if route_id.startswith("R5_"):
        return C0Policy(
            grounding_required=False,
            c0_mode="BYPASS_FALLBACK",
            decision_source="FALLBACK_TERMINAL",
            evidence_contract_required=False,
            bypass_reason=f"Terminal fallback route {route_id} skips C0 retrieval",
        )

    # R4 with preloaded context: explicit bypass with context reference.
    if route_id.startswith("R4_") and not plan.grounding_required:
        return C0Policy(
            grounding_required=False,
            c0_mode="BYPASS_PRELOADED_CONTEXT",
            decision_source="PRELOADED_CONTEXT",
            evidence_contract_required=False,
            bypass_reason="R4_SINGLE_ACTION with preloaded context",
            preloaded_context_ref=route.route_replay_key or "r4_preloaded",
        )

    # R4 with grounding required: retrieval required.
    if route_id.startswith("R4_") and plan.grounding_required:
        return C0Policy(
            grounding_required=True,
            c0_mode="RETRIEVE_REQUIRED",
            decision_source="L1_PLAN_DERIVED",
            evidence_contract_required=True,
            support_target=route.support_target.value,
        )

    # R3 grounded routes: retrieval required (L1 or L0 derived).
    if route_id in ("R3_GROUNDED", "R3_SIMPLE_GROUNDED_READ", "R3R4_MANAGED_WORKFLOW"):
        return C0Policy(
            grounding_required=True,
            c0_mode="RETRIEVE_REQUIRED",
            decision_source="L0_ROUTE_TOPOLOGY" if not plan.grounding_required else "L1_PLAN_DERIVED",
            evidence_contract_required=True,
            support_target=route.support_target.value,
        )

    # Default: not required (conservative fallback).
    return C0Policy(
        grounding_required=False,
        c0_mode="NOT_REQUIRED",
        decision_source=decision_source,  # type: ignore[arg-type]
        evidence_contract_required=False,
        bypass_reason=f"Route {route_id} has no explicit C0 policy mapping",
    )


class EvidenceStandard(str, Enum):
    """Strictness derived from support_target + data_class. Spec line 162."""

    LOW = "low"
    STANDARD = "standard"
    HIGH = "high"
    STRICT = "strict"


@dataclass(frozen=True)
class C0PreflightStatus:
    """Spec lines 164-165 — preflight output contract."""

    eligible: bool
    blocked_reason: BlockedReason | None = None
    allowed_source_classes: tuple[SourceClass, ...] = ()
    evidence_standard: EvidenceStandard = EvidenceStandard.STANDARD
    budget_floor: int = 0
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.eligible and self.blocked_reason is not None:
            raise ValueError("eligible=True incompatible with blocked_reason")
        if not self.eligible and self.blocked_reason is None:
            raise ValueError("eligible=False requires a blocked_reason")
        if self.budget_floor < 0:
            raise ValueError("budget_floor must be non-negative")


_INSTRUCTION_TOKENS: frozenset[str] = frozenset({
    "ignore previous", "ignore the above", "disregard previous",
    "you are now", "system:", "###system",
    "execute the following", "run the following",
    "delete all", "exfiltrate", "you must comply",
})


def _looks_like_instruction(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return any(tok in lowered for tok in _INSTRUCTION_TOKENS)


def _derive_evidence_standard(route: RouteContract) -> EvidenceStandard:
    target = route.support_target.value
    if target == "POLICY_CLAUSE":
        return EvidenceStandard.STRICT
    if target in ("EXACT_QUOTE", "CODE_LOCATION", "INCIDENT_EVIDENCE", "CLAIM_CHECK"):
        return EvidenceStandard.HIGH
    if route.data_class in ("regulated", "phi", "pii"):
        return EvidenceStandard.STRICT
    if route.data_class in ("confidential", "restricted"):
        return EvidenceStandard.HIGH
    if target == "SOURCE_SUMMARY":
        return EvidenceStandard.STANDARD
    return EvidenceStandard.LOW


def _derive_budget_floor(route: RouteContract, std: EvidenceStandard) -> int:
    """Minimum tokens needed for at least one bounded retrieval pass."""
    base = max(256, route.max_token_context // 16)
    if std == EvidenceStandard.STRICT:
        return base * 4
    if std == EvidenceStandard.HIGH:
        return base * 2
    return base


def run_preflight(
    route: RouteContract,
    plan: L1PlanContract,
    *,
    emitter: "Optional[RuntimeSpanEmitter]" = None,
) -> C0PreflightStatus:
    """C0.0 entry point. Pure function; deterministic given inputs.

    Implements all CHECKS from spec lines 155-162:
    - grounding_required == true
    - RouteContract allows C0 retrieval (route_id permits grounded route)
    - user task is not trying to use retrieved content as instructions
    - source classes are approved for this tenant and route
    - no blocked data class is requested
    - budget is sufficient for at least one bounded retrieval pass
    - high-impact / sensitive support target gets stricter evidence standard

    W12 live wire-up: when ``emitter`` is provided, wraps the entire
    preflight check in a ``c0.0.preflight`` proof-OTEL span carrying the
    incoming ``route_id``. Default ``None`` keeps the historical behavior.

    W4 c0-policy-rectification-deferred-f7b2a9:
        OTEL span includes C0 policy provenance fields:
        - l1_grounding_required: L1 advisory signal
        - route_c0_mode: Frozen C0 mode from RouteContract
        - evidence_contract_required: Whether evidence required
        - c0_policy_decision_source: Who decided (L0_ROUTE_TOPOLOGY, etc.)
    """
    if emitter is None:
        return _run_preflight_impl(route, plan)

    # W4: Extract C0 policy fields for OTEL span
    c0_policy = route.c0_policy
    span_attrs = {
        "l1_grounding_required": bool(plan.grounding_required),
        "route_c0_mode": c0_policy.c0_mode if c0_policy else "NOT_SET",
        "evidence_contract_required": c0_policy.evidence_contract_required if c0_policy else False,
        "c0_policy_decision_source": c0_policy.decision_source if c0_policy else "UNKNOWN",
    }

    with emitter.span(
        "c0.0.preflight",
        reason_codes=["preflight_started"],
        route_id=route.route_id,
        **span_attrs,  # W4: C0 policy provenance fields
    ):
        return _run_preflight_impl(route, plan)


def _run_preflight_impl(
    route: RouteContract,
    plan: L1PlanContract,
) -> C0PreflightStatus:
    """W3 c0-policy-rectification-f7b2a9: C0 preflight obeys RouteContract.c0_policy.

    L0 has frozen the C0 policy; C0 performs only eligibility checks,
    not semantic need recomputation. No route-name prefix checks here.
    """
    # W3: C0 policy must be frozen by L0.
    if route.c0_policy is None:
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=BlockedReason.ROUTE_DISALLOWS_C0,
            notes=("RouteContract.c0_policy is None; L0 must freeze C0 policy",),
        )

    c0_policy = route.c0_policy

    # W3: Bypass modes — C0 does not run retrieval.
    bypass_modes = ("BYPASS_PRELOADED_CONTEXT", "BYPASS_CACHE_RETURN", "BYPASS_FALLBACK", "NOT_REQUIRED")
    if c0_policy.c0_mode in bypass_modes:
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=BlockedReason.GROUNDING_NOT_REQUIRED,
            notes=(
                f"c0_mode={c0_policy.c0_mode} (source={c0_policy.decision_source})",
                f"bypass_reason={c0_policy.bypass_reason or 'none'}",
            ),
        )

    # W3: Only RETRIEVE_REQUIRED proceeds to eligibility checks.
    if c0_policy.c0_mode != "RETRIEVE_REQUIRED":
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=BlockedReason.ROUTE_DISALLOWS_C0,
            notes=(f"Unknown c0_mode={c0_policy.c0_policy}",),
        )

    # W3: Evidence contract required check.
    if not c0_policy.evidence_contract_required:
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=BlockedReason.GROUNDING_NOT_REQUIRED,
            notes=("c0_policy.evidence_contract_required=False",),
        )

    # W3: C0-owned eligibility checks (ACL/source/budget/freshness/etc).
    # 2. Instruction-payload sniff on user task (G10 gate, spec line 158)
    if _looks_like_instruction(plan.user_task_text):
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=BlockedReason.INSTRUCTION_PAYLOAD,
            notes=("User task carries instruction-injection signals; G10 fails",),
        )

    # 3. Data class allowed?
    if not route.allows_data_class(route.data_class):
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=BlockedReason.DATA_CLASS_BLOCKED,
            notes=(f"data_class={route.data_class!r} not in allowed set",),
        )

    # 4. Source classes — derive allowed set from route
    if route.allowed_sources:
        allowed = tuple(s for s in route.allowed_sources if s not in route.disallowed_sources)
    else:
        allowed = tuple(s for s in SourceClass if s not in route.disallowed_sources)

    if not allowed:
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=BlockedReason.SOURCE_CLASS_FORBIDDEN,
            notes=("All source classes are disallowed for this route",),
        )

    # 5. Evidence standard + budget floor
    std = _derive_evidence_standard(route)
    floor = _derive_budget_floor(route, std)

    if route.token_budget < floor:
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=BlockedReason.BUDGET_INSUFFICIENT,
            notes=(f"token_budget={route.token_budget} < floor={floor} for std={std.value}",),
        )

    # 6. Tenant scope (must be set explicitly, not empty)
    if not route.tenant_scope.strip():
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=BlockedReason.TENANT_OUT_OF_SCOPE,
            notes=("tenant_scope is empty",),
        )

    return C0PreflightStatus(
        eligible=True,
        blocked_reason=None,
        allowed_source_classes=allowed,
        evidence_standard=std,
        budget_floor=floor,
        notes=(),
    )


__all__ = [
    "C0PreflightStatus",
    "EvidenceStandard",
    "build_c0_policy",  # W3: L0 C0 policy construction
    "run_preflight",
]

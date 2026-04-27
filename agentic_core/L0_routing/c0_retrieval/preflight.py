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

from .route_contract import L1PlanContract, RouteContract
from .verdicts import BlockedReason, SourceClass


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
    """
    if emitter is None:
        return _run_preflight_impl(route, plan)
    with emitter.span(
        "c0.0.preflight",
        reason_codes=["preflight_started"],
        route_id=route.route_id,
    ):
        return _run_preflight_impl(route, plan)


def _run_preflight_impl(
    route: RouteContract,
    plan: L1PlanContract,
) -> C0PreflightStatus:
    """Original C0.0 preflight implementation (W12 split)."""

    # 1. grounding_required gate
    if not route.grounding_required or not plan.grounding_required:
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=BlockedReason.GROUNDING_NOT_REQUIRED,
            notes=("RouteContract or L1PlanContract did not request grounding",),
        )

    # 2. Route allows C0 retrieval (R1/R5 cache/fallback paths skip C0)
    if route.route_id.startswith("R1_") or route.route_id.startswith("R5_"):
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=BlockedReason.ROUTE_DISALLOWS_C0,
            notes=(f"route_id={route.route_id!r} is a terminal cache/fallback path",),
        )

    # 3. Instruction-payload sniff on user task (G10 gate, spec line 158)
    if _looks_like_instruction(plan.user_task_text):
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=BlockedReason.INSTRUCTION_PAYLOAD,
            notes=("User task carries instruction-injection signals; G10 fails",),
        )

    # 4. Data class allowed?
    if not route.allows_data_class(route.data_class):
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=BlockedReason.DATA_CLASS_BLOCKED,
            notes=(f"data_class={route.data_class!r} not in allowed set",),
        )

    # 5. Source classes — derive allowed set from route
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

    # 6. Evidence standard + budget floor
    std = _derive_evidence_standard(route)
    floor = _derive_budget_floor(route, std)

    if route.token_budget < floor:
        return C0PreflightStatus(
            eligible=False,
            blocked_reason=BlockedReason.BUDGET_INSUFFICIENT,
            notes=(f"token_budget={route.token_budget} < floor={floor} for std={std.value}",),
        )

    # 7. Tenant scope (must be set explicitly, not empty)
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
    "run_preflight",
]

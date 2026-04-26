"""PA.4 Validate Slot Contract — 17-check validation matrix (spec lines 1066–1164).

Each check is a deterministic boolean function returning a structured
:class:`ValidationCheckResult`. The aggregate :class:`PA4ValidationReport`
exposes pass/fail counts plus a tuple of failed-check ids for telemetry and
PA.7 dispatch routing.

Spec checks implemented (organized by category):

CONTEXT-CONTRACT (5):
    1. evidence_status_consistent_with_plan
    2. unresolved_gaps_present_or_grounding_not_required
    3. contradictions_preserved_when_present
    4. support_score_meets_threshold
    5. citation_mode_respected

SCHEMA & TOOLS (4):
    6. r0_schema_parseable
    7. r0_can_represent_abstain
    8. r0_can_represent_citations
    9. tools_match_registry_and_token

AUTHORITY (3):
    10. no_user_attempts_to_override_system
    11. no_c0_attempts_to_override_system
    12. no_h0_overrides_d0_fences

REPLAY (3):
    13. policy_hash_consistent_across_inputs
    14. blueprint_hash_consistent
    15. replay_metadata_complete

GOVERNANCE (2):
    16. allowed_tool_posture_respected
    17. capability_token_present_when_tools_bound
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .input_contracts import UpstreamInputBundle
from .pa1_bom_resolver import PromptBOMResolved
from .pa2_slot_composition import AuthorityStack, detect_authority_violations


@dataclass(frozen=True)
class ValidationCheckResult:
    check_id: str
    category: str
    passed: bool
    detail: str = ""


@dataclass(frozen=True)
class PA4ValidationReport:
    checks: tuple[ValidationCheckResult, ...]
    passed_count: int
    failed_count: int
    failed_ids: tuple[str, ...]
    overall_passed: bool

    @classmethod
    def from_checks(cls, checks: Iterable[ValidationCheckResult]) -> PA4ValidationReport:
        items = tuple(checks)
        passed = sum(1 for c in items if c.passed)
        failed = len(items) - passed
        failed_ids = tuple(c.check_id for c in items if not c.passed)
        return cls(
            checks=items,
            passed_count=passed,
            failed_count=failed,
            failed_ids=failed_ids,
            overall_passed=failed == 0,
        )


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _ctx_evidence_status_consistent(bundle: UpstreamInputBundle) -> ValidationCheckResult:
    plan = bundle.plan
    ev = bundle.evidence
    if plan.grounding_required and ev.status in {"BLOCKED", "EMPTY"}:
        return ValidationCheckResult(
            "evidence_status_consistent_with_plan",
            "context",
            False,
            f"plan.grounding_required=True but evidence.status={ev.status}",
        )
    return ValidationCheckResult("evidence_status_consistent_with_plan", "context", True)


def _ctx_unresolved_gaps(bundle: UpstreamInputBundle) -> ValidationCheckResult:
    plan = bundle.plan
    ev = bundle.evidence
    if plan.grounding_required and ev.status == "PASS" and ev.unresolved_gaps:
        return ValidationCheckResult(
            "unresolved_gaps_present_or_grounding_not_required",
            "context",
            False,
            f"unresolved gaps remain on PASS evidence: {ev.unresolved_gaps}",
        )
    return ValidationCheckResult("unresolved_gaps_present_or_grounding_not_required", "context", True)


def _ctx_contradictions_preserved(
    bundle: UpstreamInputBundle, bom: PromptBOMResolved
) -> ValidationCheckResult:
    if bundle.evidence.contradiction_flags and not bom.c0.contradictions_preserved:
        return ValidationCheckResult(
            "contradictions_preserved_when_present",
            "context",
            False,
            "evidence has contradiction_flags but C0 did not preserve them",
        )
    return ValidationCheckResult("contradictions_preserved_when_present", "context", True)


def _ctx_support_score(bundle: UpstreamInputBundle, support_threshold: float) -> ValidationCheckResult:
    if bundle.plan.grounding_required and bundle.evidence.support_score < support_threshold:
        return ValidationCheckResult(
            "support_score_meets_threshold",
            "context",
            False,
            f"support_score={bundle.evidence.support_score} < {support_threshold}",
        )
    return ValidationCheckResult("support_score_meets_threshold", "context", True)


def _ctx_citation_mode(bundle: UpstreamInputBundle, bom: PromptBOMResolved) -> ValidationCheckResult:
    mode = (bundle.governance.citation_mode or "").lower()
    if mode == "required" and not bom.r0.can_represent_citations:
        return ValidationCheckResult(
            "citation_mode_respected",
            "context",
            False,
            "governance.citation_mode=required but R0 cannot represent citations",
        )
    return ValidationCheckResult("citation_mode_respected", "context", True)


def _schema_parseable(bom: PromptBOMResolved) -> ValidationCheckResult:
    if not bom.r0.parseable:
        return ValidationCheckResult(
            "r0_schema_parseable", "schema", False, bom.r0.reason or "schema unparseable"
        )
    return ValidationCheckResult("r0_schema_parseable", "schema", True)


def _schema_can_abstain(bom: PromptBOMResolved, support_target: str) -> ValidationCheckResult:
    if support_target.lower() in {"strict", "grounded"} and not bom.r0.can_represent_abstain:
        return ValidationCheckResult(
            "r0_can_represent_abstain",
            "schema",
            False,
            "support_target requires abstain field but schema lacks it",
        )
    return ValidationCheckResult("r0_can_represent_abstain", "schema", True)


def _schema_can_cite(bom: PromptBOMResolved, citation_required: bool) -> ValidationCheckResult:
    if citation_required and not bom.r0.can_represent_citations:
        return ValidationCheckResult(
            "r0_can_represent_citations", "schema", False, "schema lacks citation field"
        )
    return ValidationCheckResult("r0_can_represent_citations", "schema", True)


def _tools_match(bom: PromptBOMResolved) -> ValidationCheckResult:
    if not bom.tool_binding_manifest.valid:
        return ValidationCheckResult(
            "tools_match_registry_and_token",
            "tools",
            False,
            bom.tool_binding_manifest.reason or "tool binding invalid",
        )
    return ValidationCheckResult("tools_match_registry_and_token", "tools", True)


def _authority_user_no_override(stack: AuthorityStack) -> ValidationCheckResult:
    violations = detect_authority_violations(stack)
    user_v = [v for v in violations if v.startswith("U0_")]
    if user_v:
        return ValidationCheckResult(
            "no_user_attempts_to_override_system",
            "authority",
            False,
            "; ".join(user_v),
        )
    return ValidationCheckResult("no_user_attempts_to_override_system", "authority", True)


def _authority_c0_no_override(stack: AuthorityStack) -> ValidationCheckResult:
    violations = detect_authority_violations(stack)
    c0_v = [v for v in violations if v.startswith("C0_")]
    if c0_v:
        return ValidationCheckResult("no_c0_attempts_to_override_system", "authority", False, "; ".join(c0_v))
    return ValidationCheckResult("no_c0_attempts_to_override_system", "authority", True)


def _authority_h0_no_fence_override(stack: AuthorityStack, bom: PromptBOMResolved) -> ValidationCheckResult:
    h0 = stack.slot("H0")
    d0 = stack.slot("D0")
    if h0 and d0:
        h0_lower = h0.content.lower()
        for fence in bom.d0.fences_applied:
            if fence and fence.lower().startswith("must not") and fence.lower() in h0_lower:
                continue  # H0 quoting fence is fine
            if "ignore developer fences" in h0_lower or "override fences" in h0_lower:
                return ValidationCheckResult(
                    "no_h0_overrides_d0_fences",
                    "authority",
                    False,
                    "H0 attempts to override D0 fences",
                )
    return ValidationCheckResult("no_h0_overrides_d0_fences", "authority", True)


def _replay_policy_hash(bundle: UpstreamInputBundle) -> ValidationCheckResult:
    hashes = {
        bundle.plan.policy_hash,
        bundle.route.policy_hash,
        bundle.governance.policy_hash,
        bundle.execution.policy_hash,
    } - {""}
    if len(hashes) > 1:
        return ValidationCheckResult(
            "policy_hash_consistent_across_inputs",
            "replay",
            False,
            f"distinct policy hashes: {sorted(hashes)}",
        )
    return ValidationCheckResult("policy_hash_consistent_across_inputs", "replay", True)


def _replay_blueprint_hash(bom: PromptBOMResolved) -> ValidationCheckResult:
    if not bom.execution_metadata.hashes_consistent:
        return ValidationCheckResult(
            "blueprint_hash_consistent",
            "replay",
            False,
            bom.execution_metadata.reason or "blueprint hash inconsistent",
        )
    return ValidationCheckResult("blueprint_hash_consistent", "replay", True)


def _replay_metadata_complete(bom: PromptBOMResolved) -> ValidationCheckResult:
    em = bom.execution_metadata
    missing = []
    if not em.replay_key:
        missing.append("replay_key")
    if not em.policy_hash:
        missing.append("policy_hash")
    if not em.plan_id:
        missing.append("plan_id")
    if not em.route_id:
        missing.append("route_id")
    if missing:
        return ValidationCheckResult(
            "replay_metadata_complete",
            "replay",
            False,
            f"missing: {','.join(missing)}",
        )
    return ValidationCheckResult("replay_metadata_complete", "replay", True)


def _gov_tool_posture(bundle: UpstreamInputBundle, bom: PromptBOMResolved) -> ValidationCheckResult:
    posture = (bundle.governance.allowed_tool_posture or "").lower()
    has_tools = bool(bom.tool_binding_manifest.tools)
    if posture in {"none", ""} and has_tools:
        return ValidationCheckResult(
            "allowed_tool_posture_respected",
            "governance",
            False,
            "governance forbids tools but tools were bound",
        )
    return ValidationCheckResult("allowed_tool_posture_respected", "governance", True)


def _gov_capability_token(bom: PromptBOMResolved) -> ValidationCheckResult:
    if bom.tool_binding_manifest.tools and not bom.tool_binding_manifest.capability_token:
        return ValidationCheckResult(
            "capability_token_present_when_tools_bound",
            "governance",
            False,
            "tools bound but capability_token missing",
        )
    return ValidationCheckResult("capability_token_present_when_tools_bound", "governance", True)


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------


def validate_pa4(
    *,
    bundle: UpstreamInputBundle,
    bom: PromptBOMResolved,
    stack: AuthorityStack,
    support_threshold: float = 0.6,
    citation_required: bool | None = None,
) -> PA4ValidationReport:
    """Run all 17 checks. ``citation_required`` defaults to whether the
    governance citation_mode is 'required'."""
    cit_req = (
        citation_required
        if citation_required is not None
        else (bundle.governance.citation_mode or "").lower() == "required"
    )
    checks: list[ValidationCheckResult] = [
        _ctx_evidence_status_consistent(bundle),
        _ctx_unresolved_gaps(bundle),
        _ctx_contradictions_preserved(bundle, bom),
        _ctx_support_score(bundle, support_threshold),
        _ctx_citation_mode(bundle, bom),
        _schema_parseable(bom),
        _schema_can_abstain(bom, bundle.route.support_target),
        _schema_can_cite(bom, cit_req),
        _tools_match(bom),
        _authority_user_no_override(stack),
        _authority_c0_no_override(stack),
        _authority_h0_no_fence_override(stack, bom),
        _replay_policy_hash(bundle),
        _replay_blueprint_hash(bom),
        _replay_metadata_complete(bom),
        _gov_tool_posture(bundle, bom),
        _gov_capability_token(bom),
    ]
    return PA4ValidationReport.from_checks(checks)


__all__ = [
    "PA4ValidationReport",
    "ValidationCheckResult",
    "validate_pa4",
]

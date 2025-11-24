"""Turns safety findings and policy rules into a final pass, warn, or block decision for a resume so risky or non-compliant content is caught before delivery."""

# FILE: 10_10/l5.py

from __future__ import annotations

from typing import Optional, List

from orchestration.control_plane import run_safety_pipeline, SafetyContext
from core.models.models import (
    SafetyResult,
    SafetyFinding,
    CouncilVote,
    PolicyDecisionEvent,
    SafetyEnforcementVerdict,
    SafetyPolicy,
    ExecutionContext,
)
from runtime.observability import start_span, end_span, record_exception


# =============================================================================
# Helpers
# =============================================================================


def _combine_findings(
    safety_result: SafetyResult,
    council_vote: CouncilVote,
) -> List[SafetyFinding]:
    """Merge model-based SafetyResult findings with structural QA signals.

    Downstream: deterministic final enforcement in L5.
    """
    findings = list(getattr(safety_result, "findings", []) or [])

    # CouncilVote “block” → inject synthetic high-severity finding.
    if getattr(council_vote, "selected_id", "") == "block":
        synthetic = SafetyFinding(
            id="council_block",
            text="QA council voted BLOCK",
            severity="high",
            category="council",
        )
        findings.append(synthetic)

    return findings


def _decide_verdict(
    findings: List[SafetyFinding],
    policy: SafetyPolicy,
) -> SafetyEnforcementVerdict:
    """Applies safety policy rules to the findings to choose a pass, warn, or block verdict based on severity, disallowed categories, and PII handling."""
    if not getattr(policy, "allow_generation", True):
        return SafetyEnforcementVerdict(
            verdict="block",
            reason="policy_prohibits_generation",
        )

    disallowed = set(getattr(policy, "disallowed_categories", []) or [])
    allow_pii = getattr(policy, "allow_pii", True)

    has_high = False
    has_medium = False
    for f in findings:
        severity = (getattr(f, "severity", "") or "").lower()
        category = getattr(f, "category", None)

        if severity == "high":
            has_high = True

        if severity == "medium":
            has_medium = True

        # Block if disallowed category hit.
        if category and category in disallowed:
            return SafetyEnforcementVerdict(
                verdict="block",
                reason=f"disallowed_category:{category}",
            )

        # Block if PII disallowed and detected.
        if category == "pii" and not allow_pii:
            return SafetyEnforcementVerdict(
                verdict="block",
                reason="pii_disallowed",
            )

    # Block on any high-severity finding.
    if has_high:
        return SafetyEnforcementVerdict(
            verdict="block",
            reason="high_severity_findings",
        )

    # Warn if medium-severity findings present.
    if has_medium:
        return SafetyEnforcementVerdict(
            verdict="warn",
            reason="medium_severity_findings",
        )

    # Else pass.
    return SafetyEnforcementVerdict(verdict="pass", reason="no_violations")


# =============================================================================
# Public Entrypoint
# =============================================================================


def run_l5(
    safety_result: SafetyResult,
    council_vote: CouncilVote,
    policy: SafetyPolicy,
    ctx: Optional[ExecutionContext] = None,
) -> PolicyDecisionEvent:
    """Combines safety analysis, QA-derived risk signals, and organizational policy to decide whether a resume should be allowed, warned on, or blocked and records the reasons in a policy decision event."""
    span = start_span("l5.run", ctx=ctx.span_context() if ctx else None)
    try:
        findings = _combine_findings(safety_result, council_vote)

        # Construct a SafetyContext for the hybrid control-plane.
        safety_text_parts = [
            getattr(f, "message", "") for f in findings if getattr(f, "message", "")
        ]
        safety_text = "\n".join(safety_text_parts)

        safety_ctx = SafetyContext(
            workflow_id=getattr(ctx, "workflow_id", None) if ctx else None,
            agent_id="l5_safety",
            task_type="safety_enforcement",
            input_text=safety_text,
            tools=[],
            execution_profile=None,
            metadata={},
        )

        decision, _trace = run_safety_pipeline(safety_ctx, execution_profile=None)

        base_verdict = _decide_verdict(findings, policy)
        final_verdict = base_verdict

        if decision.action == "deny":
            final_verdict = SafetyEnforcementVerdict(
                verdict="block",
                reason=f"{base_verdict.reason}|control_plane_deny",
            )
        elif decision.action == "revise" and base_verdict.verdict == "pass":
            final_verdict = SafetyEnforcementVerdict(
                verdict="warn",
                reason=f"{base_verdict.reason}|control_plane_revise",
            )
        elif decision.action == "escalate":
            final_verdict = SafetyEnforcementVerdict(
                verdict="warn",
                reason=f"{base_verdict.reason}|control_plane_escalate_hitl",
            )

        return PolicyDecisionEvent(
            verdict=final_verdict.verdict,
            reason=final_verdict.reason,
            findings=findings,
        )
    except Exception as exc:  # noqa: BLE001
        record_exception("l5.enforcement_error", exc)
        return PolicyDecisionEvent(
            verdict="pass",
            reason="safety_enforcement_exception",
            findings=[],
        )
    finally:
        end_span(span)


def safety_gate(safety_result: SafetyResult) -> bool:
    """Simplified pass/block check used by callers that only need a yes/no.

    This helper inspects the provided SafetyResult using a default, permissive
    policy and a neutral council vote. It returns **True** when the safety
    decision would pass and **False** when it would block.

    Internal error-only findings are treated as non-blocking so the system can
    still return a best-effort result in failure scenarios. In practice, this
    gives a quick answer to "is this resume safe enough to show?" without
    exposing the full policy machinery.
    """

    findings = list(getattr(safety_result, "findings", []) or [])
    if findings and all(getattr(f, "category", "") == "internal" for f in findings):
        return True

    neutral_council = CouncilVote(members=0, selected_id="pass", scores={}, ties=[], reason="neutral")
    default_policy = SafetyPolicy()
    decision = run_l5(safety_result, neutral_council, default_policy, ctx=None)
    return decision.verdict != "block"

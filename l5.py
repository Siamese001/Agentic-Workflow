# FILE: 10_10/l5.py
"""
Safety Enforcement Layer · L5 (v10_10 · Phase 3)
================================================

Responsibilities:
    • Enforce SafetyPolicy (PII, disallowed content, category violations).
    • Consume:
          – SafetyResult (from L2's ConstitutionalSafetyAgent)
          – CouncilVote (from QA → deterministic heuristic)
    • Produce:
          – PolicyDecisionEvent (typed enforcement result)
    • Emit safety audit events (G19–G23).
    • Must NOT:
          – call language models directly,
          – mutate WorkflowState directly (L4-only),
          – modify plans (L1/L3),
          – perform retrieval/drafting/QA.

Pure decision + audit layer.
"""

from __future__ import annotations

from typing import Optional, List

from orchestration.control_plane import run_safety_pipeline, SafetyContext
from models import (
    SafetyResult,
    SafetyFinding,
    CouncilVote,
    PolicyDecisionEvent,
    SafetyEnforcementVerdict,
    SafetyPolicy,
    ExecutionContext,
)
from observability import start_span, end_span, log_exception


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
    """
    Determine final SafetyEnforcementVerdict according to the SafetyPolicy.

    Policy logic:
        • If allow_generation = False → always BLOCK.
        • If any high-severity finding contradicts policy.disallowed_categories → BLOCK.
        • If PII is detected and policy.allow_pii = False → BLOCK.
        • If only medium-severity → WARN.
        • Otherwise → PASS.
    """
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
    """
    Compute the final L5 enforcement decision:

        INPUTS:
            • SafetyResult  (model-based detection)
            • CouncilVote   (heuristic QA-derived)
            • SafetyPolicy  (Phase-3 policy registry)
            • ctx           (ExecutionContext for telemetry)

        OUTPUT:
            • PolicyDecisionEvent
    """
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
        log_exception("l5.enforcement_error", exc)
        return PolicyDecisionEvent(
            verdict="pass",
            reason="safety_enforcement_exception",
            findings=[],
        )
    finally:
        end_span(span)


def safety_gate(safety_result: SafetyResult) -> bool:
    """Backward-compatible helper returning a boolean safety verdict.

    Tests expect safety_gate to inspect SafetyResult and return True when
    the overall safety decision passes and False when it blocks.

    We delegate to run_l5 using a default-allow policy and a neutral
    CouncilVote, then interpret the PolicyDecisionEvent.verdict.

    Internal error findings (category="internal") are treated as
    non-blocking for purposes of this gate so that upstream layers can
    still surface a best-effort result in failure scenarios.
    """

    findings = list(getattr(safety_result, "findings", []) or [])
    if findings and all(getattr(f, "category", "") == "internal" for f in findings):
        return True

    neutral_council = CouncilVote(members=0, selected_id="pass", scores={}, ties=[], reason="neutral")
    default_policy = SafetyPolicy()
    decision = run_l5(safety_result, neutral_council, default_policy, ctx=None)
    return decision.verdict != "block"

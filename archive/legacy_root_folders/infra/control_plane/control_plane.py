"""
Control plane orchestration for résumé processing safety pipeline.

Coordinates rule evaluation and safety decisions for comprehensive résumé improvement workflows.
"""

from typing import Tuple

from .decisions import JudgeVerdict, SafetyPipelineTrace, RulesEngineResult
from .judge_engine import evaluate_with_guard_model
from .models import PolicyDecision, SafetyContext
from .routing import resolve_rules_for_context
from .rules_engine import evaluate_rules


def run_safety_pipeline(
    context: SafetyContext,
    execution_profile: object | None = None,
) -> Tuple[PolicyDecision, SafetyPipelineTrace]:
    """
    Executes complete safety pipeline for résumé processing workflows.

    Ensures comprehensive safety validation for résumé enhancement operations.
    """

    # Step 1: resolve rules for this agent / task.
    rules = resolve_rules_for_context(context)

    # Step 2: deterministic rules engine.
    rules_result: RulesEngineResult = evaluate_rules(context, rules)

    # Step 3: guard-style judge over the rules output.
    judge_verdict: JudgeVerdict = evaluate_with_guard_model(context, rules_result)

    # Step 4: merge into a final PolicyDecision.
    if judge_verdict.verdict == "unsafe":
        action = "deny"
    elif judge_verdict.verdict == "ambiguous":
        # In ambiguous cases, prefer a revision path that allows
        # upstream layers to sanitize content instead of hard-blocking.
        action = "revise"
    else:
        action = "allow"

    decision = PolicyDecision(
        action=action,
        verdict=judge_verdict.verdict,
        reason=judge_verdict.explanation,
        rule_ids=[m.rule_id for m in rules_result.matches],
        max_severity=rules_result.max_severity,
        details={
            "has_pii": rules_result.has_pii,
            "match_count": len(rules_result.matches),
        },
    )

    trace = SafetyPipelineTrace(
        rules_engine={
            "matches": [m.dict() for m in rules_result.matches],
            "max_severity": rules_result.max_severity,
            "has_pii": rules_result.has_pii,
            "match_count": len(rules_result.matches),
        },
        judge={
            "verdict": judge_verdict.verdict,
            "signals": judge_verdict.signals,
        },
    )

    return decision, trace




from __future__ import annotations

from typing import Any, Dict

from .decisions import JudgeVerdict, RulesEngineResult
from .models import SafetyContext


def evaluate_with_guard_model(
    context: SafetyContext,
    rules_result: RulesEngineResult,
) -> JudgeVerdict:
    """Deterministic guard-model style evaluation.

    Initial implementation is deliberately simple and makes no LLM calls.
    It interprets the rule matches plus lightweight context to decide
    whether the situation is safe, unsafe, or ambiguous.
    """

    signals: Dict[str, Any] = {
        "max_severity": rules_result.max_severity,
        "match_count": len(rules_result.matches),
        "has_pii": rules_result.has_pii,
    }

    max_sev = (rules_result.max_severity or "").lower()

    if max_sev == "high":
        return JudgeVerdict(
            verdict="unsafe",
            explanation="High-severity safety rules matched in deterministic guard.",
            signals=signals,
        )

    if max_sev == "medium" or rules_result.has_pii:
        return JudgeVerdict(
            verdict="ambiguous",
            explanation="Medium-severity or PII-related signals detected; recommend revision.",
            signals=signals,
        )

    return JudgeVerdict(
        verdict="safe",
        explanation="No significant safety rule matches detected.",
        signals=signals,
    )

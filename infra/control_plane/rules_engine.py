from __future__ import annotations

import re
from typing import List

from .decisions import RuleMatch, RulesEngineResult, aggregate_severity
from .models import PolicyRule, SafetyContext


_PII_REGEXES = [
    # Email addresses
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", re.IGNORECASE),
    # Simple phone number patterns (international and local)
    re.compile(r"(?:(?:\+?\d{1,3})?[\s-]?)?(?:\d{3}[\s-]?\d{3}[\s-]?\d{4})"),
]


def _detect_pii(text: str) -> bool:
    for rx in _PII_REGEXES:
        if rx.search(text):
            return True
    return False


def evaluate_rules(context: SafetyContext, rules: List[PolicyRule]) -> RulesEngineResult:
    """Deterministic evaluation of policy rules against a SafetyContext.

    This function is pure and does not call out to any external systems.
    """

    matches: List[RuleMatch] = []
    text = context.input_text or ""

    # Built-in PII signal (even if no explicit PII rule is configured).
    has_pii_builtin = _detect_pii(text)

    for rule in rules:
        if not rule.enabled:
            continue

        hit = False
        details = {}

        # Text pattern matching.
        if rule.pattern:
            rx = re.compile(rule.pattern, re.IGNORECASE | re.MULTILINE)
            m = rx.search(text)
            if m:
                hit = True
                snippet = m.group(0)
                details["matched_snippet"] = snippet[:128]

        # Tool-based matching.
        if rule.tool_name and rule.tool_name in (context.tools or []):
            hit = True
            details["tool"] = rule.tool_name

        if not hit:
            continue

        matches.append(
            RuleMatch(
                rule_id=rule.id,
                category=rule.category,
                severity=rule.severity,
                is_pii=rule.is_pii_rule,
                details=details,
            )
        )

    all_severities = [m.severity for m in matches]
    max_sev = aggregate_severity(all_severities)

    has_pii = has_pii_builtin or any(m.is_pii for m in matches)

    return RulesEngineResult(matches=matches, max_severity=max_sev, has_pii=has_pii)




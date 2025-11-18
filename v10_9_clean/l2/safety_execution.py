# FILE: v10_9_clean/l2/safety_execution.py
"""
L2 — Safety Execution (v10_9)

Executes safety checks defined by an L1 Safety plan.

Consumes:
    • plan.steps[0]["rules"]       → list of rule names
    • plan.steps[0]["sensitivity"] → "low" | "normal" | "high"
    • plan.steps[0]["audience"]    → audience string (e.g., "general", "children")

Produces:
    • ExecutionResult with payload:
        {
            "safety_report": {
                "issues": [...],
                "passed": bool,
                "sensitivity": str,
                "audience": str,
            },
            "sanitized_content": str,
        }

This is a deterministic, local safety executor: no external calls.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

from shared.models import ExecutionResult, PlanObject
from shared.exceptions import ToolExecutionError


_PII_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PII_PHONE = re.compile(r"\b(?:\+?1[ -]?)?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}\b")


def _sanitize_pii(text: str) -> str:
    text = _PII_EMAIL.sub("[EMAIL_REDACTED]", text)
    text = _PII_PHONE.sub("[PHONE_REDACTED]", text)
    return text


def _scan_forbidden(text: str) -> List[str]:
    issues: List[str] = []
    lc = text.lower()

    # Basic “prompt injection / override” style snippets
    if "ignore previous instructions" in lc:
        issues.append("prompt_injection_pattern")

    # Basic unsafe patterns
    forbidden_terms = ["violence", "adult", "explicit"]
    for term in forbidden_terms:
        if term in lc:
            issues.append(f"unsafe_term:{term}")

    return issues


def _scan_bias(text: str) -> List[str]:
    lc = text.lower()
    patterns = []
    for p in ["he/she", "his/her", "young", "old"]:
        if p in lc:
            patterns.append(f"bias_pattern:{p}")
    return patterns


def _collect_content(state: Dict[str, Any]) -> str:
    parts: List[str] = []

    draft_res = state.get("draft_result", {})
    if isinstance(draft_res, dict):
        draft = draft_res.get("draft")
        if isinstance(draft, list):
            parts.extend(str(x) for x in draft)
        elif isinstance(draft, str):
            parts.append(draft)

    bullets = state.get("bullet_result", {}).get("bullets")
    if isinstance(bullets, list):
        parts.extend(str(b) for b in bullets)

    job = state.get("job", {})
    jd = job.get("job_description") or job.get("raw_jd")
    if jd:
        parts.append(str(jd))

    return "\n".join(parts)


async def execute_safety(plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
    try:
        if not plan.steps:
            raise ValueError("Safety plan missing steps")

        step = plan.steps[0]
        rules: List[str] = step.get("rules") or []
        sensitivity: str = step.get("sensitivity") or "normal"
        audience: str = step.get("audience") or "general"

        content = _collect_content(state)
        sanitized = _sanitize_pii(content)

        issues: List[str] = []

        if "pii_redaction" in rules:
            # compare before/after
            if sanitized != content:
                issues.append("pii_redacted")

        if "forbidden_content_scan" in rules:
            issues.extend(_scan_forbidden(content))

        if "bias_scan" in rules:
            issues.extend(_scan_bias(content))

        if "toxicity_scan" in rules:
            # deterministic stub: toxicity if too many exclamation marks
            if content.count("!") > 5:
                issues.append("high_exclamation_density")

        # audience-specific rule
        if "child_protection_rules" in rules and audience.lower() == "children":
            child_terms = ["violence", "adult", "explicit"]
            if any(t in content.lower() for t in child_terms):
                issues.append("child_protection_violation")

        unique_issues = sorted(set(issues))
        passed = len(unique_issues) == 0

        safety_report = {
            "issues": unique_issues,
            "passed": passed,
            "sensitivity": sensitivity,
            "audience": audience,
        }

        payload = {
            "safety_report": safety_report,
            "sanitized_content": sanitized,
        }

        return ExecutionResult(
            status=ExecutionResult.__fields__["status"].type_.SUCCESS,
            payload=payload,
            model="safety-exec-v10_9",
            usage={},
        )

    except Exception as exc:
        raise ToolExecutionError(f"Safety execution failed: {exc}") from exc

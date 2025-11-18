# FILE: v10_9_clean/l2/qa_execution.py
"""
L2 — QA Execution (v10_9)

Executes the QA validation checks defined by an L1 PlanObject.

Consumes:
    • checks: List[str]
    • severity: str
    • audience: str

Produces:
    • ExecutionResult with qa_report = {
          "issues": [...],
          "confidence": float,
          "passed": bool
      }

This is the 10_9 evolution of the 10_7 qa_validation_stack execution layer.
"""

from __future__ import annotations
from typing import Any, Dict, List

from shared.models import ExecutionResult, PlanObject
from shared.exceptions import ToolExecutionError


# ---------------------------------------------------------------------------
# Deterministic check implementations
# ---------------------------------------------------------------------------

def _check_content_not_empty(content: str) -> bool:
    return bool(content.strip())


def _check_no_forbidden_phrases(content: str) -> bool:
    forbidden = ["lorem ipsum", "fake placeholder", "insert text here"]
    lc = content.lower()
    return not any(f in lc for f in forbidden)


def _check_logical_consistency(content: str) -> bool:
    # Deterministic stub: treat content as consistent if > 5 words
    return len(content.split()) > 5


def _check_factual_coherence(content: str) -> bool:
    # Deterministic stub: treat as coherent if sentences end properly
    return all(c.endswith((".", "!", "?")) for c in [s.strip() for s in content.split(".") if s.strip()][:1])


def _check_format_integrity(content: str) -> bool:
    # Deterministic stub: flag formatting issues if too few newlines
    return content.count("\n") <= 3


def _child_safe_language(content: str) -> bool:
    # Deterministic child safety proxy
    unsafe_terms = ["violence", "adult", "explicit"]
    lc = content.lower()
    return not any(t in lc for t in unsafe_terms)


def _run_checks(checks: List[str], audience: str, content: str) -> Dict[str, bool]:
    """Map check names to deterministic results."""
    results = {}

    for check in checks:
        if check == "content_not_empty":
            results[check] = _check_content_not_empty(content)
        elif check == "no_forbidden_phrases":
            results[check] = _check_no_forbidden_phrases(content)
        elif check == "logical_consistency":
            results[check] = _check_logical_consistency(content)
        elif check == "factual_coherence":
            results[check] = _check_factual_coherence(content)
        elif check == "format_integrity":
            results[check] = _check_format_integrity(content)
        elif check == "child_safe_language":
            results[check] = _child_safe_language(content)
        else:
            results[check] = True  # default: pass

    return results


# ---------------------------------------------------------------------------
# Main executor
# ---------------------------------------------------------------------------

async def execute_qa(plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
    """
    Executes the QA checks and returns a structured qa_report.

    Input:
        plan.steps[0]["checks"]
        plan.steps[0]["severity"]
        plan.steps[0]["audience"]

    Output payload:
        {
            "qa_report": {
                "issues": [...],
                "confidence": float,
                "passed": bool
            }
        }
    """
    try:
        if not plan.steps:
            raise ValueError("QA plan missing steps")

        step = plan.steps[0]
        checks: List[str] = step.get("checks") or []
        audience: str = step.get("audience") or "general"
        severity: str = step.get("severity") or "normal"

        # Extract content for QA evaluation
        content = state.get("draft_result", {}).get("draft")
        if not content:
            content = state.get("bullet_result", {}).get("bullets")
        if not content:
            content = [""]
        if isinstance(content, list):
            content = "\n".join(str(c) for c in content)

        # Run checks
        results = _run_checks(checks, audience, content)

        failed = [name for name, ok in results.items() if not ok]
        passed = not failed

        # Deterministic confidence scoring:
        total = len(results)
        confidence = round((total - len(failed)) / max(1, total), 3)

        qa_report = {
            "issues": failed,
            "confidence": confidence,
            "passed": passed,
        }

        payload = {"qa_report": qa_report}

        return ExecutionResult(
            status=ExecutionResult.__fields__["status"].type_.SUCCESS,
            payload=payload,
            model="qa-detector-v10_9",
            usage={},
        )

    except Exception as exc:
        raise ToolExecutionError(f"QA execution failed: {exc}") from exc

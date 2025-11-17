"""Self-correction module consolidating correction engines and journals."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List


class SelfCorrectionSurface(str, Enum):
    RAG_RETRY = "rag_retry"
    DRAFT_RETRY = "draft_retry"
    QA_RECHECK = "qa_recheck"
    STRATEGY_REPLAN = "strategy_replan"


def all_surfaces() -> Dict[str, str]:
    return {s.name: s.value for s in SelfCorrectionSurface}


def should_retry(surface: SelfCorrectionSurface, state: Dict[str, Any], last_result: Dict[str, Any]) -> bool:
    """
    Deterministic stub to indicate whether a local retry is warranted.

    For v10.8, logic must be simple:
      - If surface is QA_RECHECK and last_result contains "qa_report"
        with any finding.status == "pending" → return True.
      - Else return False.
    """
    if surface == SelfCorrectionSurface.QA_RECHECK:
        report = last_result.get("qa_report", {})
        findings = report.get("findings", [])
        for f in findings:
            if f.get("status") == "pending":
                return True
    return False


def evaluate_correction(
    surface: SelfCorrectionSurface, state: Dict[str, Any], last_patch: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Deterministic metadata-only correction recommendation generator.
    """
    needs_retry = bool(should_retry(surface, state, last_patch))

    rec = {
        "surface": surface.value,
        "needs_retry": needs_retry,
        "needs_replan": False,
        "reason": "default_accept",
    }

    if surface == SelfCorrectionSurface.QA_RECHECK:
        rec["reason"] = "qa_pending" if needs_retry else "qa_stable"

    elif surface in (SelfCorrectionSurface.RAG_RETRY, SelfCorrectionSurface.DRAFT_RETRY):
        rec["needs_retry"] = True
        rec["reason"] = "local_retry_suggested"

    elif surface == SelfCorrectionSurface.STRATEGY_REPLAN:
        if not state.get("messages"):
            rec["needs_replan"] = True
            rec["reason"] = "no_messages_replan"
        else:
            rec["reason"] = "strategy_stable"

    return rec


CORRECTION_JOURNAL: List[Dict[str, Any]] = []


def record_correction_event(surface: str, recommendation: Dict[str, Any], plan: Dict[str, Any]) -> None:
    CORRECTION_JOURNAL.append(
        {
            "surface": surface,
            "recommendation": recommendation,
            "plan_objective": plan.get("objective"),
            "mode": plan.get("mode"),
        }
    )

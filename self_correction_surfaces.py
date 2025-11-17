from enum import Enum
from typing import Dict, Any


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

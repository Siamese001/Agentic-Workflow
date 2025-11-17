"""Self-correction module consolidating correction engines and journals."""

from __future__ import annotations
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
from typing import Dict, Any



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
from typing import Any, Dict

CORRECTION_JOURNAL = []


def record_correction_event(surface: str, recommendation: Dict[str, Any], plan: Dict[str, Any]):
    CORRECTION_JOURNAL.append(
        {
            "surface": surface,
            "recommendation": recommendation,
            "plan_objective": plan.get("objective"),
            "mode": plan.get("mode"),
        }
    )
from typing import Dict, Any


class ArbitrationEngine:
    """
    Deterministic stub arbitration engine.

    evaluate(state, qa_report, safety_patch) -> Dict[str,str]
    returns one of: accept, retry, replan, escalate
    """

    def evaluate(self, state: Dict[str, Any], qa_report: Dict[str, Any], safety_patch: Dict[str, Any]) -> Dict[str, str]:
        # 1) If safety is blocked → escalate
        sg = safety_patch.get("safety_gateway", {})
        if sg.get("status") == "blocked":
            return {
                "action": "escalate",
                "reason": "safety_blocked",
                "surface_hint": "strategy_replan",
            }

        # 2) If QA findings are pending → retry
        findings = qa_report.get("findings", [])
        for f in findings:
            if f.get("status") == "pending":
                return {
                    "action": "retry",
                    "reason": "qa_pending",
                    "surface_hint": "qa_recheck",
                }

        # 3) If there are no messages at all → replan
        messages = state.get("messages", [])
        if not messages:
            return {
                "action": "replan",
                "reason": "no_messages",
                "surface_hint": "strategy_replan",
            }

        # 4) Default: accept
        return {
            "action": "accept",
            "reason": "default_accept",
            "surface_hint": "qa_recheck",
        }
from typing import Any, Dict

CORRECTION_JOURNAL = []


def record_correction_event(surface: str, recommendation: Dict[str, Any], plan: Dict[str, Any]):
    CORRECTION_JOURNAL.append(
        {
            "surface": surface,
            "recommendation": recommendation,
            "plan_objective": plan.get("objective"),
            "mode": plan.get("mode"),
        }
    )
from typing import Dict, Any

from self_correction import SelfCorrectionSurface, should_retry


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
"""Self-correction module consolidating correction engines and journals."""

from __future__ import annotations
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
from typing import Dict, Any



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
from typing import Any, Dict

CORRECTION_JOURNAL = []


def record_correction_event(surface: str, recommendation: Dict[str, Any], plan: Dict[str, Any]):
    CORRECTION_JOURNAL.append(
        {
            "surface": surface,
            "recommendation": recommendation,
            "plan_objective": plan.get("objective"),
            "mode": plan.get("mode"),
        }
    )
from typing import Dict, Any


class ArbitrationEngine:
    """
    Deterministic stub arbitration engine.

    evaluate(state, qa_report, safety_patch) -> Dict[str,str]
    returns one of: accept, retry, replan, escalate
    """

    def evaluate(self, state: Dict[str, Any], qa_report: Dict[str, Any], safety_patch: Dict[str, Any]) -> Dict[str, str]:
        # 1) If safety is blocked → escalate
        sg = safety_patch.get("safety_gateway", {})
        if sg.get("status") == "blocked":
            return {
                "action": "escalate",
                "reason": "safety_blocked",
                "surface_hint": "strategy_replan",
            }

        # 2) If QA findings are pending → retry
        findings = qa_report.get("findings", [])
        for f in findings:
            if f.get("status") == "pending":
                return {
                    "action": "retry",
                    "reason": "qa_pending",
                    "surface_hint": "qa_recheck",
                }

        # 3) If there are no messages at all → replan
        messages = state.get("messages", [])
        if not messages:
            return {
                "action": "replan",
                "reason": "no_messages",
                "surface_hint": "strategy_replan",
            }

        # 4) Default: accept
        return {
            "action": "accept",
            "reason": "default_accept",
            "surface_hint": "qa_recheck",
        }

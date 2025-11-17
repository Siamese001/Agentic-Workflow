from typing import Dict, Any

from self_correction_surfaces import SelfCorrectionSurface, should_retry


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

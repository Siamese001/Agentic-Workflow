"""PA binding — adapts AppIngressRunner route/l1/fec/validated to apps_qna PA adapter.

AppIngressRunner calls: prompt_artifact = pa(route, l1_plan, fec, validated)
  — only when route.model_generation_required is True.

apps_qna uses a card-context-based PA that validates the assembled context
through the canonical PA.0→PA.7 pipeline (run_pa_for_card_context). This is
NOT a model dispatch — it validates that the card context satisfies PA boundary,
classifier, and budget gates.

Consumes: QnaRouteContract, L1PlanContract, fec dict, ValidatedRequest
Emits:    QnaPromptArtifact — truthy wrapper that carries the assembled card
          context and PA pipeline result. A falsy return would cause
          AppIngressRunner to skip L2 via _no_gen_disposition — apps_qna must
          never return falsy here since card-pack build IS the product.

Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W1.P1
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class QnaPromptArtifact:
    """Truthy wrapper carrying the assembled card context and PA result.

    AppIngressRunner checks truthiness to decide whether to call l2_fn.
    This must always be truthy for apps_qna — card pack build IS generation.
    """

    interview_slug: str
    route_id: str
    evidence_contract: dict[str, Any]
    pa_dispatchable: bool
    pa_disposition: str
    card_context: dict[str, Any] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return True


def qna_pa(route: Any, l1_plan: Any, fec: Any, validated: Any) -> QnaPromptArtifact:
    """PA stage binding for apps_qna.

    Assembles the card context from the evidence contract and runs the
    canonical PA.0→PA.7 pipeline to validate boundary, classifier, and
    budget gates before the card pack build (L2).

    Args:
        route: QnaRouteContract from qna_l0.
        l1_plan: L1PlanContract from qna_l1.
        fec: FinalEvidenceContract dict from qna_c0 (or empty FEC from core).
        validated: ValidatedRequest from qna_u0.

    Returns:
        QnaPromptArtifact — always truthy; carries the context for qna_l2.
    """
    from apps_qna.card_context.pa_adapter import run_pa_for_card_context

    route_id: str = getattr(route, "route_id", "") or ""
    interview_slug: str = getattr(validated, "batch_id", "") or ""
    request_id: str = getattr(validated, "request_id", "") or ""

    # Build card context from the evidence contract
    if isinstance(fec, dict):
        evidence_contract = fec
    else:
        # Core may pass a FinalEvidenceContract dataclass — convert to dict
        evidence_contract = _fec_to_dict(fec)

    card_context: dict[str, Any] = {
        "interview_slug": interview_slug,
        "route_id": route_id,
        "evidence_sufficiency": evidence_contract.get("evidence_sufficiency", "template_only"),
        "grounded": evidence_contract.get("grounded", False),
        "retrieval_sources": evidence_contract.get("retrieval_sources", []),
    }

    _LOGGER.debug("qna_pa: slug=%s route_id=%s grounded=%s",
                  interview_slug, route_id, card_context["grounded"])

    pa_result = run_pa_for_card_context(
        card_context=card_context,
        interview_slug=interview_slug,
        route_id=route_id,
        request_id=request_id,
    )

    if not pa_result.dispatchable:
        _LOGGER.warning(
            "qna_pa: PA gate blocked slug=%s disposition=%s reason=%s",
            interview_slug, pa_result.dispatch_disposition, pa_result.reason,
        )
        # Still return a truthy artifact — apps_qna card pack build proceeds
        # even when PA flags a budget overflow (PA is advisory for build-time compiler)

    return QnaPromptArtifact(
        interview_slug=interview_slug,
        route_id=route_id,
        evidence_contract=evidence_contract,
        pa_dispatchable=pa_result.dispatchable,
        pa_disposition=pa_result.dispatch_disposition,
        card_context=card_context,
    )


def _fec_to_dict(fec: Any) -> dict[str, Any]:
    """Convert a FinalEvidenceContract dataclass to a plain dict."""
    if hasattr(fec, "__dataclass_fields__"):
        return {k: getattr(fec, k, None) for k in fec.__dataclass_fields__}
    if hasattr(fec, "__dict__"):
        return dict(fec.__dict__)
    return {}


__all__ = ["QnaPromptArtifact", "qna_pa"]

"""PA binding — adapts AppIngressRunner FEC to apps_rfp prompt assembly.

AppIngressRunner calls: prompt_artifact = pa(route, l1_plan, fec, validated)

Consumes: RouteContract, L1PlanContract, FinalEvidenceContract, ValidatedRequest
Emits:    RfpPromptArtifact — carries assembled prompt context for the L2 binding

apps_rfp prompt assembly produces a structured context dict for the
RfpOrchestrator (inside the L2 binding) that grounds the proposal generation
in the retrieved evidence. The PA binding does NOT call RfpOrchestrator —
it only assembles and seals the prompt inputs.

Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W2.P1
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class RfpPromptArtifact:
    """Sealed prompt context for apps_rfp L2 execution.

    Carries the grounded evidence and request metadata needed by the L2
    binding's RfpOrchestrator invocation. Does NOT contain the proposal
    itself — that is produced by L2.
    """

    request_id: str
    rfp_document_path: str
    target_company: str
    industry: str
    architecture_posture: str
    delivery_timeline_weeks: int
    dry_run: bool
    trace_id: str
    chunks: tuple[dict, ...] = ()
    grounded: bool = False
    metadata: dict = field(default_factory=dict)
    compilation_hash: str = ""


def rfp_pa(route: Any, l1_plan: Any, fec: Any, validated: Any) -> RfpPromptArtifact:
    """PA stage binding for apps_rfp.

    Assembles the prompt artifact from the route, L1 plan, and grounding
    evidence. No model calls are made here — this is pure assembly.

    Args:
        route:     RouteContract from rfp_l0.
        l1_plan:   L1PlanContract from rfp_l1.
        fec:       FinalEvidenceContract from rfp_c0.
        validated: ValidatedRequest from rfp_u0.

    Returns:
        RfpPromptArtifact with grounded evidence and request metadata.
    """
    import hashlib
    import json

    request_id: str = getattr(route, "request_id", "") or ""
    np: dict = getattr(validated, "normalized_payload", {}) or {}
    l1_metadata: dict = dict(getattr(l1_plan, "metadata", {}) or {})

    rfp_document_path: str = (
        np.get("rfp_document_path", "")
        or l1_metadata.get("rfp_document_path", "")
        or ""
    )
    target_company: str = (
        np.get("target_company", "")
        or l1_metadata.get("target_company", "")
        or ""
    )

    # fec is always a plain dict from rfp_c0
    chunks_raw = fec.get("chunks", []) if isinstance(fec, dict) else getattr(fec, "chunks", [])
    chunks: tuple[dict, ...] = tuple(chunks_raw or [])
    grounded: bool = bool((fec.get("grounded", False) if isinstance(fec, dict) else getattr(fec, "grounded", False)) or len(chunks) > 0)

    # Industry / posture from normalized_payload if forwarded from CLI
    industry: str = np.get("industry", "technology") or "technology"
    architecture_posture: str = np.get("architecture_posture", "cloud-first") or "cloud-first"
    delivery_timeline_weeks: int = int(np.get("delivery_timeline_weeks", 0) or 0)
    dry_run: bool = bool(np.get("dry_run", False))
    trace_id: str = getattr(validated, "trace_id", "") or ""

    # Deterministic compilation hash for provenance chain
    _hash_src = json.dumps(
        {"request_id": request_id, "rfp": rfp_document_path, "company": target_company},
        sort_keys=True,
    )
    compilation_hash = hashlib.sha256(_hash_src.encode()).hexdigest()[:32]

    _LOGGER.debug(
        "rfp_pa: request_id=%s chunks=%d grounded=%s industry=%s dry_run=%s",
        request_id,
        len(chunks),
        grounded,
        industry,
        dry_run,
    )

    return RfpPromptArtifact(
        request_id=request_id,
        rfp_document_path=rfp_document_path,
        target_company=target_company,
        industry=industry,
        architecture_posture=architecture_posture,
        delivery_timeline_weeks=delivery_timeline_weeks,
        dry_run=dry_run,
        trace_id=trace_id,
        chunks=chunks,
        grounded=grounded,
        compilation_hash=compilation_hash,
        metadata={
            "collection": getattr(route, "collection", "rfp_docs"),
            "capability_token": getattr(route, "capability_token", ""),
        },
    )


__all__ = ["RfpPromptArtifact", "rfp_pa"]

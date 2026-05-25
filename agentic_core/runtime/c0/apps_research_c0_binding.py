"""C0 grounding-retrieval binding for apps_research `company_brief` task class.

Per plan apps-research-golden-template-adoption-ag9.

C0 is the FOURTH stage (conditional on grounding_required=True). Its job is to:
1. Gather evidence (manual brief text, topic context) from validated_request.app_payload.
2. Emit a FinalEvidenceContract for PA consumption.

apps_research is R3_SIMPLE_GROUNDED_READ:
- No embedding generation.
- No ChromaDB mutation.
- Evidence comes from app_payload (manual brief path, topic, target context).
- Live web retrieval is the responsibility of the apps_research engine layer;
  this C0 binding packages what has already been resolved at ingress.
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
)
from agentic_core.runtime.contracts.route_contract import RouteContract

_LOGGER = logging.getLogger(__name__)

APPS_RESEARCH_C0_CERT_REF: str = "c0-apps-research-company-brief-ag9"


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_brief_file(path_str: str) -> str | None:
    """Read manual brief from file. Returns None on any error."""
    try:
        p = Path(path_str)
        if not p.exists():
            return None
        return p.read_text(encoding="utf-8")
    except OSError:  # guardian: allow-return-none-swallow -- P1 ADG burndown
        return None


def _build_topic_evidence(app_payload: Mapping[str, Any]) -> EvidenceItem | None:
    """Build an EvidenceItem from topic + target context in app_payload."""
    topic = (
        app_payload.get("topic")
        or (app_payload.get("user_constraints") or {}).get("topic", "")
        or app_payload.get("target_company", "")
    )
    target_company = app_payload.get("target_company") or ""
    target_role = app_payload.get("target_role") or ""

    if not topic and not target_company:
        return None

    content = (
        f"Research target: {topic or target_company}"
        + (f" | Role: {target_role}" if target_role else "")
        + (f" | Company: {target_company}" if target_company and topic else "")
    )
    chunk_digest = _sha256(content)

    return EvidenceItem(
        source="app_payload.topic_context",
        content=content,
        content_type="text",
        retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
        source_id="app_payload",
        source_type="app_payload_inline",
        chunk_digest=chunk_digest,
        retrieval_method="inline",
        evidence_digest=chunk_digest,
        freshness_status="FRESH",
        acl_status="ALLOWED",
        authority_class="PRIMARY",
        contradiction_status="NONE",
        support_status="PASS",
        unknown_reason="",
    )


def _build_brief_evidence(
    brief_text: str,
    brief_path: str,
) -> EvidenceItem:
    """Build an EvidenceItem from manual brief text."""
    chunk_digest = _sha256(brief_text[:8192])
    return EvidenceItem(
        source=brief_path or "app_payload.manual_brief_text",
        content=brief_text[:8192],
        content_type="text",
        retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
        source_id=brief_path or "manual_brief",
        source_type="app_payload_inline",
        chunk_digest=chunk_digest,
        retrieval_method="inline",
        evidence_digest=chunk_digest,
        freshness_status="FRESH",
        acl_status="ALLOWED",
        authority_class="PRIMARY",
        contradiction_status="NONE",
        support_status="PASS",
        unknown_reason="",
    )


def c0_retrieve_apps_research(
    route: RouteContract,
    validated_request: ValidatedRequest,
) -> FinalEvidenceContract:
    """Emit FinalEvidenceContract for apps_research company_brief task.

    Reads exclusively from validated_request.app_payload. Does NOT:
    - Generate embeddings
    - Mutate ChromaDB
    - Make network calls (evidence from ingress payload only)

    Returns a fully-typed FinalEvidenceContract. Raises ValueError on bad input.
    """
    if not isinstance(route, RouteContract):
        raise TypeError(
            f"c0_retrieve_apps_research: expected RouteContract, got {type(route)}"
        )
    if not isinstance(validated_request, ValidatedRequest):
        raise TypeError(
            f"c0_retrieve_apps_research: expected ValidatedRequest, got {type(validated_request)}"
        )

    app_payload = validated_request.app_payload or {}
    evidence_items: list[EvidenceItem] = []

    # Priority 1: manual brief file
    manual_brief_path = app_payload.get("manual_brief_path") or ""
    if manual_brief_path:
        brief_text = _read_brief_file(manual_brief_path)
        if brief_text:
            evidence_items.append(_build_brief_evidence(brief_text, manual_brief_path))
            _LOGGER.debug("C0 apps_research: loaded manual brief from %s", manual_brief_path)
        else:
            _LOGGER.warning(
                "C0 apps_research: manual_brief_path=%r not readable; skipping",
                manual_brief_path,
            )

    # Priority 2: topic/target context from payload
    topic_item = _build_topic_evidence(app_payload)
    if topic_item is not None:
        evidence_items.append(topic_item)

    # Depth context annotation
    depth = (
        app_payload.get("depth")
        or (app_payload.get("user_constraints") or {}).get("depth", "standard")
    )
    depth_content = f"Research depth profile: {depth}"
    depth_digest = _sha256(depth_content)
    evidence_items.append(
        EvidenceItem(
            source="app_payload.depth",
            content=depth_content,
            content_type="text",
            retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
            source_id="app_payload",
            source_type="app_payload_inline",
            chunk_digest=depth_digest,
            retrieval_method="inline",
            evidence_digest=depth_digest,
            freshness_status="FRESH",
            acl_status="ALLOWED",
            authority_class="PRIMARY",
            contradiction_status="NONE",
            support_status="PASS",
            unknown_reason="",
        )
    )

    # Compute FEC compilation hash over evidence digests
    evidence_digests = [item.chunk_digest for item in evidence_items]
    evidence_bundle_str = json.dumps(evidence_digests, sort_keys=True)
    compilation_hash = _sha256(evidence_bundle_str)

    collection_ts = datetime.now(timezone.utc).isoformat()

    _LOGGER.debug(
        "C0 apps_research: %d evidence items, compilation_hash=%s",
        len(evidence_items),
        compilation_hash[:16],
    )

    return FinalEvidenceContract(
        request_id=validated_request.request_id,
        run_id=validated_request.run_id,
        app_id="apps_research",
        trace_id=validated_request.trace_id,
        evidence_items=tuple(evidence_items),
        retrieval_sources=tuple(
            item.source for item in evidence_items
        ),
        support_target_met=len(evidence_items) > 0,
        evidence_collection_timestamp=collection_ts,
        compilation_hash=compilation_hash,
        schema_version="AG9.C0.1",
        tenant_id=validated_request.tenant_id,
        l5_certification_ref=APPS_RESEARCH_C0_CERT_REF,
    )


__all__ = [
    "APPS_RESEARCH_C0_CERT_REF",
    "c0_retrieve_apps_research",
]

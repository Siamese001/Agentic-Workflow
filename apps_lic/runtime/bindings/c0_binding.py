"""C0 grounding-retrieval binding for apps_lic `outreach_message` task class.

C0 is the FOURTH stage (CONDITIONAL — fires only when route.grounding_required=True).
Its job is to gather the best-available evidence needed for prompt assembly:

    1. Lead profile data   — from ValidatedRequest.app_payload.entity_refs.lead_profile
    2. Sender profile data — from ValidatedRequest.app_payload.entity_refs.sender_profile
    3. Campaign context    — from ValidatedRequest.app_payload.campaign
    4. Personalization     — from ValidatedRequest.app_payload.personalization.inputs

AG-8 W5 invariants (apps-lic-ag8-golden-template-adoption-f3c2e1):
    - Consumes RouteContract + ValidatedRequest.app_payload ONLY.
    - Emits FinalEvidenceContract when grounding_required=True.
    - Marks dense/vector fields NOT_APPLICABLE with explicit reason: apps_lic
      does NOT generate embeddings; no dense/sparse/ChromaDB retrieval surface.
    - Populates citation_map, source_lineage_map, evidence_strata, contradiction_report.
    - side_effect_class is always 'read_only' — no ChromaDB mutation, no L4 writes.
    - allowed_prompt_slot=C0_EVIDENCE_DATA_ONLY on every EvidenceItem.

HARD LAWS:
    - C0 does NOT answer, assemble prompts, execute, route, mutate ChromaDB,
      generate embeddings, or write L4.
    - Emits EMPTY/WEAK support_status with explicit reason when required evidence
      is absent so grounding_required=True but evidence is missing → BLOCKED.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-ag8-golden-template-adoption-f3c2e1.md (W5)
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.final_evidence_contract import (
    ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
    EvidenceItem,
    FinalEvidenceContract,
    STATUS_NOT_APPLICABLE,
    STATUS_UNKNOWN,
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_BLOCKED,
    SUPPORT_STATUS_CONFLICTED,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK,
)
from agentic_core.runtime.contracts.route_contract import RouteContract
from apps_lic.engines.governed_opportunity_ingestion import (
    C0_PROFILE_REQUIRED_VECTOR_COLLECTIONS,
    InMemoryOpportunityFactStore,
    OpportunityFactDocument,
    OpportunityIngestionInput,
    STATUS_BLOCKED as C0_EVIDENCE_BLOCKED,
    STATUS_CONFLICTED as C0_EVIDENCE_CONFLICTED,
    STATUS_MISSING as C0_OPPORTUNITY_INGESTION_REQUIRED,
    STATUS_READY as C0_READY,
    STATUS_STALE as C0_EVIDENCE_STALE,
    build_opportunity_fact_documents,
    check_opportunity_evidence_readiness,
)
from apps_lic.engines.recipient_classification import (
    CLASS_UNKNOWN,
    STATUS_CONFLICTED as RECIPIENT_CLASS_CONFLICTED,
    STATUS_DERIVED as RECIPIENT_CLASS_DERIVED,
    STATUS_LOW_CONFIDENCE as RECIPIENT_CLASS_LOW_CONFIDENCE,
    STATUS_MISSING_EVIDENCE as RECIPIENT_CLASS_MISSING_EVIDENCE,
    derive_recipient_class_from_store,
)


APPS_LIC_C0_CERT_REF: str = "c0-apps-lic-outreach-message-ag8-w5-f3c2e1"
C0_READINESS_INPUT_KEY: str = "governed_opportunity_facts"
C0_INGESTION_INPUT_KEY: str = "governed_opportunity_ingestion"
C0_REQUIRED_NAMESPACES_KEY: str = "c0_required_namespaces"
C0_READINESS_GATE_PREFIX: str = "c0_readiness:"
C0_RECIPIENT_CLASS_GATE_PREFIX: str = "c0_recipient_class:"
C0_RECIPIENT_CLASS_VALUE_PREFIX: str = "c0_recipient_class_value:"
C0_RECIPIENT_CLASS_CONFIDENCE_PREFIX: str = "c0_recipient_class_confidence:"

_READINESS_BLOCK_SUPPORT_STATUS: dict[str, str] = {
    C0_OPPORTUNITY_INGESTION_REQUIRED: SUPPORT_STATUS_EMPTY,
    C0_EVIDENCE_STALE: SUPPORT_STATUS_WEAK,
    C0_EVIDENCE_CONFLICTED: SUPPORT_STATUS_CONFLICTED,
    C0_EVIDENCE_BLOCKED: SUPPORT_STATUS_BLOCKED,
}
_RECIPIENT_CLASS_BLOCKING_STATUSES = frozenset(
    {
        RECIPIENT_CLASS_MISSING_EVIDENCE,
        RECIPIENT_CLASS_LOW_CONFIDENCE,
        RECIPIENT_CLASS_CONFLICTED,
    }
)

# Explicit reason for all NOT_APPLICABLE dense/vector/sparse fields.
# apps_lic does NOT generate embeddings; no ChromaDB collection exists at C0.
_NA_REASON = (
    "apps_lic C0 uses inline app_payload evidence only (lead_profile, "
    "sender_profile, campaign context, personalization). No dense retrieval, "
    "no sparse retrieval, no ChromaDB collection, no ACL check, no freshness "
    "check, and no graph expansion applies. Embeddings are NOT generated."
)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _coerce_str_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value else ()
    if isinstance(value, Iterable):
        return tuple(str(item) for item in value if str(item or "").strip())
    return (str(value),)


def _coerce_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _metadata_from_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    metadata = packet.get("metadata") or {}
    return dict(metadata) if isinstance(metadata, Mapping) else {}


def _fact_document_from_packet(
    packet: Mapping[str, Any],
    *,
    index: int,
) -> OpportunityFactDocument | None:
    namespace = str(packet.get("namespace") or "").strip()
    if not namespace:
        return None
    metadata = _metadata_from_packet(packet)
    fact_text = str(
        packet.get("fact_text")
        or packet.get("text")
        or packet.get("content")
        or metadata.get("fact_text")
        or ""
    ).strip()
    document_id = str(
        packet.get("document_id")
        or packet.get("id")
        or f"{namespace}:{index}:{_sha256(f'{namespace}|{fact_text}|{index}')[:12]}"
    )
    return OpportunityFactDocument(
        document_id=document_id,
        namespace=namespace,
        fact_family=str(packet.get("fact_family") or metadata.get("fact_family") or namespace),
        fact_text=fact_text,
        source_id=str(packet.get("source_id") or metadata.get("source_id") or document_id),
        source_type=str(
            packet.get("source_type")
            or metadata.get("source_type")
            or "governed_opportunity_fact"
        ),
        source_lineage=_coerce_str_tuple(
            packet.get("source_lineage") or metadata.get("source_lineage")
        ),
        freshness_date=str(
            packet.get("freshness_date")
            or packet.get("collected_at")
            or metadata.get("freshness_date")
            or ""
        ),
        confidence=_coerce_float(packet.get("confidence"), 0.80),
        metadata=metadata,
    )


def _documents_from_governed_inputs(
    *,
    personalization_inputs: Mapping[str, Any],
    route: RouteContract,
) -> tuple[OpportunityFactDocument, ...]:
    documents: list[OpportunityFactDocument] = []
    raw_docs = personalization_inputs.get(C0_READINESS_INPUT_KEY) or ()
    if isinstance(raw_docs, Mapping):
        raw_docs = raw_docs.get("documents") or ()
    if isinstance(raw_docs, Iterable) and not isinstance(raw_docs, (str, bytes)):
        for index, raw_doc in enumerate(raw_docs):
            if not isinstance(raw_doc, Mapping):
                continue
            document = _fact_document_from_packet(raw_doc, index=index)
            if document is not None:
                documents.append(document)

    ingestion_raw = personalization_inputs.get(C0_INGESTION_INPUT_KEY)
    if isinstance(ingestion_raw, Mapping):
        ingestion_input = OpportunityIngestionInput(
            request_id=route.request_id,
            trace_root=route.trace_id,
            idempotency_key=str(
                ingestion_raw.get("idempotency_key")
                or f"c0-readiness:{route.run_id}"
            ),
            profile_id=str(ingestion_raw.get("profile_id") or ""),
            expected_opportunity_scope=str(
                ingestion_raw.get("expected_opportunity_scope") or ""
            ),
            contact=ingestion_raw.get("contact")
            if isinstance(ingestion_raw.get("contact"), Mapping)
            else None,
            company=ingestion_raw.get("company")
            if isinstance(ingestion_raw.get("company"), Mapping)
            else None,
            jd=ingestion_raw.get("jd"),
            company_trigger=ingestion_raw.get("company_trigger")
            if isinstance(ingestion_raw.get("company_trigger"), Mapping)
            else None,
            role_ownership=ingestion_raw.get("role_ownership")
            if isinstance(ingestion_raw.get("role_ownership"), Mapping)
            else None,
            relationship=ingestion_raw.get("relationship")
            if isinstance(ingestion_raw.get("relationship"), Mapping)
            else None,
            referral=ingestion_raw.get("referral")
            if isinstance(ingestion_raw.get("referral"), Mapping)
            else None,
            prior_thread=ingestion_raw.get("prior_thread")
            if isinstance(ingestion_raw.get("prior_thread"), Mapping)
            else None,
            collected_at=str(ingestion_raw.get("collected_at") or ""),
        )
        documents.extend(build_opportunity_fact_documents(ingestion_input))
    return tuple(documents)


def _required_namespaces(
    personalization_inputs: Mapping[str, Any],
) -> tuple[str, ...]:
    raw = personalization_inputs.get(C0_REQUIRED_NAMESPACES_KEY)
    namespaces = _coerce_str_tuple(raw)
    return namespaces or tuple(C0_PROFILE_REQUIRED_VECTOR_COLLECTIONS)


def _readiness_store_from_inputs(
    *,
    personalization_inputs: Mapping[str, Any],
    route: RouteContract,
) -> tuple[InMemoryOpportunityFactStore, tuple[OpportunityFactDocument, ...]]:
    store = InMemoryOpportunityFactStore()
    documents = _documents_from_governed_inputs(
        personalization_inputs=personalization_inputs,
        route=route,
    )
    store.upsert_documents(documents)
    return store, documents


def c0_readiness_store_from_validated_request(
    *,
    route: RouteContract,
    validated_request: ValidatedRequest,
) -> tuple[InMemoryOpportunityFactStore, tuple[OpportunityFactDocument, ...]]:
    app_payload = validated_request.app_payload or {}
    personalization_inputs = (
        (app_payload.get("personalization") or {}).get("inputs") or {}
    )
    if not isinstance(personalization_inputs, Mapping):
        personalization_inputs = {}
    return _readiness_store_from_inputs(
        personalization_inputs=personalization_inputs,
        route=route,
    )


def c0_readiness_status_from_fec(fec: FinalEvidenceContract) -> str:
    for ref in fec.gate_verdict_refs:
        text = str(ref)
        if text.startswith(C0_READINESS_GATE_PREFIX):
            return text.removeprefix(C0_READINESS_GATE_PREFIX)
    return C0_OPPORTUNITY_INGESTION_REQUIRED


def c0_recipient_class_status_from_fec(fec: FinalEvidenceContract) -> str:
    for ref in fec.gate_verdict_refs:
        text = str(ref)
        if text.startswith(C0_RECIPIENT_CLASS_GATE_PREFIX):
            return text.removeprefix(C0_RECIPIENT_CLASS_GATE_PREFIX)
    return RECIPIENT_CLASS_MISSING_EVIDENCE


def c0_recipient_class_value_from_fec(fec: FinalEvidenceContract) -> str:
    for ref in fec.gate_verdict_refs:
        text = str(ref)
        if text.startswith(C0_RECIPIENT_CLASS_VALUE_PREFIX):
            return text.removeprefix(C0_RECIPIENT_CLASS_VALUE_PREFIX)
    return CLASS_UNKNOWN


def c0_recipient_class_confidence_from_fec(fec: FinalEvidenceContract) -> float:
    for ref in fec.gate_verdict_refs:
        text = str(ref)
        if text.startswith(C0_RECIPIENT_CLASS_CONFIDENCE_PREFIX):
            return _coerce_float(
                text.removeprefix(C0_RECIPIENT_CLASS_CONFIDENCE_PREFIX),
                0.0,
            )
    return 0.0


def c0_blocking_status_from_fec(fec: FinalEvidenceContract) -> str:
    readiness_status = c0_readiness_status_from_fec(fec)
    if readiness_status != C0_READY:
        return readiness_status
    recipient_status = c0_recipient_class_status_from_fec(fec)
    recipient_class = c0_recipient_class_value_from_fec(fec)
    if (
        recipient_status in _RECIPIENT_CLASS_BLOCKING_STATUSES
        or recipient_status != RECIPIENT_CLASS_DERIVED
        or recipient_class == CLASS_UNKNOWN
    ):
        return recipient_status or RECIPIENT_CLASS_MISSING_EVIDENCE
    return C0_READY


def c0_ready_for_pa(fec: FinalEvidenceContract) -> bool:
    return c0_blocking_status_from_fec(fec) == C0_READY


def _build_lead_evidence(
    lead_profile: dict,
    run_id: str,
    timestamp_iso: str,
) -> EvidenceItem | None:
    """Build EvidenceItem for lead profile data."""
    verified_name = str(lead_profile.get("verified_name", "") or "")
    if not verified_name:
        return None

    content_parts = {
        "verified_name": verified_name,
        "title": str(lead_profile.get("title", "") or ""),
        "seniority_class": str(lead_profile.get("seniority_class", "") or ""),
        "company_name": str(lead_profile.get("company_name", "") or ""),
        "industry": str(lead_profile.get("industry", "") or ""),
        "consent_attested": bool(lead_profile.get("consent_attested", False)),
    }
    content_text = json.dumps(content_parts, sort_keys=True)
    chunk_digest = _sha256(content_text)
    evidence_id = f"{run_id}:lead_profile:app_payload"

    return EvidenceItem(
        source="lead_profile:app_payload.entity_refs.lead_profile",
        content=content_text,
        content_type="json",
        retrieval_timestamp=timestamp_iso,
        confidence_score=1.0,
        # Identity + provenance
        evidence_id=evidence_id,
        source_id="apps_lic.app_payload.entity_refs.lead_profile",
        source_type="app_payload_inline",
        source_version="inline",
        source_uri_or_ref="app_payload://entity_refs/lead_profile",
        source_owner_or_authority="user_supplied",
        retrieved_span="full",
        citation_anchor=f"lead_profile:app_payload:{chunk_digest[:12]}",
        chunk_digest=chunk_digest,
        # Retrieval scores — NOT_APPLICABLE (no dense retrieval)
        fact_vec_ref=STATUS_NOT_APPLICABLE,
        dense_score=-1.0,
        bm25_score=-1.0,
        metadata_score=-1.0,
        query_vec_ref=STATUS_NOT_APPLICABLE,
        # Trust + safety
        freshness_status=STATUS_NOT_APPLICABLE,
        acl_status=STATUS_NOT_APPLICABLE,
        origin_trust_label="USER",
        authority_class="PRIMARY",
        contradiction_status=STATUS_NOT_APPLICABLE,
        stratum="USER_INTENT",
        # Prompt slot binding
        allowed_prompt_slot=ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
        # Support outcome
        support_score=1.0,
        support_status=SUPPORT_STATUS_PASS,
        # Retrieval audit
        retrieval_method="inline",
        retrieval_run_ref=run_id,
        # Digests
        evidence_digest=chunk_digest,
        # NOT_APPLICABLE reason (required by AG-4)
        not_applicable_reason=_NA_REASON,
    )


def _build_sender_evidence(
    sender_profile: dict,
    run_id: str,
    timestamp_iso: str,
) -> EvidenceItem | None:
    """Build EvidenceItem for sender profile data."""
    sender_id = str(sender_profile.get("sender_id", "") or "")
    sender_name = str(sender_profile.get("name", "") or "")
    if not sender_id and not sender_name:
        return None

    content_parts = {
        "sender_id": sender_id,
        "name": sender_name,
        "title": str(sender_profile.get("title", "") or ""),
    }
    content_text = json.dumps(content_parts, sort_keys=True)
    chunk_digest = _sha256(content_text)
    evidence_id = f"{run_id}:sender_profile:app_payload"

    return EvidenceItem(
        source="sender_profile:app_payload.entity_refs.sender_profile",
        content=content_text,
        content_type="json",
        retrieval_timestamp=timestamp_iso,
        confidence_score=1.0,
        evidence_id=evidence_id,
        source_id="apps_lic.app_payload.entity_refs.sender_profile",
        source_type="app_payload_inline",
        source_version="inline",
        source_uri_or_ref="app_payload://entity_refs/sender_profile",
        source_owner_or_authority="user_supplied",
        retrieved_span="full",
        citation_anchor=f"sender_profile:app_payload:{chunk_digest[:12]}",
        chunk_digest=chunk_digest,
        fact_vec_ref=STATUS_NOT_APPLICABLE,
        dense_score=-1.0,
        bm25_score=-1.0,
        metadata_score=-1.0,
        query_vec_ref=STATUS_NOT_APPLICABLE,
        freshness_status=STATUS_NOT_APPLICABLE,
        acl_status=STATUS_NOT_APPLICABLE,
        origin_trust_label="USER",
        authority_class="PRIMARY",
        contradiction_status=STATUS_NOT_APPLICABLE,
        stratum="USER_INTENT",
        allowed_prompt_slot=ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
        support_score=1.0,
        support_status=SUPPORT_STATUS_PASS,
        retrieval_method="inline",
        retrieval_run_ref=run_id,
        evidence_digest=chunk_digest,
        not_applicable_reason=_NA_REASON,
    )


def _build_campaign_evidence(
    campaign: dict,
    run_id: str,
    timestamp_iso: str,
) -> EvidenceItem | None:
    """Build EvidenceItem for campaign context."""
    campaign_objective = str(campaign.get("campaign_objective", "") or "")
    if not campaign_objective:
        return None

    content_parts = {
        "campaign_objective": campaign_objective,
        "channel": str(campaign.get("channel", "") or ""),
        "audience_segment": str(campaign.get("audience_segment", "") or ""),
        "request_type": str(campaign.get("request_type", "") or ""),
    }
    content_text = json.dumps(content_parts, sort_keys=True)
    chunk_digest = _sha256(content_text)
    evidence_id = f"{run_id}:campaign:app_payload"

    return EvidenceItem(
        source="campaign:app_payload.campaign",
        content=content_text,
        content_type="json",
        retrieval_timestamp=timestamp_iso,
        confidence_score=1.0,
        evidence_id=evidence_id,
        source_id="apps_lic.app_payload.campaign",
        source_type="app_payload_inline",
        source_version="inline",
        source_uri_or_ref="app_payload://campaign",
        source_owner_or_authority="user_supplied",
        retrieved_span="full",
        citation_anchor=f"campaign:app_payload:{chunk_digest[:12]}",
        chunk_digest=chunk_digest,
        fact_vec_ref=STATUS_NOT_APPLICABLE,
        dense_score=-1.0,
        bm25_score=-1.0,
        metadata_score=-1.0,
        query_vec_ref=STATUS_NOT_APPLICABLE,
        freshness_status=STATUS_NOT_APPLICABLE,
        acl_status=STATUS_NOT_APPLICABLE,
        origin_trust_label="USER",
        authority_class="SECONDARY",
        contradiction_status=STATUS_NOT_APPLICABLE,
        stratum="USER_INTENT",
        allowed_prompt_slot=ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
        support_score=0.8,
        support_status=SUPPORT_STATUS_PASS,
        retrieval_method="inline",
        retrieval_run_ref=run_id,
        evidence_digest=chunk_digest,
        not_applicable_reason=_NA_REASON,
    )


def _build_personalization_evidence(
    personalization_inputs: dict,
    run_id: str,
    timestamp_iso: str,
) -> EvidenceItem | None:
    """Build EvidenceItem for personalization inputs (SUPPORTING stratum)."""
    if not personalization_inputs:
        return None

    content_text = json.dumps(dict(personalization_inputs), sort_keys=True)
    chunk_digest = _sha256(content_text)
    evidence_id = f"{run_id}:personalization:app_payload"

    return EvidenceItem(
        source="personalization:app_payload.personalization.inputs",
        content=content_text,
        content_type="json",
        retrieval_timestamp=timestamp_iso,
        confidence_score=0.9,
        evidence_id=evidence_id,
        source_id="apps_lic.app_payload.personalization.inputs",
        source_type="app_payload_inline",
        source_version="inline",
        source_uri_or_ref="app_payload://personalization/inputs",
        source_owner_or_authority="user_supplied",
        retrieved_span="full",
        citation_anchor=f"personalization:app_payload:{chunk_digest[:12]}",
        chunk_digest=chunk_digest,
        fact_vec_ref=STATUS_NOT_APPLICABLE,
        dense_score=-1.0,
        bm25_score=-1.0,
        metadata_score=-1.0,
        query_vec_ref=STATUS_NOT_APPLICABLE,
        freshness_status=STATUS_NOT_APPLICABLE,
        acl_status=STATUS_NOT_APPLICABLE,
        origin_trust_label="USER",
        authority_class="SECONDARY",
        contradiction_status=STATUS_NOT_APPLICABLE,
        stratum="SUPPORTING",
        allowed_prompt_slot=ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
        support_score=0.9,
        support_status=SUPPORT_STATUS_PASS,
        retrieval_method="inline",
        retrieval_run_ref=run_id,
        evidence_digest=chunk_digest,
        not_applicable_reason=_NA_REASON,
    )


def c0_retrieve_apps_lic(
    route: RouteContract,
    validated_request: ValidatedRequest,
) -> FinalEvidenceContract:
    """Gather grounding evidence for an apps_lic outreach_message request.

    W5 scope: C0 reads exclusively from ValidatedRequest.app_payload (lead_profile,
    sender_profile, campaign, personalization). No dense/sparse/ChromaDB retrieval.
    All vector/dense fields are NOT_APPLICABLE with explicit reason.

    Args:
        route: L0 routing decision. Must have grounding_required=True for this
               binding to be invoked (caller's responsibility to gate on route).
        validated_request: U0 output carrying app_payload — the SSOT for all
                           apps_lic ingress fields.

    Returns:
        FinalEvidenceContract with evidence_items + citation_map + source_lineage_map
        + evidence_strata + contradiction_report.

    Raises:
        TypeError:  if route or validated_request have wrong shape.
        ValueError: if app_payload is missing required evidence sections
                    (entity_refs + campaign). Fail-closed before assembly.
    """
    if not isinstance(route, RouteContract):
        raise TypeError(
            f"c0_retrieve_apps_lic expected RouteContract, got {type(route).__name__}"
        )
    if not isinstance(validated_request, ValidatedRequest):
        raise TypeError(
            "c0_retrieve_apps_lic expected ValidatedRequest, got "
            f"{type(validated_request).__name__}"
        )

    app_payload = validated_request.app_payload
    if "entity_refs" not in app_payload or "campaign" not in app_payload:
        raise ValueError(
            "c0_retrieve_apps_lic: app_payload missing entity_refs/campaign sections. "
            "Was apps_lic_u0_adapt skipped?"
        )

    entity_refs = app_payload.get("entity_refs") or {}
    campaign = app_payload.get("campaign") or {}
    personalization = app_payload.get("personalization") or {}
    personalization_inputs = personalization.get("inputs") or {}

    lead_profile = entity_refs.get("lead_profile") or {}
    sender_profile = entity_refs.get("sender_profile") or {}
    readiness_store, readiness_documents = _readiness_store_from_inputs(
        personalization_inputs=personalization_inputs,
        route=route,
    )
    required_namespaces = _required_namespaces(personalization_inputs)
    c0_readiness = check_opportunity_evidence_readiness(
        store=readiness_store,
        required_namespaces=required_namespaces,
    )
    recipient_derivation = derive_recipient_class_from_store(
        readiness_store,
        u0_recipient_class_hint=str(lead_profile.get("seniority_class") or ""),
    )

    timestamp_iso = datetime.now(timezone.utc).isoformat()
    run_id = route.run_id

    # ── Gather evidence items ────────────────────────────────────────────────
    items: list[EvidenceItem] = []
    sources: list[str] = []

    lead_item = _build_lead_evidence(lead_profile, run_id, timestamp_iso)
    if lead_item:
        items.append(lead_item)
        sources.append(lead_item.source)

    sender_item = _build_sender_evidence(sender_profile, run_id, timestamp_iso)
    if sender_item:
        items.append(sender_item)
        sources.append(sender_item.source)

    campaign_item = _build_campaign_evidence(campaign, run_id, timestamp_iso)
    if campaign_item:
        items.append(campaign_item)
        sources.append(campaign_item.source)

    personalization_item = _build_personalization_evidence(
        personalization_inputs, run_id, timestamp_iso
    )
    if personalization_item:
        items.append(personalization_item)
        sources.append(personalization_item.source)

    # ── Sufficiency assessment ───────────────────────────────────────────────
    # apps_lic grounding requires: lead identity (PRIMARY) + campaign context.
    # Sender + personalization are SUPPORTING but not MUST_USE for PASS.
    has_lead = lead_item is not None
    has_campaign = campaign_item is not None
    has_sender = sender_item is not None
    has_personalization = personalization_item is not None

    # MUST_USE evidence IDs (lead + campaign) — gates downstream
    must_use_ids = tuple(
        it.evidence_id for it in items
        if it.stratum == "USER_INTENT" and it.authority_class == "PRIMARY"
    )
    # SUPPORTING evidence IDs
    supporting_ids = tuple(
        it.evidence_id for it in items
        if it.stratum == "SUPPORTING"
    )
    # All USER_INTENT IDs
    user_intent_ids = tuple(it.evidence_id for it in items if it.stratum == "USER_INTENT")

    recipient_class_ready = (
        recipient_derivation.status == RECIPIENT_CLASS_DERIVED
        and recipient_derivation.derived_recipient_class != CLASS_UNKNOWN
    )
    governed_ready = c0_readiness.ready and recipient_class_ready
    target_met = has_lead and has_campaign and governed_ready
    target_partial = has_lead or has_campaign
    score = 0.0
    if has_lead:
        score += 0.40
    if has_campaign:
        score += 0.35
    if has_sender:
        score += 0.15
    if has_personalization:
        score += 0.10
    if c0_readiness.ready:
        score += 0.10
    if recipient_class_ready:
        score += 0.10

    # ── Compilation hash (binds evidence bundle for PA reference) ────────────
    canonical = json.dumps(
        [{"src": it.source, "type": it.content_type, "len": len(it.content)} for it in items],
        sort_keys=True,
    )
    compilation_hash = _sha256(canonical)

    # ── AG-4 W2 contract-level lineage refs ──────────────────────────────────
    citation_map = tuple(
        (it.evidence_id, it.citation_anchor)
        for it in items if it.citation_anchor
    )
    source_lineage_map = tuple(
        (it.evidence_id, it.source_id)
        for it in items
    )
    source_version_map = tuple(
        (it.source_id, it.source_version)
        for it in items if it.source_id
    )

    # evidence_strata: MUST_USE = lead/campaign (PRIMARY USER_INTENT),
    #                  SUPPORTING = personalization
    evidence_strata: tuple[tuple[str, tuple[str, ...]], ...] = ()
    if must_use_ids:
        evidence_strata += (("MUST_USE", must_use_ids),)
    if supporting_ids:
        evidence_strata += (("SUPPORTING", supporting_ids),)
    if user_intent_ids and not must_use_ids:
        evidence_strata += (("USER_INTENT", user_intent_ids),)

    # ── Support status ───────────────────────────────────────────────────────
    readiness_reason = c0_readiness.ingestion_required_reason
    if (
        c0_readiness.status == C0_READY
        and recipient_derivation.status != RECIPIENT_CLASS_DERIVED
    ):
        readiness_reason = (
            f"{recipient_derivation.status}: "
            + ",".join(recipient_derivation.class_reason_codes)
        ).strip(": ")

    if target_met:
        support_status_v = SUPPORT_STATUS_PASS
        unknown_reason = ""
    elif c0_readiness.status != C0_READY:
        support_status_v = _READINESS_BLOCK_SUPPORT_STATUS.get(
            c0_readiness.status,
            SUPPORT_STATUS_WEAK,
        )
        unknown_reason = readiness_reason or c0_readiness.status
    elif not recipient_class_ready:
        support_status_v = (
            SUPPORT_STATUS_CONFLICTED
            if recipient_derivation.status == RECIPIENT_CLASS_CONFLICTED
            else SUPPORT_STATUS_WEAK
        )
        unknown_reason = readiness_reason or recipient_derivation.status
    elif target_partial:
        support_status_v = SUPPORT_STATUS_WEAK
        unknown_reason = "Lead profile or campaign context is missing — partial evidence only"
    else:
        support_status_v = SUPPORT_STATUS_EMPTY
        unknown_reason = "No evidence items gathered — lead_profile and campaign both absent"

    # Blocked when grounding required but evidence is empty/weak:
    # downstream gates must see support_status ≠ PASS and block.
    if route.grounding_required and support_status_v != SUPPORT_STATUS_PASS:
        # Preserve the WEAK/EMPTY label — do NOT silently upgrade to PASS.
        pass

    if c0_readiness.status == C0_EVIDENCE_CONFLICTED:
        contradiction_report = (
            f"{C0_EVIDENCE_CONFLICTED}: "
            + ",".join(c0_readiness.conflicted_namespaces)
        )
    elif recipient_derivation.status == RECIPIENT_CLASS_CONFLICTED:
        contradiction_report = (
            f"{RECIPIENT_CLASS_CONFLICTED}: "
            + ",".join(recipient_derivation.class_reason_codes)
        )
    else:
        # apps_lic inline evidence cannot contradict itself at C0; governed
        # fact-store readiness above is the cross-source contradiction surface.
        contradiction_report = (
            STATUS_NOT_APPLICABLE
            + ": apps_lic inline app_payload evidence is user assertion only; "
            + "governed opportunity fact readiness controls public evidence."
        )

    # ── Final evidence digest ─────────────────────────────────────────────────
    final_evidence_digest = _sha256(
        compilation_hash + "|"
        + "|".join(it.evidence_digest for it in items if it.evidence_digest)
    )

    support_score_profile: tuple[tuple[str, float], ...] = (
        ("lead_present", 1.0 if has_lead else 0.0),
        ("campaign_present", 1.0 if has_campaign else 0.0),
        ("sender_present", 1.0 if has_sender else 0.0),
        ("personalization_present", 1.0 if has_personalization else 0.0),
        ("governed_c0_ready", 1.0 if c0_readiness.ready else 0.0),
        ("governed_c0_source_count", float(c0_readiness.source_count)),
        (
            "recipient_class_ready",
            1.0 if recipient_class_ready else 0.0,
        ),
        (
            "recipient_class_confidence",
            float(recipient_derivation.recipient_class_confidence),
        ),
    )
    gate_verdict_refs = (
        f"{C0_READINESS_GATE_PREFIX}{c0_readiness.status}",
        f"{C0_RECIPIENT_CLASS_GATE_PREFIX}{recipient_derivation.status}",
        (
            f"{C0_RECIPIENT_CLASS_VALUE_PREFIX}"
            f"{recipient_derivation.derived_recipient_class}"
        ),
        (
            f"{C0_RECIPIENT_CLASS_CONFIDENCE_PREFIX}"
            f"{recipient_derivation.recipient_class_confidence:.3f}"
        ),
    )
    readiness_packet_ref = "c0_readiness_packet:sha256:" + _sha256(
        json.dumps(c0_readiness.to_packet(), sort_keys=True)
    )
    recipient_packet_ref = (
        "c0_recipient_class_packet:"
        + recipient_derivation.evidence_packet_id
    )
    u0_recipient_class_hint = str(lead_profile.get("seniority_class") or "").strip()
    audit_refs = (
        readiness_packet_ref,
        recipient_packet_ref,
        "c0_recipient_class_reason_codes:"
        + ",".join(recipient_derivation.class_reason_codes),
        "c0_recipient_class_contradiction_status:"
        + recipient_derivation.contradiction_status,
        "c0_recipient_class_hitl_required:"
        + str(bool(recipient_derivation.hitl_required)).lower(),
        "c0_u0_recipient_class_hint:" + u0_recipient_class_hint,
        "c0_u0_recipient_class_hint_authority:false",
    )
    freshness_receipts = (
        f"c0_readiness_status:{c0_readiness.status}",
        "c0_required_namespaces:" + ",".join(required_namespaces),
        "c0_source_count:" + str(c0_readiness.source_count),
    )
    blocked_source_refs = tuple(
        dict.fromkeys(
            (
                *c0_readiness.blocked_namespaces,
                *c0_readiness.conflicted_namespaces,
                *c0_readiness.stale_namespaces,
            )
        )
    )
    weak_support_refinement_attempts = (
        (readiness_reason or f"{c0_readiness.status}:{recipient_derivation.status}"),
    ) if support_status_v != SUPPORT_STATUS_PASS else ()
    snapshot_refs = tuple(
        dict.fromkeys(
            (
                *c0_readiness.source_snapshot_ids,
                *recipient_derivation.source_snapshot_ids,
                *(doc.source_snapshot_id for doc in readiness_documents),
            )
        )
    )

    return FinalEvidenceContract(
        request_id=route.request_id,
        run_id=route.run_id,
        app_id=route.app_id,
        trace_id=route.trace_id,
        tenant_id=route.tenant_id,
        evidence_items=tuple(items),
        retrieval_sources=tuple(sources),
        support_target_met=target_met,
        support_target_partial=target_partial and not target_met,
        evidence_sufficiency_score=round(score if target_met else min(score, 0.59), 3),
        evidence_collection_timestamp=timestamp_iso,
        schema_version="AG-8.W5.f3c2e1.W1_C0_READINESS",
        compilation_hash=compilation_hash,
        gate_verdict_refs=gate_verdict_refs,
        snapshot_refs=snapshot_refs,
        audit_refs=audit_refs,
        l5_certification_ref=APPS_LIC_C0_CERT_REF,
        # Lineage
        route_contract_ref=getattr(route, "compilation_hash", ""),
        retrieval_plan_ref="apps_lic:inline_app_payload_only",
        query_vec_ref=STATUS_NOT_APPLICABLE,
        # No dense/sparse/graph receipts (inline path)
        dense_search_refs=(),
        sparse_search_refs=(),
        metadata_filter_refs=(),
        graph_expansion_refs=(),
        # Maps
        evidence_strata=evidence_strata,
        citation_map=citation_map,
        source_lineage_map=source_lineage_map,
        source_version_map=source_version_map,
        # ACL/freshness — N/A for inline path
        acl_verification_receipts=(),
        freshness_receipts=freshness_receipts,
        # Contradiction — N/A at W5 (single-source inline)
        contradiction_report=contradiction_report,
        # Support aggregate
        support_status=support_status_v,
        support_score_profile=support_score_profile,
        # Exclusions
        excluded_evidence_refs=(),
        blocked_source_refs=blocked_source_refs,
        weak_support_refinement_attempts=weak_support_refinement_attempts,
        # Digest
        final_evidence_digest=final_evidence_digest,
        unknown_reason=unknown_reason,
        not_applicable_reason=(
            _NA_REASON if support_status_v == STATUS_NOT_APPLICABLE else ""
        ),
    )


__all__ = [
    "APPS_LIC_C0_CERT_REF",
    "C0_EVIDENCE_BLOCKED",
    "C0_EVIDENCE_CONFLICTED",
    "C0_EVIDENCE_STALE",
    "C0_OPPORTUNITY_INGESTION_REQUIRED",
    "C0_READY",
    "C0_READINESS_INPUT_KEY",
    "c0_blocking_status_from_fec",
    "c0_readiness_status_from_fec",
    "c0_ready_for_pa",
    "c0_recipient_class_confidence_from_fec",
    "c0_recipient_class_status_from_fec",
    "c0_recipient_class_value_from_fec",
    "c0_readiness_store_from_validated_request",
    "c0_retrieve_apps_lic",
]

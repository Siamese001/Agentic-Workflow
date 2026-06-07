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

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.final_evidence_contract import (
    ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
    EvidenceItem,
    FinalEvidenceContract,
    STATUS_NOT_APPLICABLE,
    STATUS_UNKNOWN,
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK,
)
from agentic_core.runtime.contracts.route_contract import RouteContract


APPS_LIC_C0_CERT_REF: str = "c0-apps-lic-outreach-message-ag8-w5-f3c2e1"

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

    target_met = has_lead and has_campaign
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
    if target_met:
        support_status_v = SUPPORT_STATUS_PASS
        unknown_reason = ""
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

    # contradiction_report: apps_lic inline evidence cannot contradict itself
    # at C0 (single-source, no cross-source comparison at this stage).
    contradiction_report = (
        STATUS_NOT_APPLICABLE
        + ": apps_lic C0 collects inline app_payload evidence only; "
        + "no multi-source contradiction surface applies at W5."
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
        support_target_partial=target_partial,
        evidence_sufficiency_score=round(score, 3),
        evidence_collection_timestamp=timestamp_iso,
        schema_version="AG-8.W5.f3c2e1",
        compilation_hash=compilation_hash,
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
        freshness_receipts=(),
        # Contradiction — N/A at W5 (single-source inline)
        contradiction_report=contradiction_report,
        # Support aggregate
        support_status=support_status_v,
        support_score_profile=support_score_profile,
        # Exclusions
        excluded_evidence_refs=(),
        blocked_source_refs=(),
        weak_support_refinement_attempts=(),
        # Digest
        final_evidence_digest=final_evidence_digest,
        unknown_reason=unknown_reason,
        not_applicable_reason=(
            _NA_REASON if support_status_v == STATUS_NOT_APPLICABLE else ""
        ),
    )


__all__ = [
    "APPS_LIC_C0_CERT_REF",
    "c0_retrieve_apps_lic",
]

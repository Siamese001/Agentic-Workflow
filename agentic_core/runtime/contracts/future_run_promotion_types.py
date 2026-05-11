"""Future run promotion types — post-runtime writeback proposals.

Phase 8.1/8.2 contracts of apps-rg-ensemble-judge-restoration-a7c4e2.

These are inert data proposals created by L6 writeback_proposer AFTER the
runtime path completes. They have no authority — UWG admits or blocks.
Exit has zero involvement in writeback.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class FutureRunPromotionRequest:
    """Inert post-runtime promotion proposal envelope.

    Created by L6 writeback_proposer ONLY after successful X3D_ALLOW_FINISH.
    Contains typed payload ref + metadata. Has no authority — UWG admits or blocks.
    """

    promotion_type: str = ""  # r1a_exact_cache | r1b_semantic_cache | c0_evidence | index_refresh
    run_id: str = ""
    disposition_ref: str = ""
    trace_root: str = ""
    created_at: str = ""
    policy_hash: str = ""
    registry_digest_set: str = ""
    app_context: str = ""
    payload_ref: str = ""  # ref to typed payload below

    schema_version: str = "1.0"


@dataclass(frozen=True, slots=True)
class R1APromotionPayload:
    """Payload for R1A exact cache promotion.

    Created by L6 writeback_proposer post-runtime.
    Consumed by UWG -> L4 for governed cache storage.
    """

    commit_type: str = "r1a_exact_cache"
    request_digest: str = ""
    normalized_payload_digest: str = ""
    app_context: str = ""
    task_class: str = ""
    route_id: str = ""
    workflow_ref: str = ""
    policy_hash: str = ""
    blueprint_hash: str = ""
    registry_digest_set: str = ""
    prompt_profile_digest: str = ""
    output_schema_digest: str = ""
    final_response_ref: str = ""
    final_response_digest: str = ""
    exit_disposition_ref: str = ""
    replay_key: str = ""
    trace_root: str = ""
    created_at: str = ""
    ttl_seconds: int = 0
    freshness_profile: str = ""

    schema_version: str = "1.0"


@dataclass(frozen=True, slots=True)
class R1BPromotionPayload:
    """Payload for R1B semantic cache promotion.

    Created by L6 writeback_proposer post-runtime.
    Consumed by UWG -> L4 for governed semantic cache storage.
    """

    commit_type: str = "r1b_semantic_cache"
    semantic_embedding_ref: str = ""
    intent_vec_ref: str = ""
    app_context: str = ""
    task_class: str = ""
    capability: str = ""
    compatible_output_schema_digest: str = ""
    policy_hash: str = ""
    registry_digest_set: str = ""
    evidence_support_compatibility: str = ""
    workflow_ref: str = ""
    final_response_ref: str = ""
    final_response_digest: str = ""
    semantic_cache_threshold_profile: str = ""
    freshness_profile: str = ""
    replay_key: str = ""
    trace_root: str = ""
    exit_disposition_ref: str = ""

    schema_version: str = "1.0"


@dataclass(frozen=True, slots=True)
class C0EvidencePromotionPayload:
    """Payload for C0 evidence/briefing writeback promotion.

    Created by L6 writeback_proposer post-runtime when
    evidence packet is reusable and writeback policy allows.
    Consumed by UWG -> L4 for governed evidence storage.
    Stores reusable support artifacts, NOT authoritative business truth.
    """

    commit_type: str = "c0_evidence_writeback"
    evidence_contract_ref: str = ""
    source_ids: tuple[str, ...] = field(default_factory=tuple)
    source_versions: tuple[str, ...] = field(default_factory=tuple)
    acl_freshness_receipts: tuple[str, ...] = field(default_factory=tuple)
    contradiction_report: str = ""
    support_status: str = ""  # sufficient | partial | insufficient
    evidence_digest: str = ""
    citation_map: str = ""
    policy_hash: str = ""
    registry_digest_set: str = ""
    replay_key: str = ""
    trace_root: str = ""
    exit_disposition_ref: str = ""
    uwg_receipt: str = ""

    # Reusable artifact refs (optional, policy-driven)
    generated_briefing_packet_ref: str = ""
    normalized_evidence_bundle_ref: str = ""
    source_lineage_map_ref: str = ""
    retrieval_query_profile_ref: str = ""
    evidence_support_profile_ref: str = ""
    reusable_context_packet_ref: str = ""
    app_read_surface_metadata_ref: str = ""
    embedding_index_refresh_ref: str = ""

    schema_version: str = "1.0"


@dataclass(frozen=True, slots=True)
class IndexRefreshPayload:
    """Payload for index refresh promotion.

    Created by L6 writeback_proposer when index metadata
    should be updated for future retrieval efficiency.
    """

    commit_type: str = "index_refresh"
    index_type: str = ""  # semantic_index | keyword_index | hybrid_index
    collection_ref: str = ""
    documents_to_index: tuple[str, ...] = field(default_factory=tuple)
    embedding_model_ref: str = ""
    policy_hash: str = ""
    registry_digest_set: str = ""
    trace_root: str = ""
    exit_disposition_ref: str = ""

    schema_version: str = "1.0"

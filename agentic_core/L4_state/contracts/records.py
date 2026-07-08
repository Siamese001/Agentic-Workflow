"""Canonical L4/UWG dataclass records.

All records are ``frozen=True`` (immutable per parent doctrine §"Hard Write
Law"). Each record carries a ``schema_version`` and a ``deterministic_digest``
that the caller computes via :func:`compute_deterministic_digest` over the
record's canonical payload.

Doctrinal source: ``docs/reference/00_L4_State_and_UWG/00.1`` through
``00.7``. Each record class lists which doctrine document defines it.

Lineage rule: ``audit_refs`` and similar ref lists must NOT be dropped during
serialization. The digest computation here includes them.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Tuple

if TYPE_CHECKING:
    from agentic_core.runtime.contracts.posture import RuntimePosture

from agentic_core.L4_state.contracts.digests import compute_deterministic_digest

# Schema version for this canonical pack. Bump when fields change incompatibly.
L4_CONTRACT_SCHEMA_VERSION = "L4-UWG-1.0.0"


def _empty_tuple() -> Tuple[Any, ...]:
    """Default factory for tuple fields — returns an empty immutable tuple."""
    return ()


def _commit_posture() -> "RuntimePosture":
    """Return the canonical POSTURE_WRITE_INTENT instance for CommitRequest."""
    from agentic_core.runtime.contracts.posture import POSTURE_WRITE_INTENT
    return POSTURE_WRITE_INTENT


def _record_payload(record: Any, *, exclude: Tuple[str, ...] = ("deterministic_digest",)) -> Dict[str, Any]:
    """Return ``record`` as a canonical dict suitable for digest computation.

    Tuple fields are converted to lists so the JSON encoding is stable.
    The ``deterministic_digest`` field is excluded by default (you can't hash
    a value that depends on itself).
    """
    raw = asdict(record)
    payload: Dict[str, Any] = {}
    for key, value in raw.items():
        if key in exclude:
            continue
        payload[key] = _normalize(value)
    return payload


def _normalize(value: Any) -> Any:
    """Recursively convert tuples to lists for stable JSON encoding."""
    if isinstance(value, tuple):
        return [_normalize(v) for v in value]
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    return value


# ============================================================================
# 00.1 POLICY / BLUEPRINT / REGISTRY
# ============================================================================


@dataclass(frozen=True)
class PolicyManifest:
    """Versioned durable policy bundle (00.1 §PolicyManifest)."""

    policy_manifest_id: str
    policy_version: str
    policy_hash: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    tenant_overlays: Tuple[str, ...] = field(default_factory=_empty_tuple)
    route_overlays: Tuple[str, ...] = field(default_factory=_empty_tuple)
    risk_tier_rules: Tuple[str, ...] = field(default_factory=_empty_tuple)
    hitl_thresholds: Tuple[str, ...] = field(default_factory=_empty_tuple)
    refusal_policy_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    abstain_policy_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    egress_policy_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    mutation_policy_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    rollback_requirements: Tuple[str, ...] = field(default_factory=_empty_tuple)
    active_alias_state: str = "active"
    previous_alias_ref: Optional[str] = None
    next_alias_ref: Optional[str] = None
    created_at: str = ""
    created_by_surface: str = "UWG"
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class PolicyVersionRecord:
    """Immutable policy version record (00.1 §PolicyVersionRecord)."""

    policy_version_id: str
    policy_manifest_ref: str
    policy_hash: str
    valid_from: str
    publish_commit_receipt_ref: str
    alias_swap_receipt_ref: str
    tenant_scope: str
    policy_diff_ref: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    valid_until: Optional[str] = None
    retirement_record_ref: Optional[str] = None
    rollback_target_ref: Optional[str] = None
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class BlueprintRecord:
    """Immutable architecture blueprint record (00.1 §BlueprintRecord)."""

    blueprint_id: str
    blueprint_hash: str
    blueprint_type: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    layer_contract_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    route_schema_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    workflow_blueprint_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    execution_blueprint_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    prompt_assembly_blueprint_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    c0_retrieval_profile_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    l2_sandbox_blueprint_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    exit_gate_blueprint_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    l6_promotion_blueprint_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class RegistrySnapshot:
    """Point-in-time registry roster (00.1 §RegistrySnapshot)."""

    registry_snapshot_id: str
    registry_digest: str
    policy_hash: str
    blueprint_hash: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    model_registry_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    provider_registry_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    tool_registry_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    connector_registry_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    capability_registry_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    sandbox_registry_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    schema_registry_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    grader_registry_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    route_registry_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    prompt_slot_registry_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    execution_profile_registry_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    deprecation_manifest_ref: Optional[str] = None
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class CapabilityRegistryRecord:
    """Durable capability definition (00.1 §CapabilityRegistryRecord)."""

    capability_id: str
    capability_class: str
    side_effect_class: str
    sandbox_required: bool
    egress_policy_ref: str
    deprecation_state: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    allowed_tools: Tuple[str, ...] = field(default_factory=_empty_tuple)
    allowed_models: Tuple[str, ...] = field(default_factory=_empty_tuple)
    allowed_connectors: Tuple[str, ...] = field(default_factory=_empty_tuple)
    allowed_networks: Tuple[str, ...] = field(default_factory=_empty_tuple)
    allowed_file_roots: Tuple[str, ...] = field(default_factory=_empty_tuple)
    risk_tier_bounds: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class ToolRegistryRecord:
    """Durable tool registry entry (00.1 §ToolRegistryRecord)."""

    tool_id: str
    tool_version: str
    tool_provider: str
    input_schema_ref: str
    output_schema_ref: str
    side_effect_class: str
    sandbox_class_required: str
    credential_scope: str
    network_scope: str
    egress_policy_ref: str
    deprecation_state: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    tenant_scope_rules: Tuple[str, ...] = field(default_factory=_empty_tuple)
    allowed_route_ids: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class ModelRegistryRecord:
    """Durable model/provider lane (00.1 §ModelRegistryRecord)."""

    model_id: str
    provider_id: str
    provider_lane: str
    context_limit: int
    tool_calling_capability: bool
    structured_output_capability: bool
    egress_class: str
    data_retention_class: str
    deprecation_state: str
    fallback_policy_ref: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    allowed_task_classes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    allowed_risk_tiers: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class SchemaRegistryRecord:
    """Durable schema registry entry (00.1 §SchemaRegistryRecord)."""

    schema_id: str
    schema_version: str
    schema_hash: str
    contract_type: str
    owner_surface: str
    backward_compatibility: str
    deprecation_state: str
    schema_version_of_record: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    json_schema_ref: Optional[str] = None
    pydantic_model_ref: Optional[str] = None
    migration_rules_ref: Optional[str] = None
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


# ============================================================================
# 00.2 MEMORY / APPROVED LEARNING
# ============================================================================


@dataclass(frozen=True)
class MemoryRecord:
    """Durable promoted memory unit (00.2 §MemoryRecord)."""

    memory_id: str
    memory_type: str
    memory_text_or_payload_ref: str
    scope: str  # user | project | tenant | system
    tenant_id: str
    validity_window: str
    confidence_band: str
    policy_hash: str
    blueprint_hash: str
    created_at: str
    created_by_surface: str = "UWG"
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    subject_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    source_learning_promotion_ref: Optional[str] = None
    human_review_ref: Optional[str] = None
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class ApprovedExampleRecord:
    """Durable approved golden example (00.2 §ApprovedExampleRecord)."""

    example_id: str
    task_class: str
    example_payload_ref: str
    policy_hash: str
    blueprint_hash: str
    version: str
    status: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    allowed_surfaces: Tuple[str, ...] = field(default_factory=_empty_tuple)
    source_eval_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    human_calibration_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class RubricRecord:
    """Durable rubric record (00.2 §RubricRecord)."""

    rubric_id: str
    rubric_version: str
    rubric_hash: str
    task_class: str
    owner_surface: str
    policy_hash: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    score_dimensions: Tuple[str, ...] = field(default_factory=_empty_tuple)
    threshold_profile_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    grader_roster_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    calibration_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class ThresholdProfileRecord:
    """Durable threshold profile record (00.2 §ThresholdProfileRecord)."""

    threshold_profile_id: str
    risk_tier: str
    route_id: str
    task_class: str
    abstain_policy_ref: str
    unknown_policy_ref: str
    valid_from: str
    policy_hash: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    score_thresholds: Mapping[str, float] = field(default_factory=dict)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class FeedbackRecord:
    """Durable feedback record (00.2 §FeedbackRecord)."""

    feedback_id: str
    feedback_source: str
    origin_trust_label: str
    review_status: str
    calibration_status: str
    privacy_scope: str
    allowed_future_use: bool
    policy_hash: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    related_run_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    related_artifact_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class LearningPromotionRecord:
    """Durable learning promotion (00.2 §LearningPromotionRecord)."""

    promotion_id: str
    learning_proposal_ref: str
    uwg_commit_receipt_ref: str
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    l6_eval_record_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    rca_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    proving_run_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    human_approval_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    target_memory_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    target_rubric_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    target_policy_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    target_registry_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


# ============================================================================
# 00.3 RETRIEVAL SURFACES
# ============================================================================


@dataclass(frozen=True)
class RetrievalSurfaceManifest:
    """Top-level retrieval substrate manifest (00.3 §RetrievalSurfaceManifest)."""

    retrieval_surface_id: str
    snapshot_id: str
    tenant_scope: str
    policy_hash: str
    blueprint_hash: str
    freshness_profile: str
    acl_profile: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    source_manifest_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    vector_index_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    sparse_index_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    metadata_index_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    graph_projection_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    adg_snapshot_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    runtime_graph_snapshot_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    citation_anchor_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class SourceChunkManifest:
    """Canonical source-chunk manifest (00.3 §SourceChunkManifest)."""

    source_id: str
    source_version: str
    chunk_id: str
    chunk_hash: str
    parent_doc_ref: str
    section_ref: str
    source_type: str
    source_authority_class: str
    tenant_id: str
    region: str
    data_class: str
    freshness_timestamp: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    line_range: Optional[str] = None
    timestamp_range: Optional[str] = None
    acl_tags: Tuple[str, ...] = field(default_factory=_empty_tuple)
    citation_anchor_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    lineage_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class VectorIndexManifest:
    """Dense vector index manifest (00.3 §VectorIndexManifest)."""

    vector_index_id: str
    embedding_model_id: str
    embedding_model_version: str
    dimension: int
    distance_metric: str
    source_snapshot_id: str
    build_receipt_ref: str
    index_hash: str
    created_at: str
    tenant_scope: str
    acl_filter_profile: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    chunk_manifest_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class SparseIndexManifest:
    """Sparse/BM25 index manifest (00.3 §SparseIndexManifest)."""

    sparse_index_id: str
    tokenizer_version: str
    source_snapshot_id: str
    field_weights: str
    stopword_policy: str
    build_receipt_ref: str
    index_hash: str
    tenant_scope: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    chunk_manifest_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class MetadataIndexManifest:
    """Metadata index manifest (00.3 §MetadataIndexManifest)."""

    metadata_index_id: str
    source_snapshot_id: str
    filter_policy_ref: str
    acl_policy_ref: str
    build_receipt_ref: str
    index_hash: str
    tenant_scope: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    indexed_fields: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class GraphProjectionManifest:
    """Graph projection manifest (00.3 §GraphProjectionManifest)."""

    graph_projection_id: str
    graph_source: str
    graph_snapshot_id: str
    projection_version: str
    acl_projection_policy: str
    freshness_timestamp: str
    build_receipt_ref: str
    projection_hash: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    source_snapshot_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    allowed_relation_types: Tuple[str, ...] = field(default_factory=_empty_tuple)
    blocked_relation_types: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class CitationAnchorRecord:
    """Citation anchor record (00.3 §CitationAnchorRecord)."""

    citation_anchor_id: str
    source_id: str
    source_version: str
    span_ref: str
    anchor_hash: str
    anchor_status: str
    tenant_scope: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    line_range: Optional[str] = None
    section_ref: Optional[str] = None
    timestamp_range: Optional[str] = None
    stable_until: Optional[str] = None
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


# ============================================================================
# 00.4 CACHE
# ============================================================================


@dataclass(frozen=True)
class CacheEntry:
    """Base durable cache entry (00.4 §CacheEntry)."""

    cache_entry_id: str
    cache_type: str  # exact | semantic
    tenant_id: str
    normalized_request_hash: str
    task_class: str
    route_id: str
    answer_ref: str
    policy_hash: str
    blueprint_hash: str
    freshness_class: str
    created_by_surface: str = "UWG"
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    semantic_embedding_ref: Optional[str] = None
    prompt_envelope_ref: Optional[str] = None
    evidence_contract_ref: Optional[str] = None
    valid_until: Optional[str] = None
    source_snapshot_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    reuse_constraints: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class ExactCacheEntry:
    """Exact-match cache entry (00.4 §ExactCacheEntry)."""

    cache_entry_id: str
    normalized_request_hash: str
    request_shape_hash: str
    answer_ref: str
    tenant_scope: str
    policy_hash: str
    blueprint_hash: str
    output_schema_ref: str
    freshness_class: str
    replay_key: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    evidence_contract_ref: Optional[str] = None
    source_snapshot_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class SemanticCacheEntry:
    """Semantic similarity cache entry (00.4 §SemanticCacheEntry)."""

    cache_entry_id: str
    semantic_embedding_ref: str
    embedding_model_id: str
    embedding_model_version: str
    task_class: str
    answer_ref: str
    similarity_threshold_profile_ref: str
    tenant_scope: str
    policy_hash: str
    blueprint_hash: str
    freshness_class: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    evidence_contract_ref: Optional[str] = None
    reuse_safe_classes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class CacheLookupReceipt:
    """Receipt from a cache lookup (00.4 §CacheLookupReceipt)."""

    lookup_id: str
    cache_entry_ref: str
    lookup_surface: str
    tenant_id: str
    policy_hash: str
    blueprint_hash: str
    normalized_request_hash: str
    freshness_status: str
    policy_compatibility_status: str
    source_snapshot_compatibility_status: str
    decision_hint: str  # compatible | incompatible | unknown
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    request_id: Optional[str] = None
    run_id: Optional[str] = None
    similarity_score: Optional[float] = None
    reason_codes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class CacheInvalidationReceipt:
    """Cache invalidation receipt (00.4 §CacheInvalidationReceipt)."""

    invalidation_id: str
    reason_code: str
    before_snapshot: str
    after_snapshot: str
    created_by_surface: str = "UWG"
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    affected_cache_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    source_commit_receipt_ref: Optional[str] = None
    policy_change_ref: Optional[str] = None
    registry_change_ref: Optional[str] = None
    source_snapshot_change_ref: Optional[str] = None
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


# ============================================================================
# 00.5 REPLAY / SNAPSHOT / AUDIT
# ============================================================================


@dataclass(frozen=True)
class L4SnapshotManifest:
    """L4 snapshot manifest (00.5 §L4SnapshotManifest)."""

    snapshot_id: str
    tenant_id: str
    policy_hash: str
    blueprint_hash: str
    registry_snapshot_id: str
    retrieval_surface_id: str
    cache_snapshot_ref: str
    memory_snapshot_ref: str
    audit_ledger_position: int
    created_at: str
    created_by_surface: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    replay_snapshot_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    commit_receipt_ref: Optional[str] = None
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class ReplaySnapshotRecord:
    """Replay reconstruction record (00.5 §ReplaySnapshotRecord)."""

    replay_snapshot_id: str
    trace_root: str
    tenant_id: str
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    snapshot_id: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    request_id: Optional[str] = None
    run_id: Optional[str] = None
    normalized_request_hash: Optional[str] = None
    input_hash: Optional[str] = None
    prompt_hash: Optional[str] = None
    route_digest: Optional[str] = None
    evidence_contract_hash: Optional[str] = None
    sealed_artifact_hash: Optional[str] = None
    exit_disposition_hash: Optional[str] = None
    commit_receipt_hash: Optional[str] = None
    gate_verdict_hashes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    environment_digest_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class EnvironmentDigestRecord:
    """Environment digest record (00.5 §EnvironmentDigestRecord)."""

    environment_digest_id: str
    runtime_version: str
    tool_registry_digest: str
    model_registry_digest: str
    provider_lane_digest: str
    network_policy_hash: str
    clock_policy: str
    locale: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    python_version: Optional[str] = None
    package_lock_hash: Optional[str] = None
    filesystem_view_hash: Optional[str] = None
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class AuditLedgerRecord:
    """Append-only audit ledger entry (00.5 §AuditLedgerRecord)."""

    audit_record_id: str
    ledger_sequence: int
    event_type: str
    state_surface: str
    operation_type: str
    tenant_id: str
    policy_hash: str
    blueprint_hash: str
    snapshot_before: str
    actor_surface: str
    mutation_source: str
    created_at: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    request_id: Optional[str] = None
    run_id: Optional[str] = None
    trace_root: Optional[str] = None
    snapshot_after: Optional[str] = None
    receipt_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    state_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    reason_codes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    supersedes_ref: Optional[str] = None  # for correction-via-append-record
    prev_chain_hash: str = ""
    chain_hash: str = ""


@dataclass(frozen=True)
class ReceiptChainRecord:
    """Receipt chain record (00.5 §ReceiptChainRecord)."""

    receipt_chain_id: str
    audit_append_receipt_ref: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    commit_request_ref: Optional[str] = None
    uwg_validation_receipt_ref: Optional[str] = None
    write_lock_receipt_ref: Optional[str] = None
    commit_receipt_ref: Optional[str] = None
    rollback_receipt_ref: Optional[str] = None
    blocked_commit_receipt_ref: Optional[str] = None
    read_surface_refresh_receipts: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


# ============================================================================
# 00.6 UWG DURABLE WRITE GATEWAY
# ============================================================================


@dataclass(frozen=True)
class CommitRequest:
    """Cleared CommitRequest from Exit (00.6 §CommitRequest).

    Source-surface MUST be ``Exit``. Any other source is rejected by UWG.
    """

    commit_request_id: str
    cleared_exit_review_packet_ref: str
    request_id: str
    run_id: str
    trace_root: str
    tenant_id: str
    policy_hash: str
    blueprint_hash: str
    route_contract_ref: str
    replay_key: str
    rollback_plan_ref: str
    blast_radius: str
    source_surface: str = "Exit"
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    state_diff_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    gate_verdict_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    l5_certification_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    l5_certification_ref: str = ""  # W3 singular alias matching chain-wide convention
    hitl_reclearance_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    affected_state_surfaces: Tuple[str, ...] = field(default_factory=_empty_tuple)
    expected_read_surface_refreshes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    # W4: observability linkage (concern #9, D12=default-empty tuple)
    otel_span_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    # W5 P5.2: HMAC-SHA256 integrity signature (D9, default-empty = unsigned)
    signature: str = ""
    # W6 P6.2: risk/side-effect posture (concern #7; CommitRequest always write_intent)
    posture: "RuntimePosture" = field(default_factory=lambda: _commit_posture())
    # W7 P7.1: replay/determinism (concern #4; replay_key already required above; snapshot_refs new)
    snapshot_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    # W8 P8.1: write/learning firewall (concern #10; default False — gateway enforces)
    is_uwg_write_authority: bool = False
    is_future_run_only: bool = False
    # W2: Capability / sandbox / egress allowlists (concern #8, D11=default-empty)
    sandbox_required: bool = False
    egress_policy_ref: str = ""
    allowed_tools: Tuple[str, ...] = field(default_factory=_empty_tuple)
    allowed_models: Tuple[str, ...] = field(default_factory=_empty_tuple)
    allowed_networks: Tuple[str, ...] = field(default_factory=_empty_tuple)
    allowed_file_roots: Tuple[str, ...] = field(default_factory=_empty_tuple)
    registry_digest_set: Tuple[str, ...] = field(default_factory=_empty_tuple)
    capability_token_ref: str = ""
    clearance_proof_id: str = ""
    validator_receipt_id: str = ""
    staged_diff_hash: str = ""
    commit_request_signature: str = ""

    def __post_init__(self) -> None:
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref
        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"CommitRequest: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )


@dataclass(frozen=True)
class StateDiff:
    """Proposed durable state mutation (00.6 §StateDiff)."""

    state_diff_id: str
    target_surface: str
    operation_type: str
    after_candidate: str  # ref to immutable record under proposal
    schema_ref: str
    blast_radius: str
    rollback_plan_ref: str
    proposed_by_surface: str
    created_at: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    before_ref: Optional[str] = None
    validation_rules: Tuple[str, ...] = field(default_factory=_empty_tuple)
    policy_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    replay_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class WriteLockReceipt:
    """Write lock receipt (00.6 §WriteLockReceipt)."""

    write_lock_receipt_id: str
    commit_request_ref: str
    lock_scope: str
    lock_status: str  # ACQUIRED | CONTENTION | FAILED
    lock_owner: str
    policy_hash: str
    blueprint_hash: str
    snapshot_before: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    target_surfaces: Tuple[str, ...] = field(default_factory=_empty_tuple)
    acquired_at: Optional[str] = None
    expires_at: Optional[str] = None
    contention_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class UWGValidationReceipt:
    """UWG admission validation receipt (00.6 §UWGValidationReceipt)."""

    uwg_validation_receipt_id: str
    commit_request_ref: str
    validation_status: str  # PASS | FAIL
    policy_status: str
    blueprint_status: str
    schema_status: str
    gate_status: str
    l5_cert_status: str
    hitl_status: str
    replay_status: str
    rollback_status: str
    blast_radius_status: str
    write_lock_status: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    checked_rules: Tuple[str, ...] = field(default_factory=_empty_tuple)
    failed_rules: Tuple[str, ...] = field(default_factory=_empty_tuple)
    reason_codes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class UWGCommitReceipt:
    """Successful atomic commit receipt (00.6 §UWGCommitReceipt)."""

    commit_receipt_id: str
    commit_request_ref: str
    write_lock_receipt_ref: str
    uwg_validation_receipt_ref: str
    snapshot_before: str
    snapshot_after: str
    read_surface_refresh_plan_ref: str
    audit_append_receipt_ref: str
    committed_at: str
    committed_by_surface: str = "UWG"
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    state_diff_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    affected_state_surfaces: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    l5_certification_ref: str = ""
    source_surface: str = "Exit"
    policy_hash: str = ""
    blueprint_hash: str = ""
    replay_key: str = ""
    gate_verdict_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    cleared_exit_review_packet_ref: str = ""
    registry_digest_set: Tuple[str, ...] = field(default_factory=_empty_tuple)
    clearance_proof_id: str = ""
    staged_diff_hash: str = ""
    content_hash: str = ""
    prev_chain_hash: str = ""
    chain_hash: str = ""
    validator_receipt_id: str = ""

    def __post_init__(self) -> None:
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref
        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"UWGCommitReceipt: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )


@dataclass(frozen=True)
class UWGBlockedCommitReceipt:
    """Blocked commit receipt (00.6 §UWGBlockedCommitReceipt).

    ``no_mutation_assertion`` MUST be the literal string
    ``"NO_MUTATION_APPLIED"`` for blocked commits.
    """

    blocked_commit_receipt_id: str
    commit_request_ref: str
    snapshot_before: str
    audit_append_receipt_ref: str
    no_mutation_assertion: str = "NO_MUTATION_APPLIED"
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    uwg_validation_receipt_ref: Optional[str] = None
    blocked_reason_codes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    failed_rule_ids: Tuple[str, ...] = field(default_factory=_empty_tuple)
    state_surfaces_requested: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class RollbackPlan:
    """Rollback plan record (00.6 §RollbackPlan)."""

    rollback_plan_id: str
    blast_radius: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    target_surfaces: Tuple[str, ...] = field(default_factory=_empty_tuple)
    before_snapshot_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    rollback_operation_types: Tuple[str, ...] = field(default_factory=_empty_tuple)
    safety_preconditions: Tuple[str, ...] = field(default_factory=_empty_tuple)
    policy_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    schema_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    test_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class UWGRollbackReceipt:
    """Rollback receipt (00.6 §UWGRollbackReceipt)."""

    rollback_receipt_id: str
    rollback_plan_ref: str
    source_commit_receipt_ref: str
    snapshot_before_rollback: str
    snapshot_after_rollback: str
    audit_append_receipt_ref: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    affected_state_surfaces: Tuple[str, ...] = field(default_factory=_empty_tuple)
    reason_codes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


# ============================================================================
# 00.7 READ-SURFACE REFRESH
# ============================================================================


@dataclass(frozen=True)
class ReadSurfaceRefreshPlan:
    """Post-commit refresh plan (00.7 §ReadSurfaceRefreshPlan)."""

    refresh_plan_id: str
    source_commit_receipt_ref: str
    before_snapshot: str
    expected_after_snapshot: str
    stale_projection_policy: str
    retry_policy: str
    policy_hash: str
    blueprint_hash: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    affected_surfaces: Tuple[str, ...] = field(default_factory=_empty_tuple)
    required_refreshes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    optional_refreshes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    refresh_order: Tuple[str, ...] = field(default_factory=_empty_tuple)
    rollback_policy_ref: Optional[str] = None
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class ReadSurfaceRefreshReceipt:
    """Refresh receipt (00.7 §ReadSurfaceRefreshReceipt)."""

    refresh_receipt_id: str
    refresh_plan_ref: str
    source_commit_receipt_ref: str
    state_surface: str
    refresh_type: str
    before_snapshot: str
    status: str  # SUCCESS | FAILED | STALE_WARNING | SKIPPED
    retry_count: int
    started_at: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    after_snapshot: Optional[str] = None
    completed_at: Optional[str] = None
    stale_projection_warning: Optional[str] = None
    reason_codes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class IndexRefreshReceipt:
    """Index refresh receipt (00.7 §IndexRefreshReceipt)."""

    index_refresh_receipt_id: str
    index_type: str  # vector | sparse | metadata
    source_commit_receipt_ref: str
    source_snapshot_before: str
    source_snapshot_after: str
    status: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    index_manifest_before: Optional[str] = None
    index_manifest_after: Optional[str] = None
    build_receipt_ref: Optional[str] = None
    reason_codes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class GraphProjectionRefreshReceipt:
    """Graph projection refresh receipt (00.7 §GraphProjectionRefreshReceipt)."""

    graph_refresh_receipt_id: str
    source_commit_receipt_ref: str
    graph_projection_before: str
    projection_version_before: str
    relation_type_manifest_ref: str
    status: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    graph_projection_after: Optional[str] = None
    projection_version_after: Optional[str] = None
    source_snapshot_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    reason_codes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


@dataclass(frozen=True)
class AliasRefreshReceipt:
    """Alias refresh receipt (00.7 §AliasRefreshReceipt)."""

    alias_refresh_receipt_id: str
    alias_type: str  # policy | registry | route | prompt
    source_commit_receipt_ref: str
    alias_before: str
    alias_after: str
    target_record_ref: str
    status: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    reason_codes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)


# ============================================================================
# 00B.9 BLUEPRINT / POLICY VERSION MIGRATION
# Doctrinal source: docs/reference/00B_L4_State_Archive_and_UWG/
#                   00B.9_L4_Blueprint_Policy_Version_Migration.md
# ============================================================================

# Allowed values per 00B.9 doctrine
VERSION_MIGRATION_SURFACES: Tuple[str, ...] = (
    "policy",
    "blueprint",
    "registry",
    "prompt",
    "retrieval_profile",
    "rubric",
)
COMPATIBILITY_MODES: Tuple[str, ...] = (
    "backward_compatible",
    "forward_compatible",
    "breaking",
    "unknown",
)


@dataclass(frozen=True)
class VersionCompatibilityRecord:
    """Compatibility metadata between two versions of a versioned surface
    (00B.9 §VersionCompatibilityRecord).

    Doctrine: when ``compatibility == "breaking"``, ``migration_required``
    MUST be True. Enforced in ``__post_init__``.
    """

    compatibility_record_id: str
    surface: str  # one of VERSION_MIGRATION_SURFACES
    old_version_ref: str
    new_version_ref: str
    old_hash: str
    new_hash: str
    compatibility: str  # one of COMPATIBILITY_MODES
    migration_required: bool
    activation_policy: str  # immediate | aliased | canary | dark_launch
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    affected_route_classes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    affected_contract_schemas: Tuple[str, ...] = field(default_factory=_empty_tuple)
    replay_impact: str = "none"  # none | partial | full_invalidation
    rollback_impact: str = "none"  # none | partial | full
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)

    def __post_init__(self) -> None:
        if self.surface not in VERSION_MIGRATION_SURFACES:
            raise ValueError(
                f"VersionCompatibilityRecord.surface must be one of "
                f"{VERSION_MIGRATION_SURFACES}; got {self.surface!r}"
            )
        if self.compatibility not in COMPATIBILITY_MODES:
            raise ValueError(
                f"VersionCompatibilityRecord.compatibility must be one of "
                f"{COMPATIBILITY_MODES}; got {self.compatibility!r}"
            )
        if self.compatibility == "breaking" and not self.migration_required:
            raise ValueError(
                "VersionCompatibilityRecord(compatibility='breaking') requires "
                "migration_required=True per 00B.9 §RULES "
                "'Breaking changes require replay pack proof and rollback plan "
                "before activation.'"
            )


@dataclass(frozen=True)
class PolicyBlueprintMigrationPlan:
    """Migration plan for moving a versioned surface from source to target
    (00B.9 §PolicyBlueprintMigrationPlan).

    Doctrine: alias swaps require ``alias_swap_plan_ref`` AND
    ``UWG_commit_request_ref`` (00B.9 §RULES line 101). Enforced in
    ``__post_init__`` when ``activation_policy == "aliased"``.
    """

    migration_plan_id: str
    target_surface: str  # one of VERSION_MIGRATION_SURFACES
    source_version_ref: str
    target_version_ref: str
    rollback_plan_ref: str
    owner: str
    signer_identity: str
    UWG_commit_request_ref: str
    activation_policy: str = "aliased"
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    migration_steps: Tuple[str, ...] = field(default_factory=_empty_tuple)
    validation_checks: Tuple[str, ...] = field(default_factory=_empty_tuple)
    replay_pack_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    canary_or_dark_launch_policy: Optional[str] = None
    alias_swap_plan_ref: Optional[str] = None
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)

    def __post_init__(self) -> None:
        if self.target_surface not in VERSION_MIGRATION_SURFACES:
            raise ValueError(
                f"PolicyBlueprintMigrationPlan.target_surface must be one of "
                f"{VERSION_MIGRATION_SURFACES}; got {self.target_surface!r}"
            )
        if self.activation_policy == "aliased":
            if not self.alias_swap_plan_ref:
                raise ValueError(
                    "PolicyBlueprintMigrationPlan(activation_policy='aliased') "
                    "requires alias_swap_plan_ref per 00B.9 §RULES "
                    "'Alias swaps require UWG commit receipt and audit ledger "
                    "append.'"
                )
            if not self.UWG_commit_request_ref:
                raise ValueError(
                    "PolicyBlueprintMigrationPlan(activation_policy='aliased') "
                    "requires UWG_commit_request_ref per 00B.9 §RULES."
                )


@dataclass(frozen=True)
class DeprecationWindowRecord:
    """Deprecation window for a retired version of a versioned surface
    (00B.9 §DeprecationWindowRecord).

    Provides the run-start enforcement primitive: a new run starting AFTER
    ``deprecation_end`` MUST NOT use any of ``allowed_legacy_routes`` and
    MUST be blocked from any of ``blocked_new_routes`` while replaying
    ``deprecated_version_ref``.
    """

    deprecation_id: str
    deprecated_version_ref: str
    replacement_version_ref: str
    deprecation_start: str  # ISO 8601
    deprecation_end: str  # ISO 8601
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    allowed_legacy_routes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    blocked_new_routes: Tuple[str, ...] = field(default_factory=_empty_tuple)
    warning_receipt_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)

    def is_route_blocked_at(self, route_class: str, run_start_iso: str) -> bool:
        """Return True iff a run starting at ``run_start_iso`` MUST be blocked
        from ``route_class`` per 00B.9 §RULES.

        After ``deprecation_end``: route is blocked iff it appears in
        ``blocked_new_routes`` OR is not in ``allowed_legacy_routes``.
        Inside the window: only ``blocked_new_routes`` apply.
        """
        if route_class in self.blocked_new_routes:
            return True
        if run_start_iso > self.deprecation_end:
            # After window closes, only explicitly-allowed legacy routes survive
            return route_class not in self.allowed_legacy_routes
        return False


def detect_policy_version_mismatch(
    *,
    active_policy_hash: str,
    replay_snapshot_policy_hash: str,
) -> Optional[str]:
    """Return a reason code when a runtime packet bound to a replay snapshot
    encounters a different active policy hash, else None.

    Used at run_start by the runtime gate mesh to honor 00B.9 §RULES
    'Runtime packets already bound to a replay snapshot may complete under
    their bound snapshot unless policy requires fail-closed.'

    The matrix lists this as test 9.T5
    (``test_replay_bound_runtime_detects_policy_version_mismatch``).
    """
    if active_policy_hash != replay_snapshot_policy_hash:
        return "policy_version_mismatch"
    return None


# ============================================================================
# Digest helpers exposed on the module surface
# ============================================================================


def stamp_digest(record: Any) -> Any:
    """Return a copy of ``record`` with ``deterministic_digest`` filled in.

    The digest is computed from the canonical payload of the record EXCLUDING
    its current ``deterministic_digest`` field. Use this on every constructed
    record before persisting.

    Returns the same record when ``deterministic_digest`` is already populated
    — idempotent so callers can stamp records repeatedly without harm.
    """
    from dataclasses import replace

    if not hasattr(record, "deterministic_digest"):
        return record
    if getattr(record, "deterministic_digest", "") != "":
        return record
    payload = _record_payload(record)
    digest = compute_deterministic_digest(payload)
    return replace(record, deterministic_digest=digest)


def record_canonical_payload(record: Any) -> Dict[str, Any]:
    """Return canonical-payload dict for ``record`` (digest excluded).

    Public helper exposed for tests and OTel span attribute construction.
    """
    return _record_payload(record)


__all__ = [
    "L4_CONTRACT_SCHEMA_VERSION",
    "stamp_digest",
    "record_canonical_payload",
    # 00.1
    "PolicyManifest",
    "PolicyVersionRecord",
    "BlueprintRecord",
    "RegistrySnapshot",
    "CapabilityRegistryRecord",
    "ToolRegistryRecord",
    "ModelRegistryRecord",
    "SchemaRegistryRecord",
    # 00.2
    "MemoryRecord",
    "ApprovedExampleRecord",
    "RubricRecord",
    "ThresholdProfileRecord",
    "FeedbackRecord",
    "LearningPromotionRecord",
    # 00.3
    "RetrievalSurfaceManifest",
    "SourceChunkManifest",
    "VectorIndexManifest",
    "SparseIndexManifest",
    "MetadataIndexManifest",
    "GraphProjectionManifest",
    "CitationAnchorRecord",
    # 00.4
    "CacheEntry",
    "ExactCacheEntry",
    "SemanticCacheEntry",
    "CacheLookupReceipt",
    "CacheInvalidationReceipt",
    # 00.5
    "L4SnapshotManifest",
    "ReplaySnapshotRecord",
    "EnvironmentDigestRecord",
    "AuditLedgerRecord",
    "ReceiptChainRecord",
    # 00.6
    "CommitRequest",
    "StateDiff",
    "WriteLockReceipt",
    "UWGValidationReceipt",
    "UWGCommitReceipt",
    "UWGBlockedCommitReceipt",
    "RollbackPlan",
    "UWGRollbackReceipt",
    # 00.7
    "ReadSurfaceRefreshPlan",
    "ReadSurfaceRefreshReceipt",
    "IndexRefreshReceipt",
    "GraphProjectionRefreshReceipt",
    "AliasRefreshReceipt",
    # 00B.9 Blueprint / Policy Version Migration
    "VERSION_MIGRATION_SURFACES",
    "COMPATIBILITY_MODES",
    "VersionCompatibilityRecord",
    "PolicyBlueprintMigrationPlan",
    "DeprecationWindowRecord",
    "detect_policy_version_mismatch",
]

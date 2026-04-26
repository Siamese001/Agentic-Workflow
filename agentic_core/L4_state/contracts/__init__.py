"""Canonical L4/UWG record contracts.

Implements the implementation-grade contracts mandated by the doctrinal pack
``docs/reference/00_L4_State_and_UWG/``. Re-exports every record class so
callers can write::

    from agentic_core.L4_state.contracts import (
        PolicyManifest, CommitRequest, UWGCommitReceipt, ...
    )

The surface here is durable-state-only — no runtime gate verdicts, no
disposition strings, no model output objects. See parent doctrine in
``docs/reference/00_L4_State_and_UWG/00_L4_State_Archive_and_UWG_detailed.md``.
"""

from __future__ import annotations

from agentic_core.L4_state.contracts.digests import (
    canonical_json_dumps,
    compute_deterministic_digest,
)
from agentic_core.L4_state.contracts.records import (
    AliasRefreshReceipt,
    ApprovedExampleRecord,
    AuditLedgerRecord,
    BlueprintRecord,
    CacheEntry,
    CacheInvalidationReceipt,
    CacheLookupReceipt,
    CapabilityRegistryRecord,
    CitationAnchorRecord,
    CommitRequest,
    EnvironmentDigestRecord,
    ExactCacheEntry,
    FeedbackRecord,
    GraphProjectionManifest,
    GraphProjectionRefreshReceipt,
    IndexRefreshReceipt,
    L4SnapshotManifest,
    LearningPromotionRecord,
    MemoryRecord,
    MetadataIndexManifest,
    ModelRegistryRecord,
    PolicyManifest,
    PolicyVersionRecord,
    ReadSurfaceRefreshPlan,
    ReadSurfaceRefreshReceipt,
    ReceiptChainRecord,
    RegistrySnapshot,
    ReplaySnapshotRecord,
    RetrievalSurfaceManifest,
    RollbackPlan,
    RubricRecord,
    SchemaRegistryRecord,
    SemanticCacheEntry,
    SourceChunkManifest,
    SparseIndexManifest,
    StateDiff,
    ThresholdProfileRecord,
    ToolRegistryRecord,
    UWGBlockedCommitReceipt,
    UWGCommitReceipt,
    UWGRollbackReceipt,
    UWGValidationReceipt,
    VectorIndexManifest,
    WriteLockReceipt,
)
from agentic_core.L4_state.contracts.lookup import (
    AliasResolutionError,
    DeprecatedEntryError,
    InMemoryL4Store,
    L4LookupError,
    StaleSnapshotError,
    TenantScopeError,
    UnknownEntryError,
    get_default_store,
    reset_default_store,
)
from agentic_core.L4_state.contracts.proof import L4UWGProofPacket

__all__ = [
    # Digest helpers
    "canonical_json_dumps",
    "compute_deterministic_digest",
    # 00.1 Policy / Blueprint / Registry
    "PolicyManifest",
    "PolicyVersionRecord",
    "BlueprintRecord",
    "RegistrySnapshot",
    "CapabilityRegistryRecord",
    "ToolRegistryRecord",
    "ModelRegistryRecord",
    "SchemaRegistryRecord",
    # 00.2 Memory / Approved Learning
    "MemoryRecord",
    "ApprovedExampleRecord",
    "RubricRecord",
    "ThresholdProfileRecord",
    "FeedbackRecord",
    "LearningPromotionRecord",
    # 00.3 Retrieval surfaces
    "RetrievalSurfaceManifest",
    "SourceChunkManifest",
    "VectorIndexManifest",
    "SparseIndexManifest",
    "MetadataIndexManifest",
    "GraphProjectionManifest",
    "CitationAnchorRecord",
    # 00.4 Cache
    "CacheEntry",
    "ExactCacheEntry",
    "SemanticCacheEntry",
    "CacheLookupReceipt",
    "CacheInvalidationReceipt",
    # 00.5 Replay / Snapshot / Audit
    "L4SnapshotManifest",
    "ReplaySnapshotRecord",
    "EnvironmentDigestRecord",
    "AuditLedgerRecord",
    "ReceiptChainRecord",
    # 00.6 UWG
    "CommitRequest",
    "StateDiff",
    "WriteLockReceipt",
    "UWGValidationReceipt",
    "UWGCommitReceipt",
    "UWGBlockedCommitReceipt",
    "RollbackPlan",
    "UWGRollbackReceipt",
    # 00.7 Read surface refresh
    "ReadSurfaceRefreshPlan",
    "ReadSurfaceRefreshReceipt",
    "IndexRefreshReceipt",
    "GraphProjectionRefreshReceipt",
    "AliasRefreshReceipt",
    # 00.8 Proof packet
    "L4UWGProofPacket",
    # 00.1 §PHASE 2 Lookup API
    "InMemoryL4Store",
    "L4LookupError",
    "UnknownEntryError",
    "DeprecatedEntryError",
    "TenantScopeError",
    "AliasResolutionError",
    "StaleSnapshotError",
    "get_default_store",
    "reset_default_store",
]

"""Retrieval Module.

Pipeline C Phase C5: Hybrid retrieval with reranking and evidence contracts.
"""

from .anthropic_cache_control import CACHE_TTL_1H, CACHE_TTL_5M, min_cacheable_chars
from .anthropic_cache_telemetry import prefix_fingerprint, record_cache_usage
from .c0_sparse_exact_seam import (
    SparseLexicalLaneStatus,
    SparseLexicalQuerySpec,
    dedupe_hybrid_by_chunk_id,
    fec_sparse_refs_from_lane_outcomes,
    filter_candidates_exact_subphrase,
    merge_dense_sparse_rrf,
    query_sparse_lexical_lane,
)
from .cross_encoder_reranker import CrossEncoderReranker
from .evidence_contract_builder import (
    Citation,
    ContradictionStatus,
    EvidenceContract,
    EvidenceContractBuilder,
    EvidenceStatus,
    NextActionHint,
    RefinementDiagnostic,
    VerifiedChunk,
)
from .hybrid_recall_stage import HybridRecallStage, RecallResult, VectorStore
from .parent_child_hydrator import HydrationResult, ParentChildHydrator
from .prompt_envelope import (
    AssemblyStatusCode,
    PromptAssemblyStatus,
    PromptEnvelope,
    PromptEnvelopeFactory,
)
from .reranker_factory import get_reranker
from .retrieval_plan import (
    PrefilterResult,
    PrefilterVerdict,
    RetrievalMode,
    RetrievalPlan,
    RetrievalPrefilter,
)
from .senior_librarian_reranker import RerankResult, SeniorLibrarianReranker

__all__ = [
    # C0 sparse exact seam (apps_rg binding)
    "SparseLexicalLaneStatus",
    "SparseLexicalQuerySpec",
    "dedupe_hybrid_by_chunk_id",
    "fec_sparse_refs_from_lane_outcomes",
    "filter_candidates_exact_subphrase",
    "merge_dense_sparse_rrf",
    "query_sparse_lexical_lane",
    # Anthropic prompt-cache telemetry surface (provider gateway)
    "CACHE_TTL_1H",
    "CACHE_TTL_5M",
    "min_cacheable_chars",
    "prefix_fingerprint",
    "record_cache_usage",
    # Recall stage
    "HybridRecallStage",
    "RecallResult",
    "VectorStore",
    # Retrieval plan + prefilter
    "RetrievalPlan",
    "RetrievalMode",
    "RetrievalPrefilter",
    "PrefilterResult",
    "PrefilterVerdict",
    # Lineage hydration
    "ParentChildHydrator",
    "HydrationResult",
    # Reranking
    "SeniorLibrarianReranker",
    "CrossEncoderReranker",
    "RerankResult",
    "get_reranker",
    # Evidence contract (C0.4)
    "EvidenceContractBuilder",
    "EvidenceContract",
    "EvidenceStatus",
    "RefinementDiagnostic",
    "VerifiedChunk",
    "Citation",
    "ContradictionStatus",
    "NextActionHint",
    # Prompt envelope (C0.5)
    "PromptEnvelope",
    "PromptEnvelopeFactory",
    "PromptAssemblyStatus",
    "AssemblyStatusCode",
]

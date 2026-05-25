"""Retrieval Module.

Pipeline C Phase C5: Hybrid retrieval with reranking and evidence contracts.
"""

from .c0_sparse_exact_seam import (
    SparseLexicalLaneStatus,
    SparseLexicalQuerySpec,
    dedupe_hybrid_by_chunk_id,
    fec_sparse_refs_from_lane_outcomes,
    filter_candidates_exact_subphrase,
    merge_dense_sparse_rrf,
    query_sparse_lexical_lane,
)
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
from .retrieval_plan import (
    PrefilterResult,
    PrefilterVerdict,
    RetrievalMode,
    RetrievalPlan,
    RetrievalPrefilter,
)
from .senior_librarian_reranker import RerankResult, SeniorLibrarianReranker
from .cross_encoder_reranker import CrossEncoderReranker
from .reranker_factory import get_reranker

__all__ = [
    # C0 sparse exact seam (apps_rg binding)
    "SparseLexicalLaneStatus",
    "SparseLexicalQuerySpec",
    "dedupe_hybrid_by_chunk_id",
    "fec_sparse_refs_from_lane_outcomes",
    "filter_candidates_exact_subphrase",
    "merge_dense_sparse_rrf",
    "query_sparse_lexical_lane",
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

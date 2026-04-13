"""Retrieval Module.

Pipeline C Phase C5: Hybrid retrieval with reranking and evidence contracts.
"""

from .evidence_contract_builder import (
    Citation,
    ContradictionStatus,
    EvidenceContract,
    EvidenceContractBuilder,
    NextActionHint,
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

__all__ = [
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
    "RerankResult",
    # Evidence contract (C0.4)
    "EvidenceContractBuilder",
    "EvidenceContract",
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

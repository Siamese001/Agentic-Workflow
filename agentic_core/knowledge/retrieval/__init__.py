"""Retrieval Module.

Pipeline C Phase C5: Hybrid retrieval with reranking and evidence contracts.
"""

from .hybrid_recall_stage import HybridRecallStage, RecallResult
from .senior_librarian_reranker import SeniorLibrarianReranker, RerankResult
from .parent_child_hydrator import ParentChildHydrator, HydrationResult
from .evidence_contract_builder import EvidenceContractBuilder, EvidenceContract

__all__ = [
    "HybridRecallStage",
    "RecallResult",
    "SeniorLibrarianReranker",
    "RerankResult",
    "ParentChildHydrator",
    "HydrationResult",
    "EvidenceContractBuilder",
    "EvidenceContract",
]

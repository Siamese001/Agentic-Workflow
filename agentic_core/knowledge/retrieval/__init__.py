"""Retrieval Module.

Pipeline C Phase C5: Hybrid retrieval with reranking and evidence contracts.
"""

from .evidence_contract_builder import EvidenceContract, EvidenceContractBuilder
from .hybrid_recall_stage import HybridRecallStage, RecallResult
from .parent_child_hydrator import HydrationResult, ParentChildHydrator
from .senior_librarian_reranker import RerankResult, SeniorLibrarianReranker

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

"""Synthetic RAG simulator."""

import random
from typing import List

from simulations.models.rag_simulation import (
    RAGSimMetrics,
    RAGSimRequest,
    RAGSimResult,
)
from simulations.utils import model_to_payload


class RAGSimulator:
    """Runs retrieval quality simulations."""

    async def run(self, request: RAGSimRequest) -> RAGSimResult:
        doc_count = len(request.documents)
        diversity_bonus = min(doc_count / 10.0, 0.3)
        recall = round(min(1.0, 0.4 + diversity_bonus + random.uniform(0.0, 0.4)), 3)
        precision = round(min(1.0, 0.5 + random.uniform(-0.2, 0.3)), 3)
        redundancy = round(max(0.0, 0.2 + random.uniform(-0.1, 0.5)), 3)
        metrics = RAGSimMetrics(
            recall=max(0.0, recall),
            precision=max(0.0, precision),
            redundancy=min(1.0, redundancy),
        )
        top_docs: List[str] = request.documents[:3]
        return RAGSimResult(
            simulation_id=request.simulation_id,
            success=True,
            metrics=model_to_payload(metrics),
            details={"top_documents": top_docs},
        )

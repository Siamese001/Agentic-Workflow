"""Evidence Contract Builder.

Citation slip compilation, provenance verification, and precise context packet generation.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


@dataclass
class Citation:
    """Individual citation."""

    doc_id: str
    content_snippet: str
    source: str
    confidence: float
    page_number: int | None = None
    section: str | None = None


@dataclass
class EvidenceContract:
    """Evidence contract with citations and provenance."""

    query_id: str
    citations: list[Citation] = field(default_factory=list)
    context_packet: str = ""
    provenance_verified: bool = False
    support_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class EvidenceContractBuilder:
    """Builds evidence contracts with citations and provenance.

    The EvidenceContractBuilder compiles citation slips, verifies
    provenance, and generates precise context packets for generation.
    """

    def __init__(self, min_citation_confidence: float = 0.7):
        """Initialize the builder.

        Args:
            min_citation_confidence: Minimum confidence for citations
        """
        self.min_citation_confidence = min_citation_confidence
        log.info("EvidenceContractBuilder initialized")

    def build_contract(
        self,
        query_id: str,
        query: str,
        retrieved_docs: list[Any],
    ) -> EvidenceContract:
        """Build evidence contract from retrieved documents.

        Args:
            query_id: Query identifier
            query: Original query
            retrieved_docs: Retrieved and ranked documents

        Returns:
            EvidenceContract with citations
        """
        trace_id = f"evidence_{query_id}"
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L1_REASONING,
            "EvidenceContractBuilder.build_contract",
        )

        # Build citations
        citations = []
        for doc in retrieved_docs:
            citation = self._create_citation(doc)
            if citation.confidence >= self.min_citation_confidence:
                citations.append(citation)

        # Verify provenance
        provenance_verified = self._verify_provenance(citations)

        # Calculate support score
        support_score = self._calculate_support(query, citations)

        # Generate context packet
        context_packet = self._generate_context_packet(query, citations)

        contract = EvidenceContract(
            query_id=query_id,
            citations=citations,
            context_packet=context_packet,
            provenance_verified=provenance_verified,
            support_score=support_score,
            metadata={
                "citation_count": len(citations),
                "avg_confidence": sum(c.confidence for c in citations) / len(citations) if citations else 0,
            },
        )

        _emit_records_telemetry_event(
            "evidence_contract",
            f"query_{query_id}_citations_{len(citations)}",
        )

        log.debug(f"Built evidence contract: {len(citations)} citations, score={support_score:.2f}")
        return contract

    def _create_citation(self, doc: Any) -> Citation:
        """Create citation from document."""
        return Citation(
            doc_id=getattr(doc, "doc_id", "unknown"),
            content_snippet=getattr(doc, "content", "")[:200],
            source=getattr(doc, "source", "unknown"),
            confidence=getattr(doc, "rerank_score", 0.5),
        )

    def _verify_provenance(self, citations: list[Citation]) -> bool:
        """Verify provenance of citations."""
        # Mock implementation - would check canonical store for provenance
        return all(c.source != "unknown" for c in citations)

    def _calculate_support(self, query: str, citations: list[Citation]) -> float:
        """Calculate support score for query."""
        if not citations:
            return 0.0

        # Average confidence weighted by coverage
        avg_confidence = sum(c.confidence for c in citations) / len(citations)
        coverage = min(len(citations) / 5, 1.0)  # Expect at least 5 citations

        return avg_confidence * coverage

    def _generate_context_packet(self, query: str, citations: list[Citation]) -> str:
        """Generate context packet for LLM."""
        packet_parts = [f"Query: {query}\n", "Relevant Context:\n"]

        for i, citation in enumerate(citations, 1):
            packet_parts.append(
                f"[{i}] Source: {citation.source} (ID: {citation.doc_id})\n"
                f"Content: {citation.content_snippet}\n",
            )

        return "\n".join(packet_parts)


# Global instance
_global_builder: EvidenceContractBuilder | None = None


def get_evidence_contract_builder() -> EvidenceContractBuilder:
    """Get or create the global builder."""
    global _global_builder
    if _global_builder is None:
        _global_builder = EvidenceContractBuilder()
    return _global_builder

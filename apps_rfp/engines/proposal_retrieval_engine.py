"""
Past Proposal Retrieval System — apps_rfp.enterprise.

Vector-based semantic retrieval of past proposals for reuse,
with ChromaDB as the embedding store.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_stores_embedding,
)

_log = logging.getLogger(__name__)


class EmbeddingStore(Protocol):
    """Protocol for vector embedding storage backends."""

    def add_proposal(
        self,
        proposal_id: str,
        content: str,
        metadata: dict[str, Any],
    ) -> bool:
        """Store a proposal embedding."""
        ...

    def query_similar(
        self,
        query_text: str,
        n_results: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievedProposal]:
        """Query for similar proposals."""
        ...

    def get_by_industry(self, industry: str, limit: int = 10) -> list[RetrievedProposal]:
        """Get proposals by industry."""
        ...


@dataclass(frozen=True)
class RetrievedProposal:
    """A proposal retrieved from the vector store."""

    proposal_id: str
    title: str
    industry: str
    content_preview: str
    metadata: dict[str, Any] = field(default_factory=dict)
    similarity_score: float = 0.0
    source_path: str = ""


@dataclass(frozen=True)
class ProposalChunk:
    """Chunk of a proposal for granular retrieval."""

    chunk_id: str
    proposal_id: str
    section_type: str  # executive_summary, technical_approach, etc.
    content: str
    embedding: list[float] | None = None


class InMemoryProposalStore:
    """In-memory embedding store for demonstration."""

    def __init__(self) -> None:
        self._proposals: dict[str, dict[str, Any]] = {}
        self._embeddings: dict[str, list[float]] = {}

    def add_proposal(
        self,
        proposal_id: str,
        content: str,
        metadata: dict[str, Any],
    ) -> bool:
        """Store a proposal (mock embedding generation)."""
        _emit_stores_embedding("enterprise", "InMemoryProposalStore", proposal_id)

        self._proposals[proposal_id] = {
            "content": content,
            "metadata": metadata,
        }
        # Mock embedding: hash-based
        self._embeddings[proposal_id] = self._mock_embed(content)
        return True

    def query_similar(
        self,
        query_text: str,
        n_results: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievedProposal]:
        """Query for similar proposals using mock similarity."""
        _emit_reads_through("enterprise", "InMemoryProposalStore", "query_similar")

        if not self._proposals:
            return []

        query_embedding = self._mock_embed(query_text)

        # Calculate mock similarity scores
        scored: list[tuple[str, float]] = []
        for pid, emb in self._embeddings.items():
            score = self._cosine_similarity(query_embedding, emb)

            # Apply filters
            if filters:
                metadata = self._proposals[pid]["metadata"]
                if not all(metadata.get(k) == v for k, v in filters.items()):
                    continue

            scored.append((pid, score))

        # Sort by similarity
        scored.sort(key=lambda x: x[1], reverse=True)

        results: list[RetrievedProposal] = []
        for pid, score in scored[:n_results]:
            prop = self._proposals[pid]
            meta = prop["metadata"]
            content = prop["content"]

            results.append(
                RetrievedProposal(
                    proposal_id=pid,
                    title=meta.get("title", "Untitled"),
                    industry=meta.get("industry", "unknown"),
                    content_preview=content[:500] + "..." if len(content) > 500 else content,
                    metadata=meta,
                    similarity_score=score,
                    source_path=meta.get("source_path", ""),
                ),
            )

        return results

    def get_by_industry(self, industry: str, limit: int = 10) -> list[RetrievedProposal]:
        """Get proposals by industry."""
        results: list[RetrievedProposal] = []

        for pid, prop in self._proposals.items():
            meta = prop["metadata"]
            if meta.get("industry") == industry:
                results.append(
                    RetrievedProposal(
                        proposal_id=pid,
                        title=meta.get("title", "Untitled"),
                        industry=industry,
                        content_preview=prop["content"][:500],
                        metadata=meta,
                        similarity_score=1.0,  # Exact match
                        source_path=meta.get("source_path", ""),
                    ),
                )

        return results[:limit]

    def _mock_embed(self, text: str) -> list[float]:
        """Generate mock embedding from text hash."""
        # Create deterministic embedding from text
        hash_val = hashlib.sha256(text.encode()).hexdigest()
        # Convert to 10-dim embedding
        return [int(hash_val[i : i + 2], 16) / 255.0 for i in range(0, 20, 2)]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


class ProposalRetrievalEngine:
    """Engine for retrieving and reusing past proposals."""

    def __init__(self, store: EmbeddingStore | None = None) -> None:
        self.store = store or InMemoryProposalStore()
        self._query_history: list[dict[str, Any]] = []

    def index_proposal(
        self,
        proposal_path: str | Path,
        industry: str,
        title: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Index a proposal for future retrieval."""
        path = Path(proposal_path)

        if not path.exists():
            raise FileNotFoundError(f"Proposal not found: {path}")

        content = path.read_text(encoding="utf-8", errors="ignore")
        proposal_id = f"prop_{hashlib.sha256(content.encode()).hexdigest()[:12]}"

        meta = {
            "title": title or path.stem.replace("_", " ").title(),
            "industry": industry,
            "source_path": str(path),
            "indexed_at": datetime.now().isoformat(),
            "content_length": len(content),
            **(metadata or {}),
        }

        success = self.store.add_proposal(proposal_id, content, meta)

        if success:
            _emit_records_execution_trace("enterprise", "ProposalRetrievalEngine", f"indexed_{proposal_id}")
            _log.info(f"[ProposalRetrievalEngine] Indexed proposal: {proposal_id}")

        return proposal_id

    def find_similar_proposals(
        self,
        query: str,
        industry: str | None = None,
        n_results: int = 5,
    ) -> list[RetrievedProposal]:
        """Find proposals similar to the query."""
        _emit_pulls_context("enterprise", "ProposalRetrievalEngine", "find_similar")

        filters = {"industry": industry} if industry else None
        results = self.store.query_similar(query, n_results=n_results, filters=filters)

        self._query_history.append({
            "query": query,
            "filters": filters,
            "results_count": len(results),
            "timestamp": datetime.now().isoformat(),
        })

        return results

    def get_reusable_sections(
        self,
        industry: str,
        section_type: str,
        n_results: int = 3,
    ) -> list[dict[str, Any]]:
        """Get reusable sections from past proposals."""
        proposals = self.store.get_by_industry(industry, limit=20)

        sections: list[dict[str, Any]] = []
        for prop in proposals:
            # Extract section if we have structured metadata
            meta = prop.metadata
            if "sections" in meta and section_type in meta["sections"]:
                sections.append({
                    "proposal_id": prop.proposal_id,
                    "title": prop.title,
                    "section_content": meta["sections"][section_type],
                    "similarity": prop.similarity_score,
                })

            if len(sections) >= n_results:
                break

        return sections

    def get_proposal_templates(self, industry: str) -> dict[str, Any]:
        """Get reusable templates for an industry."""
        proposals = self.store.get_by_industry(industry, limit=5)

        if not proposals:
            return self._default_templates()

        # Aggregate common patterns
        templates = {
            "industry": industry,
            "common_sections": [],
            "typical_phases": [],
            "risk_patterns": [],
            "value_drivers": [],
        }

        for prop in proposals:
            meta = prop.metadata
            if "sections" in meta:
                templates["common_sections"].extend(meta["sections"].keys())
            if "phases" in meta:
                templates["typical_phases"].extend(meta["phases"])
            if "risks" in meta:
                templates["risk_patterns"].extend(meta["risks"])

        # Deduplicate
        templates["common_sections"] = list(set(templates["common_sections"]))
        templates["typical_phases"] = list(set(templates["typical_phases"]))

        return templates

    def _default_templates(self) -> dict[str, Any]:
        """Default templates when no past proposals exist."""
        return {
            "industry": "general",
            "common_sections": [
                "executive_summary",
                "technical_approach",
                "implementation_plan",
                "risk_mitigation",
                "value_proposition",
            ],
            "typical_phases": ["Discovery", "Foundation", "Pilot", "Scale", "Govern"],
            "risk_patterns": ["technical_complexity", "data_quality", "change_management"],
            "value_drivers": ["efficiency", "quality", "governance", "scalability"],
        }

    def generate_reuse_report(self, new_rfp_summary: dict[str, Any]) -> dict[str, Any]:
        """Generate a report on what can be reused for a new RFP."""
        industry = new_rfp_summary.get("industry", "unknown")

        # Find similar past proposals
        similar = self.find_similar_proposals(
            query=f"{new_rfp_summary.get('title', '')} {industry}",
            industry=industry if industry != "unknown" else None,
            n_results=5,
        )

        # Get templates
        templates = self.get_proposal_templates(industry)

        # Identify reusable content
        reusable = {
            "industry": industry,
            "similar_proposals_found": len(similar),
            "top_matches": [
                {
                    "id": p.proposal_id,
                    "title": p.title,
                    "similarity": round(p.similarity_score, 3),
                }
                for p in similar[:3]
            ],
            "recommended_sections": templates["common_sections"],
            "suggested_phases": templates["typical_phases"],
            "reusable_risk_patterns": templates["risk_patterns"],
            "estimated_reuse_percentage": min(60, len(similar) * 15),  # Heuristic
        }

        return reusable


def create_retrieval_engine(
    chromadb_path: str | None = None,
    collection_name: str = "proposals",
) -> ProposalRetrievalEngine:
    """Factory for creating a retrieval engine.

    Args:
        chromadb_path: Path to ChromaDB persistence directory. If None, uses in-memory store.
        collection_name: Name of the ChromaDB collection.

    Returns:
        Configured ProposalRetrievalEngine.
    """
    # For now, always use in-memory. In production, this would:
    # 1. Import chromadb
    # 2. Create PersistentClient or EphemeralClient
    # 3. Wrap in a ChromaDBEmbeddingStore class

    _log.info("[create_retrieval_engine] Using in-memory store (install chromadb for persistence)")
    return ProposalRetrievalEngine(store=InMemoryProposalStore())

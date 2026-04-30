"""
Past Research Retrieval System — apps_research.enterprise.

Vector-based semantic retrieval of past research artifacts
for knowledge reuse, source validation, and quality benchmarking.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_stores_embedding,
)
from tqdm import tqdm

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class RetrievedResearch:
    """A research artifact retrieved from the store."""

    research_id: str
    topic: str
    artifact_mode: str
    timestamp: str
    content_preview: str
    quality_score: float
    source_count: int
    claim_types: dict[str, int]
    metadata: dict[str, Any] = field(default_factory=dict)
    similarity_score: float = 0.0


@dataclass(frozen=True)
class SourceTrend:
    """Trend analysis for source usage."""

    source_type: str
    usage_count: int
    avg_confidence: float
    trend_direction: str


class InMemoryResearchStore:
    """In-memory store for research artifacts."""

    def __init__(self) -> None:
        self._research: dict[str, dict[str, Any]] = {}
        self._embeddings: dict[str, list[float]] = {}

    @traces_execute(layer="L4_STATE")
    def add_research(
        self,
        research_id: str,
        research_data: dict[str, Any],
        metadata: dict[str, Any],
    ) -> bool:
        """Store a research artifact."""
        _emit_stores_embedding("enterprise", "InMemoryResearchStore", research_id)

        self._research[research_id] = {
            "data": research_data,
            "metadata": metadata,
        }
        # Mock embedding from research content
        content_str = json.dumps(research_data, sort_keys=True)
        self._embeddings[research_id] = self._mock_embed(content_str)
        return True

    def query_similar(
        self,
        query: dict[str, Any],
        n_results: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievedResearch]:
        """Query for similar research artifacts."""
        _emit_reads_through("enterprise", "InMemoryResearchStore", "query_similar")

        if not self._research:
            return []

        # Create query embedding
        query_str = json.dumps(query, sort_keys=True)
        query_emb = self._mock_embed(query_str)

        # Score all research
        scored: list[tuple[str, float]] = []
        for research_id, emb in tqdm(self._embeddings.items(), desc="Processing", unit="item"):
            score = self._cosine_similarity(query_emb, emb)

            # Apply filters
            if filters:
                meta = self._research[research_id]["metadata"]
                if not all(meta.get(k) == v for k, v in filters.items()):
                    continue

            scored.append((research_id, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        results: list[RetrievedResearch] = []
        for research_id, score in tqdm(scored[:n_results], desc="Processing", unit="item"):
            rs = self._research[research_id]
            meta = rs["metadata"]
            data = rs["data"]

            results.append(
                RetrievedResearch(
                    research_id=research_id,
                    topic=meta.get("topic", "unknown"),
                    artifact_mode=meta.get("artifact_mode", "brief"),
                    timestamp=meta.get("timestamp", ""),
                    content_preview=data.get("content", "")[:500],
                    quality_score=data.get("quality_score", 0.0),
                    source_count=data.get("source_count", 0),
                    claim_types=data.get("claim_types", {}),
                    metadata=meta,
                    similarity_score=score,
                ),
            )

        return results

    def get_by_mode(self, mode: str, limit: int = 10) -> list[RetrievedResearch]:
        """Get research artifacts by mode."""
        results: list[RetrievedResearch] = []

        for research_id, rs in tqdm(self._research.items(), desc="Processing", unit="item"):
            meta = rs["metadata"]
            if meta.get("artifact_mode") == mode:
                data = rs["data"]
                results.append(
                    RetrievedResearch(
                        research_id=research_id,
                        topic=meta.get("topic", ""),
                        artifact_mode=mode,
                        timestamp=meta.get("timestamp", ""),
                        content_preview=data.get("content", "")[:500],
                        quality_score=data.get("quality_score", 0.0),
                        source_count=data.get("source_count", 0),
                        claim_types=data.get("claim_types", {}),
                        metadata=meta,
                        similarity_score=1.0,
                    ),
                )

        return sorted(results, key=lambda x: x.timestamp, reverse=True)[:limit]

    def _mock_embed(self, text: str) -> list[float]:
        """Generate mock embedding from text."""
        hash_val = hashlib.sha256(text.encode()).hexdigest()
        return [int(hash_val[i : i + 2], 16) / 255.0 for i in range(0, 20, 2)]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


class ResearchRetrievalEngine:
    """Engine for retrieving and analyzing past research."""

    def __init__(self, store: InMemoryResearchStore | None = None) -> None:
        self.store = store or InMemoryResearchStore()
        self._query_history: list[dict[str, Any]] = []

    def index_research(
        self,
        content: str,
        topic: str,
        artifact_mode: str,
        quality_score: float,
        source_count: int,
        claim_types: dict[str, int],
    ) -> str:
        """Index a research artifact for future retrieval."""
        research_id = f"research_{artifact_mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        research_data = {
            "content": content,
            "quality_score": quality_score,
            "source_count": source_count,
            "claim_types": claim_types,
        }

        meta = {
            "topic": topic,
            "artifact_mode": artifact_mode,
            "timestamp": datetime.now().isoformat(),
            "quality_score": quality_score,
        }

        success = self.store.add_research(research_id, research_data, meta)

        if success:
            _emit_records_execution_trace("enterprise", "ResearchRetrievalEngine", f"indexed_{research_id}")

        return research_id

    def find_similar_research(
        self,
        current_topic: str,
        artifact_mode: str,
        n_results: int = 5,
    ) -> list[RetrievedResearch]:
        """Find research similar to the current topic."""
        _emit_pulls_context("enterprise", "ResearchRetrievalEngine", "find_similar")

        # Build query
        query = {
            "topic": current_topic,
            "artifact_mode": artifact_mode,
        }

        results = self.store.query_similar(
            query,
            n_results=n_results,
            filters={"artifact_mode": artifact_mode},
        )

        self._query_history.append(
            {
                "query_type": "similar",
                "topic": current_topic,
                "results_count": len(results),
                "timestamp": datetime.now().isoformat(),
            }
        )

        return results

    def get_mode_history(self, mode: str, limit: int = 10) -> list[RetrievedResearch]:
        """Get historical research for a specific mode."""
        return self.store.get_by_mode(mode, limit=limit)

    def analyze_claim_trends(
        self,
        mode: str,
        window_size: int = 10,
    ) -> dict[str, SourceTrend]:
        """Analyze claim type trends for a mode."""
        artifacts = self.store.get_by_mode(mode, limit=window_size)

        if len(artifacts) < 3:
            return {}

        # Aggregate claim types
        claim_type_stats: dict[str, dict[str, Any]] = {}

        for art in tqdm(artifacts, desc="Processing", unit="item"):
            for claim_type, count in art.claim_types.items():
                if claim_type not in claim_type_stats:
                    claim_type_stats[claim_type] = {
                        "counts": [],
                        "total": 0,
                    }
                claim_type_stats[claim_type]["counts"].append(count)
                claim_type_stats[claim_type]["total"] += count

        trends: dict[str, SourceTrend] = {}
        for claim_type, stats in tqdm(claim_type_stats.items(), desc="Processing", unit="item"):
            counts = stats["counts"]
            if len(counts) >= 2:
                trend = "stable"
                if counts[-1] > counts[0] * 1.2:
                    trend = "increasing"
                elif counts[-1] < counts[0] * 0.8:
                    trend = "decreasing"

                avg_confidence = sum(counts) / len(counts) / max(stats["total"], 1)

                trends[claim_type] = SourceTrend(
                    source_type=claim_type,
                    usage_count=stats["total"],
                    avg_confidence=avg_confidence,
                    trend_direction=trend,
                )

        return trends

    def get_quality_benchmark(
        self,
        mode: str,
    ) -> dict[str, Any]:
        """Get quality benchmarks for a mode."""
        artifacts = self.store.get_by_mode(mode, limit=20)

        if not artifacts:
            return {"error": "no_historical_data"}

        # Calculate benchmarks
        quality_scores = [a.quality_score for a in artifacts]
        source_counts = [a.source_count for a in artifacts]

        return {
            "mode": mode,
            "sample_size": len(artifacts),
            "avg_quality_score": sum(quality_scores) / len(quality_scores),
            "min_quality_score": min(quality_scores),
            "max_quality_score": max(quality_scores),
            "avg_source_count": sum(source_counts) / len(source_counts),
            "quality_threshold_80th": sorted(quality_scores)[int(len(quality_scores) * 0.8)]
            if len(quality_scores) >= 5
            else 0.8,
        }

    def recommend_sources(
        self,
        topic: str,
        current_sources: list[str],
    ) -> list[dict[str, Any]]:
        """Recommend sources based on similar past research."""
        # Find similar research
        similar = self.store.query_similar(
            {"topic": topic},
            n_results=5,
        )

        if not similar:
            return []

        # Aggregate source references from similar research
        source_references: dict[str, int] = {}
        for art in similar:
            for source in art.metadata.get("sources", []):
                if source not in current_sources:
                    source_references[source] = source_references.get(source, 0) + 1

        # Sort by frequency
        recommendations: list[dict[str, Any]] = []
        for source, freq in sorted(source_references.items(), key=lambda x: x[1], reverse=True):
            recommendations.append(
                {
                    "source": source,
                    "frequency_in_similar": freq,
                    "recommendation": f"Consider adding '{source}' based on similar research",
                }
            )

        return recommendations[:5]


def create_retrieval_engine(
    chromadb_path: str | None = None,
    collection_name: str = "research_artifacts",
) -> ResearchRetrievalEngine:
    """Factory for creating a retrieval engine."""
    _log.info("[create_retrieval_engine] Using in-memory store (install chromadb for persistence)")
    return ResearchRetrievalEngine(store=InMemoryResearchStore())

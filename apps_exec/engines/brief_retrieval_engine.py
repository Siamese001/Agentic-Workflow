"""
Past Brief Retrieval System — apps_exec.enterprise.

Vector-based semantic retrieval of past executive briefs for
style consistency, content reuse, and quality benchmarking.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_stores_embedding,
)

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class RetrievedBrief:
    """An executive brief retrieved from the store."""

    brief_id: str
    audience_persona: str
    timestamp: str
    content_preview: str
    quality_score: float
    style_markers: dict[str, Any]
    word_count: int
    sections: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)
    similarity_score: float = 0.0


@dataclass(frozen=True)
class StyleTrend:
    """Trend analysis for a style dimension."""

    dimension: str
    values: list[float]
    trend_direction: str
    average_score: float
    best_example_id: str


class InMemoryBriefStore:
    """In-memory store for executive briefs."""

    def __init__(self) -> None:
        self._briefs: dict[str, dict[str, Any]] = {}
        self._embeddings: dict[str, list[float]] = {}

    def add_brief(
        self,
        brief_id: str,
        brief_data: dict[str, Any],
        metadata: dict[str, Any],
    ) -> bool:
        """Store an executive brief."""
        _emit_stores_embedding("enterprise", "InMemoryBriefStore", brief_id)

        self._briefs[brief_id] = {
            "data": brief_data,
            "metadata": metadata,
        }
        # Mock embedding from brief content
        content_str = json.dumps(brief_data, sort_keys=True)
        self._embeddings[brief_id] = self._mock_embed(content_str)
        return True

    def query_similar(
        self,
        query: dict[str, Any],
        n_results: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievedBrief]:
        """Query for similar briefs."""
        _emit_reads_through("enterprise", "InMemoryBriefStore", "query_similar")

        if not self._briefs:
            return []

        # Create query embedding
        query_str = json.dumps(query, sort_keys=True)
        query_emb = self._mock_embed(query_str)

        # Score all briefs
        scored: list[tuple[str, float]] = []
        for brief_id, emb in self._embeddings.items():
            score = self._cosine_similarity(query_emb, emb)

            # Apply filters
            if filters:
                meta = self._briefs[brief_id]["metadata"]
                if not all(meta.get(k) == v for k, v in filters.items()):
                    continue

            scored.append((brief_id, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        results: list[RetrievedBrief] = []
        for brief_id, score in scored[:n_results]:
            br = self._briefs[brief_id]
            meta = br["metadata"]
            data = br["data"]

            results.append(
                RetrievedBrief(
                    brief_id=brief_id,
                    audience_persona=meta.get("audience_persona", "unknown"),
                    timestamp=meta.get("timestamp", ""),
                    content_preview=data.get("content", "")[:500],
                    quality_score=data.get("quality_score", 0.0),
                    style_markers=data.get("style_markers", {}),
                    word_count=data.get("word_count", 0),
                    sections=data.get("sections", []),
                    metadata=meta,
                    similarity_score=score,
                )
            )

        return results

    def get_by_audience(self, audience: str, limit: int = 10) -> list[RetrievedBrief]:
        """Get briefs for a specific audience."""
        results: list[RetrievedBrief] = []

        for brief_id, br in self._briefs.items():
            meta = br["metadata"]
            if meta.get("audience_persona") == audience:
                data = br["data"]
                results.append(
                    RetrievedBrief(
                        brief_id=brief_id,
                        audience_persona=audience,
                        timestamp=meta.get("timestamp", ""),
                        content_preview=data.get("content", "")[:500],
                        quality_score=data.get("quality_score", 0.0),
                        style_markers=data.get("style_markers", {}),
                        word_count=data.get("word_count", 0),
                        sections=data.get("sections", []),
                        metadata=meta,
                        similarity_score=1.0,
                    )
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


class BriefRetrievalEngine:
    """Engine for retrieving and analyzing past briefs."""

    def __init__(self, store: InMemoryBriefStore | None = None) -> None:
        self.store = store or InMemoryBriefStore()
        self._query_history: list[dict[str, Any]] = []

    def index_brief(
        self,
        content: str,
        audience_persona: str,
        quality_score: float,
        style_markers: dict[str, Any],
        sections: list[str],
    ) -> str:
        """Index a brief for future retrieval."""
        brief_id = f"brief_{audience_persona}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        brief_data = {
            "content": content,
            "quality_score": quality_score,
            "style_markers": style_markers,
            "word_count": len(content.split()),
            "sections": sections,
        }

        meta = {
            "audience_persona": audience_persona,
            "timestamp": datetime.now().isoformat(),
            "quality_score": quality_score,
        }

        success = self.store.add_brief(brief_id, brief_data, meta)

        if success:
            _emit_records_execution_trace("enterprise", "BriefRetrievalEngine", f"indexed_{brief_id}")

        return brief_id

    def find_similar_briefs(
        self,
        current_brief: dict[str, Any],
        audience_persona: str,
        n_results: int = 5,
    ) -> list[RetrievedBrief]:
        """Find briefs similar to the current brief."""
        _emit_pulls_context("enterprise", "BriefRetrievalEngine", "find_similar")

        # Build query from current brief
        query = {
            "audience_persona": audience_persona,
            "sections": current_brief.get("sections", []),
        }

        results = self.store.query_similar(
            query,
            n_results=n_results,
            filters={"audience_persona": audience_persona},
        )

        self._query_history.append({
            "query_type": "similar",
            "audience": audience_persona,
            "results_count": len(results),
            "timestamp": datetime.now().isoformat(),
        })

        return results

    def get_audience_history(self, audience: str, limit: int = 10) -> list[RetrievedBrief]:
        """Get historical briefs for a specific audience."""
        return self.store.get_by_audience(audience, limit=limit)

    def analyze_style_trends(
        self,
        audience: str,
        window_size: int = 10,
    ) -> dict[str, StyleTrend]:
        """Analyze style trends for an audience."""
        # Get recent briefs for this audience
        briefs = self.store.get_by_audience(audience, limit=window_size)

        if len(briefs) < 3:
            return {}

        # Analyze by style dimension
        dimensions = ["buzzword_density", "evidence_density", "readability_score", "professional_tone"]
        trends: dict[str, StyleTrend] = {}

        for dim in dimensions:
            values: list[float] = []
            best_score = 0.0
            best_id = ""

            for brief in briefs:
                score = brief.style_markers.get(dim, 0.0)
                values.append(score)
                if score > best_score:
                    best_score = score
                    best_id = brief.brief_id

            if values:
                avg = sum(values) / len(values)
                # Trend direction
                if len(values) >= 2:
                    slope = (values[-1] - values[0]) / len(values)
                    if slope > 0.05:
                        direction = "improving"
                    elif slope < -0.05:
                        direction = "declining"
                    else:
                        direction = "stable"
                else:
                    direction = "stable"

                trends[dim] = StyleTrend(
                    dimension=dim,
                    values=values,
                    trend_direction=direction,
                    average_score=avg,
                    best_example_id=best_id,
                )

        return trends

    def get_style_benchmark(
        self,
        audience: str,
    ) -> dict[str, Any]:
        """Get style benchmarks for an audience."""
        briefs = self.store.get_by_audience(audience, limit=20)

        if not briefs:
            return {"error": "no_historical_data"}

        # Calculate benchmarks
        quality_scores = [b.quality_score for b in briefs]
        word_counts = [b.word_count for b in briefs]

        # Aggregate style markers
        marker_sums: dict[str, float] = {}
        marker_counts: dict[str, int] = {}

        for brief in briefs:
            for marker, value in brief.style_markers.items():
                if isinstance(value, (int, float)):
                    marker_sums[marker] = marker_sums.get(marker, 0.0) + value
                    marker_counts[marker] = marker_counts.get(marker, 0) + 1

        marker_avgs = {
            k: marker_sums[k] / marker_counts[k]
            for k in marker_sums
        }

        return {
            "audience": audience,
            "sample_size": len(briefs),
            "avg_quality_score": sum(quality_scores) / len(quality_scores),
            "min_quality_score": min(quality_scores),
            "max_quality_score": max(quality_scores),
            "avg_word_count": sum(word_counts) / len(word_counts),
            "style_benchmarks": marker_avgs,
        }

    def recommend_sections(
        self,
        audience: str,
        current_sections: list[str],
    ) -> list[dict[str, Any]]:
        """Recommend sections based on high-performing past briefs."""
        briefs = self.store.get_by_audience(audience, limit=10)

        if not briefs:
            return []

        # Find sections in high-quality briefs not in current briefs
        current_set = set(current_sections)
        high_quality = [b for b in briefs if b.quality_score > 0.8]

        if not high_quality:
            high_quality = briefs

        section_frequency: dict[str, int] = {}
        for brief in high_quality:
            for section in brief.sections:
                section_frequency[section] = section_frequency.get(section, 0) + 1

        recommendations: list[dict[str, Any]] = []
        for section, freq in section_frequency.items():
            if section not in current_set:
                recommendations.append({
                    "section": section,
                    "frequency_in_top_briefs": freq,
                    "recommendation": f"Consider adding '{section}' section",
                })

        # Sort by frequency
        recommendations.sort(key=lambda x: x["frequency_in_top_briefs"], reverse=True)
        return recommendations[:5]


def create_retrieval_engine(
    chromadb_path: str | None = None,
    collection_name: str = "briefs",
) -> BriefRetrievalEngine:
    """Factory for creating a retrieval engine."""
    _log.info("[create_retrieval_engine] Using in-memory store (install chromadb for persistence)")
    return BriefRetrievalEngine(store=InMemoryBriefStore())

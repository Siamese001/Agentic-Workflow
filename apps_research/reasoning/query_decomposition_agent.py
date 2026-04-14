"""
L1 Research Query Decomposition Agent — apps_research.enterprise.

Decomposes research topics into structured query components
with source requirements and claim-type mapping.

Layer 1 Cognition: Context expansion, adaptive retrieval, intent parsing.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_pulls_context,
    _emit_records_execution_trace,
)
from tqdm import tqdm

_log = logging.getLogger(__name__)


class QueryType(str, Enum):
    """Types of research queries."""

    EXPLORATORY = "exploratory"  # Open-ended discovery
    COMPARATIVE = "comparative"  # Side-by-side comparison
    TREND_ANALYSIS = "trend_analysis"  # Temporal pattern detection
    POSITION_STATEMENT = "position_statement"  # Argument construction
    TECHNICAL_DEEP_DIVE = "technical_deep_dive"  # Detailed technical analysis
    MARKET_LANDSCAPE = "market_landscape"  # Competitive overview


class EvidenceRequirement(str, Enum):
    """Evidence requirement levels."""

    REQUIRED = "required"  # Must have sources
    PREFERRED = "preferred"  # Nice to have
    OPTIONAL = "optional"  # Can be inferred


@dataclass(frozen=True)
class ResearchQueryComponent:
    """A single decomposed research query component."""

    component_id: str
    parent_query_id: str
    query_text: str
    query_type: QueryType
    evidence_required: EvidenceRequirement
    sources_needed: int
    claim_types_expected: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    search_keywords: list[str] = field(default_factory=list)


@dataclass
class QueryDecomposition:
    """Full decomposition of a research query."""

    original_topic: str
    artifact_mode: str
    target_audience: str
    components: list[ResearchQueryComponent] = field(default_factory=list)
    execution_order: list[str] = field(default_factory=list)
    source_gaps: list[str] = field(default_factory=list)
    estimated_research_time_ms: int = 0


@dataclass
class DecompositionSummary:
    """Summary across all decomposed queries."""

    total_topics: int = 0
    total_components: int = 0
    total_sources_needed: int = 0
    query_type_distribution: dict[str, int] = field(default_factory=dict)
    evidence_coverage_ratio: float = 0.0


class QueryDecomposer:
    """L1 agent for decomposing research queries."""

    # Mode-specific query patterns
    MODE_QUERY_PATTERNS: dict[str, list[tuple[str, QueryType, EvidenceRequirement, int]]] = {
        "brief": [
            ("executive_summary", QueryType.EXPLORATORY, EvidenceRequirement.REQUIRED, 3),
            ("key_findings", QueryType.EXPLORATORY, EvidenceRequirement.REQUIRED, 5),
            ("strategic_implications", QueryType.EXPLORATORY, EvidenceRequirement.PREFERRED, 2),
        ],
        "comparison": [
            ("comparison_overview", QueryType.COMPARATIVE, EvidenceRequirement.REQUIRED, 2),
            ("dimension_analysis", QueryType.COMPARATIVE, EvidenceRequirement.REQUIRED, 4),
            ("recommendation", QueryType.POSITION_STATEMENT, EvidenceRequirement.PREFERRED, 2),
        ],
        "trend": [
            ("trend_overview", QueryType.TREND_ANALYSIS, EvidenceRequirement.REQUIRED, 3),
            ("signal_analysis", QueryType.TREND_ANALYSIS, EvidenceRequirement.REQUIRED, 4),
            ("horizon_implications", QueryType.TREND_ANALYSIS, EvidenceRequirement.PREFERRED, 2),
        ],
        "position": [
            ("position_statement", QueryType.POSITION_STATEMENT, EvidenceRequirement.REQUIRED, 1),
            ("supporting_evidence", QueryType.EXPLORATORY, EvidenceRequirement.REQUIRED, 5),
            ("counterarguments", QueryType.COMPARATIVE, EvidenceRequirement.PREFERRED, 3),
            ("conclusion", QueryType.POSITION_STATEMENT, EvidenceRequirement.OPTIONAL, 1),
        ],
        "thought_leadership": [
            ("hook", QueryType.EXPLORATORY, EvidenceRequirement.OPTIONAL, 1),
            ("insight", QueryType.POSITION_STATEMENT, EvidenceRequirement.PREFERRED, 2),
            ("evidence", QueryType.EXPLORATORY, EvidenceRequirement.REQUIRED, 3),
            ("call_to_action", QueryType.POSITION_STATEMENT, EvidenceRequirement.OPTIONAL, 1),
        ],
    }

    # Keywords for query type detection
    QUERY_TYPE_KEYWORDS: dict[QueryType, list[str]] = {
        QueryType.COMPARATIVE: ["compare", "versus", "vs", "difference", "better", "best"],
        QueryType.TREND_ANALYSIS: ["trend", "future", "predict", "forecast", "emerging", "growing"],
        QueryType.POSITION_STATEMENT: ["should", "position", "recommend", "strategy", "approach"],
        QueryType.TECHNICAL_DEEP_DIVE: ["implementation", "architecture", "technical", "how does"],
        QueryType.MARKET_LANDSCAPE: ["market", "competitive", "landscape", "ecosystem", "vendors"],
    }

    def __init__(self) -> None:
        self._decomposition_cache: dict[str, QueryDecomposition] = {}

    def decompose(
        self,
        topic: str,
        artifact_mode: str,
        target_audience: str = "technical",
        comparison_subjects: list[str] | None = None,
    ) -> QueryDecomposition:
        """Decompose a research query into components."""
        _emit_records_execution_trace("enterprise", "QueryDecomposer", f"decompose_{artifact_mode}")

        # Check cache
        cache_key = f"{topic}:{artifact_mode}:{hash(str(comparison_subjects)) % 10000}"
        if cache_key in self._decomposition_cache:
            return self._decomposition_cache[cache_key]

        # Detect query type from topic
        detected_type = self._detect_query_type(topic)

        # Get mode-specific components
        patterns = self.MODE_QUERY_PATTERNS.get(artifact_mode, self.MODE_QUERY_PATTERNS["brief"])

        components: list[ResearchQueryComponent] = []
        for idx, (section_name, query_type, evidence_req, sources) in tqdm(
            enumerate(patterns, 1), desc="Processing", unit="item"
        ):
            comp_id = f"Q-{artifact_mode[:3].upper()}-{idx:02d}"

            # Adjust query type based on section
            effective_type = query_type if query_type != QueryType.EXPLORATORY else detected_type

            components.append(
                ResearchQueryComponent(
                    component_id=comp_id,
                    parent_query_id=cache_key,
                    query_text=self._generate_query_text(topic, section_name, effective_type),
                    query_type=effective_type,
                    evidence_required=evidence_req,
                    sources_needed=sources,
                    claim_types_expected=self._determine_claim_types(effective_type, evidence_req),
                    dependencies=self._determine_dependencies(components, idx),
                    search_keywords=self._generate_keywords(topic, section_name),
                ),
            )

        # Determine execution order
        execution_order = self._determine_execution_order(components)

        # Calculate estimated time
        total_time = sum(c.sources_needed * 30000 for c in components)  # 30s per source

        # Identify source gaps
        source_gaps = self._identify_source_gaps(components)

        decomposition = QueryDecomposition(
            original_topic=topic,
            artifact_mode=artifact_mode,
            target_audience=target_audience,
            components=components,
            execution_order=execution_order,
            source_gaps=source_gaps,
            estimated_research_time_ms=total_time,
        )

        self._decomposition_cache[cache_key] = decomposition
        return decomposition

    def decompose_batch(
        self,
        queries: list[tuple[str, str, str]],
    ) -> list[QueryDecomposition]:
        """Decompose multiple research queries."""
        _emit_pulls_context("enterprise", "QueryDecomposer", "decompose_batch")

        results: list[QueryDecomposition] = []
        for topic, mode, audience in tqdm(queries, desc="Processing", unit="item"):
            try:
                decomp = self.decompose(topic, mode, audience)
                results.append(decomp)
            except Exception as exc:
                _log.error(f"[QueryDecomposer] Failed to decompose {topic}: {exc}")
                results.append(
                    QueryDecomposition(
                        original_topic=topic,
                        artifact_mode=mode,
                        target_audience=audience,
                        source_gaps=["decomposition_failed"],
                    ),
                )

        return results

    def generate_summary(
        self,
        decompositions: list[QueryDecomposition],
    ) -> DecompositionSummary:
        """Generate summary statistics across all decompositions."""
        _emit_captures_pattern("enterprise", "QueryDecomposer", "generate_summary")

        summary = DecompositionSummary()
        summary.total_topics = len(decompositions)

        all_components: list[ResearchQueryComponent] = []
        for decomp in decompositions:
            all_components.extend(decomp.components)

        summary.total_components = len(all_components)
        summary.total_sources_needed = sum(c.sources_needed for c in all_components)

        # Query type distribution
        type_dist: dict[str, int] = {}
        for c in all_components:
            type_key = c.query_type.value
            type_dist[type_key] = type_dist.get(type_key, 0) + 1
        summary.query_type_distribution = type_dist

        # Evidence coverage
        required_evidence = sum(
            1 for c in all_components if c.evidence_required == EvidenceRequirement.REQUIRED
        )
        covered_evidence = sum(
            1
            for c in all_components
            if c.evidence_required == EvidenceRequirement.REQUIRED and c.sources_needed > 0
        )
        summary.evidence_coverage_ratio = covered_evidence / max(required_evidence, 1)

        return summary

    def _detect_query_type(self, topic: str) -> QueryType:
        """Detect query type from topic text."""
        topic_lower = topic.lower()

        scores: dict[QueryType, int] = {}
        for qtype, keywords in self.QUERY_TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in topic_lower)
            if score > 0:
                scores[qtype] = score

        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]

        return QueryType.EXPLORATORY

    def _generate_query_text(
        self,
        topic: str,
        section_name: str,
        query_type: QueryType,
    ) -> str:
        """Generate specific query text for a component."""
        templates: dict[QueryType, str] = {
            QueryType.EXPLORATORY: f"What are the key aspects of {topic} relevant to {section_name}?",
            QueryType.COMPARATIVE: f"How does {topic} compare across different dimensions for {section_name}?",
            QueryType.TREND_ANALYSIS: f"What trends in {topic} are relevant to {section_name}?",
            QueryType.POSITION_STATEMENT: f"What position should be taken on {topic} regarding {section_name}?",
            QueryType.TECHNICAL_DEEP_DIVE: f"What technical details of {topic} are needed for {section_name}?",
            QueryType.MARKET_LANDSCAPE: f"What market context for {topic} supports {section_name}?",
        }

        return templates.get(query_type, f"Research {topic} for {section_name}")

    def _determine_claim_types(
        self,
        query_type: QueryType,
        evidence_req: EvidenceRequirement,
    ) -> list[str]:
        """Determine expected claim types for this component."""
        if evidence_req == EvidenceRequirement.REQUIRED:
            return ["direct_evidence", "interpretation"]
        elif evidence_req == EvidenceRequirement.PREFERRED:
            return ["interpretation", "analyst_inference"]
        else:
            return ["analyst_inference", "assumption"]

    def _determine_dependencies(
        self,
        existing_components: list[ResearchQueryComponent],
        current_idx: int,
    ) -> list[str]:
        """Determine which components this component depends on."""
        # First component has no dependencies
        if current_idx == 1 or not existing_components:
            return []

        # Later components may depend on foundational ones
        foundational = [c.component_id for c in existing_components[:2]]
        return foundational

    def _generate_keywords(
        self,
        topic: str,
        section_name: str,
    ) -> list[str]:
        """Generate search keywords for this component."""
        base_keywords = topic.lower().split()
        section_keywords = section_name.lower().replace("_", " ").split()

        return list(set(base_keywords + section_keywords))[:10]

    def _determine_execution_order(
        self,
        components: list[ResearchQueryComponent],
    ) -> list[str]:
        """Determine optimal execution order."""
        # Sort by evidence requirement (required first)
        priority = {
            EvidenceRequirement.REQUIRED: 1,
            EvidenceRequirement.PREFERRED: 2,
            EvidenceRequirement.OPTIONAL: 3,
        }

        sorted_comps = sorted(components, key=lambda c: priority.get(c.evidence_required, 2))
        return [c.component_id for c in sorted_comps]

    def _identify_source_gaps(
        self,
        components: list[ResearchQueryComponent],
    ) -> list[str]:
        """Identify potential source gaps."""
        gaps: list[str] = []

        # Check for components with high source requirements
        high_source_comps = [c for c in components if c.sources_needed > 5]
        for c in high_source_comps:
            gaps.append(f"{c.component_id}:high_source_requirement")

        # Check for comparative components without comparison subjects
        comparative_comps = [c for c in components if c.query_type == QueryType.COMPARATIVE]
        for c in comparative_comps:
            if not any(kw in ["compare", "versus", "vs"] for kw in c.search_keywords):
                gaps.append(f"{c.component_id}:missing_comparison_targets")

        return gaps


class QueryDecompositionAgent:
    """Agent wrapper for research query decomposition."""

    def __init__(self) -> None:
        self.decomposer = QueryDecomposer()

    def analyze_research_query(
        self,
        topic: str,
        artifact_mode: str,
        target_audience: str = "technical",
    ) -> tuple[QueryDecomposition, DecompositionSummary]:
        """Analyze a research query."""
        _emit_records_execution_trace("enterprise", "QueryDecompositionAgent", "analyze_query")

        # Decompose the query
        decomposition = self.decomposer.decompose(topic, artifact_mode, target_audience)

        # Generate summary (single query, so simple stats)
        summary = DecompositionSummary(
            total_topics=1,
            total_components=len(decomposition.components),
            total_sources_needed=sum(c.sources_needed for c in decomposition.components),
            query_type_distribution={c.query_type.value: 1 for c in decomposition.components},
        )

        return decomposition, summary

    def get_research_execution_plan(
        self,
        decomposition: QueryDecomposition,
    ) -> dict[str, Any]:
        """Generate a research execution plan from decomposition."""
        total_sources = sum(c.sources_needed for c in decomposition.components)
        required_sources = sum(
            c.sources_needed
            for c in decomposition.components
            if c.evidence_required == EvidenceRequirement.REQUIRED
        )

        return {
            "topic": decomposition.original_topic,
            "artifact_mode": decomposition.artifact_mode,
            "target_audience": decomposition.target_audience,
            "total_components": len(decomposition.components),
            "total_sources_needed": total_sources,
            "required_sources": required_sources,
            "execution_sequence": decomposition.execution_order,
            "estimated_time_ms": decomposition.estimated_research_time_ms,
            "source_gaps": decomposition.source_gaps,
            "component_breakdown": [
                {
                    "id": c.component_id,
                    "type": c.query_type.value,
                    "evidence": c.evidence_required.value,
                    "sources": c.sources_needed,
                }
                for c in decomposition.components
            ],
        }

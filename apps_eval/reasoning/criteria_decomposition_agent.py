"""
L1 Evaluation Criteria Decomposition Agent — apps_eval.enterprise.

Decomposes evaluation criteria into structured, measurable test components
with dependency mapping and coverage analysis.

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

_log = logging.getLogger(__name__)


class CriteriaType(str, Enum):
    """Classification of evaluation criteria types."""

    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    RELIABILITY = "reliability"
    USABILITY = "usability"
    SCALABILITY = "scalability"
    COMPLIANCE = "compliance"
    DETERMINISM = "determinism"


class TestComplexity(str, Enum):
    """Test implementation complexity tiers."""

    UNIT = "unit"  # Single function/component
    INTEGRATION = "integration"  # Multi-component
    SYSTEM = "system"  # End-to-end
    BENCHMARK = "benchmark"  # Performance/stress


@dataclass(frozen=True)
class TestComponent:
    """A single decomposed test component from a criteria."""

    component_id: str
    parent_criteria_id: str
    name: str
    description: str
    criteria_type: CriteriaType
    complexity: TestComplexity
    test_method: str  # unit, integration, property_based, fuzz
    coverage_target: float  # 0-1
    dependencies: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)


@dataclass
class CriteriaDecomposition:
    """Full decomposition of an evaluation criteria."""

    source_criteria_id: str
    source_text: str
    dimension: str
    weight: float
    components: list[TestComponent] = field(default_factory=list)
    test_order: list[str] = field(default_factory=list)
    estimated_execution_time_ms: int = 0
    coverage_gaps: list[str] = field(default_factory=list)


@dataclass
class DecompositionSummary:
    """Summary across all decomposed criteria."""

    total_criteria: int = 0
    total_components: int = 0
    total_estimated_time_ms: int = 0
    coverage_by_dimension: dict[str, float] = field(default_factory=dict)
    complexity_distribution: dict[str, int] = field(default_factory=dict)
    test_type_distribution: dict[str, int] = field(default_factory=dict)
    critical_path: list[str] = field(default_factory=list)


class CriteriaDecomposer:
    """L1 agent for decomposing evaluation criteria."""

    # Pattern maps for criteria classification
    TYPE_PATTERNS: dict[CriteriaType, list[str]] = {
        CriteriaType.PERFORMANCE: [
            "latency", "throughput", "response time", "milliseconds",
            "seconds", "concurrent", "load", "scale", "benchmark",
            "ops per second", "requests per", "rps", "tps",
        ],
        CriteriaType.SECURITY: [
            "encrypt", "authentication", "authorization", "audit",
            "penetration", "vulnerability", "access control", "rbac",
            "mfa", "sso", "security", "sanitize", "validate",
        ],
        CriteriaType.RELIABILITY: [
            "uptime", "availability", "fault tolerance", "retry",
            "circuit breaker", "graceful degradation", "failure",
            "recovery", "backup", "replication", "mttr", "mtbf",
        ],
        CriteriaType.SCALABILITY: [
            "horizontal scale", "vertical scale", "shard", "partition",
            "distributed", "cluster", "node", "replica", "elastic",
            "auto-scale", "million", "billion", "terabyte",
        ],
        CriteriaType.COMPLIANCE: [
            "gdpr", "hipaa", "soc2", "iso27001", "compliance",
            "regulatory", "audit", "certification", "standard",
        ],
        CriteriaType.DETERMINISM: [
            "deterministic", "repeatable", "idempotent", "pure function",
            "no side effects", "immutable", "stable output", "time-independent",
        ],
    }

    def __init__(self) -> None:
        self._decomposition_cache: dict[str, CriteriaDecomposition] = {}

    def decompose(
        self,
        criteria_id: str,
        criteria_text: str,
        dimension: str,
        weight: float,
    ) -> CriteriaDecomposition:
        """Decompose a single evaluation criteria into test components."""
        _emit_records_execution_trace("enterprise", "CriteriaDecomposer", f"decompose_{criteria_id}")

        # Check cache
        cache_key = f"{criteria_id}:{hash(criteria_text) % 10000}"
        if cache_key in self._decomposition_cache:
            return self._decomposition_cache[cache_key]

        # Classify criteria type
        criteria_type = self._classify_criteria_type(criteria_text)

        # Extract components based on patterns
        components = self._extract_components(criteria_id, criteria_text, criteria_type)

        # Determine test execution order
        test_order = self._determine_test_order(components)

        # Calculate execution time estimate
        total_time = sum(self._estimate_execution_time(c) for c in components)

        # Identify coverage gaps
        coverage_gaps = self._identify_coverage_gaps(criteria_text, components)

        decomposition = CriteriaDecomposition(
            source_criteria_id=criteria_id,
            source_text=criteria_text,
            dimension=dimension,
            weight=weight,
            components=components,
            test_order=test_order,
            estimated_execution_time_ms=total_time,
            coverage_gaps=coverage_gaps,
        )

        self._decomposition_cache[cache_key] = decomposition
        return decomposition

    def decompose_batch(
        self,
        criteria_items: list[tuple[str, str, str, float]],
    ) -> list[CriteriaDecomposition]:
        """Decompose multiple evaluation criteria."""
        _emit_pulls_context("enterprise", "CriteriaDecomposer", "decompose_batch")

        results: list[CriteriaDecomposition] = []
        for criteria_id, criteria_text, dimension, weight in criteria_items:
            try:
                decomp = self.decompose(criteria_id, criteria_text, dimension, weight)
                results.append(decomp)
            except Exception as exc:
                _log.error(f"[CriteriaDecomposer] Failed to decompose {criteria_id}: {exc}")
                # Return minimal decomposition on failure
                results.append(
                    CriteriaDecomposition(
                        source_criteria_id=criteria_id,
                        source_text=criteria_text,
                        dimension=dimension,
                        weight=weight,
                        coverage_gaps=["decomposition_failed"],
                    )
                )

        return results

    def generate_summary(
        self,
        decompositions: list[CriteriaDecomposition],
    ) -> DecompositionSummary:
        """Generate summary statistics across all decompositions."""
        _emit_captures_pattern("enterprise", "CriteriaDecomposer", "generate_summary")

        summary = DecompositionSummary()
        summary.total_criteria = len(decompositions)

        complexity_dist: dict[str, int] = {}
        type_dist: dict[str, int] = {}
        dim_coverage: dict[str, list[float]] = {}

        for decomp in decompositions:
            summary.total_components += len(decomp.components)
            summary.total_estimated_time_ms += decomp.estimated_execution_time_ms

            # Track dimension coverage
            coverage = 1.0 - (len(decomp.coverage_gaps) / max(len(decomp.components), 1))
            if decomp.dimension not in dim_coverage:
                dim_coverage[decomp.dimension] = []
            dim_coverage[decomp.dimension].append(coverage)

            for comp in decomp.components:
                complexity_dist[comp.complexity.value] = complexity_dist.get(comp.complexity.value, 0) + 1
                type_dist[comp.criteria_type.value] = type_dist.get(comp.criteria_type.value, 0) + 1

        summary.complexity_distribution = complexity_dist
        summary.test_type_distribution = type_dist
        summary.coverage_by_dimension = {
            dim: sum(covs) / len(covs) for dim, covs in dim_coverage.items()
        }

        # Identify critical path (highest weight items with most dependencies)
        weighted_items = sorted(
            decompositions,
            key=lambda d: d.weight * len([c for c in d.components if c.complexity == TestComplexity.BENCHMARK]),
            reverse=True,
        )
        summary.critical_path = [d.source_criteria_id for d in weighted_items[:5]]

        return summary

    def _classify_criteria_type(self, text: str) -> CriteriaType:
        """Classify criteria by type based on keyword patterns."""
        text_lower = text.lower()

        scores: dict[CriteriaType, int] = {}
        for criteria_type, patterns in self.TYPE_PATTERNS.items():
            score = sum(1 for p in patterns if p in text_lower)
            if score > 0:
                scores[criteria_type] = score

        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]

        return CriteriaType.FUNCTIONAL

    def _extract_components(
        self,
        criteria_id: str,
        criteria_text: str,
        criteria_type: CriteriaType,
    ) -> list[TestComponent]:
        """Extract test components from criteria text."""
        components: list[TestComponent] = []

        # Parse compound criteria
        sub_criteria = self._split_compound_criteria(criteria_text)

        for idx, sub_crit in enumerate(sub_criteria, 1):
            comp_id = f"{criteria_id}-TC{idx:02d}"

            # Determine complexity and test method
            complexity = self._estimate_complexity(sub_crit)
            test_method = self._determine_test_method(sub_crit, complexity)

            components.append(
                TestComponent(
                    component_id=comp_id,
                    parent_criteria_id=criteria_id,
                    name=self._generate_component_name(sub_crit),
                    description=sub_crit,
                    criteria_type=criteria_type,
                    complexity=complexity,
                    test_method=test_method,
                    coverage_target=0.8 if complexity == TestComplexity.UNIT else 0.9,
                    success_criteria=self._generate_success_criteria(sub_crit, criteria_type),
                )
            )

        return components

    def _split_compound_criteria(self, text: str) -> list[str]:
        """Split compound criteria into individual items."""
        import re

        separators = [
            r";\s*",
            r",\s+and\s+",
            r"\s+and\s+(?=must|shall|should|will)",
            r"\s+as well as\s+",
        ]

        parts = [text]
        for sep in separators:
            new_parts: list[str] = []
            for part in parts:
                new_parts.extend(re.split(sep, part, flags=re.IGNORECASE))
            parts = [p.strip() for p in new_parts if p.strip()]

        return parts if parts else [text]

    def _estimate_complexity(self, text: str) -> TestComplexity:
        """Estimate test complexity from text analysis."""
        text_lower = text.lower()

        # Benchmark indicators
        if any(kw in text_lower for kw in ["performance", "latency", "throughput", "benchmark", "load test"]):
            return TestComplexity.BENCHMARK

        # System indicators
        if any(kw in text_lower for kw in ["end-to-end", "e2e", "workflow", "pipeline", "full stack"]):
            return TestComplexity.SYSTEM

        # Integration indicators
        if any(kw in text_lower for kw in ["integration", "api", "database", "service", "component"]):
            return TestComplexity.INTEGRATION

        return TestComplexity.UNIT

    def _determine_test_method(self, text: str, complexity: TestComplexity) -> str:
        """Determine appropriate test method."""
        text_lower = text.lower()

        if complexity == TestComplexity.BENCHMARK:
            return "performance_benchmark"

        if "property" in text_lower or "invariant" in text_lower:
            return "property_based"

        if "fuzz" in text_lower or "random" in text_lower:
            return "fuzzing"

        if complexity == TestComplexity.UNIT:
            return "unit_test"

        return "integration_test"

    def _estimate_execution_time(self, component: TestComponent) -> int:
        """Estimate execution time in milliseconds."""
        time_map = {
            TestComplexity.UNIT: 100,  # 100ms
            TestComplexity.INTEGRATION: 500,  # 500ms
            TestComplexity.SYSTEM: 2000,  # 2s
            TestComplexity.BENCHMARK: 10000,  # 10s
        }
        return time_map.get(component.complexity, 500)

    def _generate_component_name(self, text: str) -> str:
        """Generate a short component name from criteria text."""
        words = text.split()[:6]
        key_words = [w for w in words if len(w) > 3 and w.isalpha()]

        if key_words:
            return " ".join(key_words[:3]).title()

        return "Test Component"

    def _generate_success_criteria(self, text: str, criteria_type: CriteriaType) -> list[str]:
        """Generate success criteria for a component."""
        criteria: list[str] = []

        # Base criterion
        criteria.append("Test passes with expected outcome")

        # Type-specific criteria
        if criteria_type == CriteriaType.PERFORMANCE:
            criteria.extend([
                "Performance metric meets defined threshold",
                "No degradation under concurrent load",
            ])
        elif criteria_type == CriteriaType.SECURITY:
            criteria.extend([
                "Security scan passes with no critical findings",
                "Access controls properly enforced",
            ])
        elif criteria_type == CriteriaType.DETERMINISM:
            criteria.extend([
                "Output is identical across multiple executions",
                "No time-dependent or random dependencies",
            ])

        return criteria

    def _determine_test_order(self, components: list[TestComponent]) -> list[str]:
        """Determine optimal test execution order."""
        # Run unit tests first, then integration, then system, then benchmarks
        complexity_order = {
            TestComplexity.UNIT: 1,
            TestComplexity.INTEGRATION: 2,
            TestComplexity.SYSTEM: 3,
            TestComplexity.BENCHMARK: 4,
        }

        sorted_components = sorted(
            components,
            key=lambda c: complexity_order.get(c.complexity, 2),
        )

        return [c.component_id for c in sorted_components]

    def _identify_coverage_gaps(self, text: str, components: list[TestComponent]) -> list[str]:
        """Identify potential coverage gaps in the criteria."""
        gaps: list[str] = []
        text_lower = text.lower()

        # Check for quantified criteria without specific thresholds
        if any(kw in text_lower for kw in ["fast", "quick", "responsive"]):
            if not any(kw in text_lower for kw in ["ms", "milliseconds", "seconds", "<"]):
                gaps.append("missing_performance_threshold")

        # Check for edge case coverage
        if "error" not in text_lower and "failure" not in text_lower:
            gaps.append("missing_error_handling_tests")

        # Check for scale context
        if "scale" in text_lower and not any(kw in text_lower for kw in ["concurrent", "parallel", "load"]):
            gaps.append("missing_scale_parameters")

        return gaps


class CriteriaDecompositionAgent:
    """Agent wrapper for evaluation criteria decomposition."""

    def __init__(self) -> None:
        self.decomposer = CriteriaDecomposer()

    def analyze_evaluation_criteria(
        self,
        criteria_items: list[dict[str, Any]],
    ) -> tuple[list[CriteriaDecomposition], DecompositionSummary]:
        """Analyze all evaluation criteria."""
        _emit_records_execution_trace("enterprise", "CriteriaDecompositionAgent", "analyze_criteria")

        # Convert to tuples for batch processing
        criteria_tuples = [
            (c["criteria_id"], c["text"], c.get("dimension", "general"), c.get("weight", 1.0))
            for c in criteria_items
        ]

        # Decompose all criteria
        decompositions = self.decomposer.decompose_batch(criteria_tuples)

        # Generate summary
        summary = self.decomposer.generate_summary(decompositions)

        return decompositions, summary

    def get_test_execution_plan(
        self,
        decompositions: list[CriteriaDecomposition],
    ) -> dict[str, Any]:
        """Generate a test execution plan from decompositions."""
        # Aggregate all components
        all_components: list[TestComponent] = []
        for d in decompositions:
            all_components.extend(d.components)

        # Sort by complexity and dimension weight
        def sort_key(c: TestComponent) -> tuple:
            decomp = next((d for d in decompositions if d.source_criteria_id == c.parent_criteria_id), None)
            priority = decomp.weight if decomp else 1.0
            complexity_order = {"unit": 1, "integration": 2, "system": 3, "benchmark": 4}
            return (priority, complexity_order.get(c.complexity.value, 2))

        sorted_components = sorted(all_components, key=sort_key)

        # Calculate execution batches
        max_batch_time_ms = 30000  # 30 seconds per batch
        current_batch_time = 0
        current_batch: list[str] = []
        batches: list[list[str]] = []

        for comp in sorted_components:
            time_ms = self.decomposer._estimate_execution_time(comp)

            if current_batch_time + time_ms > max_batch_time_ms:
                batches.append(current_batch)
                current_batch = [comp.component_id]
                current_batch_time = time_ms
            else:
                current_batch.append(comp.component_id)
                current_batch_time += time_ms

        if current_batch:
            batches.append(current_batch)

        return {
            "total_components": len(all_components),
            "total_estimated_time_ms": sum(d.estimated_execution_time_ms for d in decompositions),
            "execution_batches": len(batches),
            "batch_breakdown": batches,
            "unit_tests": len([c for c in all_components if c.complexity == TestComplexity.UNIT]),
            "integration_tests": len([c for c in all_components if c.complexity == TestComplexity.INTEGRATION]),
            "system_tests": len([c for c in all_components if c.complexity == TestComplexity.SYSTEM]),
            "benchmarks": len([c for c in all_components if c.complexity == TestComplexity.BENCHMARK]),
            "coverage_gaps": list(set(
                gap for d in decompositions for gap in d.coverage_gaps
            )),
        }

"""
L1 Requirement Decomposition Agent — apps_rfp.enterprise.

Decomposes RFP requirements into structured, actionable components
with dependency mapping and implementation sizing.

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


class RequirementType(str, Enum):
    """Classification of requirement types."""

    FUNCTIONAL = "functional"
    TECHNICAL = "technical"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"
    UI_UX = "ui_ux"
    DATA = "data"
    TESTING = "testing"


class ComplexityTier(str, Enum):
    """Implementation complexity tiers."""

    TRIVIAL = "trivial"  # < 4 hours
    SIMPLE = "simple"  # 4-16 hours
    MODERATE = "moderate"  # 16-40 hours
    COMPLEX = "complex"  # 40-80 hours
    ENTERPRISE = "enterprise"  # > 80 hours


@dataclass(frozen=True)
class DecomposedComponent:
    """A single decomposed component from a requirement."""

    component_id: str
    parent_req_id: str
    name: str
    description: str
    requirement_type: RequirementType
    complexity: ComplexityTier
    estimated_hours: int
    dependencies: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    technical_notes: str = ""


@dataclass
class RequirementDecomposition:
    """Full decomposition of an RFP requirement."""

    source_requirement_id: str
    source_text: str
    category: str
    priority: str
    components: list[DecomposedComponent] = field(default_factory=list)
    implementation_order: list[str] = field(default_factory=list)
    total_estimated_hours: int = 0
    risk_flags: list[str] = field(default_factory=list)


@dataclass
class DecompositionSummary:
    """Summary across all decomposed requirements."""

    total_requirements: int = 0
    total_components: int = 0
    total_estimated_hours: int = 0
    complexity_distribution: dict[str, int] = field(default_factory=dict)
    type_distribution: dict[str, int] = field(default_factory=dict)
    critical_path: list[str] = field(default_factory=list)
    risk_requirements: list[str] = field(default_factory=list)


class RequirementDecomposer:
    """L1 agent for decomposing RFP requirements."""

    # Pattern maps for requirement classification
    TYPE_PATTERNS: dict[RequirementType, list[str]] = {
        RequirementType.SECURITY: [
            "encrypt", "authentication", "authorization", "audit", "compliance",
            "gdpr", "hipaa", "soc2", "penetration test", "vulnerability",
            "mfa", "sso", "rbac", "access control",
        ],
        RequirementType.PERFORMANCE: [
            "latency", "throughput", "concurrent", "scale", "million",
            "response time", "99th percentile", "availability", "sla",
            "load balancing", "caching", "optimize",
        ],
        RequirementType.INTEGRATION: [
            "api", "integration", "webhook", "connector", "sync",
            "import", "export", "etl", "middleware", "protocol",
            "rest", "graphql", "soap", "message queue",
        ],
        RequirementType.DATA: [
            "database", "data warehouse", "lake", "schema", "migration",
            "backup", "retention", "archive", "analytics", "reporting",
            "sql", "nosql", "blob", "vector",
        ],
        RequirementType.UI_UX: [
            "user interface", "dashboard", "portal", "responsive",
            "accessibility", "wcag", "mobile", "tablet", "workflow",
            "drag and drop", "visualization", "chart",
        ],
        RequirementType.TESTING: [
            "test", "validation", "verification", "qa", "acceptance",
            "unit test", "integration test", "e2e", "automation",
            "coverage", "regression", "load test",
        ],
    }

    def __init__(self) -> None:
        self._decomposition_cache: dict[str, RequirementDecomposition] = {}

    def decompose(
        self,
        req_id: str,
        req_text: str,
        category: str,
        priority: str,
    ) -> RequirementDecomposition:
        """Decompose a single requirement into components."""
        _emit_records_execution_trace("enterprise", "RequirementDecomposer", f"decompose_{req_id}")

        # Check cache
        cache_key = f"{req_id}:{hash(req_text) % 10000}"
        if cache_key in self._decomposition_cache:
            return self._decomposition_cache[cache_key]

        # Classify requirement type
        req_type = self._classify_requirement_type(req_text)

        # Extract components based on patterns
        components = self._extract_components(req_id, req_text, req_type)

        # Determine implementation order
        impl_order = self._determine_implementation_order(components)

        # Calculate totals
        total_hours = sum(c.estimated_hours for c in components)

        # Identify risk flags
        risk_flags = self._identify_risk_flags(req_text, components)

        decomposition = RequirementDecomposition(
            source_requirement_id=req_id,
            source_text=req_text,
            category=category,
            priority=priority,
            components=components,
            implementation_order=impl_order,
            total_estimated_hours=total_hours,
            risk_flags=risk_flags,
        )

        self._decomposition_cache[cache_key] = decomposition
        return decomposition

    def decompose_batch(
        self,
        requirements: list[tuple[str, str, str, str]],
    ) -> list[RequirementDecomposition]:
        """Decompose multiple requirements."""
        _emit_pulls_context("enterprise", "RequirementDecomposer", "decompose_batch")

        results: list[RequirementDecomposition] = []
        for req_id, req_text, category, priority in requirements:
            try:
                decomp = self.decompose(req_id, req_text, category, priority)
                results.append(decomp)
            except Exception as exc:
                _log.error(f"[RequirementDecomposer] Failed to decompose {req_id}: {exc}")
                # Return minimal decomposition on failure
                results.append(
                    RequirementDecomposition(
                        source_requirement_id=req_id,
                        source_text=req_text,
                        category=category,
                        priority=priority,
                        risk_flags=["decomposition_failed"],
                    )
                )

        return results

    def generate_summary(
        self,
        decompositions: list[RequirementDecomposition],
    ) -> DecompositionSummary:
        """Generate summary statistics across all decompositions."""
        _emit_captures_pattern("enterprise", "RequirementDecomposer", "generate_summary")

        summary = DecompositionSummary()
        summary.total_requirements = len(decompositions)

        complexity_dist: dict[str, int] = {}
        type_dist: dict[str, int] = {}
        all_critical: list[str] = []

        for decomp in decompositions:
            summary.total_components += len(decomp.components)
            summary.total_estimated_hours += decomp.total_estimated_hours

            if decomp.risk_flags:
                summary.risk_requirements.append(decomp.source_requirement_id)

            for comp in decomp.components:
                complexity_dist[comp.complexity.value] = complexity_dist.get(comp.complexity.value, 0) + 1
                type_dist[comp.requirement_type.value] = type_dist.get(comp.requirement_type.value, 0) + 1

                # Identify critical path items
                if comp.complexity in {ComplexityTier.COMPLEX, ComplexityTier.ENTERPRISE}:
                    all_critical.append(comp.component_id)

        summary.complexity_distribution = complexity_dist
        summary.type_distribution = type_dist
        summary.critical_path = all_critical[:10]  # Top 10 critical items

        return summary

    def _classify_requirement_type(self, text: str) -> RequirementType:
        """Classify requirement by type based on keyword patterns."""
        text_lower = text.lower()

        scores: dict[RequirementType, int] = {}
        for req_type, patterns in self.TYPE_PATTERNS.items():
            score = sum(1 for p in patterns if p in text_lower)
            if score > 0:
                scores[req_type] = score

        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]

        return RequirementType.FUNCTIONAL

    def _extract_components(
        self,
        req_id: str,
        req_text: str,
        req_type: RequirementType,
    ) -> list[DecomposedComponent]:
        """Extract implementation components from requirement text."""
        components: list[DecomposedComponent] = []

        # Parse compound requirements (those with "and", "as well as", etc.)
        sub_requirements = self._split_compound_requirements(req_text)

        for idx, sub_req in enumerate(sub_requirements, 1):
            comp_id = f"{req_id}-C{idx:02d}"

            # Determine complexity and hours
            complexity = self._estimate_complexity(sub_req)
            hours = self._complexity_to_hours(complexity)

            # Generate acceptance criteria
            acceptance = self._generate_acceptance_criteria(sub_req, req_type)

            components.append(
                DecomposedComponent(
                    component_id=comp_id,
                    parent_req_id=req_id,
                    name=self._generate_component_name(sub_req),
                    description=sub_req,
                    requirement_type=req_type,
                    complexity=complexity,
                    estimated_hours=hours,
                    acceptance_criteria=acceptance,
                    technical_notes=self._generate_technical_notes(sub_req, req_type),
                )
            )

        return components

    def _split_compound_requirements(self, text: str) -> list[str]:
        """Split compound requirements into individual items."""
        # Split on common conjunctions and separators
        separators = [
            r";\s*",
            r",\s+and\s+",
            r"\s+and\s+(?=must|shall|should|will)",
            r"\s+as well as\s+",
            r"\s+in addition\s+to\s+",
        ]

        import re
        parts = [text]
        for sep in separators:
            new_parts: list[str] = []
            for part in parts:
                new_parts.extend(re.split(sep, part, flags=re.IGNORECASE))
            parts = [p.strip() for p in new_parts if p.strip()]

        return parts if parts else [text]

    def _estimate_complexity(self, text: str) -> ComplexityTier:
        """Estimate implementation complexity from text analysis."""
        text_lower = text.lower()

        # Enterprise indicators
        enterprise_indicators = [
            "enterprise", "organization-wide", "multi-tenant", "multi-region",
            "high availability", "99.99", "millions of", "billions of",
            "machine learning", "ai model", "neural", "nlp", "computer vision",
        ]
        if any(ind in text_lower for ind in enterprise_indicators):
            return ComplexityTier.ENTERPRISE

        # Complex indicators
        complex_indicators = [
            "integration", "real-time", "streaming", "workflow", "orchestration",
            "distributed", "microservices", "event-driven", "complex",
        ]
        if any(ind in text_lower for ind in complex_indicators):
            return ComplexityTier.COMPLEX

        # Moderate indicators
        moderate_indicators = [
            "api", "database", "authentication", "authorization", "report",
            "dashboard", "notification", "batch", "etl",
        ]
        if any(ind in text_lower for ind in moderate_indicators):
            return ComplexityTier.MODERATE

        # Simple indicators
        simple_indicators = [
            "ui component", "form", "button", "link", "page", "view",
            "simple", "basic", "standard",
        ]
        if any(ind in text_lower for ind in simple_indicators):
            return ComplexityTier.SIMPLE

        return ComplexityTier.MODERATE

    def _complexity_to_hours(self, complexity: ComplexityTier) -> int:
        """Convert complexity tier to estimated hours."""
        mapping = {
            ComplexityTier.TRIVIAL: 2,
            ComplexityTier.SIMPLE: 8,
            ComplexityTier.MODERATE: 24,
            ComplexityTier.COMPLEX: 60,
            ComplexityTier.ENTERPRISE: 120,
        }
        return mapping.get(complexity, 24)

    def _generate_acceptance_criteria(self, text: str, req_type: RequirementType) -> list[str]:
        """Generate acceptance criteria for a component."""
        criteria: list[str] = []

        # Base criterion
        criteria.append(f"Feature operates as described: {text[:80]}...")

        # Type-specific criteria
        if req_type == RequirementType.SECURITY:
            criteria.extend([
                "Security scan passes with no critical vulnerabilities",
                "Access controls are properly enforced",
            ])
        elif req_type == RequirementType.PERFORMANCE:
            criteria.extend([
                "Performance benchmarks meet specified SLAs",
                "Load testing confirms scalability requirements",
            ])
        elif req_type == RequirementType.INTEGRATION:
            criteria.extend([
                "Integration tests pass with mock and real endpoints",
                "Error handling covers all documented failure modes",
            ])
        elif req_type == RequirementType.UI_UX:
            criteria.extend([
                "UI renders correctly on target browsers/devices",
                "Accessibility requirements (WCAG 2.1 AA) are met",
            ])

        return criteria

    def _generate_component_name(self, text: str) -> str:
        """Generate a short component name from requirement text."""
        # Extract key noun phrases
        words = text.split()[:8]  # First 8 words
        key_words = [w for w in words if len(w) > 3 and w.isalpha()]

        if key_words:
            return " ".join(key_words[:4]).title()

        return "Implementation Component"

    def _generate_technical_notes(self, text: str, req_type: RequirementType) -> str:
        """Generate technical implementation notes."""
        notes: list[str] = []

        if req_type == RequirementType.SECURITY:
            notes.append("Requires security review before deployment")
        if req_type == RequirementType.PERFORMANCE:
            notes.append("Performance testing required with production-like data volumes")
        if req_type == RequirementType.INTEGRATION:
            notes.append("Coordinate with external system owners for API access")
        if "legacy" in text.lower():
            notes.append("Integration with legacy systems - assess technical debt")

        return "; ".join(notes) if notes else ""

    def _determine_implementation_order(self, components: list[DecomposedComponent]) -> list[str]:
        """Determine optimal implementation order based on dependencies."""
        # Sort by complexity (foundations first, complex later)
        complexity_order = {
            ComplexityTier.TRIVIAL: 1,
            ComplexityTier.SIMPLE: 2,
            ComplexityTier.MODERATE: 3,
            ComplexityTier.COMPLEX: 4,
            ComplexityTier.ENTERPRISE: 5,
        }

        sorted_components = sorted(
            components,
            key=lambda c: complexity_order.get(c.complexity, 3),
        )

        return [c.component_id for c in sorted_components]

    def _identify_risk_flags(self, text: str, components: list[DecomposedComponent]) -> list[str]:
        """Identify risk flags in the requirement."""
        flags: list[str] = []
        text_lower = text.lower()

        # Timeline risks
        if any(word in text_lower for word in ["urgent", "asap", "immediate", "critical"]):
            flags.append("timeline_pressure")

        # Technical risks
        if any(word in text_lower for word in ["unproven", "bleeding edge", "experimental"]):
            flags.append("technical_uncertainty")

        # Integration risks
        if any(word in text_lower for word in ["third party", "external", "vendor"]):
            flags.append("external_dependency")

        # Resource risks
        if len([c for c in components if c.complexity == ComplexityTier.ENTERPRISE]) > 0:
            flags.append("high_effort_requirement")

        return flags


class RequirementDecompositionAgent:
    """Agent wrapper for requirement decomposition."""

    def __init__(self) -> None:
        self.decomposer = RequirementDecomposer()

    def analyze_rfp_requirements(
        self,
        requirements: list[dict[str, Any]],
    ) -> tuple[list[RequirementDecomposition], DecompositionSummary]:
        """Analyze all requirements from an RFP."""
        _emit_records_execution_trace("enterprise", "RequirementDecompositionAgent", "analyze_rfp")

        # Convert to tuples for batch processing
        req_tuples = [
            (r["req_id"], r["text"], r.get("category", "general"), r.get("priority", "preferred"))
            for r in requirements
        ]

        # Decompose all requirements
        decompositions = self.decomposer.decompose_batch(req_tuples)

        # Generate summary
        summary = self.decomposer.generate_summary(decompositions)

        return decompositions, summary

    def get_implementation_plan(
        self,
        decompositions: list[RequirementDecomposition],
    ) -> dict[str, Any]:
        """Generate an implementation plan from decompositions."""
        # Aggregate all components
        all_components: list[DecomposedComponent] = []
        for d in decompositions:
            all_components.extend(d.components)

        # Sort by complexity and priority
        priority_order = {"mandatory": 1, "preferred": 2, "optional": 3}

        def sort_key(c: DecomposedComponent) -> tuple:
            decomp = next((d for d in decompositions if d.source_requirement_id == c.parent_req_id), None)
            priority = decomp.priority if decomp else "preferred"
            complexity_order = {"trivial": 1, "simple": 2, "moderate": 3, "complex": 4, "enterprise": 5}
            return (priority_order.get(priority, 2), complexity_order.get(c.complexity.value, 3))

        sorted_components = sorted(all_components, key=sort_key)

        # Calculate phases (assuming 160 hours per 2-week sprint)
        hours_per_sprint = 160
        current_sprint_hours = 0
        current_sprint: list[str] = []
        sprints: list[list[str]] = []

        for comp in sorted_components:
            if current_sprint_hours + comp.estimated_hours > hours_per_sprint:
                sprints.append(current_sprint)
                current_sprint = [comp.component_id]
                current_sprint_hours = comp.estimated_hours
            else:
                current_sprint.append(comp.component_id)
                current_sprint_hours += comp.estimated_hours

        if current_sprint:
            sprints.append(current_sprint)

        return {
            "total_components": len(all_components),
            "total_estimated_hours": sum(c.estimated_hours for c in all_components),
            "estimated_sprints": len(sprints),
            "sprint_breakdown": sprints,
            "high_complexity_items": [
                c.component_id for c in all_components
                if c.complexity in {ComplexityTier.COMPLEX, ComplexityTier.ENTERPRISE}
            ],
            "risk_flags": list(set(
                flag for d in decompositions for flag in d.risk_flags
            )),
        }

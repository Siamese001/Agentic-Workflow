"""
L1 Brief Requirement Decomposition Agent — apps_exec.enterprise.

Decomposes executive brief requirements into structured, persona-targeted
components with evidence mapping and narrative flow analysis.

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


class SectionType(str, Enum):
    """Types of brief sections."""

    EXECUTIVE_SUMMARY = "executive_summary"
    ARCHITECTURE_OVERVIEW = "architecture_overview"
    GOVERNANCE_MODEL = "governance_model"
    CAPABILITY_HIGHLIGHTS = "capability_highlights"
    EVIDENCE_ANCHORS = "evidence_anchors"
    RISK_POSTURE = "risk_posture"
    STRATEGIC_DIFFERENTIATION = "strategic_differentiation"
    ROI_FRAMEWORK = "roi_framework"
    TECHNICAL_DEPTH = "technical_depth"
    CALL_TO_ACTION = "call_to_action"


class AudiencePriority(str, Enum):
    """Priority level for audience-specific content."""

    CRITICAL = "critical"  # Must include
    HIGH = "high"  # Strongly recommended
    MEDIUM = "medium"  # Include if space
    LOW = "low"  # Optional


@dataclass(frozen=True)
class BriefComponent:
    """A single decomposed brief component."""

    component_id: str
    section_type: SectionType
    title: str
    description: str
    priority: AudiencePriority
    evidence_required: list[str] = field(default_factory=list)
    word_count_target: int = 150
    dependencies: list[str] = field(default_factory=list)
    key_messages: list[str] = field(default_factory=list)


@dataclass
class BriefDecomposition:
    """Full decomposition of brief requirements for a persona."""

    audience_persona: str
    source_material_summary: str
    components: list[BriefComponent] = field(default_factory=list)
    narrative_flow: list[str] = field(default_factory=list)
    evidence_gaps: list[str] = field(default_factory=list)
    suggested_tone: str = "professional"


@dataclass
class DecompositionSummary:
    """Summary across all decomposed briefs."""

    total_personas: int = 0
    total_components: int = 0
    total_word_count_target: int = 0
    evidence_coverage: float = 0.0
    critical_sections: int = 0
    optional_sections: int = 0


class BriefDecomposer:
    """L1 agent for decomposing executive brief requirements."""

    # Persona-specific section templates
    PERSONA_SECTIONS: dict[str, list[tuple[SectionType, AudiencePriority, int]]] = {
        "recruiter": [
            (SectionType.EXECUTIVE_SUMMARY, AudiencePriority.CRITICAL, 200),
            (SectionType.CAPABILITY_HIGHLIGHTS, AudiencePriority.CRITICAL, 150),
            (SectionType.EVIDENCE_ANCHORS, AudiencePriority.HIGH, 100),
            (SectionType.CALL_TO_ACTION, AudiencePriority.HIGH, 50),
        ],
        "cto": [
            (SectionType.EXECUTIVE_SUMMARY, AudiencePriority.CRITICAL, 150),
            (SectionType.ARCHITECTURE_OVERVIEW, AudiencePriority.CRITICAL, 300),
            (SectionType.GOVERNANCE_MODEL, AudiencePriority.CRITICAL, 200),
            (SectionType.TECHNICAL_DEPTH, AudiencePriority.HIGH, 250),
            (SectionType.RISK_POSTURE, AudiencePriority.HIGH, 150),
            (SectionType.EVIDENCE_ANCHORS, AudiencePriority.MEDIUM, 100),
        ],
        "svp_eng": [
            (SectionType.EXECUTIVE_SUMMARY, AudiencePriority.HIGH, 150),
            (SectionType.ARCHITECTURE_OVERVIEW, AudiencePriority.HIGH, 200),
            (SectionType.GOVERNANCE_MODEL, AudiencePriority.CRITICAL, 250),
            (SectionType.TECHNICAL_DEPTH, AudiencePriority.CRITICAL, 300),
            (SectionType.EVIDENCE_ANCHORS, AudiencePriority.HIGH, 150),
            (SectionType.RISK_POSTURE, AudiencePriority.MEDIUM, 100),
        ],
        "board": [
            (SectionType.EXECUTIVE_SUMMARY, AudiencePriority.CRITICAL, 250),
            (SectionType.STRATEGIC_DIFFERENTIATION, AudiencePriority.CRITICAL, 200),
            (SectionType.ROI_FRAMEWORK, AudiencePriority.CRITICAL, 200),
            (SectionType.RISK_POSTURE, AudiencePriority.HIGH, 150),
            (SectionType.GOVERNANCE_MODEL, AudiencePriority.HIGH, 150),
            (SectionType.CALL_TO_ACTION, AudiencePriority.HIGH, 100),
        ],
    }

    # Evidence patterns to look for
    EVIDENCE_PATTERNS: list[str] = [
        "test coverage",
        "benchmark",
        "performance",
        "latency",
        "throughput",
        "determinism",
        "governance",
        "audit",
        "compliance",
        "security",
        "scalability",
        "reliability",
    ]

    def __init__(self) -> None:
        self._decomposition_cache: dict[str, BriefDecomposition] = {}

    def decompose(
        self,
        audience_persona: str,
        source_material: str,
        custom_requirements: list[str] | None = None,
    ) -> BriefDecomposition:
        """Decompose brief requirements for a specific persona."""
        _emit_records_execution_trace("enterprise", "BriefDecomposer", f"decompose_{audience_persona}")

        # Check cache
        cache_key = f"{audience_persona}:{hash(source_material) % 10000}"
        if cache_key in self._decomposition_cache:
            return self._decomposition_cache[cache_key]

        # Get persona-specific sections
        section_config = self.PERSONA_SECTIONS.get(audience_persona, self.PERSONA_SECTIONS["recruiter"])

        # Extract evidence from source material
        available_evidence = self._extract_evidence(source_material)

        # Build components
        components: list[BriefComponent] = []
        for idx, (section_type, priority, word_count) in tqdm(
            enumerate(section_config, 1), desc="Processing", unit="item"
        ):
            comp_id = f"{audience_persona[:3].upper()}-SEC{idx:02d}"

            # Map required evidence for this section
            evidence_req = self._map_evidence_requirements(section_type, available_evidence)

            components.append(
                BriefComponent(
                    component_id=comp_id,
                    section_type=section_type,
                    title=self._generate_section_title(section_type, audience_persona),
                    description=self._generate_section_description(section_type),
                    priority=priority,
                    evidence_required=evidence_req,
                    word_count_target=word_count,
                    dependencies=self._determine_dependencies(section_type, components),
                    key_messages=self._generate_key_messages(section_type, audience_persona),
                ),
            )

        # Determine narrative flow
        narrative_flow = self._determine_narrative_flow(components)

        # Identify evidence gaps
        evidence_gaps = self._identify_evidence_gaps(components, available_evidence)

        # Determine tone
        suggested_tone = self._determine_tone(audience_persona)

        decomposition = BriefDecomposition(
            audience_persona=audience_persona,
            source_material_summary=source_material[:500],
            components=components,
            narrative_flow=narrative_flow,
            evidence_gaps=evidence_gaps,
            suggested_tone=suggested_tone,
        )

        self._decomposition_cache[cache_key] = decomposition
        return decomposition

    def decompose_batch(
        self,
        personas: list[str],
        source_material: str,
    ) -> list[BriefDecomposition]:
        """Decompose briefs for multiple personas."""
        _emit_pulls_context("enterprise", "BriefDecomposer", "decompose_batch")

        results: list[BriefDecomposition] = []
        for persona in tqdm(personas, desc="Processing", unit="item"):
            try:
                decomp = self.decompose(persona, source_material)
                results.append(decomp)
            except (RuntimeError, ValueError, TypeError, AttributeError, KeyError) as exc:
                _log.error(f"[BriefDecomposer] Failed to decompose for {persona}: {exc}")
                # Return minimal decomposition on failure
                results.append(
                    BriefDecomposition(
                        audience_persona=persona,
                        source_material_summary=source_material[:500],
                        evidence_gaps=["decomposition_failed"],
                    ),
                )

        return results

    def generate_summary(
        self,
        decompositions: list[BriefDecomposition],
    ) -> DecompositionSummary:
        """Generate summary statistics across all decompositions."""
        _emit_captures_pattern("enterprise", "BriefDecomposer", "generate_summary")

        summary = DecompositionSummary()
        summary.total_personas = len(decompositions)

        all_components: list[BriefComponent] = []
        for decomp in decompositions:
            all_components.extend(decomp.components)

        summary.total_components = len(all_components)
        summary.total_word_count_target = sum(c.word_count_target for c in all_components)
        summary.critical_sections = len(
            [c for c in all_components if c.priority == AudiencePriority.CRITICAL]
        )
        summary.optional_sections = len([c for c in all_components if c.priority == AudiencePriority.LOW])

        # Calculate evidence coverage
        total_evidence_reqs = sum(len(c.evidence_required) for c in all_components)
        evidence_found = sum(1 for c in all_components for e in c.evidence_required if e)
        summary.evidence_coverage = evidence_found / max(total_evidence_reqs, 1)

        return summary

    def _extract_evidence(self, source_material: str) -> list[str]:
        """Extract evidence patterns from source material."""
        found: list[str] = []
        source_lower = source_material.lower()

        for pattern in self.EVIDENCE_PATTERNS:
            if pattern in source_lower:
                found.append(pattern)

        return found

    def _map_evidence_requirements(
        self,
        section_type: SectionType,
        available_evidence: list[str],
    ) -> list[str]:
        """Map evidence requirements for a section type."""
        section_evidence_map: dict[SectionType, list[str]] = {
            SectionType.ARCHITECTURE_OVERVIEW: ["scalability", "reliability", "performance"],
            SectionType.GOVERNANCE_MODEL: ["governance", "audit", "compliance", "determinism"],
            SectionType.CAPABILITY_HIGHLIGHTS: ["test coverage", "benchmark", "performance"],
            SectionType.TECHNICAL_DEPTH: ["latency", "throughput", "benchmark"],
            SectionType.RISK_POSTURE: ["security", "compliance", "audit"],
        }

        required = section_evidence_map.get(section_type, [])
        # Filter to available evidence
        return [e for e in required if e in available_evidence]

    def _generate_section_title(self, section_type: SectionType, persona: str) -> str:
        """Generate a section title based on type and persona."""
        persona_titles: dict[str, dict[SectionType, str]] = {
            "recruiter": {
                SectionType.EXECUTIVE_SUMMARY: "Candidate Overview",
                SectionType.CAPABILITY_HIGHLIGHTS: "Key Skills & Achievements",
                SectionType.CALL_TO_ACTION: "Next Steps",
            },
            "cto": {
                SectionType.EXECUTIVE_SUMMARY: "Technical Assessment",
                SectionType.ARCHITECTURE_OVERVIEW: "System Architecture",
                SectionType.GOVERNANCE_MODEL: "Engineering Governance",
            },
            "board": {
                SectionType.EXECUTIVE_SUMMARY: "Strategic Assessment",
                SectionType.ROI_FRAMEWORK: "Business Value & ROI",
                SectionType.STRATEGIC_DIFFERENTIATION: "Competitive Positioning",
            },
        }

        default_titles: dict[SectionType, str] = {
            SectionType.EXECUTIVE_SUMMARY: "Executive Summary",
            SectionType.ARCHITECTURE_OVERVIEW: "Architecture Overview",
            SectionType.GOVERNANCE_MODEL: "Governance Model",
            SectionType.CAPABILITY_HIGHLIGHTS: "Capability Highlights",
            SectionType.EVIDENCE_ANCHORS: "Evidence & Validation",
            SectionType.RISK_POSTURE: "Risk Posture",
            SectionType.STRATEGIC_DIFFERENTIATION: "Strategic Differentiation",
            SectionType.ROI_FRAMEWORK: "ROI Framework",
            SectionType.TECHNICAL_DEPTH: "Technical Deep Dive",
            SectionType.CALL_TO_ACTION: "Recommended Actions",
        }

        persona_title_map = persona_titles.get(persona, {})
        return persona_title_map.get(
            section_type, default_titles.get(section_type, section_type.value.replace("_", " ").title())
        )

    def _generate_section_description(self, section_type: SectionType) -> str:
        """Generate a description for a section type."""
        descriptions: dict[SectionType, str] = {
            SectionType.EXECUTIVE_SUMMARY: "High-level overview capturing key points for the audience",
            SectionType.ARCHITECTURE_OVERVIEW: "System architecture and design decisions",
            SectionType.GOVERNANCE_MODEL: "Engineering practices, quality gates, and enforcement",
            SectionType.CAPABILITY_HIGHLIGHTS: "Core competencies and demonstrated achievements",
            SectionType.EVIDENCE_ANCHORS: "Quantifiable proof points and validation data",
            SectionType.RISK_POSTURE: "Risk awareness and mitigation strategies",
            SectionType.STRATEGIC_DIFFERENTIATION: "Unique positioning and competitive advantages",
            SectionType.ROI_FRAMEWORK: "Business value quantification and investment rationale",
            SectionType.TECHNICAL_DEPTH: "Detailed technical implementation and engineering rigor",
            SectionType.CALL_TO_ACTION: "Clear next steps and engagement recommendations",
        }
        return descriptions.get(section_type, "Section content")

    def _determine_dependencies(
        self,
        section_type: SectionType,
        existing_components: list[BriefComponent],
    ) -> list[str]:
        """Determine which sections this section depends on."""
        # Executive summary typically depends on everything
        if section_type == SectionType.EXECUTIVE_SUMMARY and existing_components:
            return [c.component_id for c in existing_components]

        # Technical depth depends on architecture overview
        if section_type == SectionType.TECHNICAL_DEPTH:
            arch_comp = next(
                (c for c in existing_components if c.section_type == SectionType.ARCHITECTURE_OVERVIEW), None
            )
            if arch_comp:
                return [arch_comp.component_id]

        return []

    def _generate_key_messages(self, section_type: SectionType, persona: str) -> list[str]:
        """Generate key messages for a section and persona."""
        persona_messages: dict[str, dict[SectionType, list[str]]] = {
            "recruiter": {
                SectionType.EXECUTIVE_SUMMARY: [
                    "Strong AI/ML platform engineering background",
                    "Production-grade system design experience",
                    "Governance and compliance awareness",
                ],
                SectionType.CAPABILITY_HIGHLIGHTS: [
                    "Multi-agent orchestration",
                    "Deterministic execution systems",
                    "Enterprise-grade quality gates",
                ],
            },
            "cto": {
                SectionType.ARCHITECTURE_OVERVIEW: [
                    "Layered architecture with clear boundaries",
                    "Deterministic execution guarantees",
                    "Comprehensive observability",
                ],
                SectionType.GOVERNANCE_MODEL: [
                    "Static analysis enforcement",
                    "Automated quality gates",
                    "Traceability and auditability",
                ],
            },
            "board": {
                SectionType.STRATEGIC_DIFFERENTIATION: [
                    "Deterministic AI - unique market positioning",
                    "Governance-first architecture",
                    "Enterprise-ready from day one",
                ],
                SectionType.ROI_FRAMEWORK: [
                    "Reduced operational risk through determinism",
                    "Faster time-to-production with governance",
                    "Lower compliance costs via automation",
                ],
            },
        }

        default_messages: dict[SectionType, list[str]] = {
            SectionType.EXECUTIVE_SUMMARY: ["Clear value proposition", "Technical credibility"],
            SectionType.ARCHITECTURE_OVERVIEW: ["Sound design principles", "Scalable patterns"],
            SectionType.GOVERNANCE_MODEL: ["Quality enforcement", "Risk mitigation"],
        }

        persona_msg_map = persona_messages.get(persona, {})
        return persona_msg_map.get(
            section_type, default_messages.get(section_type, ["Key point 1", "Key point 2"])
        )

    def _determine_narrative_flow(self, components: list[BriefComponent]) -> list[str]:
        """Determine optimal section ordering for narrative flow."""
        # Sort by priority and logical dependencies
        priority_order = {
            AudiencePriority.CRITICAL: 1,
            AudiencePriority.HIGH: 2,
            AudiencePriority.MEDIUM: 3,
            AudiencePriority.LOW: 4,
        }

        sorted_comps = sorted(components, key=lambda c: priority_order.get(c.priority, 3))
        return [c.component_id for c in sorted_comps]

    def _identify_evidence_gaps(
        self,
        components: list[BriefComponent],
        available_evidence: list[str],
    ) -> list[str]:
        """Identify gaps where evidence is required but not available."""
        gaps: list[str] = []

        for comp in components:
            for req_evidence in comp.evidence_required:
                if req_evidence not in available_evidence:
                    gaps.append(f"{comp.section_type.value}:{req_evidence}")

        return gaps

    def _determine_tone(self, persona: str) -> str:
        """Determine appropriate tone for persona."""
        tones: dict[str, str] = {
            "recruiter": "conversational and highlight-focused",
            "cto": "technical and precise",
            "svp_eng": "engineering-focused with metrics",
            "board": "strategic and business-oriented",
        }
        return tones.get(persona, "professional")


class BriefDecompositionAgent:
    """Agent wrapper for brief requirement decomposition."""

    def __init__(self) -> None:
        self.decomposer = BriefDecomposer()

    def analyze_brief_requirements(
        self,
        personas: list[str],
        source_material: str,
    ) -> tuple[list[BriefDecomposition], DecompositionSummary]:
        """Analyze brief requirements for all target personas."""
        _emit_records_execution_trace("enterprise", "BriefDecompositionAgent", "analyze_requirements")

        # Decompose for all personas
        decompositions = self.decomposer.decompose_batch(personas, source_material)

        # Generate summary
        summary = self.decomposer.generate_summary(decompositions)

        return decompositions, summary

    def get_brief_production_plan(
        self,
        decompositions: list[BriefDecomposition],
    ) -> dict[str, Any]:
        """Generate a production plan from decompositions."""
        # Aggregate all components
        all_components: list[BriefComponent] = []
        for d in decompositions:
            all_components.extend(d.components)

        # Group by persona
        by_persona: dict[str, list[str]] = {}
        for d in decompositions:
            by_persona[d.audience_persona] = [c.component_id for c in d.components]

        # Calculate production metrics
        total_word_count = sum(c.word_count_target for c in all_components)
        critical_count = len([c for c in all_components if c.priority == AudiencePriority.CRITICAL])

        return {
            "total_briefs": len(decompositions),
            "total_sections": len(all_components),
            "total_word_count_target": total_word_count,
            "critical_sections": critical_count,
            "sections_by_persona": by_persona,
            "evidence_gaps": list(set(gap for d in decompositions for gap in d.evidence_gaps)),
            "production_sequence": [
                "ingest_source_material",
                "extract_evidence",
                "generate_sections",
                "validate_style",
                "assemble_briefs",
                "emit_artifacts",
            ],
        }

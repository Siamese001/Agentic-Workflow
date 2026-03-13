"""
Research Assembly Engine — apps_research.

Assembles deterministic research artifact sections, comparison matrices,
and source registers from a research request.

Deterministic: table schemas, section ordering, source register format.
Model-ready:   synthesis narrative, strategic implications, interpretation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from apps_research.types.research_types import (
    ArtifactMode,
    ClaimType,
    ComparisonRow,
    ResearchRequest,
    ResearchSection,
    SourceEntry,
)

_log = logging.getLogger(__name__)

_COMPARISON_DIMENSIONS = [
    "architecture_model",
    "governance_approach",
    "determinism_level",
    "scalability",
    "enterprise_readiness",
    "open_source",
]

_AGENTIC_FRAMEWORKS = {
    "agentic_core (this repo)": {
        "architecture_model": "Layered L0-L6 with ADG enforcement",
        "governance_approach": "Constitutional pre-commit hooks + policy hash enforcement",
        "determinism_level": "High — static analysis enforced",
        "scalability": "Designed for enterprise scale",
        "enterprise_readiness": "Production-grade with full auditability",
        "open_source": "Yes",
    },
    "LangGraph": {
        "architecture_model": "Graph-based stateful agent workflows",
        "governance_approach": "Application-layer only",
        "determinism_level": "Medium — depends on LLM temperature",
        "scalability": "Good for mid-scale workloads",
        "enterprise_readiness": "Growing; requires governance overlay",
        "open_source": "Yes",
    },
    "AutoGen": {
        "architecture_model": "Multi-agent conversation framework",
        "governance_approach": "Minimal built-in governance",
        "determinism_level": "Low — conversational by design",
        "scalability": "Research-oriented; scaling requires custom work",
        "enterprise_readiness": "Emerging",
        "open_source": "Yes",
    },
    "CrewAI": {
        "architecture_model": "Role-based crew orchestration",
        "governance_approach": "Role definitions; no enforcement layer",
        "determinism_level": "Medium",
        "scalability": "Good for task crews",
        "enterprise_readiness": "Moderate",
        "open_source": "Yes",
    },
}


@dataclass
class ResearchAssemblyResult:
    """Output of research assembly pass."""

    sections: list[ResearchSection] = field(default_factory=list)
    comparison_matrix: list[ComparisonRow] = field(default_factory=list)
    source_register: list[SourceEntry] = field(default_factory=list)


class ResearchAssemblyEngine:
    """Assemble research artifact from a research request.

    Builds deterministic sections appropriate for the requested mode.
    Marks each claim with its type (direct_evidence, interpretation, etc.).
    """

    AGENT_ID = "RESEARCH_ASSEMBLY"

    def __init__(self, config: object | None = None) -> None:
        self._config = config

    def execute(self, request: ResearchRequest) -> ResearchAssemblyResult:
        """Assemble research artifact.

        Args:
            request: ResearchRequest with topic, mode, audience.

        Returns:
            ResearchAssemblyResult with sections, matrix, source register.
        """
        mode = request.mode if isinstance(request.mode, ArtifactMode) else ArtifactMode(request.mode)
        sources = self._build_source_register(request)
        sections = self._build_sections(request, mode, sources)
        matrix = self._build_comparison_matrix(request) if mode == ArtifactMode.COMPARISON else []

        _log.info(
            "[ResearchAssemblyEngine] mode=%s sections=%d sources=%d", mode.value, len(sections), len(sources)
        )
        return ResearchAssemblyResult(
            sections=sections,
            comparison_matrix=matrix,
            source_register=sources,
        )

    def _build_source_register(self, request: ResearchRequest) -> list[SourceEntry]:
        """Build a source register from repo-internal evidence."""
        sources = [
            SourceEntry(
                source_id="SRC-001",
                title="agentic_core L0-L6 Architecture",
                claim_type=ClaimType.DIRECT_EVIDENCE,
                confidence=0.95,
                summary="Six-layer architecture with enforced dependency boundaries",
                url="docs/architecture/",
                section_id="executive_summary",
            ),
            SourceEntry(
                source_id="SRC-002",
                title="ADG Anti-Pattern Burndown Ratchet",
                claim_type=ClaimType.DIRECT_EVIDENCE,
                confidence=0.95,
                summary="Pre-commit enforcement of architectural governance rules",
                url="agentic_core/L5_safety/",
                section_id="key_findings",
            ),
            SourceEntry(
                source_id="SRC-003",
                title="PolicyHashEnforcer — L0 Routing",
                claim_type=ClaimType.DIRECT_EVIDENCE,
                confidence=0.90,
                summary="InstructionPacket policy hash validation at routing entry",
                url="agentic_core/L0_routing/enforcement/policy_hash_enforcer.py",
                section_id="key_findings",
            ),
            SourceEntry(
                source_id="SRC-004",
                title="ExecutionScopeNondeterminismVisitor",
                claim_type=ClaimType.DIRECT_EVIDENCE,
                confidence=0.90,
                summary="Static AST analysis of non-deterministic calls in execution scope",
                url="agentic_core/L5_safety/static_checks/determinism_serialization_check.py",
                section_id="strategic_implications",
            ),
            SourceEntry(
                source_id="SRC-005",
                title="Analyst inference: enterprise agentic AI governance trends",
                claim_type=ClaimType.ANALYST_INFERENCE,
                confidence=0.70,
                summary="Growing enterprise demand for auditability in agentic AI systems",
                url="",
                section_id="strategic_implications",
            ),
        ]
        if request.comparison_subjects:
            for idx, subject in enumerate(request.comparison_subjects):
                sources.append(
                    SourceEntry(
                        source_id=f"SRC-C{idx + 1:02d}",
                        title=f"Comparison subject: {subject}",
                        claim_type=ClaimType.INTERPRETATION,
                        confidence=0.65,
                        summary=f"Framework characteristics of {subject} from public documentation",
                        url="",
                        section_id="comparison_matrix",
                    )
                )
        return sources

    def _build_sections(
        self,
        request: ResearchRequest,
        mode: ArtifactMode,
        sources: list[SourceEntry],
    ) -> list[ResearchSection]:
        """Build sections appropriate for the requested mode."""
        topic = request.topic
        horizon = request.time_horizon or "current"
        src_ids = tuple(s.source_id for s in sources[:4])

        section_map: dict[str, list[ResearchSection]] = {
            ArtifactMode.BRIEF: [
                ResearchSection(
                    section_id="executive_summary",
                    heading="Executive Summary",
                    body=(
                        f"**Topic:** {topic}\n\n"
                        f"This brief examines {topic} with a focus on enterprise agentic AI platforms. "
                        "The evidence base draws from this repository's implementation, which provides "
                        "a working reference architecture for production-grade agentic systems.\n\n"
                        f"*Audience: {request.audience_style.value}. Time horizon: {horizon}.*"
                    ),
                    is_deterministic=True,
                    claim_type=ClaimType.DIRECT_EVIDENCE,
                    sources=src_ids,
                    word_count=70,
                ),
                ResearchSection(
                    section_id="key_findings",
                    heading="Key Findings",
                    body=(
                        "**Finding 1 [DIRECT_EVIDENCE]:** Production agentic systems require "
                        "governance enforcement at the architecture layer, not the application layer. "
                        "Evidence: L0 routing enforcement via PolicyHashEnforcer (SRC-003).\n\n"
                        "**Finding 2 [DIRECT_EVIDENCE]:** Determinism contracts must be enforced "
                        "statically, not at runtime. Evidence: ExecutionScopeNondeterminismVisitor (SRC-004).\n\n"
                        "**Finding 3 [ANALYST_INFERENCE]:** Enterprise buyers increasingly require "
                        "auditability as a first-class platform feature, not a post-hoc addition (SRC-005).\n\n"
                        "*Claim type labels: DIRECT_EVIDENCE = from implementation; ANALYST_INFERENCE = analyst judgment.*"
                    ),
                    is_deterministic=True,
                    claim_type=ClaimType.DIRECT_EVIDENCE,
                    sources=src_ids,
                    word_count=100,
                ),
                ResearchSection(
                    section_id="strategic_implications",
                    heading="Strategic Implications",
                    body=(
                        "**Implication 1 [INTERPRETATION]:** Platforms that treat governance as "
                        "infrastructure (not configuration) will have lower compliance cost at scale.\n\n"
                        "**Implication 2 [INTERPRETATION]:** The ADG enforcement model — where "
                        "violations are ratcheted down over time — is a replicable pattern for "
                        "any enterprise architecture quality program.\n\n"
                        "**Implication 3 [ANALYST_INFERENCE]:** Agentic AI platforms that cannot "
                        "demonstrate deterministic execution paths will face regulatory headwinds "
                        "in financial services and healthcare.\n\n"
                        "*INTERPRETATION = derived from evidence; ANALYST_INFERENCE = analyst judgment.*"
                    ),
                    is_deterministic=False,
                    claim_type=ClaimType.INTERPRETATION,
                    sources=src_ids,
                    word_count=100,
                ),
            ],
            ArtifactMode.COMPARISON: [
                ResearchSection(
                    section_id="comparison_overview",
                    heading="Comparison Overview",
                    body=(
                        f"**Scope:** Comparative analysis of agentic AI frameworks on topic: {topic}\n\n"
                        f"**Subjects:** {', '.join(request.comparison_subjects) if request.comparison_subjects else 'major agentic frameworks'}\n\n"
                        "**Dimensions evaluated:** architecture model, governance approach, "
                        "determinism level, scalability, enterprise readiness, open source status.\n\n"
                        "*All framework characterizations are analyst interpretations from public documentation.*"
                    ),
                    is_deterministic=True,
                    claim_type=ClaimType.INTERPRETATION,
                    sources=src_ids,
                    word_count=70,
                ),
                ResearchSection(
                    section_id="comparison_matrix",
                    heading="Comparison Matrix",
                    body="*See structured comparison matrix in artifact output.*",
                    is_deterministic=True,
                    claim_type=ClaimType.INTERPRETATION,
                    sources=src_ids,
                    word_count=10,
                ),
                ResearchSection(
                    section_id="recommendation",
                    heading="Recommendation",
                    body=(
                        "**Recommendation [ANALYST_INFERENCE]:** For enterprise deployments requiring "
                        "auditability, determinism enforcement, and governance at scale, "
                        "agentic platforms with constitutional enforcement (pre-commit governance, "
                        "policy hash validation, static analysis) are preferred over frameworks "
                        "that treat governance as application-layer configuration.\n\n"
                        "*This recommendation is analyst inference, not direct evidence.*"
                    ),
                    is_deterministic=False,
                    claim_type=ClaimType.ANALYST_INFERENCE,
                    sources=src_ids,
                    word_count=70,
                ),
            ],
            ArtifactMode.TREND: [
                ResearchSection(
                    section_id="trend_overview",
                    heading="Trend Overview",
                    body=(
                        f"**Topic:** {topic}\n"
                        f"**Time horizon:** {horizon}\n\n"
                        "Emerging trend: enterprise organizations are moving from single-model AI deployments "
                        "to multi-hop agentic workflows with explicit governance contracts.\n\n"
                        "*Trend characterizations are analyst inferences unless otherwise labeled.*"
                    ),
                    is_deterministic=True,
                    claim_type=ClaimType.ANALYST_INFERENCE,
                    sources=src_ids,
                    word_count=60,
                ),
                ResearchSection(
                    section_id="signal_analysis",
                    heading="Signal Analysis",
                    body=(
                        "**Signal 1 [DIRECT_EVIDENCE]:** Agentic platforms are adopting static "
                        "analysis as a governance enforcement mechanism (source: this repo).\n\n"
                        "**Signal 2 [ANALYST_INFERENCE]:** Regulatory pressure in financial services "
                        "and healthcare is accelerating governance-first AI platform adoption.\n\n"
                        "**Signal 3 [ANALYST_INFERENCE]:** Open-source agentic frameworks are converging "
                        "toward explicit orchestration graphs as the dominant pattern."
                    ),
                    is_deterministic=False,
                    claim_type=ClaimType.ANALYST_INFERENCE,
                    sources=src_ids,
                    word_count=80,
                ),
                ResearchSection(
                    section_id="horizon_implications",
                    heading="Horizon Implications",
                    body=(
                        "**Near-term (0-12 months) [ANALYST_INFERENCE]:** Governance tooling for "
                        "agentic AI will become a purchase criterion, not just a nice-to-have.\n\n"
                        "**Medium-term (1-3 years) [ANALYST_INFERENCE]:** Platform consolidation "
                        "around 2-3 dominant orchestration frameworks with enterprise governance layers."
                    ),
                    is_deterministic=False,
                    claim_type=ClaimType.ANALYST_INFERENCE,
                    sources=src_ids,
                    word_count=60,
                ),
            ],
            ArtifactMode.THOUGHT_LEADERSHIP: [
                ResearchSection(
                    section_id="hook",
                    heading="Opening Hook",
                    body=(
                        "Most agentic AI platforms treat governance as a checklist. "
                        "This repository treats it as a constitutional requirement — "
                        "enforced at every commit, every routing decision, and every output."
                    ),
                    is_deterministic=True,
                    claim_type=ClaimType.DIRECT_EVIDENCE,
                    sources=src_ids,
                    word_count=40,
                ),
                ResearchSection(
                    section_id="insight",
                    heading="Core Insight",
                    body=(
                        f"**Topic:** {topic}\n\n"
                        "The key insight is that determinism and governance must be enforced "
                        "at the architecture layer — not the application layer. "
                        "When governance is application-layer config, it gets overridden. "
                        "When it is constitutional — pre-commit hooks, signed instruction packets, "
                        "static analysis ratchets — it becomes load-bearing infrastructure."
                    ),
                    is_deterministic=False,
                    claim_type=ClaimType.INTERPRETATION,
                    sources=src_ids,
                    word_count=70,
                ),
                ResearchSection(
                    section_id="evidence",
                    heading="Evidence from Implementation",
                    body=(
                        "Evidence base:\n"
                        "- PolicyHashEnforcer: validates InstructionPacket.policy_hash at L0 routing entry\n"
                        "- ADG Anti-Pattern Burndown Ratchet: ratchets down violations at each commit\n"
                        "- ExecutionScopeNondeterminismVisitor: static AST enforcement across L1-L3\n\n"
                        "*All evidence is from this repository's implementation.*"
                    ),
                    is_deterministic=True,
                    claim_type=ClaimType.DIRECT_EVIDENCE,
                    sources=src_ids,
                    word_count=60,
                ),
                ResearchSection(
                    section_id="call_to_action",
                    heading="Call to Action",
                    body=(
                        "If you are building an agentic AI platform: "
                        "start with governance infrastructure, not features. "
                        "The architecture of this repository is available as a reference. "
                        "The patterns — ADG enforcement, policy hash validation, determinism contracts — "
                        "are replicable without this codebase."
                    ),
                    is_deterministic=False,
                    claim_type=ClaimType.ANALYST_INFERENCE,
                    sources=src_ids,
                    word_count=60,
                ),
            ],
        }

        return section_map.get(mode, section_map[ArtifactMode.BRIEF])

    def _build_comparison_matrix(self, request: ResearchRequest) -> list[ComparisonRow]:
        """Build a structured comparison matrix for comparison mode."""
        subjects = request.comparison_subjects or list(_AGENTIC_FRAMEWORKS.keys())
        rows: list[ComparisonRow] = []
        for subject in subjects:
            dims = _AGENTIC_FRAMEWORKS.get(
                subject,
                dict.fromkeys(_COMPARISON_DIMENSIONS, "Unknown — requires primary research"),
            )
            rows.append(ComparisonRow(subject=subject, dimensions=dims))
        return rows

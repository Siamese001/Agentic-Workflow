"""
L3 Multi-Agent Section Orchestration — apps_rfp.enterprise.

Orchestrates multiple specialized agents to generate proposal sections,
with coordination, dependency management, and quality aggregation.

Layer 3 Orchestration: Multi-hop workflows, agent dispatch, lineage tracking.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,
    _emit_records_workflow_lineage,
)
from tqdm import tqdm

_log = logging.getLogger(__name__)


class SectionType(str, Enum):
    """Types of proposal sections."""

    EXECUTIVE_SUMMARY = "executive_summary"
    CURRENT_STATE = "current_state"
    FUTURE_STATE = "future_state"
    TECHNICAL_APPROACH = "technical_approach"
    IMPLEMENTATION_ROADMAP = "implementation_roadmap"
    RISK_AND_GOVERNANCE = "risk_and_governance"
    VALUE_CASE = "value_case"
    TEAM_AND_QUALIFICATIONS = "team_and_qualifications"
    PRICING = "pricing"
    SOLUTION_APPENDIX = "solution_appendix"


class SectionStatus(str, Enum):
    """Status of section generation."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class SectionRequest:
    """Request to generate a proposal section."""

    section_type: SectionType
    section_id: str
    dependencies: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    max_words: int = 500
    required_evidence: list[str] = field(default_factory=list)


@dataclass
class SectionResult:
    """Result of generating a proposal section."""

    section_id: str
    section_type: SectionType
    heading: str
    body: str
    status: SectionStatus
    word_count: int = 0
    evidence_cited: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    quality_score: float = 0.0
    generation_time_ms: int = 0
    error: str = ""


@dataclass
class OrchestrationPlan:
    """Execution plan for multi-agent section generation."""

    sections: list[SectionRequest] = field(default_factory=list)
    execution_order: list[list[str]] = field(default_factory=list)  # Parallelizable batches
    estimated_total_time_ms: int = 0
    critical_path: list[str] = field(default_factory=list)


class SectionGenerationAgent:
    """Specialized agent for generating a specific proposal section type."""

    def __init__(self, section_type: SectionType) -> None:
        self.section_type = section_type
        self._templates = self._load_templates()

    async def generate(self, request: SectionRequest) -> SectionResult:
        """Generate the section content."""
        _emit_dispatches_agent("enterprise", f"SectionAgent_{self.section_type.value}", "generate")

        start_time = asyncio.get_event_loop().time()

        try:
            # Select template
            template = self._templates.get(
                request.section_type, self._templates[SectionType.SOLUTION_APPENDIX]
            )

            # Generate content (mock for now - would call LLM in production)
            content = self._render_template(template, request.context)

            # Calculate metrics
            word_count = len(content.split())
            elapsed_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)

            # Extract evidence citations
            evidence = self._extract_evidence(content)

            return SectionResult(
                section_id=request.section_id,
                section_type=request.section_type,
                heading=self._get_heading(request.section_type),
                body=content,
                status=SectionStatus.COMPLETED,
                word_count=word_count,
                evidence_cited=evidence,
                assumptions=self._extract_assumptions(request.context),
                quality_score=self._calculate_quality(content, request),
                generation_time_ms=elapsed_ms,
            )

        except (RuntimeError, ValueError, TypeError, AttributeError, KeyError) as exc:
            _log.error(f"[SectionGenerationAgent] Failed to generate {request.section_id}: {exc}")
            return SectionResult(
                section_id=request.section_id,
                section_type=request.section_type,
                heading=self._get_heading(request.section_type),
                body="",
                status=SectionStatus.FAILED,
                error=str(exc),
            )

    def _load_templates(self) -> dict[SectionType, str]:
        """Load section templates."""
        return {
            SectionType.EXECUTIVE_SUMMARY: """
# {{org_name}} — Agentic AI Platform Proposal

**Challenge:** {{problem_statement}}

**Proposed Solution:** A sovereign agentic AI platform with deterministic governance,
multi-hop orchestration, and full auditability.

**Key Outcomes:**
- {{outcome_1}}
- {{outcome_2}}
- {{outcome_3}}

**Investment:** {{investment_range}} over {{timeline}}.
""",
            SectionType.TECHNICAL_APPROACH: """
## Technical Architecture

Our solution deploys a six-layer agentic platform:

**L0 Routing:** Policy-enforced entry with InstructionPacket signing
**L1 Cognition:** Adaptive retrieval and RAG pipeline
**L2 Execution:** Deterministic execution contracts
**L3 Orchestration:** Multi-hop agent workflows (this proposal system)
**L4 State:** Versioned, auditable state management
**L5 Safety:** Static analysis and hallucination gates
**L6 Observability:** OpenTelemetry-aligned tracing

**Key Technical Decisions:**
- Architecture Posture: {{architecture_posture}}
- Data Strategy: {{data_strategy}}
- Integration Pattern: {{integration_pattern}}
""",
            SectionType.IMPLEMENTATION_ROADMAP: """
## Implementation Roadmap

{{phases}}

Each phase includes:
- Governance milestone: Policy enforcement checkpoint
- Measurement milestone: Value validation against KPIs
- Risk review: Go/no-go decision gate
""",
            SectionType.RISK_AND_GOVERNANCE: """
## Risk and Governance

**Governance Model:**
All outputs carry provenance metadata. Static analysis runs on every commit.
Policy enforced at L0 routing via signed InstructionPackets.

**Risk Register:**
{{risk_table}}

**Mitigation Strategy:**
- Early identification through decomposition analysis
- Proactive monitoring via L6 observability
- Escalation protocols for critical risks
""",
            SectionType.VALUE_CASE: """
## Value Case

**Quantified Benefits:**
{{value_drivers}}

**ROI Framework:**
- Investment: {{investment}}
- Break-even: {{break_even_timeline}}
- 3-year NPV: {{npv_estimate}}

**Intangible Benefits:**
- Audit-ready compliance posture
- Reduced cognitive load on engineering teams
- Future-proof architecture for AI evolution
""",
            SectionType.SOLUTION_APPENDIX: """
## Appendix: Technical Details

**Platform Capabilities:**
{{capabilities}}

**Integration Requirements:**
{{integrations}}

**Success Metrics:**
{{success_metrics}}
""",
        }

    def _render_template(self, template: str, context: dict[str, Any]) -> str:
        """Render template with context variables."""
        import re

        content = template

        # Simple variable substitution {{var_name}}
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value) if value else "[TBD]")

        # Handle list variables like {{phases}}
        def render_list(match: re.Match) -> str:
            var_name = match.group(1)
            if var_name in context and isinstance(context[var_name], list):
                items = context[var_name]
                return "\n".join(f"- {item}" for item in items)
            return "[TBD]"

        content = re.sub(r"\{\{(\w+)\}\}", render_list, content)

        return content.strip()

    def _get_heading(self, section_type: SectionType) -> str:
        """Get display heading for section type."""
        headings = {
            SectionType.EXECUTIVE_SUMMARY: "Executive Summary",
            SectionType.CURRENT_STATE: "Current State Analysis",
            SectionType.FUTURE_STATE: "Future State Architecture",
            SectionType.TECHNICAL_APPROACH: "Technical Approach",
            SectionType.IMPLEMENTATION_ROADMAP: "Implementation Roadmap",
            SectionType.RISK_AND_GOVERNANCE: "Risk and Governance",
            SectionType.VALUE_CASE: "Value Case",
            SectionType.TEAM_AND_QUALIFICATIONS: "Team and Qualifications",
            SectionType.PRICING: "Investment and Pricing",
            SectionType.SOLUTION_APPENDIX: "Solution Appendix",
        }
        return headings.get(section_type, section_type.value.replace("_", " ").title())

    def _extract_evidence(self, content: str) -> list[str]:
        """Extract evidence citations from generated content."""
        # Mock - would use actual citation extraction
        return ["platform_capability_extraction", "past_proposal_analysis"]

    def _extract_assumptions(self, context: dict[str, Any]) -> list[str]:
        """Extract assumptions from context."""
        assumptions: list[str] = []
        if "assumptions" in context:
            assumptions.extend(context["assumptions"])
        return assumptions

    def _calculate_quality(self, content: str, request: SectionRequest) -> float:
        """Calculate quality score for generated section."""
        score = 0.7  # Base score

        # Length check
        words = len(content.split())
        if request.max_words * 0.5 <= words <= request.max_words * 1.2:
            score += 0.1

        # Evidence check
        if len(self._extract_evidence(content)) >= len(request.required_evidence):
            score += 0.1

        # Content completeness check
        if "[TBD]" not in content:
            score += 0.1

        return min(1.0, score)


class SectionOrchestrator:
    """L3 Orchestrator for coordinating multiple section generation agents."""

    def __init__(self) -> None:
        self._agents: dict[SectionType, SectionGenerationAgent] = {}
        self._results: dict[str, SectionResult] = {}
        self._lineage: list[dict[str, Any]] = []

    def register_agent(self, section_type: SectionType, agent: SectionGenerationAgent) -> None:
        """Register a specialized agent for a section type."""
        self._agents[section_type] = agent

    def create_orchestration_plan(
        self,
        required_sections: list[SectionType],
        parsed_rfp: dict[str, Any],
        decompositions: list[dict[str, Any]],
    ) -> OrchestrationPlan:
        """Create an execution plan for section generation."""
        _emit_records_execution_trace("enterprise", "SectionOrchestrator", "create_plan")

        # Create section requests
        sections: list[SectionRequest] = []
        for idx, section_type in tqdm(enumerate(required_sections, 1), desc="Processing", unit="item"):
            section_id = f"SEC-{idx:02d}-{section_type.value[:8].upper()}"

            # Build context from RFP and decompositions
            context = self._build_section_context(section_type, parsed_rfp, decompositions)

            # Determine dependencies
            dependencies = self._determine_dependencies(section_type, required_sections)

            sections.append(
                SectionRequest(
                    section_type=section_type,
                    section_id=section_id,
                    dependencies=dependencies,
                    context=context,
                    max_words=self._get_section_word_limit(section_type),
                )
            )

        # Build execution order (dependency-aware batches)
        execution_order = self._compute_execution_order(sections)

        # Estimate time
        estimated_time = sum(2000 for _ in sections)  # 2s per section mock

        return OrchestrationPlan(
            sections=sections,
            execution_order=execution_order,
            estimated_total_time_ms=estimated_time,
            critical_path=self._identify_critical_path(sections),
        )

    async def execute_plan(self, plan: OrchestrationPlan) -> list[SectionResult]:
        """Execute the orchestration plan."""
        _emit_orchestrates_workflow("enterprise", "SectionOrchestrator", "execute_plan")

        results: list[SectionResult] = []

        # Execute in dependency order
        for batch in tqdm(plan.execution_order, desc="Processing", unit="item"):
            _emit_coordinates_agents("enterprise", "SectionOrchestrator", f"batch_{len(batch)}")

            # Create tasks for parallel execution within batch
            tasks: list[asyncio.Task[SectionResult]] = []
            for section_id in batch:
                request = next(r for r in plan.sections if r.section_id == section_id)
                agent = self._agents.get(request.section_type)

                if agent:
                    task = asyncio.create_task(agent.generate(request))
                    tasks.append(task)
                else:
                    _log.warning(f"[SectionOrchestrator] No agent for {request.section_type}")

            # Wait for batch completion
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in tqdm(batch_results, desc="Processing", unit="item"):
                if isinstance(result, Exception):
                    _log.error(f"[SectionOrchestrator] Batch error: {result}")
                else:
                    results.append(result)
                    self._results[result.section_id] = result

                    # Record lineage
                    self._lineage.append(
                        {
                            "section_id": result.section_id,
                            "status": str(result.status),
                            "quality_score": result.quality_score,
                            "generation_time_ms": result.generation_time_ms,
                        }
                    )

            _emit_records_workflow_lineage(
                "enterprise", "SectionOrchestrator", f"completed_batch_{len(batch)}"
            )

        return results

    def get_combined_proposal(self) -> dict[str, Any]:
        """Get all sections combined into a complete proposal."""
        completed = [r for r in self._results.values() if r.status == SectionStatus.COMPLETED]

        # Sort by section type order
        type_order = list(SectionType)
        sorted_results = sorted(
            completed,
            key=lambda r: type_order.index(r.section_type) if r.section_type in type_order else 999,
        )

        total_words = sum(r.word_count for r in sorted_results)
        avg_quality = (
            sum(r.quality_score for r in sorted_results) / len(sorted_results) if sorted_results else 0
        )

        return {
            "sections": [
                {
                    "section_id": r.section_id,
                    "heading": r.heading,
                    "body": r.body,
                    "word_count": r.word_count,
                    "evidence_cited": r.evidence_cited,
                    "assumptions": r.assumptions,
                }
                for r in sorted_results
            ],
            "total_sections": len(sorted_results),
            "total_word_count": total_words,
            "average_quality_score": round(avg_quality, 3),
            "generation_lineage": self._lineage,
        }

    def _build_section_context(
        self,
        section_type: SectionType,
        parsed_rfp: dict[str, Any],
        decompositions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build context specific to a section type."""
        base_context = {
            "org_name": parsed_rfp.get("organization", "the Client"),
            "problem_statement": parsed_rfp.get("problem_statement", "Business challenge"),
            "industry": parsed_rfp.get("industry", "technology"),
            "timeline": parsed_rfp.get("timeline", "6 months"),
        }

        if section_type == SectionType.EXECUTIVE_SUMMARY:
            base_context.update(
                {
                    "outcome_1": "Reduced operational costs through automation",
                    "outcome_2": "Improved decision quality with AI augmentation",
                    "outcome_3": "Full auditability for compliance requirements",
                    "investment_range": "$250K - $500K",
                }
            )

        elif section_type == SectionType.TECHNICAL_APPROACH:
            base_context.update(
                {
                    "architecture_posture": parsed_rfp.get("architecture_posture", "cloud-first"),
                    "data_strategy": "Vector-native with structured fallbacks",
                    "integration_pattern": "API-first with event-driven extensions",
                }
            )

        elif section_type == SectionType.IMPLEMENTATION_ROADMAP:
            phases = decompositions[0].get("sprint_breakdown", []) if decompositions else []
            base_context["phases"] = (
                [f"Phase {i + 1}: {len(p)} components" for i, p in enumerate(phases[:5])]
                if phases
                else [
                    "Discovery: Requirements validation",
                    "Foundation: Core platform deployment",
                    "Pilot: First production workload",
                    "Scale: Multi-use-case expansion",
                    "Govern: Continuous governance",
                ]
            )

        elif section_type == SectionType.VALUE_CASE:
            base_context.update(
                {
                    "value_drivers": [
                        "40-60% reduction in manual processing time",
                        "Audit-ready compliance posture from day one",
                        "Scalable architecture for future AI evolution",
                    ],
                    "investment": base_context.get("investment_range", "$250K - $500K"),
                    "break_even_timeline": "12-18 months",
                    "npv_estimate": "$1.2M - $2.5M over 3 years",
                }
            )

        return base_context

    def _determine_dependencies(
        self,
        section_type: SectionType,
        all_sections: list[SectionType],
    ) -> list[str]:
        """Determine which sections must complete before this one."""
        dependencies: dict[SectionType, list[SectionType]] = {
            SectionType.FUTURE_STATE: [SectionType.CURRENT_STATE],
            SectionType.IMPLEMENTATION_ROADMAP: [SectionType.TECHNICAL_APPROACH],
            SectionType.VALUE_CASE: [SectionType.EXECUTIVE_SUMMARY, SectionType.FUTURE_STATE],
        }

        required_before = dependencies.get(section_type, [])
        return [
            f"SEC-{all_sections.index(t) + 1:02d}-{t.value[:8].upper()}"
            for t in required_before
            if t in all_sections
        ]

    def _compute_execution_order(self, sections: list[SectionRequest]) -> list[list[str]]:
        """Compute parallelizable execution batches."""
        # Simple approach: no dependencies = batch 1, with deps = subsequent batches
        batches: list[list[str]] = []
        completed: set[str] = set()

        remaining = {s.section_id for s in sections}

        while remaining:
            batch: list[str] = []

            for section_id in remaining:
                request = next(s for s in sections if s.section_id == section_id)
                # Can execute if all dependencies are completed
                if all(dep in completed for dep in request.dependencies):
                    batch.append(section_id)

            if not batch:
                # Circular dependency or missing dependency
                _log.error("[SectionOrchestrator] Unable to resolve dependencies")
                batch = list(remaining)  # Force execution

            batches.append(batch)
            completed.update(batch)
            remaining -= set(batch)

        return batches

    def _get_section_word_limit(self, section_type: SectionType) -> int:
        """Get recommended word limit for section type."""
        limits = {
            SectionType.EXECUTIVE_SUMMARY: 300,
            SectionType.CURRENT_STATE: 400,
            SectionType.FUTURE_STATE: 500,
            SectionType.TECHNICAL_APPROACH: 600,
            SectionType.IMPLEMENTATION_ROADMAP: 500,
            SectionType.RISK_AND_GOVERNANCE: 400,
            SectionType.VALUE_CASE: 400,
            SectionType.TEAM_AND_QUALIFICATIONS: 300,
            SectionType.PRICING: 300,
            SectionType.SOLUTION_APPENDIX: 800,
        }
        return limits.get(section_type, 500)

    def _identify_critical_path(self, sections: list[SectionRequest]) -> list[str]:
        """Identify the critical path through sections."""
        # Sections with most dependents are on critical path
        dependents_count: dict[str, int] = {}
        for s in sections:
            for dep in s.dependencies:
                dependents_count[dep] = dependents_count.get(dep, 0) + 1

        # Sort by number of dependents (descending)
        critical = sorted(dependents_count.keys(), key=lambda k: dependents_count[k], reverse=True)
        return critical[:3]  # Top 3 most depended-on sections


class MultiAgentProposalOrchestrator:
    """High-level orchestrator for multi-agent proposal generation."""

    def __init__(self) -> None:
        self.section_orchestrator = SectionOrchestrator()
        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """Initialize all section generation agents."""
        for section_type in SectionType:
            agent = SectionGenerationAgent(section_type)
            self.section_orchestrator.register_agent(section_type, agent)

    async def generate_proposal(
        self,
        parsed_rfp: dict[str, Any],
        decompositions: list[dict[str, Any]],
        required_sections: list[SectionType] | None = None,
    ) -> dict[str, Any]:
        """Generate complete proposal using multiple agents."""
        _emit_orchestrates_workflow("enterprise", "MultiAgentProposalOrchestrator", "generate_proposal")

        sections = required_sections or [
            SectionType.EXECUTIVE_SUMMARY,
            SectionType.CURRENT_STATE,
            SectionType.FUTURE_STATE,
            SectionType.TECHNICAL_APPROACH,
            SectionType.IMPLEMENTATION_ROADMAP,
            SectionType.RISK_AND_GOVERNANCE,
            SectionType.VALUE_CASE,
        ]

        # Create execution plan
        plan = self.section_orchestrator.create_orchestration_plan(
            required_sections=sections,
            parsed_rfp=parsed_rfp,
            decompositions=decompositions,
        )

        _log.info(
            f"[MultiAgentProposalOrchestrator] Plan: {len(plan.sections)} sections, "
            f"{len(plan.execution_order)} batches"
        )

        # Execute plan
        results = await self.section_orchestrator.execute_plan(plan)

        # Aggregate results
        proposal = self.section_orchestrator.get_combined_proposal()

        # Add orchestration metadata
        proposal["orchestration_metadata"] = {
            "total_sections_requested": len(sections),
            "sections_completed": len([r for r in results if r.status == SectionStatus.COMPLETED]),
            "sections_failed": len([r for r in results if r.status == SectionStatus.FAILED]),
            "execution_batches": len(plan.execution_order),
            "critical_path": plan.critical_path,
        }

        return proposal

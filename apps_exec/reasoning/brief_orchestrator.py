"""
L3 Multi-Agent Brief Orchestration — apps_exec.enterprise.

Orchestrates multiple specialized brief generation agents with
coordination, dependency management, and result aggregation.

Layer 3 Orchestration: Multi-hop workflows, agent dispatch, lineage tracking.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,
    _emit_records_workflow_lineage,
)

_log = logging.getLogger(__name__)


class BriefAgentType(str, Enum):
    """Types of brief generation agents."""

    SOURCE_INGESTION = "source_ingestion"
    CAPABILITY_EXTRACT = "capability_extract"
    SECTION_GENERATE = "section_generate"
    STYLE_VALIDATE = "style_validate"
    BRIEF_ASSEMBLE = "brief_assemble"
    QUALITY_CHECK = "quality_check"


class AgentStatus(str, Enum):
    """Status of agent execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class BriefAgentRequest:
    """Request to execute a brief generation agent."""

    agent_type: BriefAgentType
    agent_id: str
    dependencies: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    timeout_ms: int = 30000


@dataclass
class BriefAgentResult:
    """Result from executing a brief generation agent."""

    agent_id: str
    agent_type: BriefAgentType
    status: AgentStatus
    result_data: dict[str, Any] = field(default_factory=dict)
    execution_time_ms: int = 0
    error: str = ""


@dataclass
class BriefOrchestrationPlan:
    """Execution plan for multi-agent brief generation."""

    agents: list[BriefAgentRequest] = field(default_factory=list)
    execution_order: list[list[str]] = field(default_factory=list)
    estimated_total_time_ms: int = 0
    critical_path: list[str] = field(default_factory=list)


class BriefGenerationAgent:
    """Specialized agent for a specific brief generation task."""

    def __init__(self, agent_type: BriefAgentType) -> None:
        self.agent_type = agent_type

    async def execute(self, request: BriefAgentRequest) -> BriefAgentResult:
        """Execute the brief generation task."""
        _emit_dispatches_agent("enterprise", f"BriefAgent_{self.agent_type.value}", "execute")

        start_time = asyncio.get_event_loop().time()

        try:
            # Route to appropriate implementation
            result_data = await self._run_implementation(request)

            elapsed_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)

            return BriefAgentResult(
                agent_id=request.agent_id,
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                result_data=result_data,
                execution_time_ms=elapsed_ms,
            )

        except Exception as exc:
            _log.error(f"[BriefGenerationAgent] {self.agent_type} failed: {exc}")
            return BriefAgentResult(
                agent_id=request.agent_id,
                agent_type=self.agent_type,
                status=AgentStatus.FAILED,
                error=str(exc),
            )

    async def _run_implementation(self, request: BriefAgentRequest) -> dict[str, Any]:
        """Run the agent-specific implementation."""
        implementations = {
            BriefAgentType.SOURCE_INGESTION: self._ingest_sources,
            BriefAgentType.CAPABILITY_EXTRACT: self._extract_capabilities,
            BriefAgentType.SECTION_GENERATE: self._generate_sections,
            BriefAgentType.STYLE_VALIDATE: self._validate_style,
            BriefAgentType.BRIEF_ASSEMBLE: self._assemble_brief,
            BriefAgentType.QUALITY_CHECK: self._check_quality,
        }

        impl = implementations.get(self.agent_type)
        if impl:
            return await impl(request.context)

        return {"error": "Unknown agent type"}

    async def _ingest_sources(self, context: dict[str, Any]) -> dict[str, Any]:
        """Ingest source documents."""
        source_dirs = context.get("source_dirs", [])
        # Mock ingestion
        return {
            "documents_ingested": len(source_dirs) * 3,
            "total_chars": 15000,
            "capabilities_found": ["L0_routing", "L1_reasoning", "L2_execution", "L3_orchestration"],
        }

    async def _extract_capabilities(self, context: dict[str, Any]) -> dict[str, Any]:
        """Extract capabilities from ingested content."""
        # Mock extraction
        return {
            "capabilities": [
                {"name": "Multi-agent orchestration", "evidence": "ExecOrchestrator.py"},
                {"name": "Deterministic execution", "evidence": "lifecycle_trace_contract.py"},
                {"name": "Quality gating", "evidence": "style_gate_validator.py"},
            ],
            "evidence_anchors": 8,
        }

    async def _generate_sections(self, context: dict[str, Any]) -> dict[str, Any]:
        """Generate brief sections."""
        persona = context.get("persona", "recruiter")
        # Mock section generation
        sections = {
            "recruiter": ["Executive Summary", "Key Skills", "Experience Highlights"],
            "cto": ["Executive Summary", "Architecture", "Governance", "Technical Depth"],
            "board": ["Executive Summary", "Strategic Value", "ROI Framework"],
        }
        return {
            "sections_generated": sections.get(persona, ["Executive Summary"]),
            "word_count": 450,
        }

    async def _validate_style(self, context: dict[str, Any]) -> dict[str, Any]:
        """Validate style compliance."""
        # Mock validation
        return {
            "buzzword_density": 0.02,
            "evidence_count": 5,
            "style_violations": [],
            "passed": True,
        }

    async def _assemble_brief(self, context: dict[str, Any]) -> dict[str, Any]:
        """Assemble final brief."""
        persona = context.get("persona", "recruiter")
        return {
            "brief_assembled": True,
            "persona": persona,
            "total_sections": 4,
            "final_word_count": 520,
        }

    async def _check_quality(self, context: dict[str, Any]) -> dict[str, Any]:
        """Perform final quality check."""
        return {
            "quality_score": 0.88,
            "gates_passed": True,
            "recommendations": [],
        }


class BriefOrchestrator:
    """L3 Orchestrator for coordinating multiple brief generation agents."""

    def __init__(self) -> None:
        self._agents: dict[BriefAgentType, BriefGenerationAgent] = {}
        self._results: dict[str, BriefAgentResult] = {}
        self._lineage: list[dict[str, Any]] = []

    def register_agent(self, agent_type: BriefAgentType, agent: BriefGenerationAgent) -> None:
        """Register a specialized agent."""
        self._agents[agent_type] = agent

    def create_orchestration_plan(
        self,
        personas: list[str],
        source_dirs: list[str],
    ) -> BriefOrchestrationPlan:
        """Create an execution plan for brief generation."""
        _emit_records_execution_trace("enterprise", "BriefOrchestrator", "create_plan")

        # Define agent execution pipeline
        agents: list[BriefAgentRequest] = [
            BriefAgentRequest(
                agent_type=BriefAgentType.SOURCE_INGESTION,
                agent_id="AGENT-01-INGEST",
                context={"source_dirs": source_dirs},
                timeout_ms=60000,
            ),
            BriefAgentRequest(
                agent_type=BriefAgentType.CAPABILITY_EXTRACT,
                agent_id="AGENT-02-EXTRACT",
                dependencies=["AGENT-01-INGEST"],
                context={},
                timeout_ms=30000,
            ),
            BriefAgentRequest(
                agent_type=BriefAgentType.SECTION_GENERATE,
                agent_id="AGENT-03-GENERATE",
                dependencies=["AGENT-02-EXTRACT"],
                context={"personas": personas},
                timeout_ms=45000,
            ),
            BriefAgentRequest(
                agent_type=BriefAgentType.STYLE_VALIDATE,
                agent_id="AGENT-04-VALIDATE",
                dependencies=["AGENT-03-GENERATE"],
                context={},
                timeout_ms=20000,
            ),
            BriefAgentRequest(
                agent_type=BriefAgentType.BRIEF_ASSEMBLE,
                agent_id="AGENT-05-ASSEMBLE",
                dependencies=["AGENT-04-VALIDATE"],
                context={"personas": personas},
                timeout_ms=20000,
            ),
            BriefAgentRequest(
                agent_type=BriefAgentType.QUALITY_CHECK,
                agent_id="AGENT-06-QUALITY",
                dependencies=["AGENT-05-ASSEMBLE"],
                context={},
                timeout_ms=15000,
            ),
        ]

        # Compute execution order
        execution_order = self._compute_execution_order(agents)

        return BriefOrchestrationPlan(
            agents=agents,
            execution_order=execution_order,
            estimated_total_time_ms=192000,  # Sum of all timeouts
            critical_path=["AGENT-01-INGEST", "AGENT-02-EXTRACT", "AGENT-03-GENERATE", "AGENT-05-ASSEMBLE"],
        )

    async def execute_plan(self, plan: BriefOrchestrationPlan) -> list[BriefAgentResult]:
        """Execute the orchestration plan."""
        _emit_orchestrates_workflow("enterprise", "BriefOrchestrator", "execute_plan")

        results: list[BriefAgentResult] = []

        for batch in plan.execution_order:
            _emit_coordinates_agents("enterprise", "BriefOrchestrator", f"batch_{len(batch)}")

            # Create tasks for parallel execution
            tasks: list[asyncio.Task[BriefAgentResult]] = []
            for agent_id in batch:
                request = next(a for a in plan.agents if a.agent_id == agent_id)
                agent = self._agents.get(request.agent_type)

                if agent:
                    task = asyncio.create_task(agent.execute(request))
                    tasks.append(task)

            # Wait for batch completion
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    _log.error(f"[BriefOrchestrator] Batch error: {result}")
                else:
                    results.append(result)
                    self._results[result.agent_id] = result

                    self._lineage.append({
                        "agent_id": result.agent_id,
                        "agent_type": result.agent_type.value,
                        "status": result.status.value,
                        "execution_time_ms": result.execution_time_ms,
                    })

            _emit_records_workflow_lineage("enterprise", "BriefOrchestrator", f"completed_batch_{len(batch)}")

        return results

    def get_combined_results(self) -> dict[str, Any]:
        """Get all results combined into a single brief generation report."""
        completed = [r for r in self._results.values() if r.status == AgentStatus.COMPLETED]

        # Aggregate results by agent type
        by_type: dict[str, list[BriefAgentResult]] = {}
        for r in completed:
            if r.agent_type.value not in by_type:
                by_type[r.agent_type.value] = []
            by_type[r.agent_type.value].append(r)

        # Extract key metrics
        quality_score = 0.0
        if BriefAgentType.QUALITY_CHECK.value in by_type:
            quality_result = by_type[BriefAgentType.QUALITY_CHECK.value][0]
            quality_score = quality_result.result_data.get("quality_score", 0.0)

        gates_passed = True
        if BriefAgentType.STYLE_VALIDATE.value in by_type:
            style_result = by_type[BriefAgentType.STYLE_VALIDATE.value][0]
            gates_passed = style_result.result_data.get("passed", True)

        return {
            "agents_executed": len(completed),
            "quality_score": quality_score,
            "style_gates_passed": gates_passed,
            "total_execution_time_ms": sum(r.execution_time_ms for r in completed),
            "results_by_type": {
                atype: [r.result_data for r in results]
                for atype, results in by_type.items()
            },
            "execution_lineage": self._lineage,
        }

    def _compute_execution_order(self, agents: list[BriefAgentRequest]) -> list[list[str]]:
        """Compute parallelizable execution batches."""
        batches: list[list[str]] = []
        completed: set[str] = set()

        remaining = {a.agent_id for a in agents}

        while remaining:
            batch: list[str] = []

            for agent_id in remaining:
                request = next(a for a in agents if a.agent_id == agent_id)
                if all(dep in completed for dep in request.dependencies):
                    batch.append(agent_id)

            if not batch:
                _log.error("[BriefOrchestrator] Unable to resolve dependencies")
                batch = list(remaining)

            batches.append(batch)
            completed.update(batch)
            remaining -= set(batch)

        return batches


class MultiAgentBriefEngine:
    """High-level engine for multi-agent brief generation."""

    def __init__(self) -> None:
        self.orchestrator = BriefOrchestrator()
        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """Initialize all brief generation agents."""
        for agent_type in BriefAgentType:
            agent = BriefGenerationAgent(agent_type)
            self.orchestrator.register_agent(agent_type, agent)

    async def generate_briefs(
        self,
        personas: list[str],
        source_dirs: list[str],
    ) -> dict[str, Any]:
        """Run complete multi-agent brief generation."""
        _emit_orchestrates_workflow("enterprise", "MultiAgentBriefEngine", "generate_briefs")

        # Create execution plan
        plan = self.orchestrator.create_orchestration_plan(personas, source_dirs)

        _log.info(f"[MultiAgentBriefEngine] Plan: {len(plan.agents)} agents, "
                  f"{len(plan.execution_order)} batches")

        # Execute plan
        results = await self.orchestrator.execute_plan(plan)

        # Aggregate results
        combined = self.orchestrator.get_combined_results()

        # Add orchestration metadata
        combined["orchestration_metadata"] = {
            "total_agents_requested": len(plan.agents),
            "agents_completed": len([r for r in results if r.status == AgentStatus.COMPLETED]),
            "agents_failed": len([r for r in results if r.status == AgentStatus.FAILED]),
            "execution_batches": len(plan.execution_order),
            "critical_path": plan.critical_path,
            "target_personas": personas,
        }

        return combined

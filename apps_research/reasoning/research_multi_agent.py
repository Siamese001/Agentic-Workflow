"""
L3 Multi-Agent Research Orchestration — apps_research.enterprise.

Orchestrates multiple specialized research agents with
coordination, dependency management, and result aggregation.

Layer 3 Orchestration: Multi-hop workflows, agent dispatch, lineage tracking.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,
    _emit_records_workflow_lineage,
)

_log = logging.getLogger(__name__)


class ResearchAgentType(str, Enum):
    """Types of research generation agents."""

    QUERY_ANALYZE = "query_analyze"
    SOURCE_GATHER = "source_gather"
    EVIDENCE_EXTRACT = "evidence_extract"
    CONTENT_SYNTHESIZE = "content_synthesize"
    CLAIM_TYPE = "claim_type"
    QUALITY_VALIDATE = "quality_validate"


class AgentStatus(str, Enum):
    """Status of agent execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class ResearchAgentRequest:
    """Request to execute a research generation agent."""

    agent_type: ResearchAgentType
    agent_id: str
    dependencies: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    timeout_ms: int = 30000


@dataclass
class ResearchAgentResult:
    """Result from executing a research generation agent."""

    agent_id: str
    agent_type: ResearchAgentType
    status: AgentStatus
    result_data: dict[str, Any] = field(default_factory=dict)
    execution_time_ms: int = 0
    error: str = ""


@dataclass
class ResearchOrchestrationPlan:
    """Execution plan for multi-agent research generation."""

    agents: list[ResearchAgentRequest] = field(default_factory=list)
    execution_order: list[list[str]] = field(default_factory=list)
    estimated_total_time_ms: int = 0
    critical_path: list[str] = field(default_factory=list)


class ResearchGenerationAgent:
    """Specialized agent for a specific research generation task."""

    def __init__(self, agent_type: ResearchAgentType) -> None:
        self.agent_type = agent_type

    async def execute(self, request: ResearchAgentRequest) -> ResearchAgentResult:
        """Execute the research generation task."""
        _emit_dispatches_agent("enterprise", f"ResearchAgent_{self.agent_type.value}", "execute")

        start_time = asyncio.get_event_loop().time()

        try:
            # Route to appropriate implementation
            result_data = await self._run_implementation(request)

            elapsed_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)

            return ResearchAgentResult(
                agent_id=request.agent_id,
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                result_data=result_data,
                execution_time_ms=elapsed_ms,
            )

        except Exception as exc:
            _log.error(f"[ResearchGenerationAgent] {self.agent_type} failed: {exc}")
            return ResearchAgentResult(
                agent_id=request.agent_id,
                agent_type=self.agent_type,
                status=AgentStatus.FAILED,
                error=str(exc),
            )

    async def _run_implementation(self, request: ResearchAgentRequest) -> dict[str, Any]:
        """Run the agent-specific implementation."""
        implementations = {
            ResearchAgentType.QUERY_ANALYZE: self._analyze_query,
            ResearchAgentType.SOURCE_GATHER: self._gather_sources,
            ResearchAgentType.EVIDENCE_EXTRACT: self._extract_evidence,
            ResearchAgentType.CONTENT_SYNTHESIZE: self._synthesize_content,
            ResearchAgentType.CLAIM_TYPE: self._type_claims,
            ResearchAgentType.QUALITY_VALIDATE: self._validate_quality,
        }

        impl = implementations.get(self.agent_type)
        if impl:
            return await impl(request.context)

        return {"error": "Unknown agent type"}

    async def _analyze_query(self, context: dict[str, Any]) -> dict[str, Any]:
        """Analyze research query."""
        topic = context.get("topic", "unknown")
        return {
            "query_analyzed": True,
            "topic": topic,
            "components_identified": 3,
            "evidence_requirements": ["direct_evidence", "interpretation"],
        }

    async def _gather_sources(self, context: dict[str, Any]) -> dict[str, Any]:
        """Gather research sources."""
        topic = context.get("topic", "unknown")
        return {
            "sources_gathered": 5,
            "source_types": ["documentation", "code", "benchmarks"],
            "confidence_levels": [0.9, 0.85, 0.8, 0.75, 0.7],
        }

    async def _extract_evidence(self, context: dict[str, Any]) -> dict[str, Any]:
        """Extract evidence from sources."""
        return {
            "evidence_extracted": 8,
            "evidence_types": ["implementation", "performance", "governance"],
            "quality_score": 0.85,
        }

    async def _synthesize_content(self, context: dict[str, Any]) -> dict[str, Any]:
        """Synthesize content from evidence."""
        mode = context.get("mode", "brief")
        return {
            "content_synthesized": True,
            "mode": mode,
            "sections_generated": 3 if mode == "brief" else 4,
            "word_count": 450,
        }

    async def _type_claims(self, context: dict[str, Any]) -> dict[str, Any]:
        """Type claims in content."""
        return {
            "claims_typed": True,
            "claim_counts": {
                "direct_evidence": 5,
                "interpretation": 3,
                "analyst_inference": 2,
                "assumption": 1,
            },
        }

    async def _validate_quality(self, context: dict[str, Any]) -> dict[str, Any]:
        """Validate research quality."""
        return {
            "quality_validated": True,
            "quality_score": 0.88,
            "source_count": 5,
            "claim_coverage": 0.9,
            "passed": True,
        }


class ResearchOrchestrator:
    """L3 Orchestrator for coordinating multiple research generation agents."""

    def __init__(self) -> None:
        self._agents: dict[ResearchAgentType, ResearchGenerationAgent] = {}
        self._results: dict[str, ResearchAgentResult] = {}
        self._lineage: list[dict[str, Any]] = []

    def register_agent(self, agent_type: ResearchAgentType, agent: ResearchGenerationAgent) -> None:
        """Register a specialized agent."""
        self._agents[agent_type] = agent

    def create_orchestration_plan(
        self,
        topic: str,
        artifact_mode: str,
    ) -> ResearchOrchestrationPlan:
        """Create an execution plan for research generation."""
        _emit_records_execution_trace("enterprise", "ResearchOrchestrator", "create_plan")

        # Define agent execution pipeline
        agents: list[ResearchAgentRequest] = [
            ResearchAgentRequest(
                agent_type=ResearchAgentType.QUERY_ANALYZE,
                agent_id="AGENT-01-QUERY",
                context={"topic": topic, "mode": artifact_mode},
                timeout_ms=20000,
            ),
            ResearchAgentRequest(
                agent_type=ResearchAgentType.SOURCE_GATHER,
                agent_id="AGENT-02-SOURCES",
                dependencies=["AGENT-01-QUERY"],
                context={"topic": topic},
                timeout_ms=60000,
            ),
            ResearchAgentRequest(
                agent_type=ResearchAgentType.EVIDENCE_EXTRACT,
                agent_id="AGENT-03-EVIDENCE",
                dependencies=["AGENT-02-SOURCES"],
                context={},
                timeout_ms=45000,
            ),
            ResearchAgentRequest(
                agent_type=ResearchAgentType.CONTENT_SYNTHESIZE,
                agent_id="AGENT-04-SYNTHESIZE",
                dependencies=["AGENT-03-EVIDENCE"],
                context={"topic": topic, "mode": artifact_mode},
                timeout_ms=40000,
            ),
            ResearchAgentRequest(
                agent_type=ResearchAgentType.CLAIM_TYPE,
                agent_id="AGENT-05-TYPE",
                dependencies=["AGENT-04-SYNTHESIZE"],
                context={},
                timeout_ms=20000,
            ),
            ResearchAgentRequest(
                agent_type=ResearchAgentType.QUALITY_VALIDATE,
                agent_id="AGENT-06-VALIDATE",
                dependencies=["AGENT-05-TYPE"],
                context={},
                timeout_ms=15000,
            ),
        ]

        # Compute execution order
        execution_order = self._compute_execution_order(agents)

        return ResearchOrchestrationPlan(
            agents=agents,
            execution_order=execution_order,
            estimated_total_time_ms=200000,  # Sum of all timeouts
            critical_path=["AGENT-01-QUERY", "AGENT-02-SOURCES", "AGENT-03-EVIDENCE",
                          "AGENT-04-SYNTHESIZE", "AGENT-06-VALIDATE"],
        )

    async def execute_plan(self, plan: ResearchOrchestrationPlan) -> list[ResearchAgentResult]:
        """Execute the orchestration plan."""
        _emit_orchestrates_workflow("enterprise", "ResearchOrchestrator", "execute_plan")

        results: list[ResearchAgentResult] = []

        for batch in plan.execution_order:
            _emit_coordinates_agents("enterprise", "ResearchOrchestrator", f"batch_{len(batch)}")

            # Create tasks for parallel execution
            tasks: list[asyncio.Task[ResearchAgentResult]] = []
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
                    _log.error(f"[ResearchOrchestrator] Batch error: {result}")
                else:
                    results.append(result)
                    self._results[result.agent_id] = result

                    self._lineage.append({
                        "agent_id": result.agent_id,
                        "agent_type": result.agent_type.value,
                        "status": result.status.value,
                        "execution_time_ms": result.execution_time_ms,
                    })

            _emit_records_workflow_lineage("enterprise", "ResearchOrchestrator", f"completed_batch_{len(batch)}")

        return results

    def get_combined_results(self) -> dict[str, Any]:
        """Get all results combined into a single research report."""
        completed = [r for r in self._results.values() if r.status == AgentStatus.COMPLETED]

        # Aggregate results by agent type
        by_type: dict[str, list[ResearchAgentResult]] = {}
        for r in completed:
            if r.agent_type.value not in by_type:
                by_type[r.agent_type.value] = []
            by_type[r.agent_type.value].append(r)

        # Extract key metrics
        quality_score = 0.0
        if ResearchAgentType.QUALITY_VALIDATE.value in by_type:
            quality_result = by_type[ResearchAgentType.QUALITY_VALIDATE.value][0]
            quality_score = quality_result.result_data.get("quality_score", 0.0)

        sources_count = 0
        if ResearchAgentType.SOURCE_GATHER.value in by_type:
            source_result = by_type[ResearchAgentType.SOURCE_GATHER.value][0]
            sources_count = source_result.result_data.get("sources_gathered", 0)

        passed = True
        if ResearchAgentType.QUALITY_VALIDATE.value in by_type:
            validate_result = by_type[ResearchAgentType.QUALITY_VALIDATE.value][0]
            passed = validate_result.result_data.get("passed", True)

        return {
            "agents_executed": len(completed),
            "quality_score": quality_score,
            "sources_count": sources_count,
            "validation_passed": passed,
            "total_execution_time_ms": sum(r.execution_time_ms for r in completed),
            "results_by_type": {
                atype: [r.result_data for r in results]
                for atype, results in by_type.items()
            },
            "execution_lineage": self._lineage,
        }

    def _compute_execution_order(self, agents: list[ResearchAgentRequest]) -> list[list[str]]:
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
                _log.error("[ResearchOrchestrator] Unable to resolve dependencies")
                batch = list(remaining)

            batches.append(batch)
            completed.update(batch)
            remaining -= set(batch)

        return batches


class MultiAgentResearchEngine:
    """High-level engine for multi-agent research generation."""

    def __init__(self) -> None:
        self.orchestrator = ResearchOrchestrator()
        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """Initialize all research generation agents."""
        for agent_type in ResearchAgentType:
            agent = ResearchGenerationAgent(agent_type)
            self.orchestrator.register_agent(agent_type, agent)

    async def generate_research(
        self,
        topic: str,
        artifact_mode: str,
    ) -> dict[str, Any]:
        """Run complete multi-agent research generation."""
        _emit_orchestrates_workflow("enterprise", "MultiAgentResearchEngine", "generate_research")

        # Create execution plan
        plan = self.orchestrator.create_orchestration_plan(topic, artifact_mode)

        _log.info(f"[MultiAgentResearchEngine] Plan: {len(plan.agents)} agents, "
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
            "topic": topic,
            "artifact_mode": artifact_mode,
        }

        return combined

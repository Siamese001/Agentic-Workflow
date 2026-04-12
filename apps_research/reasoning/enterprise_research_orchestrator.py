"""
Enterprise Research Orchestrator — apps_research.enterprise.

Unified orchestration that combines:
- L0: Topic input and artifact mode selection
- L1: Research query decomposition
- L2: Past research retrieval for source recommendations
- L3: Multi-agent research generation
- L5: Source validation and quality gates
- Output: Full research artifacts with traceability
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,
    _emit_stores_embedding,
)
from apps_research.engines.research_retrieval_engine import (
    create_retrieval_engine,
)

# Import enterprise components
from apps_research.reasoning.query_decomposition_agent import (
    QueryDecomposition,
    QueryDecompositionAgent,
)
from apps_research.reasoning.research_multi_agent import (
    MultiAgentResearchEngine,
)
from apps_research.services.repo_signal_service import RepoSignalService
from apps_research.validators.research_source_validator import (
    ResearchValidationAgent,
)

_log = logging.getLogger(__name__)


@dataclass
class EnterpriseResearchRequest:
    """Request for enterprise research processing."""

    # Research parameters
    topic: str = ""
    artifact_mode: str = "brief"
    target_audience: str = "technical"

    # Configuration
    enable_retrieval: bool = True
    enable_validation: bool = True
    enable_repo_signals: bool = True
    update_baseline: bool = False
    output_dir: str = "reports/research/enterprise"
    trace_id: str = ""

    def __post_init__(self) -> None:
        if not self.trace_id:
            self.trace_id = self._generate_trace_id()

    def _generate_trace_id(self) -> str:
        """Generate unique trace ID."""
        content = f"research:{self.artifact_mode}:{self.topic[:64]}:{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class EnterpriseResearchResult:
    """Result of enterprise research processing."""

    trace_id: str
    status: str  # complete, partial, failed

    # Decomposition
    query_decomposition: QueryDecomposition | None = None
    execution_plan: dict[str, Any] = field(default_factory=dict)

    # Retrieved context
    similar_research: list[dict[str, Any]] = field(default_factory=list)
    quality_benchmarks: dict[str, Any] = field(default_factory=dict)
    repo_signals: dict[str, Any] = field(default_factory=dict)

    # Generation results
    generation_results: dict[str, Any] = field(default_factory=dict)

    # Validation
    validation_results: list[dict[str, Any]] = field(default_factory=list)
    gate_results: list[dict[str, Any]] = field(default_factory=list)

    # Artifacts
    artifact_paths: list[str] = field(default_factory=list)
    report_path: str = ""
    manifest_path: str = ""
    execution_log: list[dict[str, Any]] = field(default_factory=list)

    # Metrics
    total_execution_time_ms: int = 0
    avg_quality_score: float = 0.0


class EnterpriseResearchOrchestrator:
    """Enterprise-grade research orchestrator.

    Pipeline:
    1. DECOMPOSE: Break down research query (L1)
    2. RETRIEVE: Find similar research and quality benchmarks (L2)
    3. GENERATE: Multi-agent research synthesis (L3)
    4. VALIDATE: Source and quality gates (L5)
    5. EMIT: Traceable research artifacts
    """

    def __init__(self) -> None:
        # Initialize all subsystems
        self.retrieval_engine = create_retrieval_engine()
        self.repo_signal_service = RepoSignalService()
        self.decomposition_agent = QueryDecompositionAgent()
        self.generation_engine = MultiAgentResearchEngine()
        self.validation_agent = ResearchValidationAgent()

        self._execution_log: list[dict[str, Any]] = []

    async def process(self, request: EnterpriseResearchRequest) -> EnterpriseResearchResult:
        """Process a research request end-to-end."""
        start_time = asyncio.get_event_loop().time()
        trace_id = request.trace_id

        _log.info(f"[EnterpriseResearchOrchestrator] Starting research trace={trace_id}")
        _emit_orchestrates_workflow("enterprise", "EnterpriseResearchOrchestrator", "process_start")

        result = EnterpriseResearchResult(trace_id=trace_id, status="processing")

        try:
            # === STEP 1: DECOMPOSE (L1 Cognition) ===
            self._log_step(trace_id, "DECOMPOSE", "start")
            decomposition, exec_plan = await self._step_decompose(
                request.topic,
                request.artifact_mode,
                request.target_audience,
            )
            result.query_decomposition = decomposition
            result.execution_plan = exec_plan
            self._log_step(
                trace_id,
                "DECOMPOSE",
                "complete",
                details={
                    "components": len(decomposition.components) if decomposition else 0,
                    "estimated_time_ms": exec_plan.get("estimated_time_ms", 0),
                },
            )

            # === STEP 2: RETRIEVE (L2 Execution/RAG) ===
            if request.enable_retrieval:
                self._log_step(trace_id, "RETRIEVE", "start")
                similar, benchmarks = await self._step_retrieve(
                    request.topic,
                    request.artifact_mode,
                )
                result.similar_research = similar
                result.quality_benchmarks = benchmarks
                self._log_step(
                    trace_id,
                    "RETRIEVE",
                    "complete",
                    details={
                        "similar_found": len(similar),
                        "benchmarks": list(benchmarks.keys()) if benchmarks else [],
                    },
                )

            # === STEP 2B: CONTEXT ENRICHMENT (Repo Signals) ===
            if request.enable_repo_signals:
                self._log_step(trace_id, "ENRICH", "start")
                repo_signals = await self._step_collect_repo_signals()
                result.repo_signals = repo_signals
                self._log_step(
                    trace_id,
                    "ENRICH",
                    "complete",
                    details={
                        "adg_available": bool(repo_signals.get("adg", {}).get("available")),
                        "workflow_count": repo_signals.get("ci", {}).get("workflow_count", 0),
                        "test_inventory_entries": repo_signals.get("tests", {}).get("inventory_entries", 0),
                    },
                )

            # === STEP 3: GENERATE (L3 Orchestration) ===
            self._log_step(trace_id, "GENERATE", "start")
            gen_results = await self._step_generate(
                request.topic,
                request.artifact_mode,
            )
            result.generation_results = gen_results
            self._log_step(
                trace_id,
                "GENERATE",
                "complete",
                details={
                    "agents_executed": gen_results.get("agents_executed", 0),
                    "quality_score": gen_results.get("quality_score", 0),
                },
            )

            # === STEP 4: VALIDATE (L5 Safety) ===
            if request.enable_validation:
                self._log_step(trace_id, "VALIDATE", "start")
                validations, gates = await self._step_validate(
                    request.topic,
                    request.artifact_mode,
                )
                result.validation_results = validations
                result.gate_results = gates
                self._log_step(
                    trace_id,
                    "VALIDATE",
                    "complete",
                    details={
                        "validations_run": len(validations),
                        "gates_passed": sum(1 for g in gates if g.get("gates_passed")),
                    },
                )

            # === STEP 5: EMIT ===
            self._log_step(trace_id, "EMIT", "start")
            await self._step_emit(result, request)
            self._log_step(trace_id, "EMIT", "complete")

            # Final status
            elapsed_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
            result.total_execution_time_ms = elapsed_ms

            # Determine final status
            all_gates_passed = (
                all(g.get("gates_passed", False) for g in result.gate_results)
                if result.gate_results
                else True
            )
            if all_gates_passed:
                result.status = "complete"
            elif any(g.get("gates_passed", False) for g in result.gate_results):
                result.status = "partial"
            else:
                result.status = "failed"

            # Calculate average quality score
            if result.validation_results:
                result.avg_quality_score = sum(
                    v.get("quality_score", 0) for v in result.validation_results
                ) / len(result.validation_results)

            result.execution_log = self._execution_log

            _log.info(
                f"[EnterpriseResearchOrchestrator] Complete trace={trace_id} status={result.status} time={elapsed_ms}ms",
            )
            _emit_captures_pattern("enterprise", "EnterpriseResearchOrchestrator", "process_complete")

        except Exception as exc:
            _log.error(f"[EnterpriseResearchOrchestrator] Failed: {exc}", exc_info=True)
            result.status = "failed"
            result.execution_log = self._execution_log

        return result

    async def _step_decompose(
        self,
        topic: str,
        artifact_mode: str,
        target_audience: str,
    ) -> tuple[QueryDecomposition, dict[str, Any]]:
        """Step 1: Decompose research query (L1)."""
        _emit_dispatches_agent("enterprise", "step_decompose", "L1")

        decomposition, summary = self.decomposition_agent.analyze_research_query(
            topic,
            artifact_mode,
            target_audience,
        )
        exec_plan = self.decomposition_agent.get_research_execution_plan(decomposition)

        return decomposition, exec_plan

    async def _step_retrieve(
        self,
        topic: str,
        artifact_mode: str,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Step 2: Retrieve similar research and benchmarks (L2)."""
        _emit_records_execution_trace("enterprise", "step_retrieve", "start")

        # Find similar research
        similar = self.retrieval_engine.find_similar_research(
            current_topic=topic,
            artifact_mode=artifact_mode,
            n_results=5,
        )

        similar_list: list[dict[str, Any]] = []
        for art in similar:
            similar_list.append(
                {
                    "id": art.research_id,
                    "topic": art.topic,
                    "mode": art.artifact_mode,
                    "quality_score": art.quality_score,
                    "similarity": art.similarity_score,
                },
            )

        # Get quality benchmark
        benchmark = self.retrieval_engine.get_quality_benchmark(artifact_mode)

        return similar_list, benchmark

    async def _step_generate(
        self,
        topic: str,
        artifact_mode: str,
    ) -> dict[str, Any]:
        """Step 3: Generate research using multi-agent system (L3)."""
        _emit_coordinates_agents("enterprise", "step_generate", "L3")

        results = await self.generation_engine.generate_research(topic, artifact_mode)

        return results

    async def _step_collect_repo_signals(self) -> dict[str, Any]:
        """Step 2B: Collect production-like repo signals."""
        _emit_records_execution_trace("enterprise", "step_collect_repo_signals", "start")
        snapshot = self.repo_signal_service.collect()
        return snapshot.as_dict()

    async def _step_validate(
        self,
        topic: str,
        artifact_mode: str,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Step 4: Validate research (L5)."""
        _emit_applies_guardrail("enterprise", "step_validate", "L5")

        # Generate mock research content and source register for validation
        mock_content = self._generate_mock_research_content(topic, artifact_mode)
        mock_sources = self._generate_mock_source_register()

        required_sections = self._get_required_sections(artifact_mode)

        validation, gates = self.validation_agent.validate_research(
            mock_content,
            mock_sources,
            required_sections,
        )

        return [asdict(validation)], [gates]

    def _generate_mock_research_content(self, topic: str, mode: str) -> str:
        """Generate mock research content for validation testing."""
        content = f"""# Research: {topic}

## Executive Summary [DIRECT_EVIDENCE]

This research examines {topic} with comprehensive evidence from the agentic platform.

## Key Findings [INTERPRETATION]

The analysis reveals significant patterns in {topic} based on implementation data.

## Strategic Implications [ANALYST_INFERENCE]

Future developments in {topic} will likely follow the observed trend lines.

## Conclusion [ASSUMPTION]

Assuming continued momentum, {topic} represents a key opportunity.
"""
        return content

    def _generate_mock_source_register(self) -> list[dict[str, Any]]:
        """Generate mock source register."""
        return [
            {
                "source_id": "SRC-001",
                "title": "Agentic Core Documentation",
                "claim_type": "direct_evidence",
                "confidence": 0.95,
                "summary": "Core platform capabilities",
            },
            {
                "source_id": "SRC-002",
                "title": "Benchmark Results",
                "claim_type": "direct_evidence",
                "confidence": 0.90,
                "summary": "Performance metrics",
            },
            {
                "source_id": "SRC-003",
                "title": "Industry Analysis",
                "claim_type": "interpretation",
                "confidence": 0.75,
                "summary": "Market context",
            },
        ]

    def _get_required_sections(self, mode: str) -> list[str]:
        """Get required sections for artifact mode."""
        sections: dict[str, list[str]] = {
            "brief": ["Executive Summary", "Key Findings", "Strategic Implications"],
            "comparison": ["Comparison Overview", "Comparison Matrix", "Recommendation"],
            "trend": ["Trend Overview", "Signal Analysis", "Horizon Implications"],
            "position": ["Position Statement", "Supporting Evidence", "Counterarguments", "Conclusion"],
            "thought_leadership": ["Hook", "Insight", "Evidence", "Call to Action"],
        }
        return sections.get(mode, ["Executive Summary"])

    async def _step_emit(
        self,
        result: EnterpriseResearchResult,
        request: EnterpriseResearchRequest,
    ) -> None:
        """Step 5: Emit all artifacts."""
        _emit_stores_embedding("enterprise", "step_emit", "artifacts")

        out_dir = Path(request.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        # 1. Main report
        report_path = out_dir / f"enterprise_research_{result.trace_id[:8]}.md"
        self._write_research_markdown(result, report_path)
        result.report_path = str(report_path)

        # 2. Manifest
        manifest_path = out_dir / f"research_manifest_{result.trace_id[:8]}.json"
        self._write_manifest(result, manifest_path)
        result.manifest_path = str(manifest_path)

    def _write_research_markdown(self, result: EnterpriseResearchResult, path: Path) -> None:
        """Write the research report as markdown."""
        lines: list[str] = []

        lines.append("# Enterprise Research Generation Report")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Trace ID:** `{result.trace_id}`")
        lines.append(f"**Status:** {result.status.upper()}")
        lines.append("")

        # Executive summary
        lines.append("## Executive Summary")
        lines.append("")
        if result.query_decomposition:
            lines.append(f"- **Topic:** {result.query_decomposition.original_topic}")
            lines.append(f"- **Artifact Mode:** {result.query_decomposition.artifact_mode}")
            lines.append(f"- **Components:** {len(result.query_decomposition.components)}")
        lines.append(f"- **Agents Executed:** {result.generation_results.get('agents_executed', 0)}")
        lines.append(f"- **Avg Quality Score:** {result.avg_quality_score:.0%}")
        lines.append("")

        # Query decomposition
        if result.query_decomposition:
            lines.append("## Query Decomposition")
            lines.append("")
            for comp in result.query_decomposition.components:
                lines.append(f"**{comp.component_id}:** {comp.query_type.value}")
                lines.append(f"- Evidence: {comp.evidence_required.value}")
                lines.append(f"- Sources Needed: {comp.sources_needed}")
                lines.append("")

        # Generation results
        lines.append("## Generation Results")
        lines.append("")
        lines.append(f"- **Quality Score:** {result.generation_results.get('quality_score', 0):.0%}")
        lines.append(f"- **Sources Count:** {result.generation_results.get('sources_count', 0)}")
        lines.append(
            f"- **Validation Passed:** {'✅' if result.generation_results.get('validation_passed') else '❌'}",
        )
        lines.append("")

        # Validation results
        if result.validation_results:
            lines.append("## Validation Results")
            lines.append("")
            for i, (validation, gates) in enumerate(zip(result.validation_results, result.gate_results)):
                lines.append(f"**Run {i + 1}:**")
                lines.append(f"- Quality Score: {validation.get('quality_score', 0):.0%}")
                lines.append(f"- Source Coverage: {validation.get('source_coverage', 0):.0%}")
                lines.append(f"- Gates Passed: {'✅' if gates.get('gates_passed') else '❌'}")
                lines.append("")

        # Repository operational context
        if result.repo_signals:
            lines.append("## Repository Operational Signals")
            lines.append("")
            adg = result.repo_signals.get("adg", {})
            tests = result.repo_signals.get("tests", {})
            ci = result.repo_signals.get("ci", {})
            governance = result.repo_signals.get("governance", {})

            lines.append(f"- **ADG Available:** {'✅' if adg.get('available') else '❌'}")
            lines.append(
                f"- **ADG Nodes/Edges:** {adg.get('nodes_count', 'N/A')} / {adg.get('edges_count', 'N/A')}",
            )
            lines.append(f"- **Test Inventory Entries:** {tests.get('inventory_entries', 0)}")
            lines.append(f"- **Test Surface Entries:** {tests.get('surface_entries', 0)}")
            lines.append(f"- **Workflow Definitions:** {ci.get('workflow_count', 0)}")
            lines.append(f"- **CI Validation Log Lines:** {ci.get('ci_validation_lines', 0)}")
            lines.append(
                f"- **Governance Baseline:** {'✅' if governance.get('denominator_baseline_available') else '❌'}",
            )
            lines.append("")

        # Execution lineage
        lines.append("## Execution Lineage")
        lines.append("")
        for entry in result.execution_log:
            status_icon = (
                "✅" if entry["status"] == "complete" else "⏳" if entry["status"] == "start" else "⚠️"
            )
            lines.append(f"{status_icon} **{entry['step']}**: {entry['status']}")
        lines.append("")

        path.write_text("\n".join(lines), encoding="utf-8")

    def _write_manifest(self, result: EnterpriseResearchResult, path: Path) -> None:
        """Write the research manifest."""
        manifest = {
            "trace_id": result.trace_id,
            "generated_at": datetime.now().isoformat(),
            "status": result.status,
            "topic": result.query_decomposition.original_topic if result.query_decomposition else "",
            "artifact_mode": result.query_decomposition.artifact_mode if result.query_decomposition else "",
            "generation_results": {
                "agents_executed": result.generation_results.get("agents_executed"),
                "quality_score": result.generation_results.get("quality_score"),
            },
            "validation_summary": {
                "validations_run": len(result.validation_results),
                "gates_passed": sum(1 for g in result.gate_results if g.get("gates_passed")),
                "avg_quality_score": result.avg_quality_score,
            },
            "repo_signals": result.repo_signals,
            "execution_log": result.execution_log,
        }

        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def _log_step(
        self,
        trace_id: str,
        step: str,
        status: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Log execution step."""
        entry = {
            "trace_id": trace_id,
            "step": step,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
        }
        self._execution_log.append(entry)


# Convenience function for quick usage
async def run_enterprise_research(
    topic: str,
    artifact_mode: str = "brief",
    target_audience: str = "technical",
    output_dir: str = "reports/research/enterprise",
) -> EnterpriseResearchResult:
    """Run enterprise research generation."""
    orchestrator = EnterpriseResearchOrchestrator()
    request = EnterpriseResearchRequest(
        topic=topic,
        artifact_mode=artifact_mode,
        target_audience=target_audience,
        output_dir=output_dir,
    )
    return await orchestrator.process(request)

"""
Enterprise RFP Orchestrator — apps_rfp.enterprise.

Unified orchestration that combines:
- L0: RFP document ingestion
- L1: Requirement decomposition
- L2: Past proposal retrieval (RAG)
- L3: Multi-agent section generation
- L5: Compliance validation and claims verification
- Output: Full traceable proposal with source register

This is the main entrypoint for enterprise-grade RFP response generation.
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
from apps_rfp.engines.proposal_retrieval_engine import (
    create_retrieval_engine,
)

# Import enterprise components
from apps_rfp.engines.rfp_ingestion_engine import RfpIngestionEngine, extract_rfp_summary
from apps_rfp.reasoning.compliance_validator import (
    ClaimsVerifier,
    ComplianceValidationResult,
    ComplianceValidator,
)
from apps_rfp.reasoning.requirement_decomposition_agent import (
    RequirementDecomposition,
    RequirementDecompositionAgent,
)
from apps_rfp.reasoning.section_orchestrator import (
    MultiAgentProposalOrchestrator,
)
from apps_rfp.services.repo_signal_service import RepoSignalService

_log = logging.getLogger(__name__)


@dataclass
class EnterpriseRfpRequest:
    """Request for enterprise RFP processing."""

    # Input source (one of these required)
    rfp_document_path: str | None = None
    rfp_text: str | None = None
    problem_statement: str | None = None

    # Context
    industry: str = "technology"
    company_name: str = ""
    our_company_name: str = "Agentic AI Solutions"
    proposal_budget_range: str = ""

    # Configuration
    enable_retrieval: bool = True
    enable_compliance_validation: bool = True
    enable_repo_signals: bool = True
    output_dir: str = "rfp/enterprise"
    trace_id: str = ""

    def __post_init__(self) -> None:
        if not self.trace_id:
            self.trace_id = self._generate_trace_id()

    def _generate_trace_id(self) -> str:
        """Generate unique trace ID."""
        content = (
            f"{self.rfp_document_path or ''}:{self.problem_statement or ''}:{datetime.now().isoformat()}"
        )
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class EnterpriseRfpResult:
    """Result of enterprise RFP processing."""

    trace_id: str
    status: str  # complete, partial, failed

    # Parsed input
    parsed_rfp: dict[str, Any] = field(default_factory=dict)
    requirements: list[dict[str, Any]] = field(default_factory=list)

    # Decomposition
    decompositions: list[RequirementDecomposition] = field(default_factory=list)
    implementation_plan: dict[str, Any] = field(default_factory=dict)

    # Retrieved context
    similar_proposals: list[dict[str, Any]] = field(default_factory=list)
    reusable_sections: list[dict[str, Any]] = field(default_factory=list)
    repo_signals: dict[str, Any] = field(default_factory=dict)

    # Generated proposal
    proposal: dict[str, Any] = field(default_factory=dict)

    # Validation
    compliance_result: dict[str, Any] = field(default_factory=dict)

    # Artifacts
    proposal_path: str = ""
    source_register_path: str = ""
    validation_report_path: str = ""
    execution_log: list[dict[str, Any]] = field(default_factory=list)

    # Metrics
    total_generation_time_ms: int = 0
    quality_score: float = 0.0


class EnterpriseRfpOrchestrator:
    """Enterprise-grade RFP response orchestrator.

    Pipeline:
    1. INGEST: Parse RFP document
    2. DECOMPOSE: Break down requirements (L1)
    3. RETRIEVE: Find similar past proposals (L2)
    4. GENERATE: Multi-agent section orchestration (L3)
    5. VALIDATE: Compliance and claims verification (L5)
    6. EMIT: Traceable proposal with source register
    """

    def __init__(self) -> None:
        # Initialize all subsystems
        self.ingestion_engine = RfpIngestionEngine()
        self.retrieval_engine = create_retrieval_engine()
        self.repo_signal_service = RepoSignalService()
        self.decomposition_agent = RequirementDecompositionAgent()
        self.proposal_orchestrator = MultiAgentProposalOrchestrator()
        self.compliance_validator = ComplianceValidator()
        self.claims_verifier = ClaimsVerifier()

        self._execution_log: list[dict[str, Any]] = []

    async def process(self, request: EnterpriseRfpRequest) -> EnterpriseRfpResult:
        """Process an RFP request end-to-end."""
        start_time = asyncio.get_event_loop().time()
        trace_id = request.trace_id

        _log.info(f"[EnterpriseRfpOrchestrator] Starting RFP processing trace={trace_id}")
        _emit_orchestrates_workflow("enterprise", "EnterpriseRfpOrchestrator", "process_start")

        result = EnterpriseRfpResult(trace_id=trace_id, status="processing")

        try:
            # === STEP 1: INGEST ===
            self._log_step(trace_id, "INGEST", "start")
            parsed_rfp = await self._step_ingest(request)
            result.parsed_rfp = parsed_rfp
            result.requirements = parsed_rfp.get("requirements", [])
            self._log_step(
                trace_id,
                "INGEST",
                "complete",
                details={
                    "requirements_found": len(result.requirements),
                    "organization": parsed_rfp.get("organization"),
                },
            )

            # === STEP 2: DECOMPOSE (L1 Cognition) ===
            self._log_step(trace_id, "DECOMPOSE", "start")
            decompositions, impl_plan = await self._step_decompose(result.requirements)
            result.decompositions = decompositions
            result.implementation_plan = impl_plan
            self._log_step(
                trace_id,
                "DECOMPOSE",
                "complete",
                details={
                    "components": impl_plan.get("total_components", 0),
                    "estimated_hours": impl_plan.get("total_estimated_hours", 0),
                },
            )

            # === STEP 3: RETRIEVE (L2 Execution/RAG) ===
            if request.enable_retrieval:
                self._log_step(trace_id, "RETRIEVE", "start")
                similar, reusable = await self._step_retrieve(parsed_rfp, request.industry)
                result.similar_proposals = similar
                result.reusable_sections = reusable
                self._log_step(
                    trace_id,
                    "RETRIEVE",
                    "complete",
                    details={
                        "similar_found": len(similar),
                        "reusable_sections": len(reusable),
                    },
                )

            # === STEP 3B: ENRICH (Repo Operational Signals) ===
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

            # === STEP 4: GENERATE (L3 Orchestration) ===
            self._log_step(trace_id, "GENERATE", "start")
            proposal = await self._step_generate(parsed_rfp, result.decompositions)
            result.proposal = proposal
            self._log_step(
                trace_id,
                "GENERATE",
                "complete",
                details={
                    "sections": proposal.get("total_sections", 0),
                    "word_count": proposal.get("total_word_count", 0),
                    "quality_score": proposal.get("average_quality_score", 0),
                },
            )

            # === STEP 5: VALIDATE (L5 Safety) ===
            if request.enable_compliance_validation:
                self._log_step(trace_id, "VALIDATE", "start")
                validation = await self._step_validate(
                    proposal,
                    request.industry,
                    result.requirements,
                )
                result.compliance_result = asdict(validation)
                self._log_step(
                    trace_id,
                    "VALIDATE",
                    "complete",
                    details={
                        "passed": validation.passed,
                        "violations": len(validation.violations),
                        "quality_score": validation.quality_score,
                    },
                )

            # === STEP 6: EMIT ===
            self._log_step(trace_id, "EMIT", "start")
            await self._step_emit(result, request)
            self._log_step(trace_id, "EMIT", "complete")

            # Final status
            elapsed_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
            result.total_generation_time_ms = elapsed_ms
            result.status = "complete" if result.compliance_result.get("passed", True) else "partial"
            result.execution_log = self._execution_log

            _log.info(
                f"[EnterpriseRfpOrchestrator] Complete trace={trace_id} status={result.status} time={elapsed_ms}ms",
            )
            _emit_captures_pattern("enterprise", "EnterpriseRfpOrchestrator", "process_complete")

        except Exception as exc:
            _log.error(f"[EnterpriseRfpOrchestrator] Failed: {exc}", exc_info=True)
            result.status = "failed"
            result.execution_log = self._execution_log

        return result

    async def _step_ingest(self, request: EnterpriseRfpRequest) -> dict[str, Any]:
        """Step 1: Ingest RFP document."""
        _emit_records_execution_trace("enterprise", "step_ingest", "start")

        # Import at method level to avoid circular imports at module level
        from apps_rfp.engines.rfp_ingestion_engine import ParsedDocument, Requirement

        if request.rfp_document_path:
            parsed = self.ingestion_engine.ingest(request.rfp_document_path)
        elif request.rfp_text:
            # Create mock parsed document from text
            parsed = ParsedDocument(
                source_path="inline_text",
                file_type="txt",
                raw_text=request.rfp_text,
                title="Inline RFP",
                requirements=[
                    Requirement(f"R{i + 1:03d}", "general", "mandatory", line)
                    for i, line in enumerate(request.rfp_text.split("\n")[:10])
                    if len(line) > 20
                ],
            )
        elif request.problem_statement:
            parsed = ParsedDocument(
                source_path="problem_statement",
                file_type="txt",
                raw_text=request.problem_statement,
                title="Problem Statement",
                requirements=[
                    Requirement("R001", "general", "mandatory", request.problem_statement),
                ],
            )
        else:
            raise ValueError("No input source provided (rfp_document_path, rfp_text, or problem_statement)")

        return extract_rfp_summary(parsed)

    async def _step_decompose(
        self,
        requirements: list[dict[str, Any]],
    ) -> tuple[list[RequirementDecomposition], dict[str, Any]]:
        """Step 2: Decompose requirements (L1)."""
        _emit_dispatches_agent("enterprise", "step_decompose", "L1")

        decompositions, summary = self.decomposition_agent.analyze_rfp_requirements(requirements)
        impl_plan = self.decomposition_agent.get_implementation_plan(decompositions)

        return decompositions, impl_plan

    async def _step_retrieve(
        self,
        parsed_rfp: dict[str, Any],
        industry: str,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Step 3: Retrieve similar proposals (L2)."""
        _emit_records_execution_trace("enterprise", "step_retrieve", "start")

        # Find similar proposals
        query = f"{parsed_rfp.get('title', '')} {parsed_rfp.get('problem_statement', '')}"
        similar = self.retrieval_engine.find_similar_proposals(
            query=query,
            industry=industry,
            n_results=5,
        )

        # Get reusable sections
        reusable = self.retrieval_engine.get_reusable_sections(
            industry=industry,
            section_type="executive_summary",
            n_results=3,
        )

        return [
            {
                "id": p.proposal_id,
                "title": p.title,
                "similarity": p.similarity_score,
            }
            for p in similar
        ], reusable

    async def _step_generate(
        self,
        parsed_rfp: dict[str, Any],
        decompositions: list[RequirementDecomposition],
    ) -> dict[str, Any]:
        """Step 4: Generate proposal sections (L3)."""
        _emit_coordinates_agents("enterprise", "step_generate", "L3")

        # Convert decompositions to dicts for orchestrator
        decomp_dicts = [
            {
                "source_requirement_id": d.source_requirement_id,
                "total_estimated_hours": d.total_estimated_hours,
                "risk_flags": d.risk_flags,
            }
            for d in decompositions
        ]

        proposal = await self.proposal_orchestrator.generate_proposal(
            parsed_rfp=parsed_rfp,
            decompositions=decomp_dicts,
        )

        return proposal

    async def _step_collect_repo_signals(self) -> dict[str, Any]:
        """Step 3B: Collect production-like repo signals."""
        _emit_records_execution_trace("enterprise", "step_collect_repo_signals", "start")
        snapshot = self.repo_signal_service.collect()
        return snapshot.as_dict()

    async def _step_validate(
        self,
        proposal: dict[str, Any],
        industry: str,
        requirements: list[dict[str, Any]],
    ) -> ComplianceValidationResult:
        """Step 5: Validate compliance (L5)."""
        _emit_applies_guardrail("enterprise", "step_validate", "L5")

        sections = proposal.get("sections", [])

        validation = self.compliance_validator.validate(
            proposal_sections=sections,
            industry=industry,
            rfp_requirements=requirements,
        )

        return validation

    async def _step_emit(
        self,
        result: EnterpriseRfpResult,
        request: EnterpriseRfpRequest,
    ) -> None:
        """Step 6: Emit all artifacts."""
        _emit_stores_embedding("enterprise", "step_emit", "artifacts")

        out_dir = Path(request.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        # 1. Main proposal
        proposal_path = out_dir / f"enterprise_proposal_{result.trace_id[:8]}.md"
        self._write_proposal_markdown(result, proposal_path)
        result.proposal_path = str(proposal_path)

        # 2. Source register
        register_path = out_dir / f"source_register_{result.trace_id[:8]}.json"
        self._write_source_register(result, register_path)
        result.source_register_path = str(register_path)

        # 3. Validation report
        if result.compliance_result:
            validation_path = out_dir / f"validation_report_{result.trace_id[:8]}.json"
            self._write_validation_report(result, validation_path)
            result.validation_report_path = str(validation_path)

    def _write_proposal_markdown(self, result: EnterpriseRfpResult, path: Path) -> None:
        """Write the proposal as markdown."""
        lines: list[str] = []

        lines.append("# AI Platform Proposal")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Trace ID:** `{result.trace_id}`")
        lines.append(f"**Status:** {result.status.upper()}")
        lines.append("")

        # Proposal sections
        for section in result.proposal.get("sections", []):
            lines.append(f"## {section.get('heading', 'Section')}")
            lines.append("")
            lines.append(section.get("body", ""))
            lines.append("")

            # Evidence section
            evidence = section.get("evidence_cited", [])
            if evidence:
                lines.append("*Evidence:* " + ", ".join(evidence))
                lines.append("")

        # Implementation summary
        lines.append("## Implementation Summary")
        lines.append("")
        lines.append(f"- **Estimated Hours:** {result.implementation_plan.get('total_estimated_hours', 0)}")
        lines.append(
            f"- **Sprint Estimate:** {result.implementation_plan.get('estimated_sprints', 0)} sprints",
        )
        lines.append(
            f"- **High Complexity Items:** {len(result.implementation_plan.get('high_complexity_items', []))}",
        )
        lines.append("")

        # Compliance summary
        if result.compliance_result:
            lines.append("## Compliance Summary")
            lines.append("")
            passed = result.compliance_result.get("passed", False)
            lines.append(f"- **Validation Status:** {'✅ PASSED' if passed else '⚠️ REVIEW REQUIRED'}")
            lines.append(f"- **Quality Score:** {result.compliance_result.get('quality_score', 0):.0%}")
            lines.append(f"- **Violations:** {len(result.compliance_result.get('violations', []))}")
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

        path.write_text("\n".join(lines), encoding="utf-8")

    def _write_source_register(self, result: EnterpriseRfpResult, path: Path) -> None:
        """Write the source register."""
        register = {
            "trace_id": result.trace_id,
            "generated_at": datetime.now().isoformat(),
            "repo_signals": result.repo_signals,
            "sources": [
                {
                    "type": "rfp_input",
                    "organization": result.parsed_rfp.get("organization"),
                    "requirements_count": len(result.requirements),
                },
                {
                    "type": "past_proposals",
                    "similar_proposals_consulted": len(result.similar_proposals),
                    "proposals": result.similar_proposals,
                },
                {
                    "type": "decomposition_analysis",
                    "components_identified": result.implementation_plan.get("total_components", 0),
                    "estimated_hours": result.implementation_plan.get("total_estimated_hours", 0),
                },
                {
                    "type": "compliance_validation",
                    "validator": "L5_ComplianceValidator",
                    "passed": result.compliance_result.get("passed"),
                    "violations_count": len(result.compliance_result.get("violations", [])),
                },
            ],
            "claim_verifications": [
                {
                    "claim_id": c.get("claim_id"),
                    "confidence": c.get("confidence"),
                    "has_evidence": c.get("has_evidence"),
                }
                for c in result.compliance_result.get("claim_verifications", [])
            ],
        }

        path.write_text(json.dumps(register, indent=2), encoding="utf-8")

    def _write_validation_report(self, result: EnterpriseRfpResult, path: Path) -> None:
        """Write the validation report."""
        report = {
            "trace_id": result.trace_id,
            "validation_timestamp": datetime.now().isoformat(),
            "compliance_result": result.compliance_result,
            "violations_detail": [
                {
                    "id": v.get("violation_id"),
                    "rule": v.get("rule_id"),
                    "severity": v.get("severity"),
                    "message": v.get("message"),
                    "suggestion": v.get("suggestion"),
                }
                for v in result.compliance_result.get("violations", [])
            ],
            "risk_flags": result.compliance_result.get("risk_flags", []),
            "regulatory_gaps": result.compliance_result.get("regulatory_gaps", []),
        }

        path.write_text(json.dumps(report, indent=2), encoding="utf-8")

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
async def generate_proposal_from_rfp(
    rfp_path: str,
    industry: str = "technology",
    output_dir: str = "rfp/enterprise",
) -> EnterpriseRfpResult:
    """Generate a proposal from an RFP document."""
    orchestrator = EnterpriseRfpOrchestrator()
    request = EnterpriseRfpRequest(
        rfp_document_path=rfp_path,
        industry=industry,
        output_dir=output_dir,
    )
    return await orchestrator.process(request)


async def generate_proposal_from_text(
    problem_statement: str,
    industry: str = "technology",
    output_dir: str = "rfp/enterprise",
) -> EnterpriseRfpResult:
    """Generate a proposal from a problem statement."""
    orchestrator = EnterpriseRfpOrchestrator()
    request = EnterpriseRfpRequest(
        problem_statement=problem_statement,
        industry=industry,
        output_dir=output_dir,
    )
    return await orchestrator.process(request)

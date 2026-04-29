"""
Enterprise Evaluation Orchestrator — apps_eval.enterprise.

Unified orchestration that combines:
- L0: Evaluation criteria parsing
- L1: Criteria decomposition
- L2: Past evaluation retrieval for trend analysis
- L3: Multi-agent evaluation orchestration
- L5: Validation and scoring gates
- Output: Full evaluation report with traceability
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

from apps_eval._telemetry import (
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,
    _emit_stores_embedding,
)
from apps_eval.engines.evaluation_retrieval_engine import (
    create_retrieval_engine,
)
from apps_eval.outputs import enterprise_eval_renderer

# Import enterprise components
from apps_eval.reasoning.criteria_decomposition_agent import (
    CriteriaDecomposition,
    CriteriaDecompositionAgent,
)
from apps_eval.reasoning.evaluation_orchestrator import (
    MultiAgentEvaluationEngine,
)
from apps_eval.services.repo_signal_service import RepoSignalService
from apps_eval.validators.evaluation_validator import (
    EvaluationValidator,
    ScoringGate,
)

_log = logging.getLogger(__name__)


@dataclass
class EnterpriseEvalRequest:
    """Request for enterprise evaluation processing."""

    # Evaluation scope
    suite_ids: list[str] = field(default_factory=list)
    criteria_items: list[dict[str, Any]] = field(default_factory=list)

    # Context
    target_modules: list[str] = field(default_factory=list)
    evaluation_type: str = "benchmark"  # benchmark, regression, acceptance

    # Configuration
    enable_retrieval: bool = True
    enable_validation: bool = True
    enable_repo_signals: bool = True
    update_baseline: bool = False
    output_dir: str = "artifacts/eval/enterprise"
    trace_id: str = ""

    def __post_init__(self) -> None:
        if not self.trace_id:
            self.trace_id = self._generate_trace_id()

    def _generate_trace_id(self) -> str:
        """Generate unique trace ID."""
        content = f"eval:{','.join(sorted(self.suite_ids))}:{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class EnterpriseEvalResult:
    """Result of enterprise evaluation processing."""

    trace_id: str
    status: str  # complete, partial, failed

    # Decomposition
    decompositions: list[CriteriaDecomposition] = field(default_factory=list)
    test_plan: dict[str, Any] = field(default_factory=dict)

    # Retrieved context
    similar_evaluations: list[dict[str, Any]] = field(default_factory=list)
    trend_analysis: dict[str, Any] = field(default_factory=dict)
    repo_signals: dict[str, Any] = field(default_factory=dict)

    # Evaluation results
    evaluation_results: dict[str, Any] = field(default_factory=dict)

    # Validation
    validation_result: dict[str, Any] = field(default_factory=dict)
    gate_result: dict[str, Any] = field(default_factory=dict)

    # Artifacts
    report_path: str = ""
    manifest_path: str = ""
    baseline_path: str = ""
    execution_log: list[dict[str, Any]] = field(default_factory=list)

    # Metrics
    total_execution_time_ms: int = 0
    quality_score: float = 0.0


class EnterpriseEvalOrchestrator:
    """Enterprise-grade evaluation orchestrator.

    Pipeline:
    1. DECOMPOSE: Break down criteria (L1)
    2. RETRIEVE: Find similar evaluations (L2)
    3. EXECUTE: Multi-agent evaluation (L3)
    4. VALIDATE: Quality gates (L5)
    5. EMIT: Traceable evaluation report
    """

    def __init__(self) -> None:
        # Initialize all subsystems
        self.retrieval_engine = create_retrieval_engine()
        self.repo_signal_service = RepoSignalService()
        self.decomposition_agent = CriteriaDecompositionAgent()
        self.evaluation_engine = MultiAgentEvaluationEngine()
        self.validator = EvaluationValidator()
        self.scoring_gate = ScoringGate()

        self._execution_log: list[dict[str, Any]] = []

    async def process(self, request: EnterpriseEvalRequest) -> EnterpriseEvalResult:
        """Process an evaluation request end-to-end."""
        start_time = asyncio.get_event_loop().time()
        trace_id = request.trace_id

        _log.info(f"[EnterpriseEvalOrchestrator] Starting evaluation trace={trace_id}")
        _emit_orchestrates_workflow("enterprise", "EnterpriseEvalOrchestrator", "process_start")

        result = EnterpriseEvalResult(trace_id=trace_id, status="processing")

        try:
            # === STEP 1: DECOMPOSE (L1 Cognition) ===
            if request.criteria_items:
                self._log_step(trace_id, "DECOMPOSE", "start")
                decompositions, test_plan = await self._step_decompose(request.criteria_items)
                result.decompositions = decompositions
                result.test_plan = test_plan
                self._log_step(
                    trace_id,
                    "DECOMPOSE",
                    "complete",
                    details={
                        "components": test_plan.get("total_components", 0),
                        "estimated_time_ms": test_plan.get("total_estimated_time_ms", 0),
                    },
                )

            # === STEP 2: RETRIEVE (L2 Execution/RAG) ===
            if request.enable_retrieval:
                self._log_step(trace_id, "RETRIEVE", "start")
                similar, trends = await self._step_retrieve(request.suite_ids, request.evaluation_type)
                result.similar_evaluations = similar
                result.trend_analysis = trends
                self._log_step(
                    trace_id,
                    "RETRIEVE",
                    "complete",
                    details={
                        "similar_found": len(similar),
                        "trends_analyzed": len(trends),
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

            # === STEP 3: EXECUTE (L3 Orchestration) ===
            self._log_step(trace_id, "EXECUTE", "start")
            eval_results = await self._step_execute(
                request.suite_ids,
                result.decompositions,
            )
            result.evaluation_results = eval_results
            self._log_step(
                trace_id,
                "EXECUTE",
                "complete",
                details={
                    "agents_executed": eval_results.get("agents_executed", 0),
                    "overall_score": eval_results.get("overall_score", 0),
                },
            )

            # === STEP 4: VALIDATE (L5 Safety) ===
            if request.enable_validation:
                self._log_step(trace_id, "VALIDATE", "start")
                validation, gates = await self._step_validate(
                    eval_results,
                    request.criteria_items,
                )
                result.validation_result = asdict(validation)
                result.gate_result = gates
                self._log_step(
                    trace_id,
                    "VALIDATE",
                    "complete",
                    details={
                        "validation_passed": validation.passed,
                        "gates_passed": gates.get("gates_passed", False),
                        "violations": len(validation.violations),
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
            if result.validation_result.get("passed", False) and result.gate_result.get(
                "gates_passed", False
            ):
                result.status = "complete"
            elif result.gate_result.get("gates_passed", False):
                result.status = "partial"
            else:
                result.status = "failed"

            result.execution_log = self._execution_log

            _log.info(
                f"[EnterpriseEvalOrchestrator] Complete trace={trace_id} status={result.status} time={elapsed_ms}ms"
            )
            _emit_captures_pattern("enterprise", "EnterpriseEvalOrchestrator", "process_complete")

        except (RuntimeError, ValueError, TypeError, AttributeError, KeyError, OSError) as exc:
            _log.error(f"[EnterpriseEvalOrchestrator] Failed: {exc}", exc_info=True)
            result.status = "failed"
            result.execution_log = self._execution_log

        return result

    async def _step_decompose(
        self,
        criteria_items: list[dict[str, Any]],
    ) -> tuple[list[CriteriaDecomposition], dict[str, Any]]:
        """Step 1: Decompose evaluation criteria (L1)."""
        _emit_dispatches_agent("enterprise", "step_decompose", "L1")

        decompositions, summary = self.decomposition_agent.analyze_evaluation_criteria(criteria_items)
        test_plan = self.decomposition_agent.get_test_execution_plan(decompositions)

        return decompositions, test_plan

    async def _step_retrieve(
        self,
        suite_ids: list[str],
        eval_type: str,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Step 2: Retrieve similar evaluations (L2)."""
        _emit_records_execution_trace("enterprise", "step_retrieve", "start")

        # Find similar evaluations
        query = {"suite_ids": suite_ids, "type": eval_type}
        similar = self.retrieval_engine.find_similar_evaluations(
            current_result=query,
            suite_ids=suite_ids,
            n_results=5,
        )

        # Analyze trends for key dimensions
        trends: dict[str, Any] = {}
        for dim in ["correctness", "determinism", "governance", "latency"]:
            trend = self.retrieval_engine.analyze_trends(dim, window_size=10)
            if trend:
                trends[dim] = {
                    "direction": trend.trend_direction,
                    "slope": trend.slope,
                    "prediction": trend.prediction_next,
                }

        return [
            {
                "id": e.eval_id,
                "trace_id": e.trace_id,
                "timestamp": e.timestamp,
                "overall_score": e.overall_score,
                "similarity": e.similarity_score,
            }
            for e in similar
        ], trends

    async def _step_execute(
        self,
        suite_ids: list[str],
        decompositions: list[CriteriaDecomposition],
    ) -> dict[str, Any]:
        """Step 3: Execute multi-agent evaluation (L3)."""
        _emit_coordinates_agents("enterprise", "step_execute", "L3")

        # Convert decompositions to context
        decomp_dicts = [
            {
                "criteria_id": d.source_criteria_id,
                "components": len(d.components),
                "estimated_time_ms": d.estimated_execution_time_ms,
            }
            for d in decompositions
        ]

        context = {"decompositions": decomp_dicts}

        results = await self.evaluation_engine.run_evaluation(suite_ids, context)

        return results

    async def _step_collect_repo_signals(self) -> dict[str, Any]:
        """Step 2B: Collect production-like repo signals."""
        _emit_records_execution_trace("enterprise", "step_collect_repo_signals", "start")
        snapshot = self.repo_signal_service.collect()
        return snapshot.as_dict()

    async def _step_validate(
        self,
        eval_results: dict[str, Any],
        criteria_items: list[dict[str, Any]],
    ) -> tuple[Any, dict[str, Any]]:
        """Step 4: Validate evaluation results (L5)."""
        _emit_applies_guardrail("enterprise", "step_validate", "L5")

        # Run validation
        validation = self.validator.validate(
            eval_result=eval_results,
            suite_configs=[],
            criteria_decompositions=criteria_items,
        )

        # Run gates
        gates = self.scoring_gate.evaluate(eval_results)

        return validation, gates

    async def _step_emit(
        self,
        result: EnterpriseEvalResult,
        request: EnterpriseEvalRequest,
    ) -> None:
        """Step 5: Emit all artifacts."""
        _emit_stores_embedding("enterprise", "step_emit", "artifacts")

        out_dir = Path(request.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        # 1. Main report
        report_path = out_dir / f"enterprise_eval_{result.trace_id[:8]}.md"
        enterprise_eval_renderer.write_evaluation_markdown(result, report_path)
        result.report_path = str(report_path)

        # 2. Manifest
        manifest_path = out_dir / f"eval_manifest_{result.trace_id[:8]}.json"
        enterprise_eval_renderer.write_manifest(result, manifest_path)
        result.manifest_path = str(manifest_path)

        # 3. Baseline (if updating)
        if request.update_baseline:
            baseline_path = out_dir / f"baseline_{result.trace_id[:8]}.json"
            enterprise_eval_renderer.write_baseline(result, baseline_path)
            result.baseline_path = str(baseline_path)

    # W5.1 (2026-04-29): _write_evaluation_markdown / _write_manifest /
    # _write_baseline moved to apps_eval/outputs/enterprise_eval_renderer.py
    # to keep orchestration logic separate from artifact emission.

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
async def run_enterprise_evaluation(
    suite_ids: list[str],
    criteria_items: list[dict[str, Any]] | None = None,
    output_dir: str = "artifacts/eval/enterprise",
) -> EnterpriseEvalResult:
    """Run an enterprise evaluation."""
    orchestrator = EnterpriseEvalOrchestrator()
    request = EnterpriseEvalRequest(
        suite_ids=suite_ids,
        criteria_items=criteria_items or [],
        output_dir=output_dir,
    )
    return await orchestrator.process(request)

"""Judge Orchestrator — coordinates multi-rubric evaluation runs.

Ties together all judge components into a single evaluation pipeline:
1. Load applicable rubrics via RubricEngine
2. Assemble evidence via EvidenceAssembler
3. Route to deterministic or LLM judges
4. Collect verdicts into JudgeReport
5. Persist verdicts via VerdictStore

Usage::

    orchestrator = JudgeOrchestrator(
        repo_root="c:/Git/Agentic-Workflow",
        adg_db_path="artifacts/adg/adg_indexed_latest.sqlite",
    )
    report = await orchestrator.evaluate("agentic_core/L2_execution/providers.py")
    print(report.overall_score, report.fail_count)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from agentic_core.evaluation.judges.deterministic_judges import (
    DETERMINISTIC_JUDGES,
    run_deterministic_judge,
)
from agentic_core.evaluation.judges.evidence_assembler import EvidenceAssembler
from agentic_core.evaluation.judges.llm_judges import LLM_JUDGES, run_llm_judge
from agentic_core.evaluation.judges.provider_registry import (
    JudgeProviderRegistry,
    create_default_registry,
)
from agentic_core.evaluation.judges.rubric_engine import RubricEngine
from agentic_core.evaluation.judges.types import (
    JudgeReport,
    JudgeReportRow,
    JudgeVerdict,
    VerdictOutcome,
)
from agentic_core.evaluation.judges.verdict_store import VerdictStore

_log = logging.getLogger(__name__)


class JudgeOrchestrator:
    """Coordinates multi-rubric evaluation runs across modules.

    Supports:
    - Single-module evaluation with all applicable rubrics
    - Batch evaluation across multiple modules
    - Deterministic-only mode (no LLM calls)
    - Custom rubric selection
    - Persistent verdict storage
    """

    def __init__(
        self,
        repo_root: str = "",
        adg_db_path: str = "",
        rubrics_path: str = "",
        verdict_db_path: str = "",
        provider_registry: JudgeProviderRegistry | None = None,
    ) -> None:
        self._repo_root = repo_root
        self._assembler = EvidenceAssembler(
            repo_root=repo_root,
            adg_db_path=adg_db_path,
        )
        self._rubric_engine = RubricEngine(rubrics_path) if rubrics_path else RubricEngine()
        self._store = (
            VerdictStore(verdict_db_path)
            if verdict_db_path
            else VerdictStore()
        )
        self._registry = provider_registry or create_default_registry()

    @property
    def rubric_engine(self) -> RubricEngine:
        return self._rubric_engine

    @property
    def verdict_store(self) -> VerdictStore:
        return self._store

    @property
    def provider_registry(self) -> JudgeProviderRegistry:
        return self._registry

    def _collect_relations_for_rubrics(
        self, rubric_ids: list[str],
    ) -> list[str]:
        """Collect all ADG relations needed across the selected rubrics."""
        relations: set[str] = set()
        for rid in rubric_ids:
            reqs = self._rubric_engine.evidence_requirements_for(rid)
            for req in reqs:
                if req.get("evidence_type") == "adg_edge" and req.get("relation"):
                    relations.add(req["relation"])
        return sorted(relations) if relations else []

    async def evaluate(
        self,
        module_path: str,
        rubric_ids: list[str] | None = None,
        deterministic_only: bool = False,
        layer: str = "",
        entity_type: str = "module",
        persist: bool = True,
    ) -> JudgeReport:
        """Evaluate a single module against applicable rubrics.

        Args:
            module_path: Relative path to the module.
            rubric_ids: Specific rubric IDs to evaluate. If None, auto-select.
            deterministic_only: Skip LLM-based rubrics.
            layer: Architecture layer for rubric filtering.
            entity_type: Entity type for rubric filtering.
            persist: Whether to persist verdicts to the store.

        Returns:
            JudgeReport with all verdicts and scorecard.
        """
        now = datetime.now(timezone.utc).isoformat()

        # Select rubrics
        if rubric_ids:
            rubrics = [
                self._rubric_engine.get(rid)
                for rid in rubric_ids
                if self._rubric_engine.get(rid) is not None
            ]
        else:
            rubrics = self._rubric_engine.get_applicable_rubrics(
                layer=layer,
                entity_type=entity_type,
                deterministic_only=deterministic_only,
            )

        if not rubrics:
            return JudgeReport(
                target=module_path,
                overall_score=0.0,
                passed=True,
                created_at=now,
                error="No applicable rubrics found",
            )

        selected_ids = [r.rubric_id for r in rubrics]

        # Assemble evidence
        relations = self._collect_relations_for_rubrics(selected_ids)
        bundle = self._assembler.assemble(
            module_path=module_path,
            relations=relations if relations else None,
            include_source=True,
        )

        # Run judges
        verdicts: list[JudgeVerdict] = []

        for rubric in rubrics:
            rid = rubric.rubric_id
            verdict: JudgeVerdict | None = None

            if rid in DETERMINISTIC_JUDGES:
                verdict = run_deterministic_judge(rid, bundle)
            elif rid in LLM_JUDGES and not deterministic_only:
                provider = self._registry.default
                if provider:
                    try:
                        verdict = await run_llm_judge(
                            rid, bundle, provider, self._rubric_engine,
                        )
                    except Exception as exc:
                        _log.warning(
                            "[JudgeOrchestrator] LLM judge %s failed: %s",
                            rid,
                            exc,
                        )
                        verdict = JudgeVerdict(
                            verdict_id=f"err-{rid}",
                            target=module_path,
                            dimension=rubric.dimension,
                            rubric_id=rid,
                            outcome=VerdictOutcome.ERROR.value,
                            score=0.0,
                            reasoning=f"LLM judge error: {exc}",
                            provider_id=provider.provider_id,
                            adg_digest=bundle.adg_digest,
                            created_at=now,
                        )

            if verdict:
                verdicts.append(verdict)

        # Build scorecard
        scorecard = self._build_scorecard(verdicts)

        # Compute overall score
        if verdicts:
            scored = [v for v in verdicts if v.outcome != VerdictOutcome.SKIP.value]
            overall = (
                round(sum(v.score for v in scored) / len(scored), 4)
                if scored
                else 1.0
            )
        else:
            overall = 1.0

        passed = all(
            v.outcome != VerdictOutcome.FAIL.value for v in verdicts
        )

        report = JudgeReport(
            target=module_path,
            verdicts=verdicts,
            scorecard=scorecard,
            overall_score=overall,
            passed=passed,
            adg_digest=bundle.adg_digest,
            created_at=now,
        )

        # Persist
        if persist and verdicts:
            try:
                self._store.store_verdicts(verdicts)
            except Exception as exc:
                _log.warning("[JudgeOrchestrator] Persist failed: %s", exc)

        return report

    async def evaluate_batch(
        self,
        module_paths: list[str],
        rubric_ids: list[str] | None = None,
        deterministic_only: bool = True,
        persist: bool = True,
    ) -> list[JudgeReport]:
        """Evaluate multiple modules. Returns list of JudgeReports."""
        reports: list[JudgeReport] = []
        for path in module_paths:
            report = await self.evaluate(
                module_path=path,
                rubric_ids=rubric_ids,
                deterministic_only=deterministic_only,
                persist=persist,
            )
            reports.append(report)
        return reports

    def _build_scorecard(
        self, verdicts: list[JudgeVerdict],
    ) -> list[JudgeReportRow]:
        """Build scorecard rows from verdicts, grouped by dimension."""
        dim_data: dict[str, list[JudgeVerdict]] = {}
        for v in verdicts:
            dim_data.setdefault(v.dimension, []).append(v)

        rows: list[JudgeReportRow] = []
        for dim, dim_verdicts in sorted(dim_data.items()):
            scored = [
                v for v in dim_verdicts if v.outcome != VerdictOutcome.SKIP.value
            ]
            if not scored:
                continue

            avg_score = round(sum(v.score for v in scored) / len(scored), 4)

            # Worst outcome wins for the dimension
            if any(v.outcome == VerdictOutcome.FAIL.value for v in scored):
                outcome = VerdictOutcome.FAIL.value
            elif any(v.outcome == VerdictOutcome.WARN.value for v in scored):
                outcome = VerdictOutcome.WARN.value
            elif any(v.outcome == VerdictOutcome.ERROR.value for v in scored):
                outcome = VerdictOutcome.ERROR.value
            else:
                outcome = VerdictOutcome.PASS.value

            # Worst severity
            severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
            worst_sev = min(scored, key=lambda v: severity_order.get(v.severity, 99))

            rubric_ids_in_dim = sorted({v.rubric_id for v in dim_verdicts})

            rows.append(
                JudgeReportRow(
                    dimension=dim,
                    display_name=dim.replace("_", " ").title(),
                    score=avg_score,
                    outcome=outcome,
                    severity=worst_sev.severity,
                    rubric_id=", ".join(rubric_ids_in_dim),
                    verdict_count=len(dim_verdicts),
                ),
            )

        return sorted(rows, key=lambda r: r.score)

    def summary(self) -> dict[str, Any]:
        """Summary of orchestrator configuration."""
        return {
            "rubrics": self._rubric_engine.summary(),
            "providers": self._registry.summary(),
            "verdict_store": self._store.stats(),
            "deterministic_judges": sorted(DETERMINISTIC_JUDGES.keys()),
            "llm_judges": sorted(LLM_JUDGES.keys()),
        }


__all__ = ["JudgeOrchestrator"]

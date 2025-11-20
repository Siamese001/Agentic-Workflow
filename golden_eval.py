# FILE: 10_10/golden_eval.py
"""
Golden State Evaluator (v10_10)
===============================

This module provides a deterministic evaluation harness for the v10_10
agentic workflow. It operates on the final L4 state patch (a plain dict)
and compares it against golden expectations defined in JSON.

Goals:
    • No LLM calls.
    • No orchestration, execution, or planning.
    • Purely deterministic scoring.
    • CI/CD-friendly: non-zero exit on regression when wired via CLI.

Core Concepts:
    • GoldenExpectation: what "good" looks like for a scenario.
    • EvalMetric: a single metric with score + pass/fail + reason.
    • EvalReport: aggregate of metrics and a total score.

Typical usage in CI:
    1. Run the workflow to produce a state patch.
    2. Load a GoldenExpectation from disk.
    3. Call evaluate_patch(patch, expectation).
    4. Fail CI if total_score < threshold or any critical metric fails.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from pydantic import BaseModel, Field


# =============================================================================
# Evaluation Models
# =============================================================================

class GoldenExpectation(BaseModel):
    """
    Defines what "good" looks like for a single scenario.

    Fields:
        scenario_id:          Unique identifier for the scenario.
        required_sections:    Section titles that MUST be present.
        min_evidence:         Minimum number of RAG evidence items required.
        allow_blocking_safety:false if ANY blocking safety finding is unacceptable.
        max_failed_qa:        Maximum number of failed QA checks allowed.
        min_total_score:      Minimum total score (0.0 - 1.0) to consider scenario passing.
    """
    scenario_id: str
    required_sections: List[str] = Field(default_factory=list)
    min_evidence: int = 1
    allow_blocking_safety: bool = False
    max_failed_qa: int = 0
    min_total_score: float = 0.8


class EvalMetric(BaseModel):
    """
    Single evaluation metric.
    """
    name: str
    score: float  # 0.0 to 1.0
    passed: bool
    reason: str


class EvalReport(BaseModel):
    """
    Aggregate evaluation report for a scenario.
    """
    scenario_id: str
    total_score: float
    metrics: List[EvalMetric]
    passed: bool
    threshold: float


# =============================================================================
# Core Evaluation Logic
# =============================================================================

def evaluate_patch(
    state_patch: Dict[str, Any],
    expectation: GoldenExpectation,
) -> EvalReport:
    """
    Evaluate a single state patch (final_state_patch from L3/L4) against a
    GoldenExpectation.

    The `state_patch` is expected to be shaped like:

        {
            "strategy_text": str | None,
            "rag_evidence": [ { "text": ..., "score": ..., "source": ... }, ... ],
            "drafted_sections": [ { "title": ..., "text": ..., ... }, ... ],
            "qa_findings": [ { "id": ..., "passed": bool, ... }, ... ],
            "safety_findings": [ { "id": ..., "category": ..., "blocking": bool, ... }, ... ],
            "correction_signals": [ { "surface": ..., "severity": ..., ... }, ... ],
            "safety_passed": bool
        }

    This function performs a set of deterministic checks and returns
    an EvalReport with granular metrics + total score.
    """

    metrics: List[EvalMetric] = []

    # -------------------------------------------------------------------------
    # 1. Sections: coverage of required sections
    # -------------------------------------------------------------------------
    drafted_sections = state_patch.get("drafted_sections", []) or []
    titles = {str(sec.get("title", "")).strip().lower() for sec in drafted_sections}

    missing_sections = [
        sec for sec in expectation.required_sections
        if sec.strip().lower() not in titles
    ]
    if expectation.required_sections:
        if missing_sections:
            score_sections = max(0.0, 1.0 - len(missing_sections) / max(1, len(expectation.required_sections)))
            metrics.append(
                EvalMetric(
                    name="sections_coverage",
                    score=score_sections,
                    passed=False,
                    reason=f"Missing sections: {missing_sections}",
                )
            )
        else:
            metrics.append(
                EvalMetric(
                    name="sections_coverage",
                    score=1.0,
                    passed=True,
                    reason="All required sections present.",
                )
            )

    # -------------------------------------------------------------------------
    # 2. Evidence: RAG evidence sufficiency
    # -------------------------------------------------------------------------
    rag_evidence = state_patch.get("rag_evidence", []) or []
    num_evidence = len(rag_evidence)
    if num_evidence < expectation.min_evidence:
        score_evidence = num_evidence / max(1, expectation.min_evidence)
        metrics.append(
            EvalMetric(
                name="rag_evidence_sufficiency",
                score=score_evidence,
                passed=False,
                reason=f"Expected at least {expectation.min_evidence} evidence items; found {num_evidence}.",
            )
        )
    else:
        metrics.append(
            EvalMetric(
                name="rag_evidence_sufficiency",
                score=1.0,
                passed=True,
                reason=f"Sufficient evidence items ({num_evidence}).",
            )
        )

    # -------------------------------------------------------------------------
    # 3. QA: number of failed QA checks
    # -------------------------------------------------------------------------
    qa_findings = state_patch.get("qa_findings", []) or []
    failed_qa = [q for q in qa_findings if not q.get("passed", False)]
    num_failed_qa = len(failed_qa)

    if num_failed_qa > expectation.max_failed_qa:
        score_qa = max(0.0, 1.0 - (num_failed_qa - expectation.max_failed_qa) / max(1, len(qa_findings) or 1))
        metrics.append(
            EvalMetric(
                name="qa_failures",
                score=score_qa,
                passed=False,
                reason=f"{num_failed_qa} QA checks failed; allowed max {expectation.max_failed_qa}.",
            )
        )
    else:
        metrics.append(
            EvalMetric(
                name="qa_failures",
                score=1.0,
                passed=True,
                reason=f"{num_failed_qa} QA failures within allowed threshold.",
            )
        )

    # -------------------------------------------------------------------------
    # 4. Safety: blocking findings
    # -------------------------------------------------------------------------
    safety_findings = state_patch.get("safety_findings", []) or []
    blocking = [f for f in safety_findings if f.get("blocking", False)]

    if blocking and not expectation.allow_blocking_safety:
        metrics.append(
            EvalMetric(
                name="safety_blocking",
                score=0.0,
                passed=False,
                reason=f"Blocking safety findings present: {len(blocking)}.",
            )
        )
    else:
        metrics.append(
            EvalMetric(
                name="safety_blocking",
                score=1.0,
                passed=True,
                reason="No disallowed blocking safety findings.",
            )
        )

    # -------------------------------------------------------------------------
    # 5. Strategy presence
    # -------------------------------------------------------------------------
    strategy_text = state_patch.get("strategy_text") or ""
    if len(strategy_text.strip()) < 40:
        score_strategy = max(0.0, len(strategy_text.strip()) / 40.0)
        metrics.append(
            EvalMetric(
                name="strategy_quality",
                score=score_strategy,
                passed=False,
                reason="Strategy text is too short or missing.",
            )
        )
    else:
        metrics.append(
            EvalMetric(
                name="strategy_quality",
                score=1.0,
                passed=True,
                reason="Strategy text appears present and substantive.",
            )
        )

    # -------------------------------------------------------------------------
    # 6. Safety gate pass/fail consistency
    # -------------------------------------------------------------------------
    safety_passed = bool(state_patch.get("safety_passed", False))
    if blocking and safety_passed and not expectation.allow_blocking_safety:
        metrics.append(
            EvalMetric(
                name="safety_gate_consistency",
                score=0.0,
                passed=False,
                reason="Safety gate passed even though blocking findings exist.",
            )
        )
    else:
        metrics.append(
            EvalMetric(
                name="safety_gate_consistency",
                score=1.0,
                passed=True,
                reason="Safety gate consistent with safety findings.",
            )
        )

    # -------------------------------------------------------------------------
    # Aggregate overall score
    # -------------------------------------------------------------------------
    if metrics:
        total_score = sum(m.score for m in metrics) / len(metrics)
    else:
        total_score = 1.0

    passed = total_score >= expectation.min_total_score
    return EvalReport(
        scenario_id=expectation.scenario_id,
        total_score=total_score,
        metrics=metrics,
        passed=passed,
        threshold=expectation.min_total_score,
    )


# =============================================================================
# JSON I/O Helpers
# =============================================================================

def load_expectations(path: str | Path) -> List[GoldenExpectation]:
    """
    Load a list of GoldenExpectation objects from a JSON file.

    Expecting a JSON array of objects like:
        [
          {
            "scenario_id": "scenario_1",
            "required_sections": ["Header", "Experience"],
            "min_evidence": 2,
            "allow_blocking_safety": false,
            "max_failed_qa": 0,
            "min_total_score": 0.9
          },
          ...
        ]
    """
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = [data]
    return [GoldenExpectation.model_validate(d) for d in data]


def save_report(report: EvalReport, path: str | Path) -> None:
    """
    Save an EvalReport to a JSON file.
    """
    path = Path(path)
    path.write_text(report.model_dump_json(indent=2, by_alias=True), encoding="utf-8")


# =============================================================================
# Optional CLI Entrypoint
# =============================================================================

def _cli():
    """
    Simple CLI:

        python 10_10/golden_eval.py \
            --patch state_patch.json \
            --expectation golden_expectation.json \
            --out eval_report.json
    """
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Golden State Evaluator (v10_10)")
    parser.add_argument("--patch", required=True, help="Path to state_patch JSON")
    parser.add_argument("--expectation", required=True, help="Path to GoldenExpectation JSON")
    parser.add_argument("--out", required=False, help="Path to write EvalReport JSON")

    args = parser.parse_args()

    try:
        patch_data = json.loads(Path(args.patch).read_text(encoding="utf-8"))
        expectations = load_expectations(args.expectation)

        if len(expectations) != 1:
            print("Expected exactly one expectation in file.", file=sys.stderr)
            sys.exit(1)

        report = evaluate_patch(patch_data, expectations[0])

        if args.out:
            save_report(report, args.out)
        else:
            print(report.model_dump_json(indent=2))

        # Exit non-zero if failed
        sys.exit(0 if report.passed else 2)

    except Exception as e:
        print(f"Golden eval failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _cli()

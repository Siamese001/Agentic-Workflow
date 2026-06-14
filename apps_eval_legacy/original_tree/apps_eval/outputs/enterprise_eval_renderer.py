"""Enterprise Eval Renderer - artifact emission for EnterpriseEvalOrchestrator.

W5.1 (2026-04-29): Methods extracted from
`apps_eval/reasoning/enterprise_eval_orchestrator.py` to keep orchestration
logic separate from artifact emission. Lives in `apps_eval/outputs/` which is
already MV-exempt via `_NON_DURABLE_WRITER_PATH_FRAGMENTS` (W1.2 Option D)
because rendered output is NOT a durable state mutation.

Pure code motion - zero behavior change.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from apps_eval.reasoning.enterprise_eval_orchestrator import (
        EnterpriseEvalResult,
    )


def write_evaluation_markdown(result: EnterpriseEvalResult, path: Path) -> None:
    """Write the evaluation report as markdown."""
    lines: list[str] = []

    lines.append("# Enterprise Evaluation Report")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Trace ID:** `{result.trace_id}`")
    lines.append(f"**Status:** {result.status.upper()}")
    lines.append("")

    # Executive summary
    lines.append("## Executive Summary")
    lines.append("")
    eval_results = result.evaluation_results
    gates_icon = "\u2705" if result.gate_result.get("gates_passed") else "\u274c"
    validation = "\u2705 PASSED" if result.validation_result.get("passed") else "\u26a0\ufe0f REVIEW"
    lines.append(f"- **Overall Score:** {eval_results.get('overall_score', 0):.0%}")
    lines.append(f"- **Agents Executed:** {eval_results.get('agents_executed', 0)}")
    lines.append(f"- **Gates Passed:** {gates_icon}")
    lines.append(f"- **Validation:** {validation}")
    lines.append("")

    # Test plan summary
    if result.test_plan:
        lines.append("## Test Plan")
        lines.append("")
        lines.append(f"- **Total Components:** {result.test_plan.get('total_components', 0)}")
        lines.append(f"- **Unit Tests:** {result.test_plan.get('unit_tests', 0)}")
        lines.append(f"- **Integration Tests:** {result.test_plan.get('integration_tests', 0)}")
        lines.append(f"- **Benchmarks:** {result.test_plan.get('benchmarks', 0)}")
        lines.append(f"- **Execution Batches:** {result.test_plan.get('execution_batches', 0)}")
        lines.append("")

    # Dimension scores
    dimension_scores = (
        eval_results.get("results_by_type", {})
        .get("scorecard_compute", [{}])[0]
        .get("dimension_scores", {})
    )
    if dimension_scores:
        lines.append("## Dimension Scores")
        lines.append("")
        lines.append("| Dimension | Score |")
        lines.append("|-----------|-------|")
        for dim, score in dimension_scores.items():
            lines.append(f"| {dim} | {score:.0%} |")
        lines.append("")

    # Validation results
    if result.validation_result:
        lines.append("## Validation Results")
        lines.append("")
        lines.append(f"- **Quality Score:** {result.validation_result.get('quality_score', 0):.0%}")
        lines.append(f"- **Violations:** {len(result.validation_result.get('violations', []))}")
        lines.append(f"- **Anomaly Flags:** {len(result.validation_result.get('anomaly_flags', []))}")
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
            f"- **ADG Nodes/Edges:** {adg.get('nodes_count', 'N/A')} / {adg.get('edges_count', 'N/A')}"
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
            "\u2705" if entry["status"] == "complete" else "\u23f3" if entry["status"] == "start" else "\u26a0\ufe0f"
        )
        lines.append(f"{status_icon} **{entry['step']}**: {entry['status']}")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def write_manifest(result: EnterpriseEvalResult, path: Path) -> None:
    """Write the evaluation manifest."""
    manifest = {
        "trace_id": result.trace_id,
        "generated_at": datetime.now().isoformat(),
        "status": result.status,
        "test_plan": result.test_plan,
        "evaluation_results": {
            "overall_score": result.evaluation_results.get("overall_score"),
            "regression_detected": result.evaluation_results.get("regression_detected"),
            "gates_passed": result.evaluation_results.get("gates_passed"),
        },
        "validation": {
            "passed": result.validation_result.get("passed"),
            "quality_score": result.validation_result.get("quality_score"),
            "violation_count": len(result.validation_result.get("violations", [])),
        },
        "gate_result": result.gate_result,
        "repo_signals": result.repo_signals,
        "execution_log": result.execution_log,
    }

    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def write_baseline(result: EnterpriseEvalResult, path: Path) -> None:
    """Write the baseline for future comparisons."""
    baseline = {
        "trace_id": result.trace_id,
        "created_at": datetime.now().isoformat(),
        "overall_score": result.evaluation_results.get("overall_score", 0.0),
        "dimension_scores": result.evaluation_results.get("results_by_type", {})
        .get("scorecard_compute", [{}])[0]
        .get("dimension_scores", {}),
    }

    path.write_text(json.dumps(baseline, indent=2), encoding="utf-8")


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_eval.outputs.enterprise_eval_renderer', "module_loaded")

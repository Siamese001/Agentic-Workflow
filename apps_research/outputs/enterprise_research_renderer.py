"""Enterprise Research Renderer - artifact emission for EnterpriseResearchOrchestrator.

W5.1 (2026-04-29): Methods extracted from
`apps_research/reasoning/enterprise_research_orchestrator.py` to keep
orchestration logic separate from artifact emission. Lives in
`apps_research/outputs/` which is already MV-exempt via
`_NON_DURABLE_WRITER_PATH_FRAGMENTS` (W1.2 Option D).

Pure code motion - zero behavior change.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from apps_research.reasoning.enterprise_research_orchestrator import (
        EnterpriseResearchResult,
    )


def write_research_markdown(result: EnterpriseResearchResult, path: Path) -> None:
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
        f"- **Validation Passed:** {'\u2705' if result.generation_results.get('validation_passed') else '\u274c'}",
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
            lines.append(f"- Gates Passed: {'\u2705' if gates.get('gates_passed') else '\u274c'}")
            lines.append("")

    # Repository operational context
    if result.repo_signals:
        lines.append("## Repository Operational Signals")
        lines.append("")
        adg = result.repo_signals.get("adg", {})
        tests = result.repo_signals.get("tests", {})
        ci = result.repo_signals.get("ci", {})
        governance = result.repo_signals.get("governance", {})

        lines.append(f"- **ADG Available:** {'\u2705' if adg.get('available') else '\u274c'}")
        lines.append(
            f"- **ADG Nodes/Edges:** {adg.get('nodes_count', 'N/A')} / {adg.get('edges_count', 'N/A')}",
        )
        lines.append(f"- **Test Inventory Entries:** {tests.get('inventory_entries', 0)}")
        lines.append(f"- **Test Surface Entries:** {tests.get('surface_entries', 0)}")
        lines.append(f"- **Workflow Definitions:** {ci.get('workflow_count', 0)}")
        lines.append(f"- **CI Validation Log Lines:** {ci.get('ci_validation_lines', 0)}")
        lines.append(
            f"- **Governance Baseline:** {'\u2705' if governance.get('denominator_baseline_available') else '\u274c'}",
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


def write_manifest(result: EnterpriseResearchResult, path: Path) -> None:
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


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_research.outputs.enterprise_research_renderer', "module_loaded")

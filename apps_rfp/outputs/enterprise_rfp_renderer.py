"""Enterprise RFP Renderer - artifact emission for EnterpriseRfpOrchestrator.

W5.1 (2026-04-29): Methods extracted from
`apps_rfp/reasoning/enterprise_orchestrator.py` to keep orchestration logic
separate from artifact emission. Lives in `apps_rfp/outputs/` which is
already MV-exempt via `_NON_DURABLE_WRITER_PATH_FRAGMENTS` (W1.2 Option D).

Pure code motion - zero behavior change.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING

from tqdm import tqdm

if TYPE_CHECKING:
    from pathlib import Path

    from apps_rfp.reasoning.enterprise_orchestrator import EnterpriseRfpResult


def write_proposal_markdown(result: EnterpriseRfpResult, path: Path) -> None:
    """Write the proposal as markdown."""
    lines: list[str] = []

    lines.append("# AI Platform Proposal")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Trace ID:** `{result.trace_id}`")
    lines.append(f"**Status:** {result.status.upper()}")
    lines.append("")

    # Proposal sections
    for section in tqdm(result.proposal.get("sections", []), desc="Processing", unit="item"):
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
        lines.append(f"- **Validation Status:** {'\u2705 PASSED' if passed else '\u26a0\ufe0f REVIEW REQUIRED'}")
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

    path.write_text("\n".join(lines), encoding="utf-8")


def write_source_register(result: EnterpriseRfpResult, path: Path) -> None:
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


def write_validation_report(result: EnterpriseRfpResult, path: Path) -> None:
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


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_rfp.outputs.enterprise_rfp_renderer', "module_loaded")

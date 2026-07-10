"""Deterministic L7 audit-ability output for apps_rg run closeout."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.utils import write_gateway as _wg
from apps_rg.runtime.run_output_contract import L7_AUDIT_ABILITY_OUTPUT_MD

L7_HOW_TRACE_JSON = "agentic_core_how_trace.json"
L7_ROUTE_FAMILY_COVERAGE_JSON = "agentic_core_l7_route_family_coverage.json"
L7_SPINE_PROOF_JSON = "agentic_core_spine_proof.json"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return {}
    return value if isinstance(value, dict) else {}


def _payload(value: dict[str, Any]) -> dict[str, Any]:
    nested = value.get("payload")
    return nested if isinstance(nested, dict) else value


def _artifact_status(path: Path, *, required: bool) -> str:
    if path.is_file() and path.stat().st_size > 0:
        return "PRESENT"
    return "MISSING_REQUIRED" if required else "NOT_OBSERVED_OPTIONAL"


def render_l7_audit_ability_output(run_dir: Path) -> str:
    """Render L7 auditability without relying on the operator summary tool."""
    root = Path(run_dir).resolve()
    how_trace = _load_json(root / L7_HOW_TRACE_JSON)
    coverage = _load_json(root / L7_ROUTE_FAMILY_COVERAGE_JSON)
    spine_proof = _load_json(root / L7_SPINE_PROOF_JSON)
    how_payload = _payload(how_trace)
    coverage_payload = _payload(coverage)
    spine_payload = _payload(spine_proof)
    summary = coverage_payload.get("summary")
    summary = summary if isinstance(summary, dict) else {}

    lines = [
        "## 3. L7 Audit Ability Output",
        "",
        "| Artifact | Path | Status |",
        "|---|---|---|",
    ]
    for label, filename, required in (
        ("HOW trace", L7_HOW_TRACE_JSON, True),
        ("Route-family coverage", L7_ROUTE_FAMILY_COVERAGE_JSON, True),
        ("Spine proof", L7_SPINE_PROOF_JSON, False),
    ):
        path = root / filename
        lines.append(f"| **{label}** | `{path}` | `{_artifact_status(path, required=required)}` |")

    lines.extend(
        [
            "",
            "| Signal | Value |",
            "|---|---|",
            (
                "| Evidence plane | "
                f"`{coverage_payload.get('evidence_plane') or how_payload.get('evidence_plane') or 'L7_AUDITABILITY'}` |"
            ),
            (
                "| HOW trace class | "
                f"`{how_payload.get('evidence_class') or how_payload.get('proof_class') or 'NOT_OBSERVED'}` |"
            ),
            (
                "| Spine proof class | "
                f"`{spine_payload.get('evidence_class') or spine_payload.get('proof_class') or 'NOT_OBSERVED'}` |"
            ),
            (
                "| Certified route families | "
                f"`{summary.get('certified', 0)} / {summary.get('total_families', 0)}` |"
            ),
            "",
            (
                f"Certified: **{summary.get('certified', 0)} / {summary.get('total_families', 0)}** | "
                f"fixture-only: {summary.get('fixture_only', 0)} | "
                f"not certified: {summary.get('not_certified', 0)}"
            ),
            "",
        ]
    )

    families = coverage_payload.get("route_families")
    if isinstance(families, list) and families:
        lines.extend(
            [
                "| Family | Status | Proof class | Exercised |",
                "|---|---|---|---|",
            ]
        )
        for row in families:
            if not isinstance(row, dict):
                continue
            status = str(row.get("certification_status") or "NOT_CERTIFIED")
            status_icon = "✅" if status == "CERTIFIED" else "❌"
            exercised = "✅" if row.get("exercised_in_current_run") else "❌"
            lines.append(
                "| "
                f"`{row.get('route_family', '?')}` | "
                f"{status_icon} {status} | "
                f"`{row.get('proof_class', 'NOT_OBSERVED')}` | "
                f"{exercised} |"
            )
        lines.append("")
    elif not coverage:
        lines.extend(["_agentic_core_l7_route_family_coverage.json not found._", ""])

    return "\n".join(lines).rstrip() + "\n"


def emit_l7_audit_ability_output(run_dir: Path) -> Path:
    root = Path(run_dir).resolve()
    path = root / L7_AUDIT_ABILITY_OUTPUT_MD
    _wg.write_text(path, render_l7_audit_ability_output(root), encoding="utf-8")
    return path


__all__ = [
    "L7_HOW_TRACE_JSON",
    "L7_ROUTE_FAMILY_COVERAGE_JSON",
    "L7_SPINE_PROOF_JSON",
    "emit_l7_audit_ability_output",
    "render_l7_audit_ability_output",
]

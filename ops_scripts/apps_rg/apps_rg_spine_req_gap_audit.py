"""Regenerate apps_rg spine REQ gap audit JSON (pa-exec-flowchart-gap-f2a8c3 W8).

Usage:
    python ops_scripts/apps_rg/apps_rg_spine_req_gap_audit.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts" / "apps_rg" / "plans" / "apps_rg_spine_req_gap_audit.json"

GAP_ROWS: tuple[dict[str, object], ...] = (
    {
        "gap_id": "GAP-SPINE-DUAL-PATH",
        "severity": "P0",
        "layers": ["U0", "C0", "PA", "L2", "EXIT"],
        "status": "CLOSED",
        "closed_wave": "W2",
        "note": "section_front_spine_bridge + single-spine CI gate",
    },
    {
        "gap_id": "GAP-SPINE-U0-PKG",
        "severity": "P0",
        "layers": ["U0"],
        "status": "CLOSED",
        "closed_wave": "W1",
        "note": "RuntimeCustomizationPackage via u0_binding",
    },
    {
        "gap_id": "GAP-SPINE-C0-SECTION",
        "severity": "P0",
        "layers": ["C0"],
        "status": "CLOSED",
        "closed_wave": "W4",
        "note": "section_c0_retrieve + STOP AS EVIDENCE GAP",
    },
    {
        "gap_id": "GAP-SPINE-PA-CORE",
        "severity": "P0",
        "layers": ["PA"],
        "status": "CLOSED",
        "closed_wave": "W8-followup",
        "note": "integrated assemble_prompt; section slot BOM + core signing receipt",
    },
    {
        "gap_id": "GAP-SPINE-SIGN",
        "severity": "P0",
        "layers": ["L0", "PA", "L2"],
        "status": "CLOSED",
        "closed_wave": "W8-followup",
        "note": "route HMAC + PA manifest + l2_handoff_receipt.json validation surface",
    },
    {
        "gap_id": "GAP-SPINE-L2-SECTION",
        "severity": "P0",
        "layers": ["L2"],
        "status": "CLOSED",
        "closed_wave": "W6",
        "note": "section sealed_l2 + l2_handoff_receipt + governed integrated l2_execute",
    },
    {
        "gap_id": "GAP-SPINE-EXIT-ONE",
        "severity": "P0",
        "layers": ["EXIT"],
        "status": "CLOSED",
        "closed_wave": "W6",
        "note": "exit_disposition_receipt authority + ExitEvalPipeline on section finalize",
    },
    {
        "gap_id": "GAP-SPINE-OTEL",
        "severity": "P1",
        "layers": ["ALL"],
        "status": "PARTIAL",
        "closed_wave": "W8-followup",
        "note": "spine_span_emit_receipt.jsonl per layer; full OTEL SDK still open",
    },
    {
        "gap_id": "GAP-SPINE-REJECT",
        "severity": "P1",
        "layers": ["U0"],
        "status": "CLOSED",
        "closed_wave": "W1",
        "note": "RejectedRequest path",
    },
    {
        "gap_id": "GAP-SPINE-L0-HMAC",
        "severity": "P1",
        "layers": ["L0"],
        "status": "CLOSED",
        "closed_wave": "W3",
        "note": "route_digest + hmac_sig",
    },
    {
        "gap_id": "GAP-SPINE-L6-EXHAUST",
        "severity": "P2",
        "layers": ["L6"],
        "status": "PARTIAL",
        "closed_wave": "W7",
        "note": "runtime_exhaust_bundle before L6 shadow; promotion blocked",
    },
)


def _layer_summary() -> dict[str, dict[str, object]]:
    layers: dict[str, dict[str, object]] = {}
    for gap in GAP_ROWS:
        sev = str(gap["severity"])
        status = str(gap["status"])
        for layer in gap.get("layers") or ():
            if layer == "ALL":
                continue
            entry = layers.setdefault(
                layer,
                {"fit": "PARTIAL", "p0_gaps": [], "p0_open": 0},
            )
            if sev == "P0" and status == "OPEN":
                entry["p0_gaps"].append(gap["gap_id"])
                entry["p0_open"] = int(entry.get("p0_open", 0)) + 1
            if status == "CLOSED" and entry["fit"] == "PARTIAL":
                entry["fit"] = "CONVERGED"
    return layers


def main() -> int:
    p0_open = sum(
        1 for g in GAP_ROWS if g.get("severity") == "P0" and g.get("status") == "OPEN"
    )
    p0_partial = sum(
        1 for g in GAP_ROWS if g.get("severity") == "P0" and g.get("status") == "PARTIAL"
    )
    p0_closed = sum(
        1 for g in GAP_ROWS if g.get("severity") == "P0" and g.get("status") == "CLOSED"
    )
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "apps_rg U0-L6 vs REQ parent contracts",
        "plan_id": "pa-exec-flowchart-gap-f2a8c3",
        "waves_completed": ["W0", "W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"],
        "gap_analysis_report": "docs/reports/apps_rg/apps_rg_spine_req_gap_analysis_20260523.md",
        "pa_drill_down": "docs/reports/apps_rg/pa_exec_flowchart_gap_analysis_20260523.md",
        "execution_plan": ".codex/plans/pa-exec-flowchart-gap-f2a8c3.md",
        "target_architecture": {
            "apps_rg_owns": "domain_contract refs, prompt_assembly content, section templates",
            "core_owns": "generic engines U0-L6, PA pipeline, signing, Exit aggregation",
            "u0_ingests": "RuntimeCustomizationPackage at core boundary",
            "one_pipeline": "section and integrated share same spine bindings",
        },
        "layers": _layer_summary(),
        "gaps": list(GAP_ROWS),
        "gap_count": len(GAP_ROWS),
        "p0_count": p0_open,
        "p0_partial_count": p0_partial,
        "p0_closed_count": p0_closed,
        "convergence_status": "PASS" if p0_open == 0 else "PARTIAL",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"artifact": str(OUT), "p0_count": p0_open, "p0_partial_count": p0_partial}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

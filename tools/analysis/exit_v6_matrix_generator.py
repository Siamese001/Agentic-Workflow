"""Generate master matrix markdown from the OTEL evidence JSON.

One row per requirement, with trace_id/span_id, source citation, status,
observed evidence, and OTEL attributes. Reads the evidence JSON produced
by ``exit_v6_master_otel_probe.py``.

Run:
    python tools/analysis/exit_v6_matrix_generator.py
"""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_IN = _REPO / "docs/reports/plans/exit_v6_MASTER_otel_evidence.json"
_OUT = _REPO / "docs/reports/plans/exit_eval_v6_MASTER_otel_matrix.md"

_FILE_LABEL = {
    "05.1": "05.1_Exit_Input_Normalization_and_Review_Packet.md",
    "05.2": "05.2_Exit_Current_Run_Checkout_Checks_X1A_to_X1F.md",
    "05.3": "05.3_Exit_Replay_Observability_Consistency_X1G_X1I.md",
    "05.4": "05.4_Exit_Write_Eligibility_and_UWG_Handoff_X1J_X3C.md",
    "05.5": "05.5_Exit_Aggregation_and_X3_Disposition.md",
    "05.6": "05.6_Exit_HITL_Freeze_Review_and_Reclearance.md",
    "05.7": "05.7_Exit_Return_Response_and_Runtime_Exhaust.md",
    "05.8": "05.8_Exit_Specific_Observability_Tests_Anti_Bypass.md",
    "05_exec": "05_Live_Runtime_Exit_Control_&_Evaluation_exec.md",
    "05_parent": "05_Live_Runtime_Exit_Control_&_Evaluation.md",
    "v4_hardening": "v4_hardening_addendum.md",
    "grader_composition": "grader_composition_spec.md",
    "runtime_to_regression": "runtime_to_regression_dataset_flow.md",
    "gap_analysis": "gap_analysis_v3_vs_industry_2026.md",
}


def _status_emoji(s: str) -> str:
    return {"OK": "PASS", "DESIGN": "DESIGN", "GAP": "GAP"}.get(s, s)


def _truncate(s: str, n: int = 80) -> str:
    s = (s or "").replace("\n", " ").replace("|", "\\|")
    return s if len(s) <= n else s[: n - 1] + "..."


def main() -> None:
    data = json.loads(_IN.read_text())
    spans = data["spans"]
    summary = data["summary"]
    obs = data["observations_summary"]
    trace_id = data["trace_id"]

    # Group by source file
    by_source: dict[str, list[dict]] = {}
    for s in spans:
        src = s["source"].split(":")[0]
        by_source.setdefault(src, []).append(s)

    lines: list[str] = []
    lines.append("# Exit Eval v6 — MASTER OTEL Evidence Matrix")
    lines.append("")
    lines.append("Row-per-requirement matrix re-ingested from **all 14 spec files** in")
    lines.append("`docs/reference/05_Exit_Evaluation_and_Control/`. Every row carries an OTEL-shaped")
    lines.append("evidence span (`trace_id` + `span_id` + `attributes`) bound to runtime observation.")
    lines.append("")
    lines.append(f"**Trace ID** (this run): `{trace_id}`  ")
    lines.append(f"**Probe**: `tools/analysis/exit_v6_master_otel_probe.py`  ")
    lines.append(f"**Registry**: `tools/analysis/exit_v6_requirements_registry.yaml`  ")
    lines.append(f"**Evidence JSON**: `docs/reports/plans/exit_v6_MASTER_otel_evidence.json`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Status | Count | Meaning |")
    lines.append(f"|---|---:|---|")
    lines.append(
        f"| **PASS** | {summary['ok']} | requirement is observed in v6 runtime (passes its validator) |"
    )
    lines.append(
        f"| **DESIGN** | {summary['design']} | requirement is design-level only (not yet wired into v6 runtime) |"
    )
    lines.append(
        f"| **GAP** | {summary['gap']} | requirement intends a runtime binding but observation does not match spec |"
    )
    lines.append(f"| **TOTAL** | {summary['total']} | requirements across all 14 spec files |")
    lines.append("")
    lines.append("## Live runtime observations (this probe run)")
    lines.append("")
    lines.append("```")
    for k, v in obs.items():
        lines.append(f"  {k:36s} = {v}")
    lines.append("```")
    lines.append("")
    lines.append("## Coverage by source file")
    lines.append("")
    lines.append("| File | Total | PASS | DESIGN | GAP |")
    lines.append("|---|---:|---:|---:|---:|")
    for src in sorted(by_source.keys()):
        rows = by_source[src]
        c = {"OK": 0, "DESIGN": 0, "GAP": 0}
        for r in rows:
            c[r["status"]] = c.get(r["status"], 0) + 1
        label = _FILE_LABEL.get(src, src)
        lines.append(f"| `{label}` | {len(rows)} | {c['OK']} | {c['DESIGN']} | {c['GAP']} |")
    lines.append("")

    # Now per-source detailed table
    for src in sorted(by_source.keys()):
        label = _FILE_LABEL.get(src, src)
        rows = by_source[src]
        lines.append(f"## {label}")
        lines.append("")
        lines.append(f"`{src}` — {len(rows)} requirements")
        lines.append("")
        lines.append("| Req ID | Source line | Requirement | Status | Span ID | Evidence |")
        lines.append("|---|---|---|:---:|---|---|")
        for r in rows:
            line_part = r["source"].split(":", 1)[1] if ":" in r["source"] else "?"
            req_text = _truncate(r["requirement"], 100)
            ev = _truncate(r["evidence"], 90)
            lines.append(
                f"| `{r['req_id']}` | {line_part} | {req_text} | "
                f"**{_status_emoji(r['status'])}** | `{r['span_id']}` | {ev} |"
            )
        lines.append("")

    # Drift / divergence section
    lines.append("## Naming-drift findings (semantic match, registry-tracked)")
    lines.append("")
    lines.append("These are **PASS** rows where v6 emits an alias of the spec name. Not a gap —")
    lines.append("captured here because user audit benefits from explicit drift tracking.")
    lines.append("")
    lines.append("| Spec name | v6 alias | Source |")
    lines.append("|---|---|---|")
    drift_rows: list[tuple] = []
    for s in spans:
        attrs = s.get("attributes", {})
        if attrs.get("naming_drift"):
            spec = attrs.get("spec_code") or attrs.get("spec_span") or attrs.get("spec_outcome", "?")
            v6 = attrs.get("v6_alias") or attrs.get("v6_span") or attrs.get("v6_outcome", "?")
            drift_rows.append((spec, v6, s["req_id"]))
    for spec, v6, rid in sorted(drift_rows):
        lines.append(f"| `{spec}` | `{v6}` | `{rid}` |")
    lines.append("")

    # Real GAPs section
    lines.append("## Real GAPs (true divergence — needs fix)")
    lines.append("")
    gap_rows = [s for s in spans if s["status"] == "GAP"]
    if not gap_rows:
        lines.append("None.")
    else:
        lines.append("| Req ID | Source | Evidence |")
        lines.append("|---|---|---|")
        for s in gap_rows:
            lines.append(f"| `{s['req_id']}` | {s['source']} | {_truncate(s['evidence'], 200)} |")
    lines.append("")

    lines.append("## How to verify any row")
    lines.append("")
    lines.append("```")
    lines.append("# Find a span by req_id")
    lines.append(
        "python -c \"import json; d=json.load(open('docs/reports/plans/exit_v6_MASTER_otel_evidence.json')); "
        "[print(json.dumps(s, indent=2)) for s in d['spans'] if s['req_id'] == '<REQ_ID>']\""
    )
    lines.append("")
    lines.append("# Re-run the entire probe (deterministic outputs except for trace_id which is per-run)")
    lines.append("python tools/analysis/exit_v6_master_otel_probe.py")
    lines.append("")
    lines.append("# Show only GAPs")
    lines.append("python tools/analysis/_show_gaps.py")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"**Generated by** `tools/analysis/exit_v6_matrix_generator.py` from `{_IN.name}`")

    _OUT.parent.mkdir(parents=True, exist_ok=True)
    _OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote matrix -> {_OUT} ({len(lines)} lines)")


if __name__ == "__main__":
    main()

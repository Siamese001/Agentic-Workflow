"""Wiring-CI consolidated report (emitted at tail of generate_full_adg.py).

Runs the full 15-gate wiring-CI fleet against a fresh ADG snapshot and
writes a single markdown + JSON artifact to `artifacts/adg/issues/`:

    wiring_ci_report_<timestamp>.md
    wiring_ci_report_<timestamp>.json

The markdown is the canonical escalation surface — open it in a browser
and you see, for the run just completed:

    * Executive summary: N blocking red, N ratchet regressions, N at baseline
    * Fleet table: each gate's tier, status, count, delta vs baseline
    * Per-gate highlights: top 5 violations with file:line for every RED gate
    * Ratchet regression DEFERRED_SCOPE markers (Constitutional §24 format —
      the Cascade post-hook auto-posts these to Notion Wave/Phase Convergence)

Non-blocking: this module NEVER raises into the caller. Errors are captured
in the JSON payload; the ADG generation continues.

Called from:
    tools/generate/generate_full_adg.py  (right before _run_p0_two_pass_runner
    so the report emits even if P0 runner halts the pipeline)
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_DIR = REPO_ROOT / "ops_scripts" / "ci" / "baselines"

# H1 consolidation: GATES list sourced from the unified SSOT registry.
# Retired 2026-04-23 as pure duplicates of canonical/validation-plane gates:
#   A1_orphan_module_ratchet  -> v_dead_production_imports
#   A6_import_cycle           -> v_structural_conformance (SC-1 cycles)
#   L1_layer_gravity          -> v_structural_conformance (SC-1 gravity)
#   S1_global_state_mutation  -> v_p2_ratchet
#   S3_exception_swallow      -> v_p1_ratchet + v_p2_ratchet
from ops_scripts.ci.adg_gates.unified_registry import (
    WIRING_GATES,
    Enforcement,
)

# Legacy tier mapping for existing parse/render pipeline.
# Band drives severity column; Enforcement drives B/R/W symbol for back-compat.
_ENF_TO_LEGACY_TIER = {
    Enforcement.BLOCK: "B",
    Enforcement.RATCHET: "R",
    Enforcement.WARN: "W",
}

GATES: list[tuple[str, str, str, str, str]] = [
    (
        spec.gate_id,
        spec.handler.rsplit("/", 1)[-1],  # script_name (basename)
        _ENF_TO_LEGACY_TIER[spec.enforcement],
        f"{spec.gate_id} [{spec.band.value}]",
        spec.band.value,
    )
    for spec in WIRING_GATES
]

# H1 consolidation (2026-04-23): 5 entries retired (A1, L1, S1, S3, A6)
# because the gates themselves were deleted as pure duplicates of
# canonical/validation-plane gates. Regressions now route through v_p1_ratchet,
# v_p2_ratchet, v_structural_conformance, and v_dead_production_imports.
_MARKER_META: dict[str, tuple[str, str, str, str, int, str, float, int, str]] = {
    "E1_trace_stub_module": (
        "adg-wiring-ci-hardening-7a5d84",
        "W2",
        "W2.4",
        "L0",
        50,
        "Observability",
        75.0,
        10000,
        "E1 trace-theater module ratchet regression",
    ),
    "L2_lpg_drift_ratchet": (
        "adg-wiring-ci-hardening-7a5d84",
        "W3",
        "W3.2",
        "L_PG",
        25,
        "State",
        65.0,
        9000,
        "L2 L_PG internal drift ratchet regression",
    ),
    "M1_module_loc_ratchet": (
        "adg-wiring-ci-hardening-7a5d84",
        "W3",
        "W3.3",
        "L_APP",
        15,
        "None",
        50.0,
        6000,
        "M1 module LOC ratchet regression",
    ),
    "S2_uwg_bypass_ratchet": (
        "adg-wiring-ci-hardening-7a5d84",
        "W4",
        "W4.2",
        "L2",
        80,
        "Write",
        90.0,
        20000,
        "S2 UWG bypass ratchet regression",
    ),
    "S4_unused_imports_ratchet": (
        "adg-wiring-ci-hardening-7a5d84",
        "W4",
        "W4.4",
        "L_APP",
        15,
        "None",
        55.0,
        7000,
        "S4 unused imports ratchet regression",
    ),
    "A3_dead_public_symbol_ratchet": (
        "adg-wiring-ci-hardening-7a5d84",
        "W2",
        "W2.3",
        "L_APP",
        20,
        "None",
        60.0,
        8000,
        "A3 dead public symbol ratchet regression",
    ),
}


def emit_wiring_ci_report(
    adg_artifacts_dir: Path,
    ts: str,
    snapshot_name: str,
) -> dict[str, Any]:
    """Run the 15-gate fleet and write the consolidated report.

    Args:
        adg_artifacts_dir: `artifacts/adg/` root; issues subdir is created if needed.
        ts: ADG run timestamp (e.g. '04232026_0925').
        snapshot_name: Filename of the SQLite snapshot this report is keyed to.

    Returns:
        dict with keys: markdown_path, json_path, summary.
        Never raises; on internal error returns a dict with 'error' populated.
    """
    issues_dir = adg_artifacts_dir / "issues"
    issues_dir.mkdir(parents=True, exist_ok=True)
    md_path = issues_dir / f"wiring_ci_report_{ts}.md"
    json_path = issues_dir / f"wiring_ci_report_{ts}.json"

    try:
        results = [_run_gate(gid, script, tier, label, band) for gid, script, tier, label, band in GATES]
        baselines = _load_baselines()
        payload = _build_payload(results, baselines, snapshot_name, ts)
        md_path.write_text(_render_markdown(payload), encoding="utf-8")
        json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        return {
            "markdown_path": md_path,
            "json_path": json_path,
            "summary": payload["summary"],
        }
    except (OSError, RuntimeError, ValueError) as exc:
        return {
            "markdown_path": None,
            "json_path": None,
            "summary": {},
            "error": f"{type(exc).__name__}: {exc}",
        }


def _run_gate(gate_id: str, script: str, tier: str, label: str, band: str = "") -> dict[str, Any]:
    path = REPO_ROOT / "ops_scripts" / "ci" / script
    try:
        proc = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=180,
            check=False,
        )
        exit_code = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except (subprocess.TimeoutExpired, OSError) as exc:
        exit_code = -1
        stdout = ""
        stderr = f"{type(exc).__name__}: {exc}"
    # Gates print a ratchet summary line AND a fleet-status line. Pick the
    # fleet-status one which always contains `violations=N`.
    header = next(
        (line for line in stdout.splitlines() if line.startswith(f"[{gate_id}]") and "violations=" in line),
        "",
    )
    # Fallback: ratchet summary line (has current=N baseline=M but no violations=).
    if not header:
        for line in stdout.splitlines():
            if line.startswith(f"[{gate_id}]"):
                header = line
                break
    count = _parse_count(header)
    violations = _parse_violations(stdout)
    return {
        "gate_id": gate_id,
        "tier": tier,
        "band": band,
        "label": label,
        "script": script,
        "exit_code": exit_code,
        "violation_count": count,
        "status": _parse_status(header),
        "top_violations": violations[:5],
        "stderr_tail": stderr.strip().splitlines()[-5:] if stderr.strip() else [],
    }


def _parse_count(header: str) -> int:
    for key in ("violations=", "current_orphans=", "current="):
        if key in header:
            try:
                return int(header.split(key, 1)[1].split()[0])
            except (IndexError, ValueError):
                continue
    return -1


def _parse_status(header: str) -> str:
    for token in ("status=pass", "status=fail", "status=warn", "status=bypass"):
        if token in header:
            return token.split("=", 1)[1]
    return "unknown"


def _parse_violations(stdout: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- FAIL") and not stripped.startswith("- WARN"):
            continue
        # Expected format: "- FAIL <subject> :: <rule> — <detail>"
        try:
            severity, rest = stripped[2:].split(" ", 1)
            left, _, detail = rest.partition(" — ")
            subject, _, rule = left.rpartition(" :: ")
            items.append(
                {
                    "severity": severity.strip(),
                    "subject": subject.strip(),
                    "rule": rule.strip(),
                    "detail": detail.strip()[:300],
                }
            )
        except ValueError:
            continue
    return items


def _load_baselines() -> dict[str, int]:
    out: dict[str, int] = {}
    if not BASELINE_DIR.is_dir():
        return out
    for path in BASELINE_DIR.glob("wiring_*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        gid = data.get("gate_id")
        count = data.get("count")
        if gid and isinstance(count, int):
            out[gid] = count
    return out


def _build_payload(
    results: list[dict[str, Any]], baselines: dict[str, int], snapshot_name: str, ts: str
) -> dict[str, Any]:
    n_block = sum(1 for r in results if r["tier"] == "B" and r["status"] == "fail")
    n_regressions = 0
    n_at_baseline = 0
    deferred_markers: list[str] = []
    for row in results:
        if row["tier"] != "R":
            continue
        gid = row["gate_id"]
        count = row["violation_count"]
        base = baselines.get(gid)
        if base is None or count < 0:
            continue
        if count > base:
            n_regressions += 1
            marker = _format_deferred_marker(gid, count, base)
            if marker:
                deferred_markers.append(marker)
        elif count == base:
            n_at_baseline += 1
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "snapshot": snapshot_name,
        "adg_timestamp": ts,
        "summary": {
            "gates_total": len(results),
            "blocking_red": n_block,
            "ratchet_regressions": n_regressions,
            "ratchet_at_baseline": n_at_baseline,
        },
        "gates": results,
        "baselines": baselines,
        "deferred_scope_markers": deferred_markers,
    }


def _format_deferred_marker(gate_id: str, current: int, baseline: int) -> str | None:
    meta = _MARKER_META.get(gate_id)
    if not meta:
        return None
    plan, wave, phase, layer, fan_in, surface, cov, tokens, reason = meta
    return (
        f"DEFERRED_SCOPE: plan={plan} wave={wave} phase={phase} "
        f"layer={layer} fan_in={fan_in} surface={surface} "
        f"coverage_gap_pct={cov} est_tokens={tokens} "
        f'reason="{reason} (+{current - baseline} above baseline={baseline})"'
    )


def _render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines: list[str] = [
        "# Wiring-CI Report",
        "",
        f"**ADG snapshot:** `{payload['snapshot']}`  ",
        f"**Run timestamp:** `{payload['adg_timestamp']}`  ",
        f"**Generated:** `{payload['generated_at']}`",
        "",
        "## Executive Summary",
        "",
        f"- **Gates run:** {summary['gates_total']}",
        f"- **Blocking (B) RED:** {summary['blocking_red']}",
        f"- **Ratchet (R) regressions above baseline:** {summary['ratchet_regressions']}",
        f"- **Ratchets at baseline (pass):** {summary['ratchet_at_baseline']}",
        "",
    ]
    if summary["blocking_red"] > 0 or summary["ratchet_regressions"] > 0:
        lines.append(
            "> ⛔ **ESCALATION:** this run contains CI-blocking wiring failures. "
            "Review the RED rows below and the DEFERRED_SCOPE markers at the tail."
        )
    else:
        lines.append("> ✅ all wiring gates at or below baseline; no regressions.")
    lines.extend(
        [
            "",
            "## Fleet Status",
            "",
            "| Gate | Band | Tier | Status | Count | Baseline | Δ | Exit |",
            "|---|:-:|:-:|:-:|---:|---:|---:|:-:|",
        ]
    )
    baselines = payload["baselines"]
    for row in payload["gates"]:
        gid = row["gate_id"]
        base = baselines.get(gid)
        base_cell = str(base) if base is not None else "—"
        if base is not None and row["violation_count"] >= 0:
            diff = row["violation_count"] - base
            delta_cell = f"+{diff}" if diff > 0 else str(diff)
        else:
            delta_cell = "—"
        icon = {"fail": "❌", "warn": "⚠️", "pass": "✅", "bypass": "🟡", "unknown": "❓"}.get(
            row["status"], "❓"
        )
        band_cell = row.get("band", "") or "—"
        lines.append(
            f"| `{gid}` | {band_cell} | {row['tier']} | {icon} {row['status']} | "
            f"{row['violation_count']} | {base_cell} | {delta_cell} | {row['exit_code']} |"
        )

    # Per-gate highlights for RED rows only.
    red_rows = [r for r in payload["gates"] if r["status"] == "fail" and r["top_violations"]]
    if red_rows:
        lines.extend(["", "## RED Gate Highlights (top 5 per gate)", ""])
        for row in red_rows:
            lines.append(f"### `{row['gate_id']}` ({row['tier']})")
            lines.append("")
            lines.append("| # | Severity | Subject | Rule | Detail |")
            lines.append("|:-:|:-:|---|---|---|")
            for i, v in enumerate(row["top_violations"], 1):
                detail = v["detail"].replace("|", "\\|")
                subject = v["subject"].replace("|", "\\|")
                lines.append(f"| {i} | {v['severity']} | `{subject}` | {v['rule']} | {detail} |")
            lines.append("")

    # DEFERRED_SCOPE markers (Constitutional §24).
    if payload["deferred_scope_markers"]:
        lines.extend(["## DEFERRED_SCOPE Markers (auto-capture)", ""])
        lines.append(
            "The Cascade post-hook `post_cascade_deferred_scope_capture.py` picks up "
            "these markers and auto-posts them as scored P1-P5 rows in the Wave/Phase "
            "Convergence Notion database. One per ratchet above baseline."
        )
        lines.extend(["", "```"])
        lines.extend(payload["deferred_scope_markers"])
        lines.append("```")
        lines.append("")

    # Escalation routing table.
    lines.extend(
        [
            "## Escalation Routing",
            "",
            "| Signal | Destination | Mechanism |",
            "|---|---|---|",
            "| Blocking gate RED | CI job failure | `run_contract_gates.py` exit 1 — PR cannot merge |",
            "| Ratchet regression | Notion Wave/Phase Convergence DB | `DEFERRED_SCOPE` markers above, auto-posted by `post_cascade_deferred_scope_capture.py` with computed P1-P5 priority |",
            "| Full history | `artifacts/windsurf/wiring_gate_violations.jsonl` | Append-only sink; every run a JSON row |",
            "| Trend markdown | `docs/reports/wiring-ci/<YYYY-MM-DD>.md` | `python tools/reports/wiring_ci_trend.py` |",
            "| This report | `artifacts/adg/issues/wiring_ci_report_<ts>.md` | Auto-emitted by `generate_full_adg.py` |",
            "",
            "## Remediation Pointers",
            "",
            "- **J1/A6/G2 blockers**: open the specific subject file listed in the RED gate highlights and route the wiring fix per the plan at `.windsurf/plans/c0-context-engine-wiring-fix-9e42a1.md` (for C0-specific failures) or a new plan for other pipelines.",
            "- **Ratchet regressions**: locate the diff against the baseline JSON in `ops_scripts/ci/baselines/`. Either fix the regressing code or add a waiver in `config/wiring_gate_waivers.yaml` with `expires_on` ≤ 30 days.",
            "- **UWG bypass (S2) regression**: write must route through `agentic_core/L2_execution/utils/write_gateway.py` OR add the source module to `UWG_APPROVED_WRITERS` with an ADR citation (see ADR-034).",
            "- **Trace-theater (E1) regression**: do not add modules whose import surface is ≥80% `lifecycle_trace_contract._emit_*`. Real logic required.",
            "",
            "## References",
            "",
            "- Plan: `.windsurf/plans/adg-wiring-ci-hardening-7a5d84.md`",
            "- Plan: `.windsurf/plans/c0-context-engine-wiring-fix-9e42a1.md`",
            "- ADR: `docs/architecture/adr/ADR-034-wiring-ci-gate-plane-and-uwg-allowlist.md`",
            "- Constitutional: §22 (graph layer primary), §24 (DEFERRED_SCOPE capture)",
            "",
        ]
    )
    return "\n".join(lines)

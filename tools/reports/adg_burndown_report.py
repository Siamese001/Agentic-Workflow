"""Render a single, simple ADG CI burndown report.

Combines two on-disk SSOTs into one human-readable markdown:

  * artifacts/adg/adg_gate_results_<ts>.json
        — per-gate classification (block/ratchet/warn × pass/blocked/regressed)
        — written by tools.generate.generate_full_adg
  * artifacts/adg/adg_burndown_table.json
        — gross / net / diff / guardian by band (P0..P3)
        — written by tools.generate.reporting.reports

**Mandatory on every ADG run:** ``emit_mandatory_adg_burndown_report()`` is invoked
from ``tools/generate/generate_full_adg.py``, ``tools/adg/run_full_adg_audit.py``, and
``ops_scripts/ci/adg_gates/run.py``. Outputs:

  * artifacts/adg/adg_burndown_report.md
  * docs/reports/adg/adg_burndown_report.md
  * **stdout** — full markdown for inline Cursor chat (see ``.claude/rules/adg-post-run-burndown.mdc``)
  * **Cursor Canvas** — ``adg-ci-burndown.canvas.tsx`` via ``tools/reports/adg_burndown_canvas.py``

Set ``ADG_BURNDOWN_INLINE_BYPASS=1`` to suppress stdout markdown (files still written).
Set ``ADG_BURNDOWN_CANVAS_BYPASS=1`` to skip canvas generation (markdown/files still written).

The report is intentionally one file with five fixed sections:

  1. Header — snapshot, timestamp, overall verdict
  2. Burndown by band — P0..P3 gross / net / diff / guardian
  3. CI gates — all 48 gates: band, enforcement, verdict, findings, signal, recommended next step
  4. Aggregates — block_pass / block_fail / ratchet_pass / ratchet_regressed / warn
  5. Top blockers — gates currently failing, ordered by finding count

No SQL, no MCP, no dependencies beyond stdlib.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from pathlib import Path
from typing import Any

from tools.reports.gate_signal_catalog import (
    VERDICT_CLUSTER_DEFINITIONS,
    display_verdict,
    display_verdict_sub,
    format_gate_signal,
    has_backlog_findings,
    needs_fix,
    recommended_next_step,
    render_verdict_legend_markdown,
    verdict_sort_key,
)

REPO = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO / "artifacts" / "adg"
BURNDOWN_TABLE_DEFAULT = ARTIFACTS / "adg_burndown_table.json"
# Mandatory outputs on every ADG run (artifact + docs mirror for operators).
BURNDOWN_REPORT_OUTPUTS: tuple[Path, ...] = (
    ARTIFACTS / "adg_burndown_report.md",
    REPO / "docs" / "reports" / "adg" / "adg_burndown_report.md",
)


def _describe(gate: dict[str, Any]) -> str:
    """High-signal cell: what Findings measures + why Verdict is PASS/FAIL/REGR."""
    return format_gate_signal(gate)


def _verdict_display(gate: dict[str, Any]) -> str:
    """Top-level verdict: FIX | TRACK | CLEAR."""
    return display_verdict(gate)


def _verdict_sub_display(gate: dict[str, Any]) -> str:
    return display_verdict_sub(gate)


def _count_by_cluster(gates: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for g in gates:
        v = display_verdict(g)
        counts[v] = counts.get(v, 0) + 1
    return counts


def _load_gate_results(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data: dict[str, Any] = json.load(fh)
    return data


def _load_burndown(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data: dict[str, Any] = json.load(fh)
    return data


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO.resolve()))
    except ValueError:
        return str(resolved)


def _latest_gate_results() -> Path:
    candidates = sorted(ARTIFACTS.glob("adg_gate_results_*.json"))
    if not candidates:
        raise FileNotFoundError(f"no adg_gate_results_*.json under {ARTIFACTS}")
    return candidates[-1]


def _inline_burndown_bypassed() -> bool:
    return os.environ.get("ADG_BURNDOWN_INLINE_BYPASS", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def emit_mandatory_adg_burndown_report(
    *,
    gate_results: Path | None = None,
    burndown: Path | None = None,
    fail_closed: bool = True,
    print_inline: bool = True,
) -> int:
    """Write burndown markdown to disk and stdout (Cursor inline display).

    Called automatically from ``generate_full_adg`` and ``run_full_adg_audit``
    so every ADG run produces a human-readable CI burndown report.

    Args:
        gate_results: ``adg_gate_results_<ts>.json`` (defaults to newest).
        burndown: ``adg_burndown_table.json`` (defaults to artifacts/adg/).
        fail_closed: When True, return 2 if inputs are missing; else 0 with warning.
        print_inline: When True, emit full markdown to stdout for Cursor Agent chat.

    Returns:
        0 on success, 2 when inputs missing (if fail_closed), 2 on write errors.
    """
    burndown_path = (burndown or BURNDOWN_TABLE_DEFAULT).resolve()
    try:
        gate_path = (gate_results or _latest_gate_results()).resolve()
    except FileNotFoundError as exc:
        print(f"[adg_burndown_report] mandatory emit skipped: {exc}", file=sys.stderr)
        return 2 if fail_closed else 0

    missing: list[str] = []
    if not gate_path.is_file():
        missing.append(f"gate-results missing: {gate_path}")
    if not burndown_path.is_file():
        missing.append(f"burndown-table missing: {burndown_path}")
    if missing:
        print(
            "[adg_burndown_report] mandatory emit blocked — " + "; ".join(missing),
            file=sys.stderr,
        )
        return 2 if fail_closed else 0

    try:
        md = render(gate_path, burndown_path)
        for out_path in BURNDOWN_REPORT_OUTPUTS:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(md, encoding="utf-8")
            try:
                label = out_path.relative_to(REPO.resolve())
            except ValueError:
                label = out_path
            print(
                f"[adg_burndown_report] wrote {label} "
                f"({len(md.splitlines())} lines, {len(md)} bytes)",
                file=sys.stderr,
            )
        if print_inline and not _inline_burndown_bypassed():
            sys.stdout.write("\n")
            sys.stdout.write(md)
            if not md.endswith("\n"):
                sys.stdout.write("\n")
            print(
                "[adg_burndown_report] inline markdown emitted to stdout for Cursor display",
                file=sys.stderr,
            )
        elif _inline_burndown_bypassed():
            print(
                "[adg_burndown_report] WARNING: inline stdout suppressed "
                "(ADG_BURNDOWN_INLINE_BYPASS=1)",
                file=sys.stderr,
            )
        from tools.reports.adg_burndown_canvas import emit_adg_burndown_canvas

        emit_adg_burndown_canvas(
            gate_results=gate_path,
            burndown=burndown_path,
            open_markdown=True,
            open_canvas=False,
        )
    except OSError as exc:
        print(f"[adg_burndown_report] mandatory emit failed: {exc}", file=sys.stderr)
        return 2
    return 0


def render(
    gate_results_path: Path,
    burndown_path: Path,
) -> str:
    """Return the full markdown report as a string."""
    gates_doc = _load_gate_results(gate_results_path)
    burndown = _load_burndown(burndown_path)

    gates: list[dict[str, Any]] = gates_doc["gates"]
    summary = gates_doc.get("summary", {})

    lines: list[str] = []
    a = lines.append

    # ---------------------------------------------------------- §1 header
    overall = "PASS" if gates_doc.get("overall_exit_code", 1) == 0 else "BLOCKED"
    a("# ADG CI Burndown Report")
    a("")
    a(f"- **Generated:** {_dt.datetime.now(_dt.timezone.utc).isoformat(timespec='seconds')}")
    a(f"- **Gate-results source:** `{_display_path(gate_results_path)}`")
    a(f"- **Burndown source:** `{_display_path(burndown_path)}`")
    a(f"- **Snapshot timestamp:** {gates_doc.get('timestamp', 'n/a')}")
    a(f"- **Total gates:** {gates_doc.get('total_gates', len(gates))}")
    a(f"- **Overall verdict:** **{overall}** (run halt — exit code)")
    cluster_counts = _count_by_cluster(gates)
    fix_n = cluster_counts.get("FIX", 0)
    track_n = cluster_counts.get("TRACK", 0)
    if fix_n or track_n:
        a(
            f"- **Action:** **FIX**={fix_n} (address for green ADG) · "
            f"**TRACK**={track_n} (CI OK, backlog) · "
            f"**CLEAR**={cluster_counts.get('CLEAR', 0)}"
        )
    a("")

    # ---------------------------------------------------- §2 burndown by band
    a("## 1. Burndown by Severity Band")
    a("")
    a("Counts come from the canonical `adg_burndown_table.json` (schema 2.2).")
    a("`gross` = raw violations found. `guardian` = guardian-exempted (still counted).")
    a("`net` = `gross - guardian`. `diff` = delta vs prior snapshot baseline.")
    a("")
    a("| Band | Label | Gross | Guardian | Net | Diff vs prev |")
    a("|------|-------|------:|---------:|----:|-------------:|")
    for band in ("P0", "P1", "P2", "P3"):
        row = burndown.get("summary", {}).get(band, {})
        a(
            f"| {band} | {row.get('label', '?')} | "
            f"{row.get('gross', 0)} | {row.get('guardian', 0)} | "
            f"{row.get('net', 0)} | {row.get('diff', 0):+d} |"
        )
    a("")
    a(
        f"_p0_clean = {burndown.get('p0_clean')} • "
        f"p1_no_ratchet = {burndown.get('p1_no_ratchet')} • "
        f"counting_mode = `{burndown.get('provenance', {}).get('counting_mode', '?')}`_"
    )
    a("")

    # ---------------------------------------------------- §2 verdict glossary + gates
    a(render_verdict_legend_markdown())
    a("## 3. All CI Gates")
    a("")
    a("One row per registered gate.")
    a("")
    a("- **Verdict** — **FIX** = address now · **TRACK** = backlog, CI OK · **CLEAR** = zero findings.")
    a("- **Sub** — detail (block / regr / floor / inventory / …); see glossary.")
    a("- **Signal** — what Findings count + short Sub note.")
    a("- **Recommended Next Step** — concrete action for this gate (fix / re-baseline / defer / none).")
    a("")
    a("| Gate ID | Band | Enf | Verdict | Sub | Findings | Signal | Recommended Next Step |")
    a("|---------|:----:|:---:|:-------:|:---:|---------:|--------|-----------------------|")
    band_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    sorted_gates = sorted(
        gates,
        key=lambda g: (
            band_order.get(g.get("band", "P3"), 9),
            verdict_sort_key(g),
            g.get("gate_id", ""),
        ),
    )
    for g in sorted_gates:
        a(
            f"| `{g.get('gate_id', '?')}` | "
            f"{g.get('band', '?')} | "
            f"{g.get('enforcement', '?')} | "
            f"{_verdict_display(g)} | "
            f"{_verdict_sub_display(g)} | "
            f"{g.get('violation_count', 0)} | "
            f"{_describe(g)} | "
            f"{recommended_next_step(g)} |"
        )
    fix_gates = [g for g in gates if needs_fix(g)]
    if fix_gates:
        a("")
        a("### Fix now (Verdict FIX)")
        a("")
        a("| Gate ID | Sub | Findings |")
        a("|---------|:---:|---------:|")
        for g in sorted(
            fix_gates,
            key=lambda r: (-int(r.get("violation_count", 0)), r.get("gate_id", "")),
        ):
            a(
                f"| `{g.get('gate_id', '?')}` | "
                f"{_verdict_sub_display(g)} | "
                f"{g.get('violation_count', 0)} |"
            )
    track_gates = [g for g in gates if has_backlog_findings(g)]
    if track_gates:
        a("")
        a("### Track later (Verdict TRACK — CI OK, backlog remains)")
        a("")
        a("| Gate ID | Sub | Findings |")
        a("|---------|:---:|---------:|")
        for g in sorted(
            track_gates,
            key=lambda r: (-int(r.get("violation_count", 0)), r.get("gate_id", "")),
        ):
            a(
                f"| `{g.get('gate_id', '?')}` | "
                f"{_verdict_sub_display(g)} | "
                f"{g.get('violation_count', 0)} |"
            )
    a("")

    # ---------------------------------------------------- §4 aggregates
    a("## 4. Aggregate Verdicts")
    a("")
    a("| Verdict | Count | Meaning |")
    a("|---------|------:|---------|")
    a(
        f"| block_pass | {summary.get('block_pass', 0)} | "
        "Block-class gates that did not halt the run (exit 0). Findings may be non-zero. |"
    )
    a(
        f"| block_fail | {summary.get('block_fail', 0)} | "
        "Block-class gates that halted the run — clear the gate blocking condition. |"
    )
    a(f"| ratchet_pass | {summary.get('ratchet_pass', 0)} | Ratchet-class gates within their baseline ceiling. |")
    a(
        f"| ratchet_regressed | {summary.get('ratchet_regressed', 0)} | "
        "Ratchet-class gates with NEW findings beyond baseline. |"
    )
    a(f"| ratchet_seed_missing | {summary.get('ratchet_seed_missing', 0)} | Ratchet-class gates without a baseline seed (first run). |")
    a(f"| warn | {summary.get('warn', 0)} | Advisory-class gates (do not gate the run). |")
    a("")
    a("### Per-gate verdict rollup (this report)")
    a("")
    a("| Verdict | Gates | Meaning |")
    a("|---------|------:|---------|")
    for label in ("FIX", "TRACK", "CLEAR"):
        n = cluster_counts.get(label, 0)
        if n == 0 and label not in cluster_counts:
            continue
        a(f"| {label} | {n} | {VERDICT_CLUSTER_DEFINITIONS[label]} |")
    a("")

    # ---------------------------------------------------- §5 top blockers
    a("## 5. Fix now (detail)")
    a("")
    blockers = [g for g in gates if needs_fix(g)]
    if not blockers:
        a("_No FIX gates._")
    else:
        a("| Gate | Band | Enf | Sub | Findings | Signal |")
        a("|------|:----:|:---:|:---:|---------:|--------|")
        for g in sorted(
            blockers, key=lambda r: (-int(r.get("violation_count", 0)), r.get("gate_id", ""))
        ):
            a(
                f"| `{g.get('gate_id', '?')}` | "
                f"{g.get('band', '?')} | "
                f"{g.get('enforcement', '?')} | "
                f"{_verdict_sub_display(g)} | "
                f"{g.get('violation_count', 0)} | "
                f"{_describe(g)} |"
            )
    a("")

    a("---")
    for line in _render_next_action_section(gate_results_path):
        a(line)
    a("---")
    a(
        "Report renderer: `tools/reports/adg_burndown_report.py`. "
        "Re-run with `python tools/reports/adg_burndown_report.py "
        "--out artifacts/adg/adg_burndown_report.md`."
    )
    return "\n".join(lines) + "\n"


def _render_next_action_section(gate_results_path: Path) -> list[str]:
    """Link burndown to latest adg_action_queue artifact (W2)."""
    lines: list[str] = []
    lines.append("## Next action")
    lines.append("")
    queues = sorted(ARTIFACTS.glob("adg_action_queue_*.json"), key=lambda p: p.stat().st_mtime)
    if not queues:
        lines.append(
            "No `adg_action_queue_*.json` found. Emit with: "
            "`python tools/reports/adg_action_queue.py --latest`"
        )
        lines.append("")
        lines.append("Playbook: [adg_action_dispatch_playbook.md](../../docs/reports/cursor/adg_action_dispatch_playbook.md)")
        lines.append("")
        return lines

    latest = queues[-1]
    try:
        doc = json.loads(latest.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        lines.append(f"- **Queue:** `{_display_path(latest)}` (unreadable)")
        lines.append("")
        return lines

    emit_status = doc.get("emit_status", "unknown")
    degraded = doc.get("provenance", {}).get("degraded", False)
    lines.append(f"- **Queue:** `{_display_path(latest)}`")
    lines.append(f"- **emit_status:** `{emit_status}`")
    lines.append(f"- **degraded:** `{degraded}`")
    if degraded:
        reasons = doc.get("provenance", {}).get("degradation_reasons") or []
        for reason in reasons:
            lines.append(f"  - {reason}")
    summary = doc.get("summary", {})
    lines.append(
        f"- **summary:** FIX={summary.get('fix_count', '?')} · "
        f"TRACK={summary.get('track_count', '?')} · "
        f"actions_emitted={summary.get('actions_emitted', '?')}"
    )
    actions = doc.get("actions") or []
    if actions:
        lines.append("")
        lines.append("| Rank | Verdict | Target | ordering_reason |")
        lines.append("|-----:|---------|--------|-----------------|")
        for action in actions[:5]:
            target = action.get("gate_id") or action.get("source_id") or "?"
            lines.append(
                f"| {action.get('rank')} | {action.get('verdict_cluster')} | "
                f"`{target}` | {action.get('ordering_reason', '')} |"
            )
    lines.append("")
    lines.append(
        "CLI: `python tools/reports/adg_action_queue.py --latest --top 10 --format markdown`"
    )
    lines.append("")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument(
        "--gate-results",
        type=Path,
        default=None,
        help="Path to adg_gate_results_<ts>.json (defaults to latest under artifacts/adg/).",
    )
    parser.add_argument(
        "--burndown",
        type=Path,
        default=ARTIFACTS / "adg_burndown_table.json",
        help="Path to adg_burndown_table.json.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ARTIFACTS / "adg_burndown_report.md",
        help="Output markdown path.",
    )
    args = parser.parse_args(argv)

    gate_results = (args.gate_results or _latest_gate_results()).resolve()
    args.burndown = args.burndown.resolve()
    args.out = args.out.resolve()

    rc = emit_mandatory_adg_burndown_report(
        gate_results=gate_results,
        burndown=args.burndown,
        fail_closed=True,
    )
    mandatory_paths = {p.resolve() for p in BURNDOWN_REPORT_OUTPUTS}
    if args.out not in mandatory_paths and rc == 0:
        md = render(gate_results, args.burndown)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(md, encoding="utf-8")
        print(
            f"[adg_burndown_report] wrote {args.out.relative_to(REPO.resolve())} "
            f"({len(md.splitlines())} lines, {len(md)} bytes)"
        )
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

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
  * **stdout** — full markdown for inline Cursor chat (see ``.cursor/rules/adg-post-run-burndown.mdc``)
  * **Cursor Canvas** — ``adg-ci-burndown.canvas.tsx`` via ``tools/reports/adg_burndown_canvas.py``

Set ``ADG_BURNDOWN_INLINE_BYPASS=1`` to suppress stdout markdown (files still written).
Set ``ADG_BURNDOWN_CANVAS_BYPASS=1`` to skip canvas generation (markdown/files still written).

The report is intentionally one file with five fixed sections:

  1. Header — snapshot, timestamp, overall verdict
  2. Burndown by band — P0..P3 gross / net / diff / guardian
  3. CI gates — all 48 gates: description, band, enforcement, status, violations
  4. Aggregates — block_pass / block_fail / ratchet_pass / ratchet_regressed / warn
  5. Top blockers — gates currently failing, ordered by violation count

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

REPO = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO / "artifacts" / "adg"
BURNDOWN_TABLE_DEFAULT = ARTIFACTS / "adg_burndown_table.json"
# Mandatory outputs on every ADG run (artifact + docs mirror for operators).
BURNDOWN_REPORT_OUTPUTS: tuple[Path, ...] = (
    ARTIFACTS / "adg_burndown_report.md",
    REPO / "docs" / "reports" / "adg" / "adg_burndown_report.md",
)


# Human descriptions for each gate. Keyed by ``gate_id`` so the file becomes the
# documentation SSOT for "what is this gate checking?". When a new gate lands,
# add its description here; missing entries fall back to the gate_class name.
GATE_DESCRIPTIONS: dict[str, str] = {
    # --- P0 layer / authority / writes -------------------------------------
    "1_critical_path_integrity": "Critical execution paths reach their canonical sinks (no broken chains).",
    "2_authority_boundary": "L0/L_PG calls cross only declared authority boundaries (UWG / spine).",
    "3_write_sovereignty": "Every state mutation flows through UWG; no direct infra writes from apps_*.",
    "4_capability_egress": "Outbound provider/SDK calls leave through sanctioned capability adapters.",
    "5_text_to_action": "User text reaches action-class tools only after prompt-governance gating.",
    "6_determinism_provenance": "Determinism digest + replay key are emitted on every trace root.",
    # --- P1 antipattern / contract -----------------------------------------
    "7_lifecycle_coverage": "Resources opened in apps_*/agentic_core have matching close/cleanup pairs.",
    "8_exception_contract": "Catch sites obey the Column-5 precise-exception contract (no bare except).",
    "9_config_references": "Every env-flag read in code is declared in .env.example.",
    "10_test_harness_coverage": "Tier-1 emit sites (trace_root / step.seal / disposition) reach the test harness.",
    "11_expected_wiring": "Each declared call wiring (entry_module → required_call) is reachable in the AST.",
    # --- P2 hygiene / structure --------------------------------------------
    "12_archives_isolation": "No imports from archives/ in production code.",
    "13_pipeline_constants_ssot": "Pipeline constants are sourced from agentic_core.L0_routing.config only.",
    "14_hardcoded_exclusions": "No hardcoded exclusion lists outside config/excluded_paths.yaml.",
    "15_subprocess_timeout": "Every subprocess.run / Popen call carries a timeout=.",
    "16_powershell_ban": "No powershell / pwsh shell invocations in tools/ or ops_scripts/.",
    "17_query_progress_bar": "Long-running queries / scans display the canonical ProgressReporter.",
    "18_terminal_cleanup": "Long-lived terminal processes have explicit terminate paths.",
    "19_zero_loss_refactor": "Removed boilerplate did not leave hollow files behind.",
    "20_guardian_exemption_gate": "Every guardian: allow-* marker has a specific justification.",
    # --- P3 style / advisory -----------------------------------------------
    "21_no_emoji_in_code": "Production code does not contain emoji literals (advisory).",
    "22_docstring_present": "Public symbols carry a docstring (advisory).",
    # --- adg_gates suite (post-Phase-D MV gates) ---------------------------
    # Captured generically here; their per-gate descriptions are derived
    # from gate_class when not overridden above.
}


def _describe(gate: dict[str, Any]) -> str:
    """Return a one-line human description for ``gate``.

    Lookup order: explicit GATE_DESCRIPTIONS map -> gate_class name (camelCase
    split). The fallback keeps the report informative for newly-added gates
    that have not yet been described in the map.
    """
    gid = gate.get("gate_id", "")
    if gid in GATE_DESCRIPTIONS:
        return GATE_DESCRIPTIONS[gid]
    cls = gate.get("gate_class") or ""
    # Camel-case split: "WriteSovereigntyGate" -> "Write Sovereignty Gate"
    out: list[str] = []
    for ch in cls:
        if out and ch.isupper() and out[-1].islower():
            out.append(" ")
        out.append(ch)
    pretty = "".join(out).replace(" Gate", "")
    return f"{pretty} (auto-derived)" if pretty else "(no description)"


def _status_glyph(classification: str) -> str:
    return {
        "pass": "PASS",
        "blocked": "FAIL",
        "regressed": "REGR",
    }.get(classification, classification.upper())


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
    a(f"- **Overall verdict:** **{overall}**")
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

    # ---------------------------------------------------- §3 all gates table
    a("## 2. All CI Gates")
    a("")
    a("One row per registered gate. `Enf` is the enforcement contract: "
      "**block** = any violation fails the run; **ratchet** = only NEW "
      "violations beyond the baseline fail; **warn** = advisory only.")
    a("")
    a("| Gate ID | Band | Enf | Status | Violations | Description |")
    a("|---------|:----:|:---:|:------:|-----------:|-------------|")
    # Order: by band (P0..P3), then by status (failures first), then by gate_id.
    band_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    status_order = {"blocked": 0, "regressed": 1, "pass": 2}
    sorted_gates = sorted(
        gates,
        key=lambda g: (
            band_order.get(g.get("band", "P3"), 9),
            status_order.get(g.get("classification", "pass"), 9),
            g.get("gate_id", ""),
        ),
    )
    for g in sorted_gates:
        a(
            f"| `{g.get('gate_id', '?')}` | "
            f"{g.get('band', '?')} | "
            f"{g.get('enforcement', '?')} | "
            f"{_status_glyph(g.get('classification', '?'))} | "
            f"{g.get('violation_count', 0)} | "
            f"{_describe(g)} |"
        )
    a("")

    # ---------------------------------------------------- §4 aggregates
    a("## 3. Aggregate Verdicts")
    a("")
    a("| Verdict | Count | Meaning |")
    a("|---------|------:|---------|")
    a(f"| block_pass | {summary.get('block_pass', 0)} | Block-class gates with zero violations. |")
    a(f"| block_fail | {summary.get('block_fail', 0)} | Block-class gates currently failing — must reach 0. |")
    a(f"| ratchet_pass | {summary.get('ratchet_pass', 0)} | Ratchet-class gates within their baseline ceiling. |")
    a(f"| ratchet_regressed | {summary.get('ratchet_regressed', 0)} | Ratchet-class gates with NEW violations beyond baseline. |")
    a(f"| ratchet_seed_missing | {summary.get('ratchet_seed_missing', 0)} | Ratchet-class gates without a baseline seed (first run). |")
    a(f"| warn | {summary.get('warn', 0)} | Advisory-class gates (do not gate the run). |")
    a("")

    # ---------------------------------------------------- §5 top blockers
    a("## 4. Top Blockers (Failing or Regressed)")
    a("")
    blockers = [g for g in gates if g.get("classification") in ("blocked", "regressed")]
    if not blockers:
        a("_No failing or regressed gates._")
    else:
        a("| Gate | Band | Enf | Violations | Description |")
        a("|------|:----:|:---:|-----------:|-------------|")
        for g in sorted(
            blockers, key=lambda r: (-int(r.get("violation_count", 0)), r.get("gate_id", ""))
        ):
            a(
                f"| `{g.get('gate_id', '?')}` | "
                f"{g.get('band', '?')} | "
                f"{g.get('enforcement', '?')} | "
                f"{g.get('violation_count', 0)} | "
                f"{_describe(g)} |"
            )
    a("")

    a("---")
    a(
        "Report renderer: `tools/reports/adg_burndown_report.py`. "
        "Re-run with `python tools/reports/adg_burndown_report.py "
        "--out artifacts/adg/adg_burndown_report.md`."
    )
    return "\n".join(lines) + "\n"


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

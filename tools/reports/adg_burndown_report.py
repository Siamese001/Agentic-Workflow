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
  * **stdout** — full markdown for inline Cursor chat (see ``.codex/rules/adg-post-run-burndown.mdc``)
  * **Cursor Canvas** — ``adg-ci-burndown.canvas.tsx`` via ``tools/reports/adg_burndown_canvas.py``

Set ``ADG_BURNDOWN_INLINE_BYPASS=1`` to suppress stdout markdown (files still written).
Set ``ADG_BURNDOWN_CANVAS_BYPASS=1`` to skip canvas generation (markdown/files still written).

The report is intentionally one file with fixed sections:

  1. Header — snapshot, timestamp, overall verdict
  2. ADG status by band — operator rollup from gate results
  3. ADG CI gates — all gates: band, enforcement, action, rows, signal, next best action
  4. Severity inventory — raw MV defect inventory by severity/source band
  5. Aggregates — block_pass / block_fail / ratchet_pass / ratchet_regressed / warn
  6. Top blockers and next action — queue-backed dispatch guidance

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
from tools.reports.adg_bcg_adapter import (
    build_bcg_gate_adapter,
    build_report_bcg_findings,
    render_report_bcg_findings_md,
)

from tools.reports.gate_signal_catalog import (
    VERDICT_CLUSTER_DEFINITIONS,
    display_verdict,
    display_verdict_sub,
    format_gate_signal,
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
    """High-signal cell: what Rows measures + why Verdict is PASS/FAIL/REGR."""
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


def _allowed_floor_display(gate: dict[str, Any]) -> str:
    enforcement = str(gate.get("enforcement", ""))
    baseline = gate.get("baseline_count")
    sub = display_verdict_sub(gate)
    if enforcement == "ratchet":
        if baseline is not None:
            return str(baseline)
        return "missing seed" if sub == "seed" else "unseeded"
    if enforcement == "warn":
        return "advisory"
    if sub == "inventory":
        return "warn inventory"
    return "0"


def _ci_band_summary(gates: list[dict[str, Any]], adapter: dict[str, Any] | None = None) -> dict[str, dict[str, int]]:
    adapter_by_id = {
        str(row.get("gate_id")): row
        for row in (adapter or {}).get("priority_rows", []) + (adapter or {}).get("report_only_rows", [])
    }
    rows: dict[str, dict[str, int]] = {}
    for band in ("P0", "P1", "P2", "P3"):
        rows[band] = {
            "total": 0,
            "fix": 0,
            "track": 0,
            "kpi": 0,
            "clear": 0,
            "block_fail": 0,
            "ratchet_regressed": 0,
            "seed_missing": 0,
            "findings": 0,
            "track_rows": 0,
            "kpi_rows": 0,
        }
    for gate in gates:
        band = str(gate.get("band", "P3"))
        row = rows.setdefault(
            band,
            {
                "total": 0,
                "fix": 0,
                "track": 0,
                "kpi": 0,
                "clear": 0,
                "block_fail": 0,
                "ratchet_regressed": 0,
                "seed_missing": 0,
                "findings": 0,
                "track_rows": 0,
                "kpi_rows": 0,
            },
        )
        violation_count = int(gate.get("violation_count") or 0)
        row["total"] += 1
        row["findings"] += violation_count
        cluster = display_verdict(gate).lower()
        adapter_row = adapter_by_id.get(str(gate.get("gate_id")))
        if adapter_row and adapter_row.get("section") == "kpi_watchlist":
            row["kpi"] += 1
            row["kpi_rows"] += violation_count
        elif cluster in ("fix", "track", "clear"):
            row[cluster] += 1
            if cluster == "track":
                row["track_rows"] += violation_count
        sub = display_verdict_sub(gate)
        if sub == "block":
            row["block_fail"] += 1
        elif sub == "regr":
            row["ratchet_regressed"] += 1
        elif sub == "seed":
            row["seed_missing"] += 1
    return rows


def _fmt_int(value: Any) -> str:
    return f"{int(value or 0):,}"


def _plural(value: int, singular: str, plural: str | None = None) -> str:
    word = singular if value == 1 else (plural or f"{singular}s")
    return f"{_fmt_int(value)} {word}"


def _band_backlog_cell(row: dict[str, int]) -> str:
    track = int(row.get("track", 0))
    track_rows = int(row.get("track_rows", 0))
    return f"{_plural(track, 'gate')} / {_plural(track_rows, 'row')}"


def _band_kpi_cell(row: dict[str, int]) -> str:
    kpi = int(row.get("kpi", 0))
    kpi_rows = int(row.get("kpi_rows", 0))
    return f"{_plural(kpi, 'gate')} / {_plural(kpi_rows, 'row')}"


def _band_status(row: dict[str, int]) -> str:
    return "BLOCKED" if int(row.get("fix", 0)) else "PASS"


def _band_plain_read(row: dict[str, int]) -> str:
    if int(row.get("fix", 0)):
        return "red gates present"
    if int(row.get("track", 0)) or int(row.get("findings", 0)):
        if not int(row.get("track", 0)) and int(row.get("kpi", 0)):
            return "green; KPI/watchlist only"
        return "green; tracked backlog"
    return "green; no backlog"


def _band_next_move(row: dict[str, int]) -> str:
    if int(row.get("fix", 0)):
        return "fix red gates first"
    if int(row.get("track", 0)) or int(row.get("findings", 0)):
        if not int(row.get("track", 0)) and int(row.get("kpi", 0)):
            return "watch trend; no burn-down action"
        return "work ranked queue; do not treat as new failures"
    return "no action"


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


def _emit_inline_markdown(md: str, *, source: str) -> None:
    sys.stdout.write("\n")
    sys.stdout.write(md)
    if not md.endswith("\n"):
        sys.stdout.write("\n")
    print(
        f"[adg_burndown_report] inline markdown emitted to stdout for Cursor display ({source})",
        file=sys.stderr,
    )


def emit_existing_burndown_markdown(*, report_path: Path | None = None) -> int:
    """Replay an already-written burndown markdown artifact to stdout."""
    if _inline_burndown_bypassed():
        print(
            "[adg_burndown_report] WARNING: inline stdout suppressed "
            "(ADG_BURNDOWN_INLINE_BYPASS=1)",
            file=sys.stderr,
        )
        return 0

    target = (report_path or BURNDOWN_REPORT_OUTPUTS[0]).resolve()
    if not target.is_file():
        print(
            f"[adg_burndown_report] inline replay blocked — missing report: {target}",
            file=sys.stderr,
        )
        return 2

    try:
        _emit_inline_markdown(target.read_text(encoding="utf-8"), source="existing artifact")
    except OSError as exc:
        print(f"[adg_burndown_report] inline replay failed: {exc}", file=sys.stderr)
        return 2
    return 0


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
            _emit_inline_markdown(md, source="fresh render")
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



def build_burndown_bcg_findings(gates_doc: dict[str, Any], burndown: dict[str, Any]) -> dict[str, Any]:
    """Build the mandatory BCG findings envelope for the burndown report."""
    gates: list[dict[str, Any]] = list(gates_doc.get("gates") or [])
    summary = gates_doc.get("summary", {}) if isinstance(gates_doc.get("summary"), dict) else {}
    overall = "PASS" if gates_doc.get("overall_exit_code", 1) == 0 else "BLOCKED"
    adapter = build_bcg_gate_adapter(gates_doc, burndown)
    fix_rows = list(adapter.get("sections", {}).get("fix_now", {}).get("rows", []))
    burn_rows = list(adapter.get("sections", {}).get("burn_down", {}).get("rows", []))
    kpi_rows = list(adapter.get("sections", {}).get("kpi_watchlist", {}).get("rows", []))
    cluster_counts = _count_by_cluster(gates)
    priority_rows: list[dict[str, Any]] = []
    for gate in sorted(fix_rows, key=lambda r: (-int(r.get("rows", 0) or 0), str(r.get("gate_id", ""))))[:4]:
        priority_rows.append(
            {
                "priority": len(priority_rows) + 1,
                "move": f"Fix {gate.get('gate_id', '?')}",
                "why_it_matters": "This gate is marked FIX, so the ADG run is not decision-grade green until it clears.",
                "evidence": f"{gate.get('band', '?')} {gate.get('enforcement', '?')} gate; rows={gate.get('rows', 0)}; sub={gate.get('sub', '?')}.",
                "next_step": gate.get("next_step"),
                "decision": "fix_gate",
            }
        )
    if not priority_rows and burn_rows:
        for gate in sorted(burn_rows, key=lambda r: (-int(r.get("rows", 0) or 0), str(r.get("gate_id", ""))))[:4]:
            priority_rows.append(
                {
                    "priority": len(priority_rows) + 1,
                    "move": f"Burn down {gate.get('gate_id', '?')}",
                    "why_it_matters": "This is accepted or advisory debt; reduce it after FIX rows are clear.",
                    "evidence": f"Burn-down gate; rows={gate.get('rows', 0)}; sub={gate.get('sub', '?')}.",
                    "next_step": gate.get("next_step"),
                    "decision": "track_after_green",
                }
            )
    if not priority_rows:
        priority_rows.append(
            {
                "priority": 1,
                "move": "Hold ADG green posture",
                "why_it_matters": "No FIX or owned burn-down findings were promoted by the burndown report.",
                "evidence": "All reported gate clusters are clear or empty.",
                "next_step": "No burndown action required from this report.",
                "decision": "hold",
            }
        )

    business_read = (
        "ADG is BLOCKED: fix the red gates before treating the run as green."
        if fix_rows
        else (
            "ADG is PASS with tracked backlog: burn down accepted debt after green."
            if burn_rows
            else (
                "ADG is PASS with KPI/watchlist signals only: monitor trends; no burn-down action is implied."
                if kpi_rows
                else "ADG is PASS and no burndown backlog was promoted."
            )
        )
    )
    return build_report_bcg_findings(
        report_kind="adg_burndown_report",
        title="BCG Burndown Brief",
        status=overall,
        status_label="ADG verdict",
        business_read=business_read,
        technical_read=[
            f"Snapshot timestamp: {gates_doc.get('timestamp', 'n/a')}",
            f"Total gates: {gates_doc.get('total_gates', len(gates))}",
            f"FIX gates: {len(fix_rows)}",
            f"Burn-down gates: {len(burn_rows)}",
            f"KPI/watchlist gates: {len(kpi_rows)}",
            f"CLEAR gates: {cluster_counts.get('CLEAR', 0)}",
            f"block_fail={summary.get('block_fail', 0)}; ratchet_regressed={summary.get('ratchet_regressed', 0)}",
        ],
        priority_rule="FIX gates first, then owned burn-down backlog, then KPI/watchlist trends outside the work queue.",
        priority_rows=priority_rows,
        why_this_order=[
            "FIX gates block a decision-grade green run.",
            "Burn-down rows are accepted debt and should not distract from red gates.",
            "KPI/watchlist rows are visible, but are not cleanup work unless owned by a plan.",
            "CLEAR rows need no action and should stay out of the work queue.",
        ],
        next_step=priority_rows[0].get("next_step", "Follow the first priority row."),
        table_limit=6,
    )

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
    gate_adapter = build_bcg_gate_adapter(gates_doc, burndown)
    adapter_by_id = {
        str(row.get("gate_id")): row
        for row in gate_adapter.get("priority_rows", []) + gate_adapter.get("report_only_rows", [])
    }
    bcg_findings = build_burndown_bcg_findings(gates_doc, burndown)
    a("")
    a(render_report_bcg_findings_md(bcg_findings))
    adapter_summary = gate_adapter.get("summary", {})
    fix_n = int(adapter_summary.get("fix_now_gates") or 0)
    burn_n = int(adapter_summary.get("burn_down_gates") or 0)
    kpi_n = int(adapter_summary.get("kpi_watchlist_gates") or 0)
    if fix_n or burn_n or kpi_n:
        a(
            f"- **Action:** **FIX**={fix_n} (address for green ADG) · "
            f"**BURN**={burn_n} (owned backlog) · "
            f"**KPI**={kpi_n} (watchlist only) · "
            f"**CLEAR**={cluster_counts.get('CLEAR', 0)}"
        )
    a("")

    # ---------------------------------------------------- §1 ADG status by band
    a("## 1. ADG Status By Band")
    a("")
    a("Operator summary from `adg_gate_results_*.json`.")
    a("Burn-down rows come from the BCG adapter priority queue; KPI/watchlist rows stay visible but do not imply cleanup work.")
    a("")
    a("| Band | Status | Fix now | Burn-down backlog | KPI / watchlist | Read it as | Next move |")
    a("|------|:------:|--------:|-------------------|-----------------|------------|-----------|")
    band_rows = _ci_band_summary(gates, gate_adapter)
    for band in ("P0", "P1", "P2", "P3"):
        row = band_rows.get(band, {})
        a(
            f"| {band} | {_band_status(row)} | {_fmt_int(row.get('fix', 0))} | "
            f"{_band_backlog_cell(row)} | {_band_kpi_cell(row)} | "
            f"{_band_plain_read(row)} | {_band_next_move(row)} |"
        )
    a("")
    a("`Fix now` counts red gates. `Burn-down backlog` is accepted work. `KPI / watchlist` is report-only unless a plan gives it an owner and target.")
    a("")

    # ---------------------------------------------------- §2 all gates
    a("## 2. ADG CI Gates")
    a("")
    a("One row per registered gate.")
    a("")
    a("- **Section** — **FIX** = address now · **BURN** = owned backlog · **KPI** = watchlist only · **CLEAR** = zero rows.")
    a("- **Sub** — detail (block / regr / floor / inventory / …); see glossary.")
    a("- **Allowed Floor** — zero-tolerance for block gates, baseline for ratchets, advisory/inventory otherwise.")
    a("- **Rows** — gate-specific `violation_count`; meaning depends on Action/Sub.")
    a("- **Signal** — what Rows count + short Sub note.")
    a("- **Next Best Action** — concrete action for this gate (fix / re-baseline / defer / none).")
    a("")
    a("| Gate ID | CI Band | Enforcement | Section | Sub | Rows | Allowed Floor | Signal | Next Best Action |")
    a("|---------|:-------:|-------------|:-------:|:---:|---------:|---------------|--------|------------------|")
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
        adapted = adapter_by_id.get(str(g.get("gate_id"))) or {}
        section_label = {
            "fix_now": "FIX",
            "burn_down": "BURN",
            "kpi_watchlist": "KPI",
            "clear": "CLEAR",
        }.get(str(adapted.get("section") or ""), _verdict_display(g))
        a(
            f"| `{g.get('gate_id', '?')}` | "
            f"{g.get('band', '?')} | "
            f"{g.get('enforcement', '?')} | "
            f"{section_label} | "
            f"{_verdict_sub_display(g)} | "
            f"{g.get('violation_count', 0)} | "
            f"{_allowed_floor_display(g)} | "
            f"{_describe(g)} | "
            f"{recommended_next_step(g)} |"
        )
    fix_gates = list(gate_adapter.get("sections", {}).get("fix_now", {}).get("rows", []))
    if fix_gates:
        a("")
        a("### Fix now (Verdict FIX)")
        a("")
        a("| Gate ID | Sub | Rows |")
        a("|---------|:---:|---------:|")
        for g in sorted(
            fix_gates,
            key=lambda r: (-int(r.get("rows", 0)), r.get("gate_id", "")),
        ):
            a(
                f"| `{g.get('gate_id', '?')}` | "
                f"{g.get('sub', '?')} | "
                f"{g.get('rows', 0)} |"
            )
    burn_gates = list(gate_adapter.get("sections", {}).get("burn_down", {}).get("rows", []))
    if burn_gates:
        a("")
        a("### Burn down later (owned backlog — CI OK)")
        a("")
        a("| Gate ID | Sub | Rows |")
        a("|---------|:---:|---------:|")
        for g in sorted(
            burn_gates,
            key=lambda r: (-int(r.get("rows", 0)), r.get("gate_id", "")),
        ):
            a(
                f"| `{g.get('gate_id', '?')}` | "
                f"{g.get('sub', '?')} | "
                f"{g.get('rows', 0)} |"
            )
    a("")

    # ---------------------------------------------------- §3 KPI/watchlist
    a("## 3. KPI / Watchlist Signals")
    a("")
    a("These rows are visible for trend awareness, but they are not burn-down work unless a plan gives them an owner, target, and retirement condition.")
    kpi_gates = list(gate_adapter.get("sections", {}).get("kpi_watchlist", {}).get("rows", []))
    if not kpi_gates:
        a("")
        a("_No KPI/watchlist rows promoted._")
    else:
        a("")
        a("| Gate ID | Band | Rows | Why it is separate | Next step |")
        a("|---------|:----:|-----:|--------------------|-----------|")
        for row in sorted(kpi_gates, key=lambda r: (-int(r.get("rows") or 0), str(r.get("gate_id") or "")))[:12]:
            a(
                f"| `{row.get('gate_id', '?')}` | "
                f"{row.get('band', '?')} | "
                f"{row.get('rows', 0)} | "
                "KPI/watchlist signal, not an owned burn-down item. | "
                f"{row.get('next_step', '')} |"
            )
    a("")

    # ---------------------------------------------------- §4 impact inventory by band
    a("## 4. Impact Inventory Burndown")
    a("")
    a("Counts come from the canonical `adg_burndown_table.json` (schema 2.2).")
    a("This is raw MV defect inventory by impact/source band; it is not one row per CI gate.")
    a("Use this section for guardian math, not the status table above, and not the BCG foundation-blocker KPI.")
    a("`gross` = raw violations found. `guardian` = guardian-exempted (still counted).")
    a("`net` = audit net (`gross - guardian`). It is impact inventory, not live gate drivers and not foundation blockers.")
    a("Critical impact inventory can be nonzero while BCG foundation blockers are zero; the BCG KPI scorecard reconciles that split.")
    a("")
    a("| Impact Band | Impact Severity | Label | Gross | Guardian | Audit net | Diff vs prev |")
    a("|-------------|-----------------|-------|------:|---------:|----:|-------------:|")
    severity_by_band = {"P0": "critical", "P1": "high", "P2": "medium", "P3": "low"}
    for band in ("P0", "P1", "P2", "P3"):
        row = burndown.get("summary", {}).get(band, {})
        a(
            f"| {band} | {severity_by_band[band]} | {row.get('label', '?')} | "
            f"{row.get('gross', 0)} | {row.get('guardian', 0)} | "
            f"{row.get('net', 0)} | {row.get('diff', 0):+d} |"
        )
    a("")
    a(
        f"_critical_inventory_clean = {burndown.get('critical_inventory_clean', burndown.get('p0_clean'))} • "
        f"p1_no_ratchet = {burndown.get('p1_no_ratchet')} • "
        f"counting_mode = `{burndown.get('provenance', {}).get('counting_mode', '?')}`_"
    )
    a("")

    # ---------------------------------------------------- §4 verdict glossary
    a(render_verdict_legend_markdown())

    # ---------------------------------------------------- §5 aggregates
    a("## 5. Aggregate Verdicts")
    a("")
    a("| Verdict | Count | Meaning |")
    a("|---------|------:|---------|")
    a(
        f"| block_pass | {summary.get('block_pass', 0)} | "
        "Block-class gates that did not halt the run (exit 0). Rows may be non-zero. |"
    )
    a(
        f"| block_fail | {summary.get('block_fail', 0)} | "
        "Block-class gates that halted the run — clear the gate blocking condition. |"
    )
    a(f"| ratchet_pass | {summary.get('ratchet_pass', 0)} | Ratchet-class gates within their baseline ceiling. |")
    a(
        f"| ratchet_regressed | {summary.get('ratchet_regressed', 0)} | "
        "Ratchet-class gates with NEW rows beyond baseline. |"
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

    # ---------------------------------------------------- §6 top blockers
    a("## 6. Fix now (detail)")
    a("")
    blockers = list(gate_adapter.get("sections", {}).get("fix_now", {}).get("rows", []))
    if not blockers:
        a("_No FIX gates._")
    else:
        a("| Gate | Band | Enf | Sub | Rows | Signal |")
        a("|------|:----:|:---:|:---:|---------:|--------|")
        for g in sorted(
            blockers, key=lambda r: (-int(r.get("rows", 0)), r.get("gate_id", ""))
        ):
            a(
                f"| `{g.get('gate_id', '?')}` | "
                f"{g.get('band', '?')} | "
                f"{g.get('enforcement', '?')} | "
                f"{g.get('sub', '?')} | "
                f"{g.get('rows', 0)} | "
                f"{g.get('signal', '')} |"
            )
    a("")

    a("---")
    for line in _render_next_action_section(gates_doc.get("timestamp")):
        a(line)
    a("---")
    a(
        "Report renderer: `tools/reports/adg_burndown_report.py`. "
        "Re-run with `python tools/reports/adg_burndown_report.py "
        "--out artifacts/adg/adg_burndown_report.md`."
    )
    return "\n".join(lines) + "\n"


def _queue_snapshot_ts(doc: dict[str, Any]) -> str | None:
    """Return the ADG snapshot timestamp declared by an action queue."""
    provenance = doc.get("provenance") or {}
    if isinstance(provenance, dict):
        active = provenance.get("active_snapshot_ts")
        if active:
            return str(active)
        for item in provenance.get("inputs") or []:
            if isinstance(item, dict) and item.get("artifact_key") == "gate_results":
                snapshot_ts = item.get("snapshot_ts")
                if snapshot_ts:
                    return str(snapshot_ts)
    snapshot_ts = doc.get("snapshot_ts") or doc.get("snapshot_timestamp")
    return str(snapshot_ts) if snapshot_ts else None


def _select_action_queue(snapshot_ts: str | None) -> tuple[Path, dict[str, Any] | None] | None:
    queues = sorted(ARTIFACTS.glob("adg_action_queue_*.json"), key=lambda p: p.stat().st_mtime)
    if not queues:
        return None

    loaded: list[tuple[Path, dict[str, Any] | None, str | None]] = []
    for queue_path in queues:
        try:
            doc = json.loads(queue_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            loaded.append((queue_path, None, None))
            continue
        loaded.append((queue_path, doc, _queue_snapshot_ts(doc)))

    if snapshot_ts:
        matching = [(path, doc) for path, doc, ts in loaded if doc is not None and ts == snapshot_ts]
        if matching:
            return matching[-1]
        if any(ts for _path, _doc, ts in loaded):
            return None

    path, doc, _ts = loaded[-1]
    return path, doc


def _render_next_action_section(snapshot_ts: str | None = None) -> list[str]:
    """Link burndown to the action queue for this ADG snapshot."""
    lines: list[str] = []
    lines.append("## Next action")
    lines.append("")
    selected = _select_action_queue(snapshot_ts)
    if selected is None:
        if snapshot_ts:
            lines.append(f"No current-run `adg_action_queue_*.json` found for snapshot `{snapshot_ts}`.")
        else:
            lines.append("No `adg_action_queue_*.json` found.")
        lines.append(
            "Emit with: `python tools/reports/adg_action_queue.py --latest`"
        )
        lines.append("")
        lines.append("Playbook: [adg_action_dispatch_playbook.md](../../docs/reports/cursor/adg_action_dispatch_playbook.md)")
        lines.append("")
        return lines

    latest, doc = selected
    if doc is None:
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
        lines.append("| Rank | Lane | Kind | Target | ordering_reason | Signal |")
        lines.append("|-----:|------|------|--------|-----------------|--------|")
        for action in actions[:5]:
            target = action.get("gate_id") or action.get("source_id") or "?"
            signal = str(action.get("signal", ""))
            if len(signal) > 120:
                signal = signal[:117] + "..."
            lines.append(
                f"| {action.get('rank')} | {action.get('verdict_cluster')} | "
                f"{action.get('action_kind', '')} | `{target}` | "
                f"{action.get('ordering_reason', '')} | {signal} |"
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

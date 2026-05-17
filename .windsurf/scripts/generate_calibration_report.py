#!/usr/bin/env python3
"""
generate_calibration_report.py — Weekly Author-Gate calibration report.

Reads:
    - .cursor/state/refactor_decisions/refactor_decision_ledger.sqlite (SSOT)
    - artifacts/windsurf/author_gate_violations.jsonl (falls back to legacy hitl_violations.jsonl)

Writes:
    - docs/reports/author-gate/<YYYY-Www>.md (canonical)
    - stdout (human-readable summary)

METRICS
-------
From author_gate_violations.jsonl:
    - total_events
    - events_by_severity (block / shadow_warn / critical)
    - firing_rate_per_day
    - top_triggers (AG-1.x counts)
    - false_positive_rate (estimated: shadow events that were dismissed / bypassed)
    - denial_ceiling_breaches (consecutive ≥3 or total ≥20)

From decisions table:
    - total_decisions + decisions_this_week
    - decisions_by_type (refactor_scope, architecture_choice, ...)
    - recommendation_acceptance_rate (where outcome bound)
    - override_vs_recommendation_rate
    - selection_latency_p50 / p95 / rubber_stamp_count (<2s)
    - precedent_hit_rate (verdict != 'none')
    - outcome_distribution (success / rework / rollback / undecided)
    - stale_unbound_count

FLIP READINESS (for 2026-04-28 shadow → block decision):
    - FP rate < 5% ?
    - firing_rate stable (no spikes) ?
    - denial ceiling never breached ?
    - recommendation: GO / HOLD / INVESTIGATE

CONSTITUTIONAL
    - No shell=True; pure stdlib
    - UTF-8 on all I/O
    - Specific exceptions (sqlite3.Error, json.JSONDecodeError, OSError)
    - Bounded: JSONL reads capped at 10k lines
"""

import argparse
import json
import sqlite3
import statistics
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
# Library-backed calibration math (W2). Inline Wilson/binning has been retired.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from tools.calibration.loop_metrics import (  # noqa: E402
    AUTHOR_GATE_ADAPTER,
    CalibrationMetrics,
    compute_metrics as _lib_compute_metrics,
    render_calibration_curve,
    render_precedent_block,
)
from tools.refactor_decisions.ledger_paths import REFACTOR_DECISION_LEDGER_DB  # noqa: E402

DB_PATH = REFACTOR_DECISION_LEDGER_DB
VIOLATIONS_PATH = REPO_ROOT / "artifacts" / "windsurf" / "author_gate_violations.jsonl"
# Back-compat: legacy name pre-2026-04-21 rename. Read-fallback if canonical missing.
_LEGACY_VIOLATIONS_PATH = REPO_ROOT / "artifacts" / "windsurf" / "hitl_violations.jsonl"
if not VIOLATIONS_PATH.exists() and _LEGACY_VIOLATIONS_PATH.exists():
    VIOLATIONS_PATH = _LEGACY_VIOLATIONS_PATH
REPORTS_DIR = REPO_ROOT / "docs" / "reports" / "author-gate"

MAX_JSONL_LINES = 10_000
RUBBER_STAMP_MS = 2_000


# ===================================================================== #
# Data loading                                                          #
# ===================================================================== #


@dataclass
class Window:
    start: datetime
    end: datetime
    label: str  # e.g. "2026-W17"


def _iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def compute_window(week_offset: int = 0) -> Window:
    """Return the Monday 00:00 UTC → Sunday 23:59:59 UTC window for this or a prior week."""
    now = datetime.now(timezone.utc)
    this_monday = now - timedelta(days=now.weekday())
    this_monday = this_monday.replace(hour=0, minute=0, second=0, microsecond=0)
    target_monday = this_monday - timedelta(weeks=week_offset)
    end = target_monday + timedelta(days=7) - timedelta(microseconds=1)
    iso_year, iso_week, _ = target_monday.isocalendar()
    label = f"{iso_year}-W{iso_week:02d}"
    return Window(start=target_monday, end=end, label=label)


def load_violations(window: Window) -> list[dict]:
    if not VIOLATIONS_PATH.exists():
        return []
    out: list[dict] = []
    try:
        with VIOLATIONS_PATH.open("r", encoding="utf-8") as fh:
            for i, line in enumerate(fh):
                if i >= MAX_JSONL_LINES:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts_raw = rec.get("timestamp")
                if not ts_raw:
                    continue
                try:
                    ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                except ValueError:
                    continue
                if window.start <= ts <= window.end:
                    rec["_ts"] = ts
                    out.append(rec)
    except OSError:
        return []
    return out


def load_decisions(window: Window) -> list[dict]:
    if not DB_PATH.exists():
        return []
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=10)
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            """
            SELECT d.*, o.outcome_label, o.tests_passed, o.regression_found,
                   o.rollback_required, o.promote_to_pattern, o.latency_to_outcome_s
              FROM decisions d
              LEFT JOIN decision_outcomes o ON o.decision_id = d.decision_id
             WHERE d.created_at >= ? AND d.created_at <= ?
             ORDER BY d.created_at ASC
            """,
            (_iso(window.start), _iso(window.end)),
        )
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
    except sqlite3.Error:
        return []


# ===================================================================== #
# Metrics                                                               #
# ===================================================================== #


@dataclass
class Metrics:
    window: Window = field(default_factory=lambda: compute_window(0))
    # Violations (gate events)
    gate_total_events: int = 0
    gate_events_by_severity: Counter = field(default_factory=Counter)
    gate_top_triggers: list[tuple[str, int]] = field(default_factory=list)
    gate_unique_fingerprints: int = 0
    gate_firing_rate_per_day: float = 0.0
    gate_max_consecutive_denials: int = 0
    gate_max_total_denials: int = 0
    # Decisions
    dec_total: int = 0
    dec_by_type: Counter = field(default_factory=Counter)
    dec_overrides: int = 0
    dec_selections_with_latency: int = 0
    dec_rubber_stamps: int = 0
    dec_latency_p50: float | None = None
    dec_latency_p95: float | None = None
    # Library-computed calibration block (W2 — replaces inline buckets/Wilson)
    dec_calibration: CalibrationMetrics | None = None
    dec_by_outcome: Counter = field(default_factory=Counter)
    dec_stale_unbound: int = 0
    # Flip readiness
    fp_rate: float | None = None
    flip_recommendation: str = ""
    flip_reasons: list[str] = field(default_factory=list)


def compute_metrics(window: Window) -> Metrics:
    m = Metrics(window=window)
    violations = load_violations(window)
    decisions = load_decisions(window)

    # ---- Violations ----
    m.gate_total_events = len(violations)
    days = max((window.end - window.start).days, 1)
    m.gate_firing_rate_per_day = round(m.gate_total_events / days, 2)

    trig_counter: Counter = Counter()
    for ev in violations:
        sev = ev.get("severity", "unknown")
        m.gate_events_by_severity[sev] += 1
        trigs = ev.get("triggers", []) or []
        for t in trigs:
            trig_counter[t] += 1
        m.gate_max_consecutive_denials = max(
            m.gate_max_consecutive_denials, int(ev.get("consecutive", 0) or 0)
        )
        m.gate_max_total_denials = max(m.gate_max_total_denials, int(ev.get("total", 0) or 0))
    m.gate_top_triggers = trig_counter.most_common(10)
    m.gate_unique_fingerprints = len({ev.get("fingerprint") for ev in violations if ev.get("fingerprint")})

    # ---- Decisions ----
    m.dec_total = len(decisions)
    latencies: list[int] = []
    for d in decisions:
        m.dec_by_type[d.get("decision_type") or "unknown"] += 1
        if d.get("override_vs_recommendation"):
            m.dec_overrides += 1
        lat = d.get("selection_latency_ms")
        if isinstance(lat, (int, float)) and lat > 0:
            latencies.append(int(lat))
            m.dec_selections_with_latency += 1
            if lat < RUBBER_STAMP_MS:
                m.dec_rubber_stamps += 1
        m.dec_by_outcome[d.get("outcome_label") or "unbound"] += 1

    if latencies:
        m.dec_latency_p50 = round(statistics.median(latencies) / 1000, 2)
        if len(latencies) >= 20:
            sorted_lat = sorted(latencies)
            idx = max(0, int(0.95 * (len(sorted_lat) - 1)))
            m.dec_latency_p95 = round(sorted_lat[idx] / 1000, 2)

    # Library-backed calibration computation (W2). Single call covers the three
    # gaps from W1: real precedent-hit count, precedent×outcome correlation, and
    # per-band calibration curve with Wilson 95% CIs.
    m.dec_calibration = _lib_compute_metrics(decisions, AUTHOR_GATE_ADAPTER, ledger_name="author_gate")

    # Stale unbound is a ledger-wide metric, not window-scoped; grab it directly.
    m.dec_stale_unbound = _stale_unbound_count()

    # ---- FP rate & flip readiness ----
    # Definition: shadow_warn events where NO matching decision was captured
    # within the same day are treated as false positives.
    shadow_events = [ev for ev in violations if ev.get("severity") == "shadow_warn"]
    captured_fps = {d.get("context_fingerprint_json", "") for d in decisions}
    # crude: count shadow events whose fingerprint does not appear in any decision
    matched_fp_count = 0
    for ev in shadow_events:
        fp = ev.get("fingerprint")
        if fp and any(fp in (cf or "") for cf in captured_fps):
            matched_fp_count += 1
    unmatched = len(shadow_events) - matched_fp_count
    if shadow_events:
        m.fp_rate = round(unmatched / len(shadow_events), 3)
    else:
        m.fp_rate = None

    reasons: list[str] = []
    if m.fp_rate is None:
        reasons.append("insufficient shadow events for FP estimate")
        m.flip_recommendation = "HOLD"
    elif m.fp_rate > 0.05:
        reasons.append(f"FP rate {m.fp_rate:.1%} exceeds 5% target")
        m.flip_recommendation = "HOLD"
    elif m.gate_max_consecutive_denials >= 3 or m.gate_max_total_denials >= 20:
        reasons.append(
            f"denial ceiling breached (consec={m.gate_max_consecutive_denials}, "
            f"total={m.gate_max_total_denials})"
        )
        m.flip_recommendation = "INVESTIGATE"
    elif m.gate_total_events == 0:
        reasons.append("zero gate events this week — cannot validate signal")
        m.flip_recommendation = "HOLD"
    else:
        m.flip_recommendation = "GO"
        reasons.append(f"FP rate {m.fp_rate:.1%} within target")
        reasons.append(f"no denial-ceiling breach (max={m.gate_max_consecutive_denials} consec)")
    m.flip_reasons = reasons

    return m


def _stale_unbound_count() -> int:
    if not DB_PATH.exists():
        return 0
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=10)
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        cur = conn.execute(
            """
            SELECT COUNT(*) FROM decisions d
             LEFT JOIN decision_outcomes o ON o.decision_id = d.decision_id
             WHERE d.status = 'surfaced' AND o.outcome_id IS NULL
               AND d.created_at < ?
            """,
            (cutoff,),
        )
        result = cur.fetchone()[0] or 0
        conn.close()
        return int(result)
    except sqlite3.Error:
        return 0


# ===================================================================== #
# Rendering                                                             #
# ===================================================================== #


def render_markdown(m: Metrics) -> str:
    lines: list[str] = []
    lines.append(f"# Author-Gate Calibration Report — {m.window.label}")
    lines.append("")
    lines.append(f"**Window:** {_iso(m.window.start)} → {_iso(m.window.end)}")
    lines.append(f"**Generated:** {_iso(datetime.now(timezone.utc))}")
    lines.append("")
    lines.append("## Flip Readiness (shadow → block)")
    lines.append("")
    lines.append(f"**Recommendation: {m.flip_recommendation}**")
    lines.append("")
    for r in m.flip_reasons:
        lines.append(f"- {r}")
    lines.append("")
    lines.append("| Criterion | Target | Observed | Status |")
    lines.append("|---|---|---|---|")
    lines.append(
        f"| FP rate | < 5% | {m.fp_rate:.1%} | {'✅' if (m.fp_rate or 1) < 0.05 else '❌'} |"
        if m.fp_rate is not None
        else "| FP rate | < 5% | — (no shadow events) | ⚠️ |"
    )
    lines.append(
        f"| Max consecutive denials | < 3 | {m.gate_max_consecutive_denials} | "
        f"{'✅' if m.gate_max_consecutive_denials < 3 else '❌'} |"
    )
    lines.append(
        f"| Max total denials | < 20 | {m.gate_max_total_denials} | "
        f"{'✅' if m.gate_max_total_denials < 20 else '❌'} |"
    )
    lines.append(
        f"| Gate events this week | > 0 | {m.gate_total_events} | "
        f"{'✅' if m.gate_total_events > 0 else '❌'} |"
    )
    lines.append("")

    lines.append("## Gate Firing")
    lines.append("")
    lines.append(f"- **Total events:** {m.gate_total_events}")
    lines.append(f"- **Daily rate:** {m.gate_firing_rate_per_day} events/day")
    lines.append(f"- **Unique fingerprints:** {m.gate_unique_fingerprints}")
    lines.append("")
    lines.append("### Events by severity")
    lines.append("")
    if m.gate_events_by_severity:
        lines.append("| Severity | Count |")
        lines.append("|---|---|")
        for sev, n in m.gate_events_by_severity.most_common():
            lines.append(f"| {sev} | {n} |")
    else:
        lines.append("_no events_")
    lines.append("")

    lines.append("### Top triggers")
    lines.append("")
    if m.gate_top_triggers:
        lines.append("| Trigger | Fires |")
        lines.append("|---|---|")
        for trig, n in m.gate_top_triggers:
            lines.append(f"| `{trig}` | {n} |")
    else:
        lines.append("_no triggers fired_")
    lines.append("")

    lines.append("## Decisions")
    lines.append("")
    lines.append(f"- **Total surfaced this week:** {m.dec_total}")
    lines.append(
        f"- **Overrides vs recommendation:** {m.dec_overrides} "
        f"({(m.dec_overrides / m.dec_total * 100 if m.dec_total else 0):.0f}%)"
    )
    lines.append(
        f"- **Rubber-stamps (<{RUBBER_STAMP_MS}ms):** {m.dec_rubber_stamps} "
        f"/ {m.dec_selections_with_latency} tracked"
    )
    if m.dec_latency_p50 is not None:
        lines.append(f"- **Selection latency p50:** {m.dec_latency_p50}s")
    if m.dec_latency_p95 is not None:
        lines.append(f"- **Selection latency p95:** {m.dec_latency_p95}s")
    lines.append(f"- **Stale unbound (>24h, ledger-wide):** {m.dec_stale_unbound}")
    lines.append("")

    lines.append("### By type")
    lines.append("")
    if m.dec_by_type:
        lines.append("| Decision type | Count |")
        lines.append("|---|---|")
        for t, n in m.dec_by_type.most_common():
            lines.append(f"| {t} | {n} |")
    else:
        lines.append("_no decisions this week_")
    lines.append("")

    lines.append("### By outcome")
    lines.append("")
    if m.dec_by_outcome:
        lines.append("| Outcome | Count |")
        lines.append("|---|---|")
        for label, n in m.dec_by_outcome.most_common():
            lines.append(f"| {label} | {n} |")
    else:
        lines.append("_no outcomes bound this week_")
    lines.append("")

    # Library-backed precedent + calibration sections (W2)
    lines.append("## Precedent Injection (meta-learning W1)")
    lines.append("")
    if m.dec_calibration is not None:
        lines.append(render_precedent_block(m.dec_calibration))
        lines.append(render_calibration_curve(m.dec_calibration, band_units_label="confidence"))
    else:
        lines.append("_calibration metrics not computed_")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Generated by `.windsurf/scripts/generate_calibration_report.py`*")
    return "\n".join(lines)


# ===================================================================== #
# CLI                                                                   #
# ===================================================================== #


def main() -> int:
    parser = argparse.ArgumentParser(description="Weekly Author-Gate calibration report.")
    parser.add_argument("--week-offset", type=int, default=0, help="0 = current ISO week, 1 = previous, etc.")
    parser.add_argument("--no-write", action="store_true", help="Print to stdout only")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=REPORTS_DIR,
        help=f"Output directory (default {REPORTS_DIR.relative_to(REPO_ROOT)})",
    )
    args = parser.parse_args()

    window = compute_window(week_offset=args.week_offset)
    metrics = compute_metrics(window)
    body = render_markdown(metrics)
    sys.stdout.write(body + "\n")

    if not args.no_write:
        try:
            args.out_dir.mkdir(parents=True, exist_ok=True)
            out_file = args.out_dir / f"{window.label}.md"
            out_file.write_text(body, encoding="utf-8")
            print(f"\n[calibration_report] Wrote {out_file}", file=sys.stderr)
        except OSError as exc:
            print(f"[calibration_report] Write failed: {exc}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

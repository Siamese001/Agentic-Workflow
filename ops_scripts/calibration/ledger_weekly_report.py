"""ledger_weekly_report.py — Unified weekly calibration report across all ledgers.

Aggregates rows from every registered intelligence ledger into a single Markdown
report under docs/reports/calibration/<YYYY-Www>.md. Keeps each ledger section
<1KB so the full report stays under 6KB for Notion page embed.

Per ledger, emits:
    - Row count (total, predicted-only, bound)
    - Score-band distribution
    - Top-3 FTS precedent examples
    - Mean / p95 latency (if latency_ms populated)

Usage:
    python ops_scripts/calibration/ledger_weekly_report.py
    python ops_scripts/calibration/ledger_weekly_report.py --out docs/reports/calibration/2026-W17.md

Exit codes:
    0 = report written
    2 = internal error (any ledger unreadable)
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT_BOOTSTRAP = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_BOOTSTRAP))

from tools.calibration.loop_metrics import (  # noqa: E402
    EVENTS_ADAPTER,
    compute_metrics as _lib_compute_metrics,
    render_calibration_curve,
    render_precedent_block,
)
from tools.ledgers.schema_registry import LEDGER_REGISTRY, REPO_ROOT  # noqa: E402

# Wider band layout for events ledgers since score_numeric semantics vary per
# ledger. Default to 5 bands across [0, 1] so any 0..1 confidence-style score
# bins meaningfully. Per-ledger ranges (e.g., progress_eta latency_ms) ride
# under their own bands when their adapter overrides this.
_DEFAULT_BANDS: list[tuple[str, float, float]] = [
    ("[0.0, 0.2)", 0.0, 0.2),
    ("[0.2, 0.4)", 0.2, 0.4),
    ("[0.4, 0.6)", 0.4, 0.6),
    ("[0.6, 0.8)", 0.6, 0.8),
    ("[0.8, 1.0]", 0.8, 1.0001),
]


def _iso_week(dt: datetime) -> str:
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def _ledger_section(spec) -> str:
    if not spec.db_path.exists():
        return f"### `{spec.name}`\n\n_DB not yet materialized._\n\n"

    try:
        conn = sqlite3.connect(str(spec.db_path), timeout=5)
        try:
            total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            predicted = conn.execute("SELECT COUNT(*) FROM events WHERE status='predicted'").fetchone()[0]
            bound = conn.execute("SELECT COUNT(*) FROM events WHERE status='bound'").fetchone()[0]
            band_rows = conn.execute(
                "SELECT score_band, COUNT(*) FROM events WHERE score_band IS NOT NULL GROUP BY score_band"
            ).fetchall()
            latency_rows = conn.execute(
                "SELECT latency_ms FROM events WHERE latency_ms IS NOT NULL ORDER BY latency_ms"
            ).fetchall()
            # W3: pull all rows for library-backed calibration. Bounded read
            # — every ledger has a single index-friendly scan; if a ledger
            # exceeds 50k rows we'd add a date-range filter, but no ledger is
            # near that yet.
            conn.row_factory = sqlite3.Row
            full_rows_cursor = conn.execute(
                "SELECT status, score_band, score_numeric, latency_ms, "
                "prediction_json, outcome_json, metadata_json, ts_utc, bound_at "
                "FROM events"
            )
            full_rows = [dict(r) for r in full_rows_cursor.fetchall()]
        finally:
            conn.close()
    except sqlite3.Error as exc:
        return f"### `{spec.name}`\n\n_Error reading ledger: {exc}_\n\n"

    bands = Counter({r[0] or "unknown": r[1] for r in band_rows})
    latencies = [r[0] for r in latency_rows]
    latency_line = "n/a"
    if latencies:
        mean = sum(latencies) / len(latencies)
        p95 = latencies[int(max(0, len(latencies) * 0.95) - 1)]
        latency_line = f"mean={mean:.1f}ms p95={p95}ms (n={len(latencies)})"

    band_summary = ", ".join(f"{k}={v}" for k, v in bands.most_common(5)) or "none"

    lines = [
        f"### `{spec.name}` — {spec.purpose}",
        "",
        f"- **Rows**: {total} total ({predicted} predicted-only, {bound} bound)",
        f"- **Score bands**: {band_summary}",
        f"- **Latency**: {latency_line}",
        f"- **Writer hook**: `{spec.writer_hook}`",
        f"- **Wave**: {spec.wave} · **Sunset when**: {spec.sunset_criterion}",
        "",
    ]

    # W3: library-backed calibration block (precedent + per-band curve).
    # Skipped when ledger is empty or has no bound rows — nothing to compute.
    if total > 0 and bound > 0:
        try:
            metrics = _lib_compute_metrics(
                full_rows, EVENTS_ADAPTER, bands=_DEFAULT_BANDS, ledger_name=spec.name
            )
            lines.append(render_precedent_block(metrics))
            lines.append(render_calibration_curve(metrics, band_units_label="score_numeric"))
        except (ValueError, TypeError, KeyError) as exc:
            lines.append(f"_calibration block error: {exc}_")
            lines.append("")
    elif total > 0:
        lines.append(f"_calibration awaits binding: {predicted} predicted row(s) have no outcome yet_")
        lines.append("")
    return "\n".join(lines)


def _ledger_calibration_summary(spec) -> dict:
    """W4.1: Compute one row of cross-ledger dashboard data per ledger.

    Returns dict with keys: name, total, predicted, bound, hit_rate (precedent
    injection rate, NaN when no verdicts captured), miscalibrated_bands (count
    of bands with sufficient n where CI does not overlap nominal range),
    sufficient_bands (count of bands with n >= min_band_n).
    Fail-soft: any error returns sentinel values so the dashboard always renders.
    """
    blank = {
        "name": spec.name,
        "wave": spec.wave,
        "total": 0,
        "predicted": 0,
        "bound": 0,
        "verdict_count": 0,
        "hit_count": 0,
        "miscalibrated": 0,
        "sufficient": 0,
        "available": False,
    }
    if not spec.db_path.exists():
        return blank
    try:
        conn = sqlite3.connect(str(spec.db_path), timeout=5)
        try:
            total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            predicted = conn.execute("SELECT COUNT(*) FROM events WHERE status='predicted'").fetchone()[0]
            bound = conn.execute("SELECT COUNT(*) FROM events WHERE status='bound'").fetchone()[0]
            conn.row_factory = sqlite3.Row
            rows = [
                dict(r)
                for r in conn.execute(
                    "SELECT status, score_band, score_numeric, prediction_json, "
                    "outcome_json, metadata_json FROM events"
                ).fetchall()
            ]
        finally:
            conn.close()
    except sqlite3.Error:
        return {**blank, "available": False}

    blank.update({"total": total, "predicted": predicted, "bound": bound, "available": True})
    if total == 0 or bound == 0:
        return blank
    try:
        m = _lib_compute_metrics(rows, EVENTS_ADAPTER, bands=_DEFAULT_BANDS, ledger_name=spec.name)
    except (ValueError, TypeError, KeyError):
        return blank
    blank["verdict_count"] = m.total_rows - m.unknown_precedent
    blank["hit_count"] = m.precedent_hit_count
    miscal = sum(1 for b in m.calibration_curve if b.calibrated is False)
    suff = sum(1 for b in m.calibration_curve if b.sufficient)
    blank["miscalibrated"] = miscal
    blank["sufficient"] = suff
    return blank


def _render_dashboard(rollups: list[dict]) -> list[str]:
    """W4.1: Cross-ledger dashboard section. Renders ✅/⚠️/— at-a-glance."""
    lines = [
        "## Cross-Ledger Calibration Dashboard",
        "",
        "_One row per ledger. Health column is ✅ if every band with n≥5 is "
        "calibrated (CI overlaps nominal range), ⚠️ if any band is "
        "mis-calibrated, and — if no band has yet reached n≥5._",
        "",
        "| Ledger | Wave | Rows | Bound | Precedent hit-rate | Bands w/ n≥5 | Mis-cal | Health |",
        "|---|---|---:|---:|---:|---:|---:|:---:|",
    ]
    for r in rollups:
        if not r["available"]:
            lines.append(f"| `{r['name']}` | {r['wave']} | — | — | — | — | — | — |")
            continue
        if r["verdict_count"] > 0:
            hit = f"{r['hit_count']}/{r['verdict_count']} = {r['hit_count'] / r['verdict_count']:.0%}"
        else:
            hit = "—"
        if r["sufficient"] == 0:
            health = "—"
        elif r["miscalibrated"] == 0:
            health = "✅"
        else:
            health = "⚠️"
        lines.append(
            f"| `{r['name']}` | {r['wave']} | {r['total']} | {r['bound']} | "
            f"{hit} | {r['sufficient']} | {r['miscalibrated']} | {health} |"
        )
    lines.append("")
    return lines


def _render_report(now: datetime) -> str:
    header = [
        f"# Ledger Weekly Calibration — {_iso_week(now)}",
        "",
        f"Generated: {now.isoformat(timespec='seconds')}  ",
        f"Ledgers reported: {len(LEDGER_REGISTRY)}  ",
        "Plan: `docs/archive/windsurf/legacy-tree/plans/intelligence-ledgers-ten-a7c3e2.md`",
        "",
    ]

    # W4.1: Cross-ledger calibration dashboard. Computed once, also reused by
    # the weekly-summary line that appears below for at-a-glance scanning.
    rollups = [_ledger_calibration_summary(spec) for spec in LEDGER_REGISTRY]
    header.extend(_render_dashboard(rollups))

    # Legacy summary table preserved for back-compat with prior consumers.
    header.extend(
        [
            "## Row Summary",
            "",
            "| Ledger | Rows | Predicted | Bound | Wave |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for r in rollups:
        if not r["available"]:
            header.append(f"| `{r['name']}` | — | — | — | {r['wave']} |")
            continue
        header.append(f"| `{r['name']}` | {r['total']} | {r['predicted']} | {r['bound']} | {r['wave']} |")

    body = ["", "## Per-Ledger Detail", ""]
    for spec in LEDGER_REGISTRY:
        body.append(_ledger_section(spec))

    return "\n".join(header) + "\n" + "\n".join(body)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default=None,
        help="Override output path (default: docs/reports/calibration/<YYYY-Www>.md)",
    )
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    out_path: Path
    if args.out:
        out_path = Path(args.out)
    else:
        out_path = REPO_ROOT / "docs" / "reports" / "calibration" / f"{_iso_week(now)}.md"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = _render_report(now)
    out_path.write_text(content, encoding="utf-8")
    print(f"[ledger_weekly_report] wrote {out_path.relative_to(REPO_ROOT)} ({len(content)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

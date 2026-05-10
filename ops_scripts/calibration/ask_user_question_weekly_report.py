"""ask_user_question weekly calibration report.

Plan: ask-user-question-shadow-loop-wiring-b4e1f7, D2.

Analyzes recommendation-vs-selection mismatch rates from the
ask_user_question_decisions ledger. Emits both JSON and Markdown
reports under docs/reports/ask_user_question/<YYYY-Www>.md.

Usage:
    python ops_scripts/calibration/ask_user_question_weekly_report.py
    python ops_scripts/calibration/ask_user_question_weekly_report.py --json
    python ops_scripts/calibration/ask_user_question_weekly_report.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = REPO_ROOT / ".windsurf" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
REPORT_DIR = REPO_ROOT / "docs" / "reports" / "ask_user_question"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class ConfidenceBand:
    """One row of the confidence calibration curve."""

    band_label: str  # e.g., "0.60-0.70"
    low: float
    high: float
    total: int = 0
    accepted: int = 0
    overridden: int = 0
    pending: int = 0

    @property
    def acceptance_rate(self) -> float:
        resolved = self.accepted + self.overridden
        return self.accepted / resolved if resolved > 0 else 0.0


@dataclass
class ContextBreakdown:
    """Per-context aggregation."""

    context: str
    total: int = 0
    accepted: int = 0
    overridden: int = 0
    pending: int = 0

    @property
    def acceptance_rate(self) -> float:
        resolved = self.accepted + self.overridden
        return self.accepted / resolved if resolved > 0 else 0.0


@dataclass
class WeeklyReport:
    """Full weekly report data."""

    week_label: str  # "2026-W20"
    period_start: str  # ISO date
    period_end: str  # ISO date
    total_decisions: int = 0
    total_accepted: int = 0
    total_overridden: int = 0
    total_pending: int = 0
    acceptance_rate: float = 0.0
    override_rate: float = 0.0
    avg_confidence: float = 0.0
    confidence_bands: list[ConfidenceBand] = field(default_factory=list)
    context_breakdown: list[ContextBreakdown] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "week_label": self.week_label,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "total_decisions": self.total_decisions,
            "total_accepted": self.total_accepted,
            "total_overridden": self.total_overridden,
            "total_pending": self.total_pending,
            "acceptance_rate": round(self.acceptance_rate, 4),
            "override_rate": round(self.override_rate, 4),
            "avg_confidence": round(self.avg_confidence, 4),
            "confidence_bands": [
                {
                    "band": b.band_label,
                    "total": b.total,
                    "accepted": b.accepted,
                    "overridden": b.overridden,
                    "pending": b.pending,
                    "acceptance_rate": round(b.acceptance_rate, 4),
                }
                for b in self.confidence_bands
            ],
            "context_breakdown": [
                {
                    "context": c.context,
                    "total": c.total,
                    "accepted": c.accepted,
                    "overridden": c.overridden,
                    "pending": c.pending,
                    "acceptance_rate": round(c.acceptance_rate, 4),
                }
                for c in self.context_breakdown
            ],
        }


# ---------------------------------------------------------------------------
# Confidence band boundaries
# ---------------------------------------------------------------------------

BAND_EDGES = [0.0, 0.50, 0.60, 0.70, 0.80, 0.90, 1.01]


def _band_label(low: float, high: float) -> str:
    if high > 1.0:
        return f"{low:.2f}-1.00"
    return f"{low:.2f}-{high:.2f}"


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------


def _fetch_rows(
    db_path: Path,
    since: str,
    until: str,
) -> list[dict[str, Any]]:
    """Fetch decisions within the time window."""
    if not db_path.exists():
        return []
    conn = sqlite3.connect(str(db_path), timeout=5)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """SELECT * FROM ask_user_question_decisions
               WHERE created_at >= ? AND created_at < ?
               ORDER BY created_at""",
            (since, until),
        ).fetchall()
        return [dict(r) for r in rows]
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def generate_report(
    db_path: Path | None = None,
    reference_date: datetime | None = None,
) -> WeeklyReport:
    """Generate the weekly calibration report.

    Args:
        db_path: Path to the ledger SQLite file.
        reference_date: End of the reporting period (default: now UTC).

    Returns:
        WeeklyReport with all metrics computed.
    """
    db = db_path or LEDGER_PATH
    now = reference_date or datetime.now(timezone.utc)
    week_end = now
    week_start = now - timedelta(days=7)

    iso_week = now.strftime("%G-W%V")
    report = WeeklyReport(
        week_label=iso_week,
        period_start=week_start.strftime("%Y-%m-%d"),
        period_end=week_end.strftime("%Y-%m-%d"),
    )

    rows = _fetch_rows(db, week_start.isoformat(), week_end.isoformat())
    if not rows:
        return report

    report.total_decisions = len(rows)

    # Classify each row
    for row in rows:
        rec = row.get("recommended_index")
        sel = row.get("selected_index")
        if sel is None:
            report.total_pending += 1
        elif rec is not None and sel == rec:
            report.total_accepted += 1
        else:
            report.total_overridden += 1

    resolved = report.total_accepted + report.total_overridden
    report.acceptance_rate = report.total_accepted / resolved if resolved > 0 else 0.0
    report.override_rate = report.total_overridden / resolved if resolved > 0 else 0.0

    # Average confidence
    conf_scores = [r["confidence_score"] for r in rows if r.get("confidence_score") is not None]
    report.avg_confidence = sum(conf_scores) / len(conf_scores) if conf_scores else 0.0

    # Confidence bands
    bands: dict[str, ConfidenceBand] = {}
    for i in range(len(BAND_EDGES) - 1):
        low, high = BAND_EDGES[i], BAND_EDGES[i + 1]
        label = _band_label(low, high)
        bands[label] = ConfidenceBand(band_label=label, low=low, high=high)

    for row in rows:
        score = row.get("confidence_score")
        if score is None:
            continue
        for label, band in bands.items():
            if band.low <= score < band.high:
                band.total += 1
                rec = row.get("recommended_index")
                sel = row.get("selected_index")
                if sel is None:
                    band.pending += 1
                elif rec is not None and sel == rec:
                    band.accepted += 1
                else:
                    band.overridden += 1
                break

    report.confidence_bands = [b for b in bands.values() if b.total > 0]

    # Context breakdown
    ctx_map: dict[str, ContextBreakdown] = {}
    for row in rows:
        ctx = row.get("context") or "unknown"
        if ctx not in ctx_map:
            ctx_map[ctx] = ContextBreakdown(context=ctx)
        cb = ctx_map[ctx]
        cb.total += 1
        rec = row.get("recommended_index")
        sel = row.get("selected_index")
        if sel is None:
            cb.pending += 1
        elif rec is not None and sel == rec:
            cb.accepted += 1
        else:
            cb.overridden += 1

    report.context_breakdown = sorted(ctx_map.values(), key=lambda c: c.total, reverse=True)

    return report


# ---------------------------------------------------------------------------
# Markdown renderer
# ---------------------------------------------------------------------------


def render_markdown(report: WeeklyReport) -> str:
    """Render the report as Markdown."""
    lines = [
        f"# Ask-User-Question Weekly Calibration — {report.week_label}",
        "",
        f"**Period**: {report.period_start} to {report.period_end}",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total decisions | {report.total_decisions} |",
        f"| Accepted (recommendation followed) | {report.total_accepted} |",
        f"| Overridden (recommendation rejected) | {report.total_overridden} |",
        f"| Pending (no selection) | {report.total_pending} |",
        f"| Acceptance rate | {report.acceptance_rate:.1%} |",
        f"| Override rate | {report.override_rate:.1%} |",
        f"| Average confidence | {report.avg_confidence:.3f} |",
        "",
    ]

    if report.confidence_bands:
        lines.extend([
            "## Confidence Calibration Curve",
            "",
            "| Band | Total | Accepted | Overridden | Pending | Acceptance Rate |",
            "|------|-------|----------|------------|---------|-----------------|",
        ])
        for b in report.confidence_bands:
            lines.append(
                f"| {b.band_label} | {b.total} | {b.accepted} | "
                f"{b.overridden} | {b.pending} | {b.acceptance_rate:.1%} |"
            )
        lines.append("")

    if report.context_breakdown:
        lines.extend([
            "## Per-Context Breakdown",
            "",
            "| Context | Total | Accepted | Overridden | Pending | Acceptance Rate |",
            "|---------|-------|----------|------------|---------|-----------------|",
        ])
        for c in report.context_breakdown:
            lines.append(
                f"| {c.context} | {c.total} | {c.accepted} | "
                f"{c.overridden} | {c.pending} | {c.acceptance_rate:.1%} |"
            )
        lines.append("")

    lines.extend([
        "## Notes",
        "",
        "- Generated by `ops_scripts/calibration/ask_user_question_weekly_report.py`",
        "- Source: `ask_user_question_decisions` table in `refactor_decision_ledger.sqlite`",
        "",
    ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ask_user_question weekly calibration report",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    parser.add_argument("--dry-run", action="store_true", help="Print to stdout, don't write files")
    parser.add_argument("--db", type=Path, default=None, help="Override ledger DB path")
    args = parser.parse_args()

    report = generate_report(db_path=args.db)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
        return 0

    md = render_markdown(report)

    if args.dry_run:
        print(md)
        return 0

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORT_DIR / f"{report.week_label}.md"
    out_path.write_text(md, encoding="utf-8")
    print(f"[ask_user_question_weekly_report] Written to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

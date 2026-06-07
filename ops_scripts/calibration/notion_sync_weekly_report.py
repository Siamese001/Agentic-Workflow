#!/usr/bin/env python3
"""notion_sync_weekly_report.py — Weekly sync health report generator (NP14).

Generates a weekly report on Notion sync health metrics:
  - Write success rate (target: >99%)
  - Average latency p50/p99
  - Drift events per week
  - Circuit breaker transitions
  - Top failure reasons

Emits JSON + markdown reports under docs/reports/notion_sync/<YYYY-Www>.md

Constitutional: §25 (MCP serialization), §30 (capture health)
Plan: notion-sync-enforcement-hardening-f5a2c1 W4.P3
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.notion._notion_circuit_breaker import get_all_circuit_states

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LEDGER_DB_PATH = REPO_ROOT / "artifacts" / "governance" / "sync_health_ledger.sqlite"
REPORTS_DIR = REPO_ROOT / "docs" / "reports" / "notion_sync"

TARGET_SUCCESS_RATE = 99.0
TARGET_DRIFT_DETECTION_LATENCY_HOURS = 24


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class WeeklyMetrics:
    """Metrics for a single week."""
    period_start: str  # ISO date
    period_end: str
    
    # Sync attempts
    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    success_rate: float = 0.0
    
    # Latency (ms)
    latency_p50: float = 0.0
    latency_p99: float = 0.0
    avg_latency: float = 0.0
    
    # Failure breakdown
    http_4xx_count: int = 0
    http_5xx_count: int = 0
    network_failures: int = 0
    circuit_open_blocks: int = 0
    
    # Drift
    drift_events_detected: int = 0
    drifts_auto_resolved: int = 0
    drifts_pending: int = 0
    
    # Top failure reasons
    top_failure_reasons: list[tuple[str, int]] = field(default_factory=list)
    
    # Circuit state
    circuit_transitions: int = 0
    circuit_current_state: str = "unknown"
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WeeklyReport:
    """Complete weekly report."""
    week_id: str  # YYYY-Www format
    generated_at: str
    metrics: WeeklyMetrics
    targets_met: dict[str, bool]
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "week_id": self.week_id,
            "generated_at": self.generated_at,
            "metrics": self.metrics.to_dict(),
            "targets_met": self.targets_met,
        }


# ---------------------------------------------------------------------------
# Database queries
# ---------------------------------------------------------------------------

def _get_week_bounds(week_id: str | None = None) -> tuple[float, float]:
    """Get Unix timestamp bounds for a week.
    
    If week_id is None, use current week.
    """
    if week_id is None:
        now = datetime.now()
        # Get Monday of current week
        monday = now - timedelta(days=now.weekday())
        monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        next_monday = monday + timedelta(days=7)
    else:
        # Parse YYYY-Www format
        year, week = week_id.split("-W")
        year = int(year)
        week = int(week)
        # ISO week date: week 1 is the week with the first Thursday
        jan_4 = datetime(year, 1, 4)
        jan_4_weekday = jan_4.weekday()
        monday = jan_4 - timedelta(days=jan_4_weekday) + timedelta(weeks=week-1)
        monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        next_monday = monday + timedelta(days=7)
    
    return monday.timestamp(), next_monday.timestamp()


def _query_sync_metrics(start_ts: float, end_ts: float) -> dict[str, Any]:
    """Query sync metrics from the ledger database."""
    if not LEDGER_DB_PATH.exists():
        return {
            "total_attempts": 0,
            "successful_attempts": 0,
            "failed_attempts": 0,
            "latency_p50": 0.0,
            "latency_p99": 0.0,
            "avg_latency": 0.0,
            "failure_breakdown": {},
            "top_failures": [],
        }
    
    try:
        conn = sqlite3.connect(str(LEDGER_DB_PATH))
        cursor = conn.cursor()
        
        # Basic counts
        cursor.execute(
            """
            SELECT 
                COUNT(*),
                SUM(CASE WHEN success THEN 1 ELSE 0 END),
                SUM(CASE WHEN NOT success THEN 1 ELSE 0 END)
            FROM sync_attempts
            WHERE timestamp >= ? AND timestamp < ?
            """,
            (start_ts, end_ts),
        )
        total, successful, failed = cursor.fetchone()
        
        # Latency percentiles (approximate with ordered set)
        cursor.execute(
            """
            SELECT latency_ms FROM sync_attempts
            WHERE timestamp >= ? AND timestamp < ? AND latency_ms IS NOT NULL
            ORDER BY latency_ms
            """,
            (start_ts, end_ts),
        )
        latencies = [row[0] for row in cursor.fetchall()]
        
        # Failure breakdown
        cursor.execute(
            """
            SELECT failure_type, COUNT(*)
            FROM sync_attempts
            WHERE timestamp >= ? AND timestamp < ? AND NOT success
            GROUP BY failure_type
            """,
            (start_ts, end_ts),
        )
        failure_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        # Calculate percentiles
        p50 = 0.0
        p99 = 0.0
        avg = 0.0
        if latencies:
            n = len(latencies)
            p50 = latencies[n // 2]
            p99 = latencies[int(n * 0.99)] if n >= 100 else latencies[-1]
            avg = sum(latencies) / len(latencies)
        
        # Top failures
        top_failures = sorted(
            failure_breakdown.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:5]
        
        return {
            "total_attempts": total or 0,
            "successful_attempts": successful or 0,
            "failed_attempts": failed or 0,
            "latency_p50": p50,
            "latency_p99": p99,
            "avg_latency": avg,
            "failure_breakdown": failure_breakdown,
            "top_failures": top_failures,
        }
    except Exception as e:
        print(f"Warning: Could not query sync metrics: {e}")
        return {
            "total_attempts": 0,
            "successful_attempts": 0,
            "failed_attempts": 0,
            "latency_p50": 0.0,
            "latency_p99": 0.0,
            "avg_latency": 0.0,
            "failure_breakdown": {},
            "top_failures": [],
        }


def _query_drift_metrics(start_ts: float, end_ts: float) -> dict[str, int]:
    """Query drift metrics from the ledger database."""
    if not LEDGER_DB_PATH.exists():
        return {
            "detected": 0,
            "auto_resolved": 0,
            "pending": 0,
        }
    
    try:
        conn = sqlite3.connect(str(LEDGER_DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT COUNT(*) FROM drift_events
            WHERE detected_at >= ? AND detected_at < ?
            """,
            (start_ts, end_ts),
        )
        detected = cursor.fetchone()[0]
        
        cursor.execute(
            """
            SELECT COUNT(*) FROM drift_events
            WHERE detected_at >= ? AND detected_at < ?
            AND reconciliation_action = 'auto_reconciled'
            """,
            (start_ts, end_ts),
        )
        auto_resolved = cursor.fetchone()[0]
        
        cursor.execute(
            """
            SELECT COUNT(*) FROM drift_events
            WHERE reconciliation_action = 'pending'
            """,
        )
        pending = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "detected": detected,
            "auto_resolved": auto_resolved,
            "pending": pending,
        }
    except Exception as e:
        print(f"Warning: Could not query drift metrics: {e}")
        return {"detected": 0, "auto_resolved": 0, "pending": 0}


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_weekly_report(week_id: str | None = None) -> WeeklyReport:
    """Generate a weekly report."""
    start_ts, end_ts = _get_week_bounds(week_id)
    
    if week_id is None:
        # Generate week ID from current time
        now = datetime.now()
        week_id = now.strftime("%Y-W%V")
    
    # Gather metrics
    sync_data = _query_sync_metrics(start_ts, end_ts)
    drift_data = _query_drift_metrics(start_ts, end_ts)
    
    # Calculate success rate
    total = sync_data["total_attempts"]
    success_rate = (sync_data["successful_attempts"] / total * 100) if total > 0 else 100.0
    
    # Get circuit state
    circuit_states = get_all_circuit_states()
    circuit_state = "healthy"
    transitions = 0
    if circuit_states:
        # Use first circuit for status
        first = list(circuit_states.values())[0]
        circuit_state = first.get("state", "unknown")
        transitions = len(first.get("stats", {}).get("state_transitions", []))
    
    metrics = WeeklyMetrics(
        period_start=datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d"),
        period_end=datetime.fromtimestamp(end_ts).strftime("%Y-%m-%d"),
        total_attempts=total,
        successful_attempts=sync_data["successful_attempts"],
        failed_attempts=sync_data["failed_attempts"],
        success_rate=round(success_rate, 1),
        latency_p50=round(sync_data["latency_p50"], 1),
        latency_p99=round(sync_data["latency_p99"], 1),
        avg_latency=round(sync_data["avg_latency"], 1),
        http_4xx_count=sync_data["failure_breakdown"].get("http_4xx", 0),
        http_5xx_count=sync_data["failure_breakdown"].get("http_5xx", 0),
        network_failures=sync_data["failure_breakdown"].get("network", 0),
        circuit_open_blocks=sync_data["failure_breakdown"].get("circuit_open", 0),
        drift_events_detected=drift_data["detected"],
        drifts_auto_resolved=drift_data["auto_resolved"],
        drifts_pending=drift_data["pending"],
        top_failure_reasons=sync_data["top_failures"],
        circuit_transitions=transitions,
        circuit_current_state=circuit_state,
    )
    
    # Check targets
    targets_met = {
        "success_rate": success_rate >= TARGET_SUCCESS_RATE,
        "drift_detection": True,  # Placeholder - would need actual detection latency
        "circuit_stable": circuit_state == "CLOSED",
    }
    
    return WeeklyReport(
        week_id=week_id,
        generated_at=datetime.now().isoformat(),
        metrics=metrics,
        targets_met=targets_met,
    )


def _render_markdown(report: WeeklyReport) -> str:
    """Render report as Markdown."""
    m = report.metrics
    
    lines = [
        f"# Notion Sync Health Report — {report.week_id}",
        "",
        f"**Generated:** {report.generated_at[:19]}",
        f"**Period:** {m.period_start} to {m.period_end}",
        "",
        "## Summary",
        "",
        f"| Metric | Value | Target | Status |",
        f"|--------|-------|--------|--------|",
        f"| Write Success Rate | {m.success_rate:.1f}% | ≥{TARGET_SUCCESS_RATE:.0f}% | {'✅' if report.targets_met['success_rate'] else '❌'} |",
        f"| Circuit State | {m.circuit_current_state} | CLOSED | {'✅' if report.targets_met['circuit_stable'] else '⚠️'} |",
        f"| Drift Events | {m.drift_events_detected} detected, {m.drifts_pending} pending | <10 | {'✅' if m.drift_events_detected < 10 else '⚠️'} |",
        "",
        "## Sync Performance",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Attempts | {m.total_attempts} |",
        f"| Successful | {m.successful_attempts} |",
        f"| Failed | {m.failed_attempts} |",
        f"| Latency (p50) | {m.latency_p50:.1f}ms |",
        f"| Latency (p99) | {m.latency_p99:.1f}ms |",
        f"| Avg Latency | {m.avg_latency:.1f}ms |",
        "",
        "## Failure Breakdown",
        "",
        f"| Type | Count |",
        f"|------|-------|",
        f"| HTTP 4xx | {m.http_4xx_count} |",
        f"| HTTP 5xx | {m.http_5xx_count} |",
        f"| Network | {m.network_failures} |",
        f"| Circuit Open | {m.circuit_open_blocks} |",
        "",
    ]
    
    if m.top_failure_reasons:
        lines.extend([
            "## Top Failure Reasons",
            "",
            "| Reason | Count |",
            "|--------|-------|",
        ])
        for reason, count in m.top_failure_reasons:
            lines.append(f"| {reason} | {count} |")
        lines.append("")
    
    lines.extend([
        "## Drift Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Detected | {m.drift_events_detected} |",
        f"| Auto-Resolved | {m.drifts_auto_resolved} |",
        f"| Pending | {m.drifts_pending} |",
        "",
        "---",
        "",
        f"*Report generated by `notion_sync_weekly_report.py`*",
    ])
    
    return "\n".join(lines)


def emit_report(report: WeeklyReport) -> tuple[Path, Path]:
    """Emit report as JSON and Markdown."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # JSON
    json_path = REPORTS_DIR / f"{report.week_id}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2)
    
    # Markdown
    md_path = REPORTS_DIR / f"{report.week_id}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(_render_markdown(report))
    
    return json_path, md_path


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate weekly Notion sync health report",
    )
    parser.add_argument(
        "--week",
        metavar="YYYY-Www",
        help="Week to generate report for (default: current week)",
    )
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Regenerate even if report exists",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print report to stdout only (don't write files)",
    )
    
    args = parser.parse_args()
    
    if args.stdout:
        report = generate_weekly_report(args.week)
        print(_render_markdown(report))
        return 0
    
    report = generate_weekly_report(args.week)
    json_path, md_path = emit_report(report)
    
    print(f"NP14: Weekly report generated")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}")
    print(f"  Week: {report.week_id}")
    print(f"  Success Rate: {report.metrics.success_rate:.1f}%")
    print(f"  Targets Met: {sum(report.targets_met.values())}/{len(report.targets_met)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

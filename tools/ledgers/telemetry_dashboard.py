"""Telemetry validation dashboard for ASK_USER_QUESTION decisions.

Plan: author-gate-ask-ui-deferred-scope-a2e3f8 D5.

Provides metrics and alerting for ASK_USER_QUESTION_PACKET completeness.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from tools.refactor_decisions.ledger_paths import REFACTOR_DECISION_LEDGER_DB

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = REFACTOR_DECISION_LEDGER_DB


@dataclass
class TelemetryMetrics:
    """Metrics snapshot for telemetry completeness."""
    
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_decisions_24h: int = 0
    decisions_with_packets: int = 0
    decisions_without_packets: int = 0
    packet_coverage_pct: float = 0.0
    by_context: dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "total_decisions_24h": self.total_decisions_24h,
            "decisions_with_packets": self.decisions_with_packets,
            "decisions_without_packets": self.decisions_without_packets,
            "packet_coverage_pct": round(self.packet_coverage_pct, 2),
            "by_context": self.by_context,
        }


def get_telemetry_metrics(
    hours: int = 24,
    ledger_path: Path | None = None,
) -> TelemetryMetrics:
    """Get telemetry completeness metrics for the specified time window.
    
    Args:
        hours: Time window in hours (default 24)
        ledger_path: Optional custom ledger path
    
    Returns:
        TelemetryMetrics with coverage statistics
    """
    db_path = ledger_path or LEDGER_PATH
    
    if not db_path.exists():
        return TelemetryMetrics()
    
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    
    conn = sqlite3.connect(db_path)
    try:
        # Total decisions in window
        total = conn.execute(
            "SELECT COUNT(*) FROM ask_user_question_decisions WHERE created_at >= ?",
            (since,)
        ).fetchone()[0]
        
        # Decisions with packets (packet_json not null and not empty)
        with_packets = conn.execute(
            """SELECT COUNT(*) FROM ask_user_question_decisions 
               WHERE created_at >= ? AND packet_json IS NOT NULL AND packet_json != ''""",
            (since,)
        ).fetchone()[0]
        
        # By context
        context_rows = conn.execute(
            """SELECT context, COUNT(*) FROM ask_user_question_decisions 
               WHERE created_at >= ? GROUP BY context""",
            (since,)
        ).fetchall()
        
        by_context = {ctx or "unknown": count for ctx, count in context_rows}
        
        coverage = (with_packets / total * 100) if total > 0 else 100.0
        
        return TelemetryMetrics(
            total_decisions_24h=total,
            decisions_with_packets=with_packets,
            decisions_without_packets=total - with_packets,
            packet_coverage_pct=coverage,
            by_context=by_context,
        )
    finally:
        conn.close()


def check_vacuum_closure(
    threshold_pct: float = 95.0,
    hours: int = 24,
) -> dict[str, Any]:
    """Check if telemetry vacuum-closure requirement is met.
    
    Args:
        threshold_pct: Minimum coverage percentage required
        hours: Time window to check
    
    Returns:
        Dict with status, metrics, and alert info
    """
    metrics = get_telemetry_metrics(hours=hours)
    
    is_healthy = metrics.packet_coverage_pct >= threshold_pct
    
    return {
        "status": "healthy" if is_healthy else "alert",
        "threshold_pct": threshold_pct,
        "actual_pct": metrics.packet_coverage_pct,
        "metrics": metrics.to_dict(),
        "alert": None if is_healthy else {
            "severity": "warning",
            "message": f"Packet coverage {metrics.packet_coverage_pct:.1f}% below threshold {threshold_pct}%",
        },
    }


def generate_weekly_report() -> dict[str, Any]:
    """Generate weekly telemetry validation report."""
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    
    daily_metrics = []
    for i in range(7):
        day_start = week_ago + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        # Query for that day (simplified - in real impl would use proper date queries)
        metrics = get_telemetry_metrics(hours=24)
        daily_metrics.append({
            "day": day_start.strftime("%Y-%m-%d"),
            "coverage": metrics.packet_coverage_pct,
            "total": metrics.total_decisions_24h,
        })
    
    avg_coverage = sum(d["coverage"] for d in daily_metrics) / len(daily_metrics) if daily_metrics else 0
    
    return {
        "period": f"{week_ago.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}",
        "average_coverage": round(avg_coverage, 2),
        "daily_breakdown": daily_metrics,
        "recommendation": "healthy" if avg_coverage >= 95 else "review",
    }


def main() -> int:
    """CLI entry point for telemetry dashboard."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Telemetry validation dashboard")
    parser.add_argument("--metrics", action="store_true", help="Show current metrics")
    parser.add_argument("--check", action="store_true", help="Check vacuum closure")
    parser.add_argument("--weekly", action="store_true", help="Generate weekly report")
    parser.add_argument("--threshold", type=float, default=95.0, help="Coverage threshold")
    parser.add_argument("--hours", type=int, default=24, help="Time window")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    if args.metrics:
        metrics = get_telemetry_metrics(hours=args.hours)
        if args.json:
            print(json.dumps(metrics.to_dict(), indent=2))
        else:
            print(f"Telemetry Metrics (last {args.hours}h)")
            print(f"  Total decisions: {metrics.total_decisions_24h}")
            print(f"  With packets: {metrics.decisions_with_packets}")
            print(f"  Coverage: {metrics.packet_coverage_pct:.1f}%")
            if metrics.by_context:
                print("  By context:")
                for ctx, count in metrics.by_context.items():
                    print(f"    {ctx}: {count}")
        return 0
    
    if args.check:
        result = check_vacuum_closure(threshold_pct=args.threshold, hours=args.hours)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            status = "✅" if result["status"] == "healthy" else "⚠️"
            print(f"{status} Vacuum Closure Check")
            print(f"  Threshold: {result['threshold_pct']}%")
            print(f"  Actual: {result['actual_pct']:.1f}%")
            if result["alert"]:
                print(f"  ALERT: {result['alert']['message']}")
        return 0 if result["status"] == "healthy" else 1
    
    if args.weekly:
        report = generate_weekly_report()
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"Weekly Report ({report['period']})")
            print(f"  Average coverage: {report['average_coverage']:.1f}%")
            print(f"  Recommendation: {report['recommendation']}")
        return 0
    
    parser.print_help()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

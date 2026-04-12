#!/usr/bin/env python3
"""
MCP Usage Tracker for Sequential Thinking Monitoring
Tracks and analyzes MCP tool usage patterns to optimize sequential thinking adoption.
"""

import json
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ToolUsageEntry:
    """Individual tool usage entry."""

    timestamp: float
    tool_name: str
    context: str
    success: bool
    response_time: float
    token_count: int
    user_query: str
    session_id: str


@dataclass
class UsageSummary:
    """Usage summary for a tool."""

    usage_count: int
    success_rate: float
    avg_response_time: float
    total_tokens: int
    last_used: float
    recommendation: str


class MCPUsageTracker:
    """Track and analyze MCP tool usage patterns."""

    def __init__(self, db_path: Path | None = None):
        """Initialize tracker with database."""
        if db_path is None:
            db_path = Path("artifacts/monitoring/mcp_usage.db")

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for usage tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tool_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    tool_name TEXT NOT NULL,
                    context TEXT,
                    success BOOLEAN NOT NULL,
                    response_time REAL,
                    token_count INTEGER,
                    user_query TEXT,
                    session_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tool_name ON tool_usage(tool_name)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON tool_usage(timestamp)
            """)

            conn.commit()

    def log_tool_usage(self, entry: ToolUsageEntry):
        """Log tool usage for analysis."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO tool_usage
                (timestamp, tool_name, context, success, response_time, token_count, user_query, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    entry.timestamp,
                    entry.tool_name,
                    entry.context,
                    entry.success,
                    entry.response_time,
                    entry.token_count,
                    entry.user_query,
                    entry.session_id,
                ),
            )
            conn.commit()

    def log_simple_usage(
        self,
        tool_name: str,
        context: str,
        success: bool,
        response_time: float = 0.0,
        token_count: int = 0,
        user_query: str = "",
        session_id: str = "",
    ):
        """Simple logging method."""
        entry = ToolUsageEntry(
            timestamp=time.time(),
            tool_name=tool_name,
            context=context,
            success=success,
            response_time=response_time,
            token_count=token_count,
            user_query=user_query,
            session_id=session_id,
        )
        self.log_tool_usage(entry)

    def analyze_usage(self, hours: int = 24) -> dict[str, UsageSummary]:
        """Analyze usage patterns and provide recommendations."""
        cutoff_time = time.time() - (hours * 3600)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT
                    tool_name,
                    COUNT(*) as usage_count,
                    AVG(CASE WHEN success = 1 THEN 1.0 ELSE 0.0 END) as success_rate,
                    AVG(response_time) as avg_response_time,
                    SUM(token_count) as total_tokens,
                    MAX(timestamp) as last_used
                FROM tool_usage
                WHERE timestamp >= ?
                GROUP BY tool_name
                ORDER BY usage_count DESC
            """,
                (cutoff_time,),
            )

            results = {}
            for row in cursor.fetchall():
                tool_name, usage_count, success_rate, avg_response_time, total_tokens, last_used = row

                recommendation = self._get_recommendation(
                    tool_name,
                    usage_count,
                    success_rate,
                    avg_response_time,
                )

                results[tool_name] = UsageSummary(
                    usage_count=usage_count,
                    success_rate=success_rate or 0.0,
                    avg_response_time=avg_response_time or 0.0,
                    total_tokens=total_tokens or 0,
                    last_used=last_used or 0.0,
                    recommendation=recommendation,
                )

        return results

    def _get_recommendation(self, tool: str, count: int, rate: float, response_time: float) -> str:
        """Get usage recommendation based on patterns."""
        tool_lower = tool.lower()

        if "sequential" in tool_lower and count < 5:
            return "INCREASE: Sequential thinking underutilized"
        elif rate < 0.7:
            return "REVIEW: Low success rate suggests tool mismatch"
        elif response_time > 10.0:
            return "OPTIMIZE: High response time may indicate performance issues"
        elif count > 50:
            return "MONITOR: High usage - ensure proper integration"
        else:
            return "MAINTAIN: Usage patterns look good"

    def get_sequential_thinking_metrics(self) -> dict[str, Any]:
        """Get specific metrics for sequential thinking usage."""
        with sqlite3.connect(self.db_path) as conn:
            # Sequential thinking specific metrics
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) as total_usage,
                    AVG(CASE WHEN success = 1 THEN 1.0 ELSE 0.0 END) as success_rate,
                    AVG(response_time) as avg_response_time,
                    SUM(token_count) as total_tokens,
                    COUNT(DISTINCT session_id) as unique_sessions
                FROM tool_usage
                WHERE tool_name LIKE '%sequential%'
                AND timestamp >= ?
            """,
                (time.time() - (24 * 3600),),
            )

            row = cursor.fetchone()
            if row:
                total_usage, success_rate, avg_response_time, total_tokens, unique_sessions = row
                return {
                    "total_usage": total_usage or 0,
                    "success_rate": success_rate or 0.0,
                    "avg_response_time": avg_response_time or 0.0,
                    "total_tokens": total_tokens or 0,
                    "unique_sessions": unique_sessions or 0,
                }

        return {
            "total_usage": 0,
            "success_rate": 0.0,
            "avg_response_time": 0.0,
            "total_tokens": 0,
            "unique_sessions": 0,
        }

    def generate_report(self, hours: int = 24) -> str:
        """Generate comprehensive usage report."""
        analysis = self.analyze_usage(hours)
        seq_metrics = self.get_sequential_thinking_metrics()

        report = f"""
# MCP Usage Report (Last {hours} hours)
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Sequential Thinking Metrics
- **Total Usage**: {seq_metrics["total_usage"]}
- **Success Rate**: {seq_metrics["success_rate"]:.2%}
- **Avg Response Time**: {seq_metrics["avg_response_time"]:.2f}s
- **Total Tokens**: {seq_metrics["total_tokens"]:,}
- **Unique Sessions**: {seq_metrics["unique_sessions"]}

## Tool Usage Analysis
"""

        for tool_name, summary in analysis.items():
            report += f"""
### {tool_name}
- **Usage Count**: {summary.usage_count}
- **Success Rate**: {summary.success_rate:.2%}
- **Avg Response Time**: {summary.avg_response_time:.2f}s
- **Total Tokens**: {summary.total_tokens:,}
- **Last Used**: {datetime.fromtimestamp(summary.last_used).strftime("%Y-%m-%d %H:%M:%S")}
- **Recommendation**: {summary.recommendation}
"""

        return report

    def export_usage_data(self, output_path: Path, hours: int = 24):
        """Export usage data to JSON for analysis."""
        cutoff_time = time.time() - (hours * 3600)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM tool_usage
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            """,
                (cutoff_time,),
            )

            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            data = []
            for row in rows:
                entry = dict(zip(columns, row))
                # Convert timestamp to readable format
                entry["timestamp_readable"] = datetime.fromtimestamp(entry["timestamp"]).isoformat()
                data.append(entry)

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Usage data exported to: {output_path}")


def main():
    """Main function for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="MCP Usage Tracker")
    parser.add_argument("--report", action="store_true", help="Generate usage report")
    parser.add_argument("--export", type=Path, help="Export usage data to JSON")
    parser.add_argument("--hours", type=int, default=24, help="Hours of data to analyze")
    parser.add_argument(
        "--log", nargs=5, help="Log usage: tool_name context success response_time token_count"
    )
    parser.add_argument("--db", type=Path, help="Database path")

    args = parser.parse_args()

    tracker = MCPUsageTracker(args.db)

    if args.log:
        tool_name, context, success_str, response_time_str, token_count_str = args.log
        success = success_str.lower() in ["true", "1", "yes"]
        response_time = float(response_time_str)
        token_count = int(token_count_str)

        tracker.log_simple_usage(tool_name, context, success, response_time, token_count)
        print(f"Logged usage for {tool_name}")

    elif args.report:
        report = tracker.generate_report(args.hours)
        print(report)

    elif args.export:
        tracker.export_usage_data(args.export, args.hours)

    else:
        # Default: show summary
        analysis = tracker.analyze_usage(args.hours)
        seq_metrics = tracker.get_sequential_thinking_metrics()

        print(f"MCP Usage Summary (Last {args.hours} hours)")
        print("=" * 50)
        print(f"Sequential Thinking Usage: {seq_metrics['total_usage']}")
        print(f"Sequential Thinking Success Rate: {seq_metrics['success_rate']:.2%}")
        print("\nTop Tools:")
        for tool_name, summary in list(analysis.items())[:5]:
            print(f"  {tool_name}: {summary.usage_count} uses ({summary.success_rate:.2%} success)")


if __name__ == "__main__":
    main()

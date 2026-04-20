#!/usr/bin/env python3
"""ADG Health Monitor - CLI tool for quick ADG health checks.

Provides real-time visibility into ADG status including node/edge counts,
layer distribution, and violation summaries. Works with SQLite directly
(no Redis required).

Usage:
    python -m infrastructure.adg_health
    python -m infrastructure.adg_health --adg <path_to_sqlite>
    python -m infrastructure.adg_health --format json
    python -m infrastructure.adg_health --format markdown
"""

import argparse
import glob
import json
import logging
import os
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class HealthMetrics:
    """Container for ADG health metrics."""

    adg_path: str
    timestamp: str
    total_nodes: int = 0
    total_edges: int = 0
    module_count: int = 0
    symbol_count: int = 0
    layer_distribution: dict[str, int] = field(default_factory=dict)
    violation_count: int = 0
    violation_by_type: dict[str, int] = field(default_factory=dict)


def find_latest_adg(repo_root: Path | None = None) -> Path | None:
    """Find the most recent ADG SQLite file.

    Args:
        repo_root: Repository root path. Defaults to current working directory.

    Returns:
        Path to latest ADG SQLite file, or None if not found.
    """
    if repo_root is None:
        repo_root = Path.cwd()

    adg_dir = repo_root / "artifacts" / "adg"
    if not adg_dir.exists():
        logger.warning(f"ADG directory not found: {adg_dir}")
        return None

    pattern = str(adg_dir / "adg_indexed_*.sqlite")
    sqlite_files = glob.glob(pattern)

    if not sqlite_files:
        logger.warning(f"No ADG SQLite files found in {adg_dir}")
        return None

    # Get most recent by modification time
    latest = max(sqlite_files, key=os.path.getmtime)
    return Path(latest)


def parse_adg_timestamp(adg_path: Path) -> str:
    """Extract timestamp from ADG filename.

    Args:
        adg_path: Path to ADG SQLite file.

    Returns:
        Formatted timestamp string.
    """
    # Format: adg_indexed_MMDDYYYY_HHMM.sqlite
    stem = adg_path.stem
    if "_" in stem:
        parts = stem.split("_")
        if len(parts) >= 3:
            date_part = parts[2]  # MMDDYYYY
            time_part = parts[3] if len(parts) > 3 else "0000"  # HHMM
            try:
                dt = datetime.strptime(f"{date_part}_{time_part}", "%m%d%Y_%H%M")
                return dt.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                pass
    return "unknown"


def query_health_metrics(conn: sqlite3.Connection, adg_path: Path) -> HealthMetrics:
    """Query health metrics from ADG SQLite.

    Args:
        conn: SQLite connection.
        adg_path: Path to ADG file (for metadata).

    Returns:
        HealthMetrics object with all metrics populated.
    """
    metrics = HealthMetrics(
        adg_path=str(adg_path),
        timestamp=parse_adg_timestamp(adg_path),
    )

    cursor = conn.cursor()

    # Total nodes
    cursor.execute("SELECT COUNT(*) FROM nodes")
    metrics.total_nodes = cursor.fetchone()[0]

    # Total edges
    cursor.execute("SELECT COUNT(*) FROM edges")
    metrics.total_edges = cursor.fetchone()[0]

    # Module count
    cursor.execute("SELECT COUNT(*) FROM nodes WHERE entity_type = 'module'")
    metrics.module_count = cursor.fetchone()[0]

    # Symbol count
    cursor.execute("SELECT COUNT(*) FROM nodes WHERE entity_type = 'symbol'")
    metrics.symbol_count = cursor.fetchone()[0]

    # Layer distribution
    cursor.execute("SELECT layer, COUNT(*) FROM nodes WHERE entity_type = 'module' GROUP BY layer")
    metrics.layer_distribution = {row[0]: row[1] for row in cursor.fetchall()}

    # Violation count
    cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type = 'violates'")
    metrics.violation_count = cursor.fetchone()[0]

    # Violations by type
    cursor.execute("SELECT symbol, COUNT(*) FROM edges WHERE relation_type = 'violates' GROUP BY symbol")
    metrics.violation_by_type = {row[0]: row[1] for row in cursor.fetchall()}

    return metrics


def format_table(metrics: HealthMetrics) -> str:
    """Format metrics as ASCII table.

    Args:
        metrics: HealthMetrics object.

    Returns:
        Formatted table string.
    """
    lines = []
    lines.append("=" * 60)
    lines.append("ADG HEALTH REPORT")
    lines.append("=" * 60)
    lines.append(f"ADG File:    {metrics.adg_path}")
    lines.append(f"Timestamp:   {metrics.timestamp}")
    lines.append("-" * 60)
    lines.append(f"Total Nodes: {metrics.total_nodes:,}")
    lines.append(f"Total Edges: {metrics.total_edges:,}")
    lines.append(f"Modules:     {metrics.module_count:,}")
    lines.append(f"Symbols:     {metrics.symbol_count:,}")
    lines.append("-" * 60)
    lines.append("LAYER DISTRIBUTION")
    lines.append("-" * 60)

    # Sort layers by count descending
    sorted_layers = sorted(metrics.layer_distribution.items(), key=lambda x: x[1], reverse=True)
    for layer, count in sorted_layers:
        lines.append(f"  {layer:15} {count:8,}")

    lines.append("-" * 60)
    lines.append(f"VIOLATIONS:  {metrics.violation_count:,}")
    lines.append("-" * 60)

    # Show top violation types
    if metrics.violation_by_type:
        sorted_violations = sorted(metrics.violation_by_type.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]  # Top 10
        for vtype, count in sorted_violations:
            lines.append(f"  {vtype:25} {count:8,}")

    lines.append("=" * 60)
    return "\n".join(lines)


def format_json(metrics: HealthMetrics) -> str:
    """Format metrics as JSON.

    Args:
        metrics: HealthMetrics object.

    Returns:
        JSON string.
    """
    data = {
        "adg_path": metrics.adg_path,
        "timestamp": metrics.timestamp,
        "total_nodes": metrics.total_nodes,
        "total_edges": metrics.total_edges,
        "module_count": metrics.module_count,
        "symbol_count": metrics.symbol_count,
        "layer_distribution": metrics.layer_distribution,
        "violation_count": metrics.violation_count,
        "violation_by_type": metrics.violation_by_type,
    }
    return json.dumps(data, indent=2)


def format_markdown(metrics: HealthMetrics) -> str:
    """Format metrics as Markdown.

    Args:
        metrics: HealthMetrics object.

    Returns:
        Markdown string.
    """
    lines = []
    lines.append("# ADG Health Report")
    lines.append("")
    lines.append(f"**ADG File:** `{metrics.adg_path}`")
    lines.append(f"**Timestamp:** {metrics.timestamp}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Nodes | {metrics.total_nodes:,} |")
    lines.append(f"| Total Edges | {metrics.total_edges:,} |")
    lines.append(f"| Modules | {metrics.module_count:,} |")
    lines.append(f"| Symbols | {metrics.symbol_count:,} |")
    lines.append(f"| Violations | {metrics.violation_count:,} |")
    lines.append("")
    lines.append("## Layer Distribution")
    lines.append("")
    lines.append("| Layer | Count |")
    lines.append("|-------|-------|")

    sorted_layers = sorted(metrics.layer_distribution.items(), key=lambda x: x[1], reverse=True)
    for layer, count in sorted_layers:
        lines.append(f"| {layer} | {count:,} |")

    if metrics.violation_by_type:
        lines.append("")
        lines.append("## Violations by Type")
        lines.append("")
        lines.append("| Type | Count |")
        lines.append("|------|-------|")
        sorted_violations = sorted(metrics.violation_by_type.items(), key=lambda x: x[1], reverse=True)[:10]
        for vtype, count in sorted_violations:
            lines.append(f"| {vtype} | {count:,} |")

    return "\n".join(lines)


def self_test() -> bool:
    """Run self-test to verify functionality.

    Returns:
        True if all tests pass.
    """
    logger.info("Running self-test...")

    # Test 1: Can we find latest ADG?
    latest = find_latest_adg()
    if latest:
        logger.info(f"✓ Found latest ADG: {latest}")
    else:
        logger.warning("✗ No ADG found (this is OK if ADG hasn't been generated)")

    # Test 2: Can we parse timestamps?
    test_path = Path("adg_indexed_04032026_2045.sqlite")
    ts = parse_adg_timestamp(test_path)
    if ts == "2026-04-03 20:45":
        logger.info("✓ Timestamp parsing works")
    else:
        logger.error(f"✗ Timestamp parsing failed: got {ts}")
        return False

    logger.info("Self-test complete")
    return True


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success).
    """
    parser = argparse.ArgumentParser(
        description="ADG Health Monitor - Quick health checks for Architecture Dependency Graph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m infrastructure.adg_health
  python -m infrastructure.adg_health --adg artifacts/adg/adg_indexed_04032026_2045.sqlite
  python -m infrastructure.adg_health --format json
        """,
    )

    parser.add_argument(
        "--adg",
        type=str,
        help="Path to ADG SQLite file (auto-detects if not specified)",
    )

    parser.add_argument(
        "--format",
        choices=["table", "json", "markdown"],
        default="table",
        help="Output format (default: table)",
    )

    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run self-test and exit",
    )

    parser.add_argument(
        "--repo-root",
        type=str,
        help="Repository root path (default: current directory)",
    )

    args = parser.parse_args()

    if args.self_test:
        return 0 if self_test() else 1

    # Determine ADG path
    if args.adg:
        adg_path: Path | None = Path(args.adg)
    else:
        repo_root = Path(args.repo_root) if args.repo_root else None
        adg_path = find_latest_adg(repo_root)

    if not adg_path:
        logger.error("No ADG SQLite file found. Run with --adg to specify path.")
        logger.error("Searched: artifacts/adg/adg_indexed_*.sqlite")
        return 1

    if not adg_path.exists():
        logger.error(f"ADG file not found: {adg_path}")
        return 1

    try:
        conn = sqlite3.connect(str(adg_path))
        metrics = query_health_metrics(conn, adg_path)
        conn.close()

        # Output based on format
        if args.format == "json":
            print(format_json(metrics))
        elif args.format == "markdown":
            print(format_markdown(metrics))
        else:
            print(format_table(metrics))

        return 0

    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")
        return 1
    except (OSError, ValueError, TypeError, AttributeError, KeyError) as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

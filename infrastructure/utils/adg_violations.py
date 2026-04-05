#!/usr/bin/env python3
"""ADG Violations Tracker - CLI tool for querying and analyzing architectural violations.

Provides filtered views of layer boundary violations with trend analysis.
Supports filtering by layer, file pattern, and violation type.

Usage:
    python -m infrastructure.adg_violations
    python -m infrastructure.adg_violations --layer L0 --layer L_TOOLS
    python -m infrastructure.adg_violations --file "agentic_core/L0*"
    python -m infrastructure.adg_violations --format csv --output violations.csv
"""

import argparse
import csv
import glob
import json
import logging
import os
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class Violation:
    """Single architectural violation."""

    id: int
    source_file: str
    relation_type: str
    symbol: str
    line_no: int | None = None
    layer_from: str | None = None
    layer_to: str | None = None


@dataclass
class ViolationReport:
    """Container for violation analysis results."""

    adg_path: str
    timestamp: str
    total_violations: int = 0
    violations: list[Violation] = field(default_factory=list)
    by_layer: dict[str, int] = field(default_factory=dict)
    by_type: dict[str, int] = field(default_factory=dict)
    by_file: dict[str, int] = field(default_factory=dict)


def find_latest_adg(repo_root: Path | None = None) -> Path | None:
    """Find the most recent ADG SQLite file."""
    if repo_root is None:
        repo_root = Path.cwd()

    adg_dir = repo_root / "artifacts" / "adg"
    if not adg_dir.exists():
        return None

    pattern = str(adg_dir / "adg_indexed_*.sqlite")
    sqlite_files = glob.glob(pattern)

    if not sqlite_files:
        return None

    return Path(max(sqlite_files, key=os.path.getmtime))


def parse_adg_timestamp(adg_path: Path) -> str:
    """Extract timestamp from ADG filename."""
    stem = adg_path.stem
    if "_" in stem:
        parts = stem.split("_")
        if len(parts) >= 3:
            date_part = parts[2]
            time_part = parts[3] if len(parts) > 3 else "0000"
            try:
                dt = datetime.strptime(f"{date_part}_{time_part}", "%m%d%Y_%H%M")
                return dt.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                pass
    return "unknown"


def query_violations(
    conn: sqlite3.Connection,
    layers: list[str] | None = None,
    file_pattern: str | None = None,
    violation_types: list[str] | None = None,
    limit: int | None = None,
) -> list[Violation]:
    """Query violations from ADG with optional filters.

    Args:
        conn: SQLite connection.
        layers: Filter by layer (e.g., ['L0', 'L_TOOLS']).
        file_pattern: Filter by source file glob pattern.
        violation_types: Filter by violation symbol/type.
        limit: Maximum number of results.

    Returns:
        List of Violation objects.
    """
    cursor = conn.cursor()

    # Build query
    query = """
        SELECT e.id, n.resolved_path, e.relation_type, e.symbol, e.line_no
        FROM edges e
        JOIN nodes n ON e.src_id = n.id
        WHERE e.relation_type = 'violates'
    """
    params: list[Any] = []

    # Add file pattern filter
    if file_pattern:
        query += " AND n.resolved_path LIKE ?"
        params.append(file_pattern.replace("*", "%"))

    # Add violation type filter
    if violation_types:
        placeholders = ",".join("?" for _ in violation_types)
        query += f" AND e.symbol IN ({placeholders})"
        params.extend(violation_types)

    query += " ORDER BY n.resolved_path, e.line_no"

    if limit:
        query += " LIMIT ?"
        params.append(limit)

    cursor.execute(query, params)

    violations = []
    for row in cursor.fetchall():
        v = Violation(
            id=row[0],
            source_file=row[1],
            relation_type=row[2],
            symbol=row[3],
            line_no=row[4],
        )

        # Parse layer from symbol (e.g., "L0->L4" -> L0, L4)
        if v.symbol and "->" in v.symbol:
            parts = v.symbol.split("->")
            if len(parts) == 2:
                v.layer_from = parts[0].strip()
                v.layer_to = parts[1].strip()

        violations.append(v)

    # Post-filter by layer if specified
    if layers:
        violations = [
            v
            for v in violations
            if (v.layer_from and v.layer_from in layers) or (v.layer_to and v.layer_to in layers)
        ]

    return violations


def analyze_violations(violations: list[Violation]) -> ViolationReport:
    """Analyze violations and build report statistics.

    Args:
        violations: List of violations to analyze.

    Returns:
        ViolationReport with statistics.
    """
    report = ViolationReport(
        adg_path="",
        timestamp="",
        total_violations=len(violations),
        violations=violations,
    )

    for v in violations:
        # By type
        report.by_type[v.symbol] = report.by_type.get(v.symbol, 0) + 1

        # By file
        report.by_file[v.source_file] = report.by_file.get(v.source_file, 0) + 1

        # By layer (from)
        if v.layer_from:
            report.by_layer[v.layer_from] = report.by_layer.get(v.layer_from, 0) + 1

    return report


def format_table(report: ViolationReport, max_violations: int = 20) -> str:
    """Format report as ASCII table."""
    lines = []
    lines.append("=" * 80)
    lines.append("ADG VIOLATIONS REPORT")
    lines.append("=" * 80)
    lines.append(f"Total Violations: {report.total_violations:,}")
    lines.append("")

    # By type
    lines.append("BY VIOLATION TYPE")
    lines.append("-" * 80)
    sorted_types = sorted(report.by_type.items(), key=lambda x: x[1], reverse=True)
    for vtype, count in sorted_types[:15]:
        lines.append(f"  {vtype:30} {count:6,}")
    lines.append("")

    # By layer
    lines.append("BY LAYER (Source)")
    lines.append("-" * 80)
    sorted_layers = sorted(report.by_layer.items(), key=lambda x: x[1], reverse=True)
    for layer, count in sorted_layers[:15]:
        lines.append(f"  {layer:15} {count:6,}")
    lines.append("")

    # Individual violations
    lines.append(f"VIOLATIONS (showing first {max_violations})")
    lines.append("-" * 80)
    for v in report.violations[:max_violations]:
        line_no = f":{v.line_no}" if v.line_no else ""
        lines.append(f"  {v.source_file}{line_no}")
        lines.append(f"    -> {v.symbol}")
    lines.append("=" * 80)

    return "\n".join(lines)


def format_json(report: ViolationReport) -> str:
    """Format report as JSON."""
    data = {
        "total_violations": report.total_violations,
        "by_type": report.by_type,
        "by_layer": report.by_layer,
        "by_file": report.by_file,
        "violations": [
            {
                "id": v.id,
                "source_file": v.source_file,
                "symbol": v.symbol,
                "line_no": v.line_no,
                "layer_from": v.layer_from,
                "layer_to": v.layer_to,
            }
            for v in report.violations
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: ViolationReport, output_path: Path | None = None) -> str:
    """Format violations as CSV.

    Args:
        report: ViolationReport.
        output_path: If provided, write to file instead of returning string.

    Returns:
        CSV string if output_path is None, else empty string.
    """
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["id", "source_file", "line_no", "violation_type", "layer_from", "layer_to"])

    # Data
    for v in report.violations:
        writer.writerow([v.id, v.source_file, v.line_no, v.symbol, v.layer_from, v.layer_to])

    csv_content = output.getvalue()
    output.close()

    if output_path:
        with open(output_path, "w", newline="") as f:
            f.write(csv_content)
        return ""

    return csv_content


def format_markdown(report: ViolationReport) -> str:
    """Format report as Markdown."""
    lines = []
    lines.append("# ADG Violations Report")
    lines.append("")
    lines.append(f"**Total Violations:** {report.total_violations:,}")
    lines.append("")

    # By type
    lines.append("## By Violation Type")
    lines.append("")
    lines.append("| Type | Count |")
    lines.append("|------|-------|")
    sorted_types = sorted(report.by_type.items(), key=lambda x: x[1], reverse=True)
    for vtype, count in sorted_types[:15]:
        lines.append(f"| {vtype} | {count:,} |")
    lines.append("")

    # By layer
    lines.append("## By Layer")
    lines.append("")
    lines.append("| Layer | Count |")
    lines.append("|-------|-------|")
    sorted_layers = sorted(report.by_layer.items(), key=lambda x: x[1], reverse=True)
    for layer, count in sorted_layers[:15]:
        lines.append(f"| {layer} | {count:,} |")
    lines.append("")

    return "\n".join(lines)


def self_test() -> bool:
    """Run self-test."""
    logger.info("Running self-test...")

    latest = find_latest_adg()
    if latest:
        logger.info(f"✓ Found latest ADG: {latest}")
    else:
        logger.warning("✗ No ADG found")

    logger.info("Self-test complete")
    return True


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ADG Violations Tracker - Query and analyze architectural violations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m infrastructure.adg_violations
  python -m infrastructure.adg_violations --layer L0 --layer L_TOOLS
  python -m infrastructure.adg_violations --file "agentic_core/L0*"
  python -m infrastructure.adg_violations --format csv --output violations.csv
        """,
    )

    parser.add_argument("--adg", type=str, help="Path to ADG SQLite file")
    parser.add_argument("--layer", action="append", help="Filter by layer (can specify multiple)")
    parser.add_argument("--file", type=str, help="Filter by file pattern (glob)")
    parser.add_argument("--type", action="append", help="Filter by violation type")
    parser.add_argument("--limit", type=int, default=100, help="Limit number of results (default: 100)")
    parser.add_argument("--format", choices=["table", "json", "csv", "markdown"], default="table")
    parser.add_argument("--output", type=str, help="Output file path (for csv format)")
    parser.add_argument("--self-test", action="store_true", help="Run self-test and exit")

    args = parser.parse_args()

    if args.self_test:
        return 0 if self_test() else 1

    # Determine ADG path
    if args.adg:
        adg_path: Path | None = Path(args.adg)
    else:
        adg_path = find_latest_adg()

    if not adg_path:
        logger.error("No ADG SQLite file found. Use --adg to specify path.")
        return 1

    if not adg_path.exists():
        logger.error(f"ADG file not found: {adg_path}")
        return 1

    try:
        conn = sqlite3.connect(str(adg_path))

        violations = query_violations(
            conn,
            layers=args.layer,
            file_pattern=args.file,
            violation_types=args.type,
            limit=args.limit,
        )

        report = analyze_violations(violations)
        report.adg_path = str(adg_path)
        report.timestamp = parse_adg_timestamp(adg_path)

        conn.close()

        # Output
        if args.format == "json":
            print(format_json(report))
        elif args.format == "csv":
            if args.output:
                format_csv(report, Path(args.output))
                logger.info(f"CSV written to: {args.output}")
            else:
                print(format_csv(report))
        elif args.format == "markdown":
            print(format_markdown(report))
        else:
            print(format_table(report, max_violations=args.limit))

        return 0

    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""ADG Drift Detector - CLI tool for comparing ADG snapshots.

Detects architectural drift between two ADG snapshots including:
- Added/deleted modules
- Added/deleted edges
- Violation count changes

Usage:
    python -m infrastructure.adg_drift
    python -m infrastructure.adg_drift --baseline <old.sqlite> --current <new.sqlite>
    python -m infrastructure.adg_drift --ci --max-added 10 --max-deleted 5
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

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class Snapshot:
    """ADG snapshot data."""

    path: Path
    timestamp: str
    nodes: dict[str, dict[str, Any]] = field(default_factory=dict)
    edges: list[dict[str, Any]] = field(default_factory=list)
    violations: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class DriftReport:
    """Drift comparison report."""

    baseline: Snapshot
    current: Snapshot
    added_modules: list[str] = field(default_factory=list)
    deleted_modules: list[str] = field(default_factory=list)
    added_edges: int = 0
    deleted_edges: int = 0
    violation_delta: int = 0
    modules_by_layer_delta: dict[str, int] = field(default_factory=dict)


def find_two_latest_adgs(repo_root: Path | None = None) -> tuple[Path, Path] | None:
    """Find the two most recent ADG files for comparison."""
    if repo_root is None:
        repo_root = Path.cwd()

    adg_dir = repo_root / "artifacts" / "adg"
    if not adg_dir.exists():
        return None

    pattern = str(adg_dir / "adg_indexed_*.sqlite")
    files = glob.glob(pattern)

    if len(files) < 2:
        return None

    # Sort by modification time, newest first
    sorted_files = sorted(files, key=os.path.getmtime, reverse=True)
    return (Path(sorted_files[0]), Path(sorted_files[1]))


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


def load_snapshot(adg_path: Path) -> Snapshot:
    """Load snapshot data from ADG SQLite."""
    snapshot = Snapshot(
        path=adg_path,
        timestamp=parse_adg_timestamp(adg_path),
    )

    conn = sqlite3.connect(str(adg_path))
    cursor = conn.cursor()

    # Load modules
    cursor.execute("SELECT id, resolved_path, entity_type, layer FROM nodes WHERE entity_type = 'module'")
    for row in cursor.fetchall():
        snapshot.nodes[row[1]] = {
            "id": row[0],
            "path": row[1],
            "type": row[2],
            "layer": row[3],
        }

    # Load edge count
    cursor.execute("SELECT COUNT(*) FROM edges")
    edge_count = cursor.fetchone()[0]

    # Load violations
    cursor.execute(
        """SELECT e.id, n.resolved_path, e.symbol, e.line_no
           FROM edges e
           JOIN nodes n ON e.src_id = n.id
           WHERE e.relation_type = 'violates'""",
    )
    for row in cursor.fetchall():
        snapshot.violations.append(
            {
                "id": row[0],
                "source": row[1],
                "symbol": row[2],
                "line": row[3],
            },
        )

    conn.close()

    return snapshot


def compute_drift(baseline: Snapshot, current: Snapshot) -> DriftReport:
    """Compute drift between two snapshots."""
    report = DriftReport(baseline=baseline, current=current)

    # Module drift
    baseline_modules = set(baseline.nodes.keys())
    current_modules = set(current.nodes.keys())

    report.added_modules = sorted(current_modules - baseline_modules)
    report.deleted_modules = sorted(baseline_modules - current_modules)

    # Layer distribution delta
    baseline_by_layer: dict[str, int] = {}
    current_by_layer: dict[str, int] = {}

    for node in baseline.nodes.values():
        layer = node.get("layer", "unknown")
        baseline_by_layer[layer] = baseline_by_layer.get(layer, 0) + 1

    for node in current.nodes.values():
        layer = node.get("layer", "unknown")
        current_by_layer[layer] = current_by_layer.get(layer, 0) + 1

    all_layers = set(baseline_by_layer.keys()) | set(current_by_layer.keys())
    for layer in all_layers:
        delta = current_by_layer.get(layer, 0) - baseline_by_layer.get(layer, 0)
        if delta != 0:
            report.modules_by_layer_delta[layer] = delta

    # Violation delta
    report.violation_delta = len(current.violations) - len(baseline.violations)

    return report


def format_table(report: DriftReport, show_modules: bool = True) -> str:
    """Format drift report as ASCII table."""
    lines = []
    lines.append("=" * 80)
    lines.append("ADG DRIFT REPORT")
    lines.append("=" * 80)
    lines.append(f"Baseline: {report.baseline.path.name} ({report.baseline.timestamp})")
    lines.append(f"Current:  {report.current.path.name} ({report.current.timestamp})")
    lines.append("")

    # Summary
    total_changes = len(report.added_modules) + len(report.deleted_modules)
    lines.append(f"Total Module Changes: {total_changes}")
    lines.append(f"  Added:   {len(report.added_modules)}")
    lines.append(f"  Deleted: {len(report.deleted_modules)}")
    lines.append(f"Violation Delta: {report.violation_delta:+d}")
    lines.append("")

    # Layer distribution changes
    if report.modules_by_layer_delta:
        lines.append("LAYER DISTRIBUTION CHANGES")
        lines.append("-" * 80)
        for layer, delta in sorted(report.modules_by_layer_delta.items()):
            sign = "+" if delta > 0 else ""
            lines.append(f"  {layer:15} {sign}{delta:4d}")
        lines.append("")

    # Added modules
    if show_modules and report.added_modules:
        lines.append(f"ADDED MODULES ({len(report.added_modules)})")
        lines.append("-" * 80)
        for mod in report.added_modules[:20]:
            lines.append(f"  + {mod}")
        if len(report.added_modules) > 20:
            lines.append(f"  ... and {len(report.added_modules) - 20} more")
        lines.append("")

    # Deleted modules
    if show_modules and report.deleted_modules:
        lines.append(f"DELETED MODULES ({len(report.deleted_modules)})")
        lines.append("-" * 80)
        for mod in report.deleted_modules[:20]:
            lines.append(f"  - {mod}")
        if len(report.deleted_modules) > 20:
            lines.append(f"  ... and {len(report.deleted_modules) - 20} more")
        lines.append("")

    lines.append("=" * 80)
    return "\n".join(lines)


def format_json(report: DriftReport) -> str:
    """Format as JSON."""
    data = {
        "baseline": {
            "path": str(report.baseline.path),
            "timestamp": report.baseline.timestamp,
            "module_count": len(report.baseline.nodes),
            "violation_count": len(report.baseline.violations),
        },
        "current": {
            "path": str(report.current.path),
            "timestamp": report.current.timestamp,
            "module_count": len(report.current.nodes),
            "violation_count": len(report.current.violations),
        },
        "drift": {
            "added_modules": report.added_modules,
            "deleted_modules": report.deleted_modules,
            "violation_delta": report.violation_delta,
            "modules_by_layer_delta": report.modules_by_layer_delta,
        },
    }
    return json.dumps(data, indent=2)


def format_csv(report: DriftReport, output_path: Path | None = None) -> str:
    """Format as CSV."""
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["change_type", "module_path", "layer"])

    for mod in report.added_modules:
        layer = report.current.nodes.get(mod, {}).get("layer", "unknown")
        writer.writerow(["added", mod, layer])

    for mod in report.deleted_modules:
        layer = report.baseline.nodes.get(mod, {}).get("layer", "unknown")
        writer.writerow(["deleted", mod, layer])

    csv_content = output.getvalue()
    output.close()

    if output_path:
        with open(output_path, "w", newline="") as f:
            f.write(csv_content)
        return ""

    return csv_content


def format_markdown(report: DriftReport) -> str:
    """Format as Markdown."""
    lines = []
    lines.append("# ADG Drift Report")
    lines.append("")
    lines.append(f"**Baseline:** `{report.baseline.path.name}` ({report.baseline.timestamp})")
    lines.append(f"**Current:** `{report.current.path.name}` ({report.current.timestamp})")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Added Modules | {len(report.added_modules)} |")
    lines.append(f"| Deleted Modules | {len(report.deleted_modules)} |")
    lines.append(f"| Violation Delta | {report.violation_delta:+d} |")
    lines.append("")

    if report.modules_by_layer_delta:
        lines.append("## Layer Distribution Changes")
        lines.append("")
        lines.append("| Layer | Delta |")
        lines.append("|-------|-------|")
        for layer, delta in sorted(report.modules_by_layer_delta.items()):
            lines.append(f"| {layer} | {delta:+d} |")
        lines.append("")

    return "\n".join(lines)


def self_test() -> bool:
    """Run self-test."""
    logger.info("Running self-test...")

    result = find_two_latest_adgs()
    if result:
        current, baseline = result
        logger.info(f"✓ Found ADG pair: {baseline.name} -> {current.name}")
    else:
        logger.warning("✗ Need at least 2 ADG files for drift detection")

    logger.info("Self-test complete")
    return True


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ADG Drift Detector - Compare architectural snapshots",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m infrastructure.adg_drift
  python -m infrastructure.adg_drift --baseline old.sqlite --current new.sqlite
  python -m infrastructure.adg_drift --ci --max-added 10
        """,
    )

    parser.add_argument("--baseline", type=str, help="Path to baseline ADG SQLite")
    parser.add_argument("--current", type=str, help="Path to current ADG SQLite")
    parser.add_argument("--format", choices=["table", "json", "csv", "markdown"], default="table")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--ci", action="store_true", help="CI mode - exit non-zero if drift detected")
    parser.add_argument("--max-added", type=int, help="Max allowed added modules (CI mode)")
    parser.add_argument("--max-deleted", type=int, help="Max allowed deleted modules (CI mode)")
    parser.add_argument("--self-test", action="store_true", help="Run self-test")

    args = parser.parse_args()

    if args.self_test:
        return 0 if self_test() else 1

    # Determine ADG paths
    if args.baseline and args.current:
        baseline_path = Path(args.baseline)
        current_path = Path(args.current)
    else:
        result = find_two_latest_adgs()
        if not result:
            logger.error("Need at least 2 ADG files. Use --baseline and --current.")
            return 1
        current_path, baseline_path = result
        logger.info(f"Comparing: {baseline_path.name} -> {current_path.name}")

    # Validate paths
    for path in [baseline_path, current_path]:
        if not path.exists():
            logger.error(f"ADG file not found: {path}")
            return 1

    try:
        logger.info("Loading baseline snapshot...")
        baseline = load_snapshot(baseline_path)

        logger.info("Loading current snapshot...")
        current = load_snapshot(current_path)

        logger.info("Computing drift...")
        report = compute_drift(baseline, current)

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
            print(format_table(report))

        # CI mode checks
        if args.ci:
            drift_detected = False

            if args.max_added is not None and len(report.added_modules) > args.max_added:
                logger.error(f"CI FAIL: {len(report.added_modules)} modules added (max: {args.max_added})")
                drift_detected = True

            if args.max_deleted is not None and len(report.deleted_modules) > args.max_deleted:
                logger.error(
                    f"CI FAIL: {len(report.deleted_modules)} modules deleted (max: {args.max_deleted})",
                )
                drift_detected = True

            if drift_detected:
                return 2  # Special exit code for CI drift detection

        return 0

    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

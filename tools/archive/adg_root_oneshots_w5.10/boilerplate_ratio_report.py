#!/usr/bin/env python3
"""
Boilerplate Ratio Dashboard

Generates per-layer metrics for boilerplate vs behavioral content.
Provides visibility into hollow file distribution across the codebase.
"""

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.L5_safety.validators.hollow_file_detector_validator import (
    BehavioralNodeCounter,
    HollowFileDetector,
)


@dataclass
class LayerStats:
    """Statistics for a single layer."""

    files: int = 0
    hollow: int = 0
    boilerplate_heavy: int = 0
    healthy: int = 0
    avg_ratio: float = 0.0
    min_ratio: float = 1.0
    max_ratio: float = 0.0
    median_ratio: float = 0.0
    total_lines: int = 0
    behavioral_nodes: int = 0
    boilerplate_nodes: int = 0


@dataclass
class RatioReport:
    """Complete boilerplate ratio report."""

    timestamp: str
    total_files: int
    layer_stats: dict[str, LayerStats] = field(default_factory=dict)
    file_details: list[dict] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)


class BoilerplateRatioAnalyzer:
    """Analyzes boilerplate ratios across the codebase."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.detector = HollowFileDetector()

    def infer_layer_from_path(self, file_path: Path) -> str:
        """Infer layer from file path."""
        path_str = str(file_path)

        # Map path patterns to layers
        if "L0_routing" in path_str:
            return "L0"
        elif "L1_reasoning" in path_str:
            return "L1"
        elif "L2_execution" in path_str:
            return "L2"
        elif "L3_orchestration" in path_str:
            return "L3"
        elif "L4_state" in path_str:
            return "L4"
        elif "L5_safety" in path_str:
            return "L5"
        elif "L6_observability" in path_str:
            return "L6"
        elif "apps" in path_str:
            return "APPS"
        elif "ops_scripts" in path_str:
            return "OPS"
        elif "tests" in path_str:
            return "TESTS"
        elif "tools" in path_str:
            return "TOOLS"
        else:
            return "UNKNOWN"

    def calculate_boilerplate_ratio(self, file_path: Path) -> tuple[float, dict]:
        """Calculate boilerplate ratio for a file."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return 1.0, {"error": "Cannot read file"}

        # Parse AST
        try:
            import ast

            tree = ast.parse(content)
        except SyntaxError:
            return 1.0, {"error": "Syntax error"}

        # Analyze with detector
        violations = self.detector.detect(file_path, tree)

        # Get node counts
        counter = BehavioralNodeCounter()
        counter.visit(tree)

        behavioral_nodes = counter.behavioral_functions + counter.behavioral_classes
        boilerplate_nodes = counter.import_statements + counter.boilerplate_statements
        total_nodes = behavioral_nodes + boilerplate_nodes

        # Calculate ratio
        if total_nodes == 0:
            ratio = 1.0  # Empty file is all boilerplate
        else:
            ratio = boilerplate_nodes / total_nodes

        # Determine classification
        if violations:
            classification = violations[0].metadata.get("classification", "healthy")
        else:
            classification = "healthy"

        metadata = {
            "behavioral_nodes": behavioral_nodes,
            "boilerplate_nodes": boilerplate_nodes,
            "total_nodes": total_nodes,
            "classification": classification,
            "lines": len(content.splitlines()),
            "violations": len(violations),
        }

        return ratio, metadata

    def scan_python_files(self) -> list[Path]:
        """Scan for all Python files in repository."""
        python_files = list(self.repo_root.rglob("*.py"))

        # Exclude common non-source directories
        python_files = [
            f
            for f in python_files
            if not any(part.startswith((".", "__")) for part in f.parts)
            and "site-packages" not in str(f)
            and ".git" not in str(f)
            and "node_modules" not in str(f)
        ]

        return python_files

    def generate_ratio_report(self) -> RatioReport:
        """Generate complete boilerplate ratio report."""
        import datetime

        # Scan all files
        python_files = self.scan_python_files()

        # Collect data by layer
        layer_data = defaultdict(list)
        file_details = []

        for file_path in python_files:
            ratio, metadata = self.calculate_boilerplate_ratio(file_path)
            layer = self.infer_layer_from_path(file_path)

            layer_data[layer].append((file_path, ratio, metadata))

            # Add file details
            file_details.append(
                {
                    "file": str(file_path.relative_to(self.repo_root)),
                    "layer": layer,
                    "ratio": ratio,
                    "classification": metadata.get("classification", "healthy"),
                    "behavioral_nodes": metadata.get("behavioral_nodes", 0),
                    "boilerplate_nodes": metadata.get("boilerplate_nodes", 0),
                    "lines": metadata.get("lines", 0),
                }
            )

        # Calculate layer statistics
        layer_stats = {}
        total_files = 0
        total_hollow = 0
        total_boilerplate_heavy = 0
        total_healthy = 0

        for layer, data in layer_data.items():
            if not data:
                continue

            ratios = [r for _, r, _ in data]

            # Count categories
            hollow = sum(1 for _, r, m in data if r == 1.0 or m.get("classification") == "hollow")
            boilerplate_heavy = sum(
                1 for _, r, m in data if r > 0.7 or m.get("classification") == "boilerplate_heavy"
            )
            healthy = sum(1 for _, r, m in data if r <= 0.7 and m.get("classification") == "healthy")

            # Calculate statistics
            avg_ratio = sum(ratios) / len(ratios)
            min_ratio = min(ratios)
            max_ratio = max(ratios)

            # Calculate median
            sorted_ratios = sorted(ratios)
            median_ratio = sorted_ratios[len(sorted_ratios) // 2]

            # Sum totals
            total_lines = sum(m.get("lines", 0) for _, _, m in data)
            behavioral_nodes = sum(m.get("behavioral_nodes", 0) for _, _, m in data)
            boilerplate_nodes = sum(m.get("boilerplate_nodes", 0) for _, _, m in data)

            layer_stats[layer] = LayerStats(
                files=len(data),
                hollow=hollow,
                boilerplate_heavy=boilerplate_heavy,
                healthy=healthy,
                avg_ratio=avg_ratio,
                min_ratio=min_ratio,
                max_ratio=max_ratio,
                median_ratio=median_ratio,
                total_lines=total_lines,
                behavioral_nodes=behavioral_nodes,
                boilerplate_nodes=boilerplate_nodes,
            )

            total_files += len(data)
            total_hollow += hollow
            total_boilerplate_heavy += boilerplate_heavy
            total_healthy += healthy

        # Create report
        report = RatioReport(
            timestamp=datetime.datetime.utcnow().isoformat(),
            total_files=total_files,
            layer_stats=layer_stats,
            file_details=file_details,
            summary={
                "total_files": total_files,
                "total_hollow": total_hollow,
                "total_boilerplate_heavy": total_boilerplate_heavy,
                "total_healthy": total_healthy,
                "overall_hollow_percentage": (total_hollow / total_files * 100) if total_files > 0 else 0,
                "overall_boilerplate_heavy_percentage": (total_boilerplate_heavy / total_files * 100)
                if total_files > 0
                else 0,
            },
        )

        return report

    def print_summary(self, report: RatioReport):
        """Print a human-readable summary."""
        print("📊 Boilerplate Ratio Report")
        print("=" * 50)
        print(f"Generated: {report.timestamp}")
        print(f"Total files: {report.total_files}")
        print()

        # Summary
        summary = report.summary
        print("📈 Overall Summary:")
        print(f"  Hollow files: {summary['total_hollow']} ({summary['overall_hollow_percentage']:.1f}%)")
        print(
            f"  Boilerplate-heavy: {summary['total_boilerplate_heavy']} ({summary['overall_boilerplate_heavy_percentage']:.1f}%)"
        )
        print(f"  Healthy: {summary['total_healthy']}")
        print()

        # Layer breakdown
        print("🏗️  Layer Breakdown:")
        for layer in sorted(report.layer_stats.keys()):
            stats = report.layer_stats[layer]
            hollow_pct = (stats.hollow / stats.files * 100) if stats.files > 0 else 0
            heavy_pct = (stats.boilerplate_heavy / stats.files * 100) if stats.files > 0 else 0

            print(f"  {layer}:")
            print(f"    Files: {stats.files}")
            print(f"    Hollow: {stats.hollow} ({hollow_pct:.1f}%)")
            print(f"    Heavy: {stats.boilerplate_heavy} ({heavy_pct:.1f}%)")
            print(f"    Avg ratio: {stats.avg_ratio:.3f}")
            print(f"    Median ratio: {stats.median_ratio:.3f}")
            print(f"    Range: {stats.min_ratio:.3f} - {stats.max_ratio:.3f}")
            print()

        # Worst offenders
        print("⚠️  Worst Offenders (Highest Boilerplate Ratio):")
        worst = sorted(report.file_details, key=lambda x: x["ratio"], reverse=True)[:10]
        for i, file_info in enumerate(worst, 1):
            print(f"  {i:2d}. {file_info['file']}")
            print(
                f"      Ratio: {file_info['ratio']:.3f} | Layer: {file_info['layer']} | Class: {file_info['classification']}"
            )

        print()

        # Healthiest files
        print("✅ Healthiest Files (Lowest Boilerplate Ratio):")
        healthiest = sorted(
            [f for f in report.file_details if f["behavioral_nodes"] > 0], key=lambda x: x["ratio"]
        )[:10]
        for i, file_info in enumerate(healthiest, 1):
            print(f"  {i:2d}. {file_info['file']}")
            print(
                f"      Ratio: {file_info['ratio']:.3f} | Layer: {file_info['layer']} | Behavioral: {file_info['behavioral_nodes']}"
            )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate boilerplate ratio report")
    parser.add_argument("--output", "-o", type=Path, help="Output JSON file")
    parser.add_argument("--repo", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--layer", help="Filter by specific layer")
    parser.add_argument("--threshold", type=float, default=0.7, help="Boilerplate-heavy threshold")

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = BoilerplateRatioAnalyzer(args.repo)

    # Generate report
    print("🔍 Analyzing boilerplate ratios...")
    report = analyzer.generate_ratio_report()

    # Filter by layer if requested
    if args.layer:
        if args.layer in report.layer_stats:
            filtered_stats = {args.layer: report.layer_stats[args.layer]}
            report.layer_stats = filtered_stats
            report.file_details = [f for f in report.file_details if f["layer"] == args.layer]
        else:
            print(f"❌ Layer '{args.layer}' not found")
            return 1

    # Print summary
    analyzer.print_summary(report)

    # Write output
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)

        output_data = {
            "timestamp": report.timestamp,
            "summary": report.summary,
            "layer_stats": {
                layer: {
                    "files": stats.files,
                    "hollow": stats.hollow,
                    "boilerplate_heavy": stats.boilerplate_heavy,
                    "healthy": stats.healthy,
                    "avg_ratio": stats.avg_ratio,
                    "min_ratio": stats.min_ratio,
                    "max_ratio": stats.max_ratio,
                    "median_ratio": stats.median_ratio,
                    "total_lines": stats.total_lines,
                    "behavioral_nodes": stats.behavioral_nodes,
                    "boilerplate_nodes": stats.boilerplate_nodes,
                }
                for layer, stats in report.layer_stats.items()
            },
            "file_details": report.file_details,
        }

        args.output.write_text(json.dumps(output_data, indent=2))
        print(f"\n💾 Report written to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

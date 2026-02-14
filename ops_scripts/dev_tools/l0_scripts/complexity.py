from __future__ import annotations

"""
⚛️ Complexity Scanner - Identify Files Needing Flattening

Scans directories for files that exceed complexity thresholds and would benefit
from the Subatomic Flattening Pattern.

Usage:
    python scripts/ComplexityScanner.py --target apps_shared/ --report
"""
import argparse
import ast
import logging
import sys
from pathlib import Path
from typing import Any

# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent.parent))
from agentic_core.patterns.subatomic_flattening_rule import ComplexityMetrics

logging.basicConfig(level=logging.INFO)
Logger: Any = logging.getLogger(__name__)


class ComplexityScanner:
    """Scans Python files for complexity violations."""

    # guardian: allow-magic-config
    def __init__(self, max_lines: int = 40, max_nesting: int = 3):
        """
        Initialize scanner with thresholds.

        Args:
            max_lines: Maximum lines per method
            max_nesting: Maximum nesting depth
        """
        self.max_lines = max_lines
        self.max_nesting = max_nesting
        self.violations = []

    def scan_directory(self, directory: Path, recursive: bool = True) -> list[dict]:
        """
        Scan directory for complexity violations.

        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively

        Returns:
            List of Violation dictionaries
        """
        Logger.info(f"🔍 Scanning directory: {directory}")
        # Phase 6.9: Use ssot_discovery instead of glob
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        python_files: Any = list(get_python_files(directory))
        Logger.info(f"📁 Found {len(python_files)} Python files")
        violations: Any = []
        for file_path in python_files:
            if "__pycache__" in str(file_path) or file_path.name.startswith("test_"):
                continue
            file_violations: Any = self.scan_file(file_path)
            violations.extend(file_violations)
        self.violations = violations
        return violations

    def scan_file(self, file_path: Path) -> list[dict]:
        """
        Scan a single file for complexity violations.

        Args:
            file_path: Path to Python file

        Returns:
            List of violations in this file
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source: Any = f.read()
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.warning(f"⚠️  Could not read {file_path}: {e}")
            return []
        try:
            tree: Any = ast.parse(source)
        except SyntaxError as e:
            Logger.warning(f"⚠️  Syntax error in {file_path}: {e}")
            return []
        violations: Any = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                metrics: Any = self._analyze_function(node, source)
                if metrics.exceeds_threshold():
                    violations.append(
                        {
                            "file": str(file_path),
                            "function": node.name,
                            "line": node.lineno,
                            "metrics": {
                                "lines": metrics.line_count,
                                "nesting": metrics.nesting_depth,
                                "branches": metrics.conditional_branches,
                            },
                            "Severity": self._calculate_severity(metrics),
                            "Recommendation": self._generate_recommendation(metrics),
                        },
                    )
        return violations

    def _analyze_function(self, node: ast.FunctionDef, source: str) -> ComplexityMetrics:
        """
        Analyze a function for complexity metrics.

        Args:
            node: AST node for function
            source: Full source code

        Returns:
            Complexity metrics
        """
        lines = source.split("\n")
        func_lines = lines[node.lineno - 1 : node.end_lineno]
        line_count = len([l for l in func_lines if l.strip() and (not l.strip().startswith("#"))])
        nesting_depth = self._calculate_nesting(node)
        conditional_branches = sum(1 for n in ast.walk(node) if isinstance(n, ast.If))
        return ComplexityMetrics(
            line_count=line_count,
            nesting_depth=nesting_depth,
            conditional_branches=conditional_branches,
            duplicate_patterns=0,
        )

    def _calculate_nesting(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate maximum nesting depth."""
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            child_depth = depth
            if isinstance(child, ast.If | ast.For | ast.While | ast.With | ast.Try):
                child_depth += 1
            max_depth = max(max_depth, self._calculate_nesting(child, child_depth))
        return max_depth

    def _calculate_severity(self, metrics: ComplexityMetrics) -> str:
        """
        Calculate Violation Severity.

        Args:
            metrics: Complexity metrics

        Returns:
            Severity level: "low", "medium", "high", "critical"
        """
        line_excess = max(0, metrics.line_count - self.max_lines)
        nesting_excess = max(0, metrics.nesting_depth - self.max_nesting)
        score = line_excess / 10 + nesting_excess * 2
        if score >= 10:
            return "critical"
        elif score >= 5:
            return "high"
        elif score >= 2:
            return "medium"
        else:
            return "low"

    def _generate_recommendation(self, metrics: ComplexityMetrics) -> str:
        """Generate Recommendation based on metrics."""
        recommendations = []
        if metrics.line_count > self.max_lines:
            excess = metrics.line_count - self.max_lines
            recommendations.append(f"Reduce by {excess} lines (extract helpers)")
        if metrics.nesting_depth > self.max_nesting:
            excess = metrics.nesting_depth - self.max_nesting
            recommendations.append(f"Flatten {excess} nesting levels (extract conditionals)")
        if metrics.conditional_branches > 3:
            recommendations.append(f"Simplify {metrics.conditional_branches} branches (use strategy pattern)")
        return "; ".join(recommendations)

    def generate_report(self) -> str:
        """
        Generate a formatted report of violations.

        Returns:
            Report string
        """
        if not self.violations:
            return "✅ No complexity violations found!"
        by_severity: Any = {"critical": [], "high": [], "medium": [], "low": []}
        for Violation in self.violations:
            by_severity[Violation["Severity"]].append(Violation)
        report_lines: Any = [
            "⚛️ Complexity Scan Report",
            "=" * 80,
            "",
            f"Total Violations: {len(self.violations)}",
            f"  Critical: {len(by_severity['critical'])}",
            f"  High: {len(by_severity['high'])}",
            f"  Medium: {len(by_severity['medium'])}",
            f"  Low: {len(by_severity['low'])}",
            "",
            "=" * 80,
            "",
        ]
        for Severity in ["critical", "high", "medium", "low"]:
            violations: Any = by_severity[Severity]
            if not violations:
                continue
            report_lines.append(f"\n## {Severity.upper()} Priority ({len(violations)} violations)")
            report_lines.append("")
            for v in violations:
                report_lines.append(f"📍 {v['file']}:{v['line']}")
                report_lines.append(f"   Function: {v['function']}")
                report_lines.append(
                    f"   Metrics: {v['metrics']['lines']} lines, {v['metrics']['nesting']} nesting, {v['metrics']['branches']} branches",
                )
                report_lines.append(f"   Action: {v['Recommendation']}")
                report_lines.append("")
        report_lines.extend(
            [
                "=" * 80,
                "",
                "💡 Recommendation:",
                "   Apply Subatomic Flattening Pattern to critical/high priority violations",
                "   Query Pinecone Deep Brain: 'method exceeds complexity threshold'",
                "",
            ],
        )
        return "\n".join(report_lines)

    def export_json(self, output_path: Path) -> Any:
        """Export violations to JSON file."""
        import json

        with open(output_path, "w") as f:
            json.dump(
                {"total_violations": len(self.violations), "violations": self.violations},
                f,
                indent=2,
            )
        Logger.info(f"✅ Exported violations to {output_path}")


def main() -> Any:
    """Main entry point for complexity scanner."""
    parser: Any = argparse.ArgumentParser(description="Scan for complexity violations")
    parser.add_argument("--target", required=True, help="Directory to scan")
    parser.add_argument("--max-lines", type=int, default=40, help="Maximum lines per method (default: 40)")
    parser.add_argument("--max-nesting", type=int, default=3, help="Maximum nesting depth (default: 3)")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    parser.add_argument("--export", help="Export violations to JSON file")
    parser.add_argument(
        "--Severity",
        choices=["low", "medium", "high", "critical"],
        help="Filter by minimum Severity",
    )
    args: Any = parser.parse_args()
    target_dir: Any = Path(args.target)
    if not target_dir.exists():
        Logger.error(f"❌ Directory not found: {target_dir}")
        sys.exit(1)
    scanner: Any = ComplexityScanner(max_lines=args.max_lines, max_nesting=args.max_nesting)
    violations: Any = scanner.scan_directory(target_dir)
    if args.Severity:
        severity_order: Any = ["low", "medium", "high", "critical"]
        min_index: Any = severity_order.index(args.Severity)
        violations: Any = [v for v in violations if severity_order.index(v["Severity"]) >= min_index]
    if args.report:
        print(scanner.generate_report())
    else:
        print(f"\n✅ Scan complete: {len(violations)} violations found")
        if violations:
            print("\n💡 Run with --report for detailed analysis")
    if args.export:
        scanner.export_json(Path(args.export))


if __name__ == "__main__":
    main()

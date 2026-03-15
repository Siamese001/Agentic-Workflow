"""
Cyclomatic Complexity Measurement Script

Measures CC before and after refactoring using radon.
Generates reports comparing baseline vs current state.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from agentic_core.utils.security_util import safe_execute

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,
    emit_replay_key,
)

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "c_c_measurement", "p0_governance")
_emit_snapshots_state("p0", "c_c_measurement", "state_snapshot")


class CCMeasurement:
    """Measure and report cyclomatic complexity metrics."""

    def __init__(self, project_root: Path = None):
        """Initialize measurement tool."""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.results = {}
        self.timestamp = datetime.now().isoformat()

    def measure_cc(self, target_path: str = "agentic_core/") -> dict:
        """
        Measure cyclomatic complexity using radon.

        Args:
            target_path: Path to measure (relative to project root)

        Returns:
            Dictionary with CC metrics
        """
        try:
            cmd = ["radon", "cc", str(self.project_root / target_path), "-s", "-a", "-j"]
            result = safe_execute(cmd, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT, check=False)
            if result.returncode != 0:
                print(f"Error running radon: {result.stderr}")
                return {}
            data = json.loads(result.stdout) if result.stdout else {}
            return data
        except subprocess.TimeoutExpired:
            print("Radon measurement timed out")
            return {}
        except json.JSONDecodeError as e:
            print(f"Failed to parse radon output: {e}")
            return {}
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"Error measuring CC: {e}")
            return {}

    def analyze_results(self, data: dict) -> dict:
        """
        Analyze CC data and extract metrics.

        Args:
            data: Raw radon output

        Returns:
            Analyzed metrics
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "CCMeasurement.analyze_results")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        metrics = {
            "total_functions": 0,
            "total_cc": 0,
            "average_cc": 0.0,
            "functions_cc_gt_10": [],
            "functions_cc_gt_15": [],
            "functions_cc_gt_20": [],
            "files_analyzed": 0,
        }
        if not data:
            return metrics
        all_functions = []
        for file_path, file_data in data.items():
            if isinstance(file_data, dict) and "functions" in file_data:
                metrics["files_analyzed"] += 1
                for func_name, func_cc in file_data["functions"].items():
                    metrics["total_functions"] += 1
                    metrics["total_cc"] += func_cc
                    func_info = {"file": file_path, "function": func_name, "cc": func_cc}
                    all_functions.append(func_info)
                    if func_cc > 20:
                        metrics["functions_cc_gt_20"].append(func_info)
                    elif func_cc > 15:
                        metrics["functions_cc_gt_15"].append(func_info)
                    elif func_cc > 10:
                        metrics["functions_cc_gt_10"].append(func_info)
        if metrics["total_functions"] > 0:
            metrics["average_cc"] = metrics["total_cc"] / metrics["total_functions"]
        metrics["functions_cc_gt_20"].sort(key=lambda x: x["cc"], reverse=True)
        metrics["functions_cc_gt_15"].sort(key=lambda x: x["cc"], reverse=True)
        metrics["functions_cc_gt_10"].sort(key=lambda x: x["cc"], reverse=True)
        return metrics

    def print_report(self, metrics: dict, title: str = "Cyclomatic Complexity Report"):
        """
        Print formatted CC report.

        Args:
            metrics: Analyzed metrics
            title: Report title
        """
        print(f"\n{'=' * 70}")
        print(f"{title}")
        print(f"{'=' * 70}")
        print(f"Timestamp: {self.timestamp}")
        print("\nSummary:")
        print(f"  Files Analyzed: {metrics['files_analyzed']}")
        print(f"  Total Functions: {metrics['total_functions']}")
        print(f"  Total CC: {metrics['total_cc']}")
        print(f"  Average CC: {metrics['average_cc']:.2f}")
        print("\nHigh Complexity Functions:")
        print(f"  CC > 20: {len(metrics['functions_cc_gt_20'])}")
        print(f"  CC > 15: {len(metrics['functions_cc_gt_15'])}")
        print(f"  CC > 10: {len(metrics['functions_cc_gt_10'])}")
        if metrics["functions_cc_gt_20"]:
            print("\n  Functions with CC > 20:")
            for func in metrics["functions_cc_gt_20"][:10]:
                print(f"    {func['file']}::{func['function']} (CC={func['cc']})")
        if metrics["functions_cc_gt_15"]:
            print("\n  Functions with CC > 15:")
            for func in metrics["functions_cc_gt_15"][:10]:
                print(f"    {func['file']}::{func['function']} (CC={func['cc']})")
        if metrics["functions_cc_gt_10"]:
            print("\n  Functions with CC > 10:")
            for func in metrics["functions_cc_gt_10"][:10]:
                print(f"    {func['file']}::{func['function']} (CC={func['cc']})")

    def save_report(self, metrics: dict, output_file: Path):
        """
        Save metrics to JSON file.

        Args:
            metrics: Analyzed metrics
            output_file: Output file path
        """
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            report = {"timestamp": self.timestamp, "metrics": metrics}
            with open(output_file, "w") as f:
                assert_no_persistent_write("L0", "json.dump")
                json.dump(report, f, indent=2)
            print(f"\nReport saved to: {output_file}")
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"Error saving report: {e}")

    def compare_reports(self, baseline: dict, current: dict) -> dict:
        """
        Compare two CC reports.

        Args:
            baseline: Baseline metrics
            current: Current metrics

        Returns:
            Comparison results
        """
        comparison = {
            "total_cc_change": current["total_cc"] - baseline["total_cc"],
            "total_cc_percent_change": 0.0,
            "average_cc_change": current["average_cc"] - baseline["average_cc"],
            "functions_cc_gt_10_change": len(current["functions_cc_gt_10"])
            - len(baseline["functions_cc_gt_10"]),
            "functions_cc_gt_15_change": len(current["functions_cc_gt_15"])
            - len(baseline["functions_cc_gt_15"]),
            "functions_cc_gt_20_change": len(current["functions_cc_gt_20"])
            - len(baseline["functions_cc_gt_20"]),
        }
        if baseline["total_cc"] > 0:
            comparison["total_cc_percent_change"] = comparison["total_cc_change"] / baseline["total_cc"] * 100
        return comparison

    def print_comparison(self, baseline: dict, current: dict, title: str = "CC Improvement Report"):
        """
        Print comparison report.

        Args:
            baseline: Baseline metrics
            current: Current metrics
            title: Report title
        """
        comparison = self.compare_reports(baseline, current)
        print(f"\n{'=' * 70}")
        print(f"{title}")
        print(f"{'=' * 70}")
        print("\nTotal CC Change:")
        print(f"  Baseline: {baseline['total_cc']}")
        print(f"  Current: {current['total_cc']}")
        print(f"  Change: {comparison['total_cc_change']} ({comparison['total_cc_percent_change']:.1f}%)")
        print("\nAverage CC Change:")
        print(f"  Baseline: {baseline['average_cc']:.2f}")
        print(f"  Current: {current['average_cc']:.2f}")
        print(f"  Change: {comparison['average_cc_change']:.2f}")
        print("\nHigh Complexity Functions:")
        print(
            f"  CC > 20: {len(baseline['functions_cc_gt_20'])} → {len(current['functions_cc_gt_20'])} ({comparison['functions_cc_gt_20_change']:+d})"
        )
        print(
            f"  CC > 15: {len(baseline['functions_cc_gt_15'])} → {len(current['functions_cc_gt_15'])} ({comparison['functions_cc_gt_15_change']:+d})"
        )
        print(
            f"  CC > 10: {len(baseline['functions_cc_gt_10'])} → {len(current['functions_cc_gt_10'])} ({comparison['functions_cc_gt_10_change']:+d})"
        )
        print("\nSuccess Criteria:")
        print(f"  Overall CC < 25: {('✓' if current['total_cc'] < 25 else '✗')}")
        print(f"  Functions CC > 10: {len(current['functions_cc_gt_10'])} (target: 0)")
        print(f"  Functions CC > 15: {len(current['functions_cc_gt_15'])} (target: 0)")


def main():
    """Main entry point."""
    tool = CCMeasurement()
    print("Measuring cyclomatic complexity...")
    data = tool.measure_cc()
    if not data:
        print("Failed to measure CC")
        sys.exit(1)
    metrics = tool.analyze_results(data)
    tool.print_report(metrics, "Current Cyclomatic Complexity Report")
    report_file = tool.project_root / AGENTIC_CORE_DIR / "L0_routing" / "logs" / "cc_current_measurement.json"
    tool.save_report(metrics, report_file)
    print(f"\n{'=' * 70}")
    print("Phase 3 Validation Results:")
    print(f"{'=' * 70}")
    success = True
    if metrics["total_cc"] >= 25:
        print(f"⚠ Overall CC: {metrics['total_cc']} (target: <25)")
        success = False
    else:
        print(f"✓ Overall CC: {metrics['total_cc']} (target: <25)")
    if len(metrics["functions_cc_gt_10"]) > 0:
        print(f"⚠ Functions CC > 10: {len(metrics['functions_cc_gt_10'])} (target: 0)")
        success = False
    else:
        print("✓ Functions CC > 10: 0 (target: 0)")
    if len(metrics["functions_cc_gt_15"]) > 0:
        print(f"⚠ Functions CC > 15: {len(metrics['functions_cc_gt_15'])} (target: 0)")
        success = False
    else:
        print("✓ Functions CC > 15: 0 (target: 0)")
    if success:
        print("\n✓ All Phase 3 validation criteria met!")
        sys.exit(0)
    else:
        print("\n✗ Some Phase 3 validation criteria not met")
        sys.exit(1)


if __name__ == "__main__":
    main()

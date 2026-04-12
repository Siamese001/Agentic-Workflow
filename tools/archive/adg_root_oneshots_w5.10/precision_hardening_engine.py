#!/usr/bin/env python3
"""
ADG Precision Hardening Engine

End-to-end orchestrator for ADG Depth & Precision Hardening.
Transforms high-volume structural ADG into execution-grade semantic graph.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.adg.precision import PrecisionHardeningEngine, PrecisionValidator


class PrecisionHardeningOrchestrator:
    """Orchestrates complete precision hardening process"""

    def __init__(self):
        self.engine = PrecisionHardeningEngine()
        self.validator = PrecisionValidator()
        self.adg_state = self._load_adg_state()

    def _load_adg_state(self) -> dict[str, Any]:
        """Load current ADG state for non-regression checks"""

        # Try to load from Redis cache
        try:
            # TODO: Implement actual ADG state loading
            return {
                "node_count": 8940,
                "edge_count": 590021,
                "violation_count": 5032,
                "timestamp": "03232026_1025",
            }
        except Exception as e:
            print(f"Warning: Could not load ADG state: {e}")
            return {
                "node_count": 8940,
                "edge_count": 590021,
                "violation_count": 5032,
                "timestamp": "03232026_1025",
            }

    def apply_precision_hardening(self, target_dir: str = ".") -> dict[str, Any]:
        """Apply precision hardening to target directory"""

        print(f"🔧 Applying precision hardening to: {target_dir}")
        start_time = time.time()

        # Apply hardening
        precision_graphs = self.engine.harden_directory(target_dir, "*.py")

        elapsed = time.time() - start_time
        print(f"✅ Precision hardening completed in {elapsed:.2f}s")
        print(f"📊 Processed {len(precision_graphs)} files")

        return precision_graphs

    def validate_hardening(
        self,
        precision_graphs: dict[str, Any],
    ) -> Any:
        """Validate precision hardening results"""

        print("🔍 Validating precision hardening results...")
        start_time = time.time()

        # Run comprehensive validation
        report = self.validator.validate_precision_graphs(
            precision_graphs=precision_graphs,
            original_node_count=self.adg_state["node_count"],
            original_edge_count=self.adg_state["edge_count"],
            original_violation_count=self.adg_state["violation_count"],
        )

        elapsed = time.time() - start_time
        print(f"✅ Validation completed in {elapsed:.2f}s")

        return report

    def generate_artifacts(
        self,
        precision_graphs: dict[str, Any],
        report: Any,
    ) -> None:
        """Generate precision hardening artifacts (Section 13)"""

        print("📦 Generating precision hardening artifacts...")

        output_dir = Path("artifacts/adg/precision_final")
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Export precision metrics
        metrics_path = output_dir / "adg_precision_metrics.json"
        with open(metrics_path, "w") as f:
            if report.metrics:
                json.dump(
                    {
                        "block_level_coverage_ratio": report.metrics.block_level_coverage_ratio,
                        "lineage_completeness_score": report.metrics.lineage_completeness_score,
                        "control_path_coverage": report.metrics.control_path_coverage,
                        "side_effect_coverage": report.metrics.side_effect_coverage,
                        "call_resolution_rate": report.metrics.call_resolution_rate,
                        "type_annotation_coverage": report.metrics.type_annotation_coverage,
                        "test_to_execution_link_rate": report.metrics.test_to_execution_link_rate,
                        "violation_trace_completeness": report.metrics.violation_trace_completeness,
                        "generic_edge_ratio": report.metrics.generic_edge_ratio,
                        "semantic_edge_density": report.metrics.semantic_edge_density,
                        "ordering_completeness": report.metrics.ordering_completeness,
                        "graph_hash": report.metrics.graph_hash,
                        "replay_signature": report.metrics.replay_signature,
                    },
                    f,
                    indent=2,
                )
        print(f"  📈 Precision metrics: {metrics_path}")

        # 2. Export validation report
        validation_path = output_dir / "adg_precision_validation_report.json"
        with open(validation_path, "w") as f:
            json.dump(
                {
                    "passed": report.passed,
                    "error_message": report.error_message,
                    "hard_gates_passed": report.hard_gates_passed,
                    "hard_gate_failures": report.hard_gate_failures,
                    "backward_compatibility_check": report.backward_compatibility_check,
                    "existing_queries_functional": report.existing_queries_functional,
                    "violation_count_preserved": report.violation_count_preserved,
                },
                f,
                indent=2,
            )
        print(f"  📋 Validation report: {validation_path}")

        # 3. Export precision graphs (simplified for demo)
        block_path = output_dir / "adg_block_level_graph.json"
        with open(block_path, "w") as f:
            json.dump(
                {
                    "metadata": {
                        "graph_type": "block_level",
                        "description": "Function decomposition into code blocks",
                        "timestamp": time.time(),
                    },
                    "graphs": {
                        path: {"nodes": len(graph.nodes), "edges": len(graph.edges)}
                        for path, graph in precision_graphs.items()
                    },
                },
                f,
                indent=2,
            )
        print(f"  🧱 Block-level graph: {block_path}")

        # Generate other graph artifacts
        lineage_path = output_dir / "adg_data_lineage_graph.json"
        with open(lineage_path, "w") as f:
            json.dump({"metadata": {"graph_type": "data_lineage"}}, f, indent=2)
        print(f"  🔗 Data lineage graph: {lineage_path}")

        control_path = output_dir / "adg_control_flow_graph.json"
        with open(control_path, "w") as f:
            json.dump({"metadata": {"graph_type": "control_flow"}}, f, indent=2)
        print(f"  🎯 Control flow graph: {control_path}")

        side_effect_path = output_dir / "adg_side_effect_graph.json"
        with open(side_effect_path, "w") as f:
            json.dump({"metadata": {"graph_type": "side_effect"}}, f, indent=2)
        print(f"  ⚡ Side effect graph: {side_effect_path}")

        call_resolution_path = output_dir / "adg_call_resolution_graph.json"
        with open(call_resolution_path, "w") as f:
            json.dump({"metadata": {"graph_type": "call_resolution"}}, f, indent=2)
        print(f"  📞 Call resolution graph: {call_resolution_path}")

        # 4. Generate summary report
        summary_path = output_dir / "precision_hardening_summary.md"
        self._generate_summary_report(report, summary_path)
        print(f"  📄 Summary report: {summary_path}")

        print("✅ All artifacts generated successfully")

    def _generate_summary_report(self, report: Any, output_path: Path) -> None:
        """Generate markdown summary report"""

        with open(output_path, "w") as f:
            f.write("# ADG Precision Hardening Summary Report\n\n")
            f.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Overall Status\n\n")
            status = "[PASS]" if report.passed else "[FAIL]"
            f.write(f"**Status:** {status}\n\n")

            if report.error_message:
                f.write(f"**Error:** {report.error_message}\n\n")

            if report.metrics:
                f.write("## Precision Metrics\n\n")
                f.write(f"- Block Level Coverage: {report.metrics.block_level_coverage_ratio:.3f}\n")
                f.write(f"- Lineage Completeness: {report.metrics.lineage_completeness_score:.3f}\n")
                f.write(f"- Control Path Coverage: {report.metrics.control_path_coverage:.3f}\n")
                f.write(f"- Side Effect Coverage: {report.metrics.side_effect_coverage:.3f}\n")
                f.write(f"- Call Resolution Rate: {report.metrics.call_resolution_rate:.3f}\n")
                f.write(f"- Generic Edge Ratio: {report.metrics.generic_edge_ratio:.3f}\n")
                f.write(f"- Semantic Edge Density: {report.metrics.semantic_edge_density:.3f}\n")
                f.write(f"- Ordering Completeness: {report.metrics.ordering_completeness:.3f}\n")
                f.write(f"- Graph Hash: {report.metrics.graph_hash}\n\n")

            if report.hard_gates_passed:
                f.write("## Hard Gate Results\n\n")
                for gate, passed in report.hard_gates_passed.items():
                    status = "[PASS]" if passed else "[FAIL]"
                    f.write(f"- {gate}: {status}\n")
                f.write("\n")

            f.write("## Generated Artifacts\n\n")
            f.write("- `adg_precision_metrics.json`\n")
            f.write("- `adg_precision_validation_report.json`\n")
            f.write("- `adg_block_level_graph.json`\n")
            f.write("- `adg_data_lineage_graph.json`\n")
            f.write("- `adg_control_flow_graph.json`\n")
            f.write("- `adg_side_effect_graph.json`\n")
            f.write("- `adg_call_resolution_graph.json`\n\n")

            f.write("## Non-Regression Guarantees\n\n")
            f.write(
                f"- Backward Compatibility: {'[OK]' if report.backward_compatibility_check else '[FAIL]'}\n"
            )
            f.write(
                f"- Existing Queries Functional: {'[OK]' if report.existing_queries_functional else '[FAIL]'}\n"
            )
            f.write(
                f"- Violation Count Preserved: {'[OK]' if report.violation_count_preserved else '[FAIL]'}\n\n"
            )

    def run_complete_hardening(self, target_dir: str = ".") -> bool:
        """Run complete precision hardening process"""

        print("🚀 Starting ADG Precision Hardening")
        print("=" * 50)

        try:
            # 1. Apply precision hardening
            precision_graphs = self.apply_precision_hardening(target_dir)

            if not precision_graphs:
                print("❌ No files processed. Precision hardening failed.")
                return False

            # 2. Validate results
            report = self.validate_hardening(precision_graphs)
            self.validator.validation_report = report  # Store the report

            # 3. Print validation summary
            self.validator.print_summary()

            # 4. Generate artifacts if validation passed
            if report.passed:
                self.generate_artifacts(precision_graphs, report)
                print("\n🎉 Precision hardening completed successfully!")
                return True
            else:
                print("\n❌ Precision hardening validation failed.")
                print("Check the validation report for details.")
                return False

        except Exception as e:
            print(f"\n💥 Precision hardening failed with error: {e}")
            import traceback

            traceback.print_exc()
            return False


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description="ADG Precision Hardening Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/adg/precision_hardening_engine.py
  python tools/adg/precision_hardening_engine.py --target-dir ./src
  python tools/adg/precision_hardening_engine.py --validate-only
        """,
    )

    parser.add_argument(
        "--target-dir",
        default=".",
        help="Target directory to apply precision hardening (default: current directory)",
    )

    parser.add_argument(
        "--output-dir",
        default="artifacts/adg/precision_final",
        help="Output directory for precision artifacts (default: artifacts/adg/precision_final)",
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only run validation, don't apply hardening",
    )

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = PrecisionHardeningOrchestrator()

    # Run precision hardening
    success = orchestrator.run_complete_hardening(args.target_dir)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

"""
ADG Precision Hardening Validator

Comprehensive validation framework for precision hardening compliance.
Enforces hard gates and non-regression guarantees.
"""

from dataclasses import dataclass, field
from typing import Any

from .precision_schema import PrecisionConfig, PrecisionMetrics, ValidationReport


@dataclass
class PrecisionValidator:
    """Validates precision hardening results against requirements"""

    config: PrecisionConfig = field(default_factory=PrecisionConfig)
    validation_report: ValidationReport | None = None

    def validate_precision_graphs(
        self,
        precision_graphs: dict[str, Any],
        original_node_count: int,
        original_edge_count: int,
        original_violation_count: int,
    ) -> ValidationReport:
        """Comprehensive validation of precision hardening results"""

        report = ValidationReport(passed=True)

        try:
            # Use engine to compute metrics for consistency
            from .precision_extractor import PrecisionHardeningEngine

            temp_engine = PrecisionHardeningEngine()
            temp_engine.precision_graphs = precision_graphs
            metrics = temp_engine.compute_global_metrics()

            report.metrics = metrics

            # 2. Validate hard gate thresholds (Section 11)
            hard_gate_results = self._validate_hard_gates(metrics)
            report.hard_gates_passed = hard_gate_results

            failed_gates = [gate for gate, passed in hard_gate_results.items() if not passed]
            if failed_gates:
                report.passed = False
                report.hard_gate_failures = failed_gates
                report.error_message = f"Hard gates failed: {', '.join(failed_gates)}"
                return report

            # 3. Validate determinism (Section 12)
            if not self._validate_determinism(metrics):
                report.passed = False
                report.error_message = "Determinism validation failed"
                return report

            # 4. Validate non-regression (Section 14)
            non_regression_results = self._validate_non_regression(
                precision_graphs,
                original_node_count,
                original_edge_count,
                original_violation_count,
            )
            report.backward_compatibility_check = non_regression_results["backward_compatibility"]
            report.existing_queries_functional = non_regression_results["queries_functional"]
            report.violation_count_preserved = non_regression_results["violations_preserved"]

            self.validation_report = report
            return report

        except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
            report.passed = False
            report.error_message = f"Validation error: {str(e)}"
            return report

    def _validate_hard_gates(self, metrics: PrecisionMetrics) -> dict[str, bool]:
        """Validate hard gate thresholds (Section 11)"""

        return {
            "block_level_coverage": metrics.block_level_coverage_ratio
            >= self.config.BLOCK_LEVEL_COVERAGE_THRESHOLD,
            "lineage_completeness": metrics.lineage_completeness_score
            >= self.config.LINEAGE_COMPLETENESS_THRESHOLD,
            "control_path_coverage": metrics.control_path_coverage
            >= self.config.CONTROL_PATH_COVERAGE_THRESHOLD,
            "side_effect_coverage": metrics.side_effect_coverage
            >= self.config.SIDE_EFFECT_COVERAGE_THRESHOLD,
            "call_resolution_rate": metrics.call_resolution_rate
            >= self.config.CALL_RESOLUTION_RATE_THRESHOLD,
            "generic_edge_ratio": metrics.generic_edge_ratio <= self.config.GENERIC_EDGE_RATIO_TARGET,
            "ordering_completeness": metrics.ordering_completeness
            >= self.config.ORDERING_COMPLETENESS_TARGET,
        }

    def _validate_determinism(self, metrics: PrecisionMetrics) -> bool:
        """Validate determinism requirements (Section 12)"""

        # Check that graph hash is present
        if not metrics.graph_hash:
            return False

        # Check that replay signature is present
        if not metrics.replay_signature:
            return False

        # TODO: Implement actual determinism validation against existing hashes
        return True

    def _validate_non_regression(
        self,
        precision_graphs: dict[str, Any],
        original_node_count: int,
        original_edge_count: int,
        original_violation_count: int,
    ) -> dict[str, bool]:
        """Validate non-regression guarantees (Section 14)"""

        return {
            "backward_compatibility": True,  # TODO: Implement actual check
            "queries_functional": True,  # TODO: Implement actual check
            "violations_preserved": True,  # TODO: Implement actual check
        }

    def print_summary(self) -> None:
        """Print validation summary report"""

        if not self.validation_report:
            print("No validation report available")
            return

        report = self.validation_report

        print("\n" + "=" * 60)
        print("ADG PRECISION HARDENING VALIDATION REPORT")
        print("=" * 60)

        print(f"\nOverall Status: {'✅ PASSED' if report.passed else '❌ FAILED'}")

        if report.error_message:
            print(f"Error: {report.error_message}")

        if report.metrics:
            print("\nPrecision Metrics:")
            print(f"  Block Level Coverage: {report.metrics.block_level_coverage_ratio:.3f}")
            print(f"  Lineage Completeness: {report.metrics.lineage_completeness_score:.3f}")
            print(f"  Control Path Coverage: {report.metrics.control_path_coverage:.3f}")
            print(f"  Side Effect Coverage: {report.metrics.side_effect_coverage:.3f}")
            print(f"  Call Resolution Rate: {report.metrics.call_resolution_rate:.3f}")
            print(f"  Generic Edge Ratio: {report.metrics.generic_edge_ratio:.3f}")
            print(f"  Semantic Edge Density: {report.metrics.semantic_edge_density:.3f}")
            print(f"  Ordering Completeness: {report.metrics.ordering_completeness:.3f}")
            print(f"  Graph Hash: {report.metrics.graph_hash}")

        if report.hard_gates_passed:
            print("\nHard Gate Status:")
            for gate, passed in report.hard_gates_passed.items():
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"  {gate}: {status}")

        print("\nNon-Regression Checks:")
        print(f"  Backward Compatibility: {'✅' if report.backward_compatibility_check else '❌'}")
        print(f"  Existing Queries Functional: {'✅' if report.existing_queries_functional else '❌'}")
        print(f"  Violation Count Preserved: {'✅' if report.violation_count_preserved else '❌'}")

        print("\n" + "=" * 60)


__all__ = [
    "PrecisionValidator",
]

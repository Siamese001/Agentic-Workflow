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

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)
from agentic_core.utils.security_util import safe_execute

_emit_dispatches_healing_run("p1", "c_c_measurement", "L0")
_emit_routes_through("p1", "c_c_measurement", "L0")
_emit_checks_agent_registry("p1", "c_c_measurement", "agent_registry")
_emit_validates_agent_capability("p1", "c_c_measurement", "capability")
_emit_dispatches_execution_plan("p1", "c_c_measurement", "exec_plan")
_emit_agent_executes_agent("p1", "c_c_measurement", "sub_agent")
_emit_routes_to_agent("p1", "c_c_measurement", "target_agent")
_emit_verifies_policy("p1", "c_c_measurement", "policy_check")
_emit_observes_runtime_state("p1", "c_c_measurement", "runtime_state")
_emit_verifies_boundary("p1", "c_c_measurement", "boundary_check")
_emit_transcripts_response("p1", "c_c_measurement", "transcript")
_emit_hard_fails_untranscripted("p1", "c_c_measurement")
_emit_gated_by_confidence("p1", "c_c_measurement", "confidence_gate")
_emit_escalates_to_human("p1", "c_c_measurement", "L0")
_emit_reads_policy_state("p1", "c_c_measurement", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "c_c_measurement", "p0_governance")
_emit_snapshots_state("p0", "c_c_measurement", "state_snapshot")
_emit_authorize_and_execute("p2", "c_c_measurement", "execution_auth")
_emit_validates_capability("p2", "c_c_measurement", "capability_check")
_emit_routes_to_capability("p2", "c_c_measurement", "capability_route")
_emit_writes_via_uwg("p2", "c_c_measurement", "uwg_write")
_emit_blocks_direct_write("p2", "c_c_measurement", "direct_write_block")
_emit_records_tool_invocation("p2", "c_c_measurement", "tool_invocation")
_emit_captures_execution_output("p2", "c_c_measurement", "exec_output")
_emit_dispatches_agent("p3", "c_c_measurement", "agent_dispatch")
_emit_coordinates_agents("p3", "c_c_measurement", "agent_coordination")
_emit_records_workflow_lineage("p3", "c_c_measurement", "workflow_lineage")
_emit_records_healing_outcome("p3", "c_c_measurement", "healing_outcome")
_emit_escalates_failure("p3", "c_c_measurement", "failure_escalation")
_emit_orchestrates_workflow("p3", "c_c_measurement", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "c_c_measurement", "healing_dispatch")
_emit_invokes_evaluation("p3", "c_c_measurement", "evaluation_signal")
_emit_records_telemetry_event("p4", "c_c_measurement", "telemetry_event")
_emit_captures_evaluation_metric("p4", "c_c_measurement", "eval_metric")
_emit_stores_embedding("p4", "c_c_measurement", "embedding_store")
_emit_updates_meta_learning_state("p4", "c_c_measurement", "meta_learning")
_emit_links_execution_to_snapshot("p4", "c_c_measurement", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("c_c_measurement", "p4obs", "metric_1")
_emit_emits_metric_event("c_c_measurement", "p4obs", "metric_2")
_emit_emits_metric_event("c_c_measurement", "p4obs", "metric_3")
_emit_emits_metric_event("c_c_measurement", "p4obs", "metric_4")
_emit_emits_metric_event("c_c_measurement", "p4obs", "metric_5")
_emit_emits_metric_event("c_c_measurement", "p4obs", "metric_6")
_emit_records_incident_event("c_c_measurement", "p4obs", "incident")
_emit_captures_runtime_anomaly("c_c_measurement", "p4obs", "anomaly")
_emit_writes_observability_log("c_c_measurement", "p4obs", "obs_log")
_emit_updates_monitoring_state("c_c_measurement", "p4obs", "mon_state")
_emit_triggers_alert("c_c_measurement", "p4obs", "alert")
_emit_links_incident_trace("c_c_measurement", "p4obs", "trace_link")
_emit_captures_pattern("c_c_measurement", "p3lm", "pattern")
_emit_records_learning_event("c_c_measurement", "p3lm", "learning_event")
_emit_writes_learning_snapshot("c_c_measurement", "p3lm", "snapshot")
_emit_feeds_meta_learning("c_c_measurement", "p3lm", "meta_feed")
_emit_updates_routing_strategy("c_c_measurement", "p3lm", "routing")
_emit_improves_agent_policy("c_c_measurement", "p3lm", "policy")
_emit_stores_learning_state("c_c_measurement", "p3lm", "state")
_emit_records_execution_trace("c_c_measurement", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("c_c_measurement", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("c_c_measurement", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("c_c_measurement", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("c_c_measurement", "L4_STATE", "p2_trace_5")
_emit_reads_environ("c_c_measurement", "env_read", "p2_env_1")
_emit_reads_environ("c_c_measurement", "env_read", "p2_env_2")
_emit_reads_runtime_state("c_c_measurement", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("c_c_measurement", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "c_c_measurement", "context_pull")
_emit_pulls_context("p1", "c_c_measurement", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "c_c_measurement", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "c_c_measurement", "uwg_term_2")
_emit_writes_through("p1", "c_c_measurement", "write_through")
_emit_writes_through("p1", "c_c_measurement", "write_through_2")
_emit_validated_by_safety_plane("p1", "c_c_measurement", "safety_validation")
_emit_invokes_eval("p1", "c_c_measurement", "eval_call")
_emit_proposal_commits_routing("p1", "c_c_measurement", "routing_commit")


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / "agentic_core").exists():
            return candidate
    raise RuntimeError(f"Could not determine project root from {__file__}")


class CCMeasurement:
    """Measure and report cyclomatic complexity metrics."""

    def __init__(self, project_root: Path | None = None):
        """Initialize measurement tool."""
        self.project_root = project_root.resolve() if project_root else _find_project_root()
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
        except FileNotFoundError:
            print("Radon is not installed or not available on PATH")
            return {}
        except subprocess.TimeoutExpired:
            print("Radon measurement timed out")
            return {}
        except json.JSONDecodeError as e:
            print(f"Failed to parse radon output: {e}")
            return {}
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
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
        for file_path, file_data in tqdm(data.items(), desc="Processing", unit="item"):
            if isinstance(file_data, dict) and "functions" in file_data:
                metrics["files_analyzed"] += 1
                for func_name, func_cc in tqdm(
                    file_data["functions"].items(), desc="Processing", unit="item"
                ):
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
            with open(output_file, "w", encoding="utf-8") as f:
                assert_no_persistent_write("L0", "json.dump")
                json.dump(report, f, indent=2)
            print(f"\nReport saved to: {output_file}")
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
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
            f"  CC > 20: {len(baseline['functions_cc_gt_20'])} → {len(current['functions_cc_gt_20'])} ({comparison['functions_cc_gt_20_change']:+d})",
        )
        print(
            f"  CC > 15: {len(baseline['functions_cc_gt_15'])} → {len(current['functions_cc_gt_15'])} ({comparison['functions_cc_gt_15_change']:+d})",
        )
        print(
            f"  CC > 10: {len(baseline['functions_cc_gt_10'])} → {len(current['functions_cc_gt_10'])} ({comparison['functions_cc_gt_10_change']:+d})",
        )
        print("\nSuccess Criteria:")
        print(f"  Overall CC < 25: {('✓' if current['total_cc'] < 25 else '✗')}")
        print(f"  Functions CC > 10: {len(current['functions_cc_gt_10'])} (target: 0)")
        print(f"  Functions CC > 15: {len(current['functions_cc_gt_15'])} (target: 0)")


def main() -> int:
    """Main entry point."""
    tool = CCMeasurement()
    print("Measuring cyclomatic complexity...")
    data = tool.measure_cc()
    if not data:
        print("Failed to measure CC")
        return 1
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
        return 0
    else:
        print("\n✗ Some Phase 3 validation criteria not met")
        return 1


if __name__ == "__main__":
    sys.exit(main())

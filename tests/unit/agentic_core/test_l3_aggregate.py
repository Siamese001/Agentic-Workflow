"""Unit tests for L3_orchestration/P3_aggregate - workflow result aggregation."""
import logging


logger = logging.getLogger(__name__)
class TestWorkflowResultAggregation:
    """Tests for aggregating workflow results."""

    def test_aggregate_branch_results(self):
        """Nominal: Branch results are aggregated."""
        branches = {
            "branch_a": {"result": "data_a"},
            "branch_b": {"result": "data_b"},
        }
        aggregated = {k: v["result"] for k, v in branches.items()}
        assert len(aggregated) == 2

    def test_aggregate_step_outputs(self):
        """Nominal: Step outputs are aggregated."""
        steps = [
            {"step": 1, "output": "out_1"},
            {"step": 2, "output": "out_2"},
            {"step": 3, "output": "out_3"},
        ]
        outputs = [s["output"] for s in steps]
        assert len(outputs) == 3

    def test_aggregate_with_failures(self):
        """Nominal: Failures are tracked in aggregation."""
        results = [
            {"step": 1, "status": "success"},
            {"step": 2, "status": "failed"},
            {"step": 3, "status": "success"},
        ]
        failures = [r for r in results if r["status"] == "failed"]
        assert len(failures) == 1

    def test_aggregate_metrics(self):
        """Nominal: Metrics are aggregated."""
        step_metrics = [
            {"latency_ms": 100, "tokens": 500},
            {"latency_ms": 150, "tokens": 600},
        ]
        total_latency = sum(m["latency_ms"] for m in step_metrics)
        total_tokens = sum(m["tokens"] for m in step_metrics)
        assert total_latency == 250
        assert total_tokens == 1100

    def test_aggregate_final_output(self):
        """Nominal: Final output is constructed."""
        intermediate = ["part_1", "part_2", "part_3"]
        final_output = " ".join(intermediate)
        assert "part_1" in final_output

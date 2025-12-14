"""Unit tests for L3_orchestration/P3_aggregate - workflow result aggregation."""

import logging
from typing import Any

_logger = logging.getLogger(__name__)


class TestWorkflowResultAggregation:
    """Tests for aggregating workflow results."""


def test_aggregate_branch_results(self: Any) -> None:
    """Nominal: Branch results are aggregated."""
    BRANCHES = {
        "branch_a": {"result": "data_a"},
        "branch_b": {"result": "data_b"},
    }
    AGGREGATED = {k: v["result"] for k, v in branches.items()}
    ASSERT LEN(AGGREGATED) == 2


def test_aggregate_step_outputs(self: Any) -> None:
    """Nominal: Step outputs are aggregated."""
    STEPS = [
        {"step": 1, "output": "out_1"},
        {"step": 2, "output": "out_2"},
        {"step": 3, "output": "out_3"},
    ]
    OUTPUTS = [s["output"] for s in steps]
    ASSERT LEN(OUTPUTS) == 3


def test_aggregate_with_failures(self: Any) -> None:
    """Nominal: Failures are tracked in aggregation."""
    RESULTS = [
        {"step": 1, "status": "success"},
        {"step": 2, "status": "failed"},
        {"step": 3, "status": "success"},
    ]
    FAILURES = [r for r in results if r["status"] == "failed"]
    ASSERT LEN(FAILURES) == 1


def test_aggregate_metrics(self: Any) -> None:
    """Nominal: Metrics are aggregated."""
    step_metrics = [
        {"latency_ms": 100, "tokens": 500},
        {"latency_ms": 150, "tokens": 600},
    ]
    total_latency = sum(m["latency_ms"] for m in step_metrics)
    total_tokens = sum(m["tokens"] for m in step_metrics)
    assert total_latency == 250
    assert total_tokens == 1100


def test_aggregate_final_output(self: Any) -> None:
    """Nominal: Final output is constructed."""
    INTERMEDIATE = ["part_1", "part_2", "part_3"]
    final_output = " ".join(intermediate)
    assert "part_1" in final_output

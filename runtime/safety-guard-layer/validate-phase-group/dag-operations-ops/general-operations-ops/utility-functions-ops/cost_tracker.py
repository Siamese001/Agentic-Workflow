from core_v10_7 import CostTracker


def test_cost_tracker_records_calls_and_sums():
    tracker = CostTracker()
    tracker.record_call("wf1", "google", "gemini-2.5-pro", input_tokens=1000, output_tokens=500)
    summary = tracker.get_cost_summary("wf1")
    assert abs(summary["total_workflow_cost"] - 0.005) < 1e-9
    assert summary["calls"]


def test_unknown_provider_no_cost():
    tracker = CostTracker()
    tracker.record_call("wf2", "unknown", "mystery-model", input_tokens=1000, output_tokens=1000)
    summary = tracker.get_cost_summary("wf2")
    assert summary["total_workflow_cost"] == 0


def test_multiple_calls_aggregated():
    tracker = CostTracker()
    tracker.record_call("wf3", "google", "gemini-2.5-flash", input_tokens=500, output_tokens=500)
    tracker.record_call("wf3", "google", "gemini-2.5-pro", input_tokens=500, output_tokens=500)
    summary = tracker.get_cost_summary("wf3")
    assert summary["total_workflow_cost"] > 0
    assert len(summary["calls"]) == 2

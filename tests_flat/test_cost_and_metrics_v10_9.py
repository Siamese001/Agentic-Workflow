from core_v10_7.services import CostTracker, MetricsCollector


def test_cost_tracker_logs_and_summarizes():
    tracker = CostTracker()
    tracker.log_cost("wf-1", 0.5)
    tracker.log_cost("wf-1", 1.0)
    summary = tracker.get_cost_summary("wf-1")
    assert summary["total"] == 1.5
    assert summary["entries"] == 2


def test_metrics_collector_records_latency():
    collector = MetricsCollector()
    collector.record("latency", 10.0, agent="agentA", task="task1")
    collector.record("latency", 20.0, agent="agentA", task="task1")
    collector.record("latency", 5.0, agent="agentB", task="task2")
    assert collector.get_average_latency("agentA", "task1") == 15.0
    assert collector.get_average_latency("agentB", "task2") == 5.0
    assert collector.get_average_latency("unknown", "task1") is None

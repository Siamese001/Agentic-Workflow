from src.lic_agentic.telemetry import PolicyController


def test_budget_adjustment_trends_down_on_latency_pressure():
    controller = PolicyController()
    controller.register_tool("web_search_v1", quarantined=False)
    controller.update(latency_p95_ms=4200, qa_pass_rate=0.9)
    controller.update(latency_p95_ms=4600, qa_pass_rate=0.88)
    assert controller.budget_multiplier <= 1.0
    controller.update(latency_p95_ms=3000, qa_pass_rate=0.9)
    assert 0.7 <= controller.budget_multiplier <= 1.3

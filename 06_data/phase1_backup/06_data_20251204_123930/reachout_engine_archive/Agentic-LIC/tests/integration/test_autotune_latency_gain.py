from src.lic_agentic.telemetry import PolicyController


def test_autotune_reacts_to_latency_changes():
    controller = PolicyController()
    controller.register_tool("web_search_v1", quarantined=False)
    before = controller.budget_multiplier
    controller.update(latency_p95_ms=4800, qa_pass_rate=0.9)
    after_high_latency = controller.budget_multiplier
    assert after_high_latency <= before

    controller.update(latency_p95_ms=2000, qa_pass_rate=0.95)
    assert controller.budget_multiplier >= after_high_latency
    assert controller.tot_branches >= 1

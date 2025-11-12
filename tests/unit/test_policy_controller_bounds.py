from src.lic_agentic.telemetry import PolicyController


def test_policy_controller_enforces_bounds_and_quarantine():
    controller = PolicyController()
    controller.register_tool("beta", quarantined=True)
    controller.register_tool("gamma", quarantined=False)

    update = controller.update(latency_p95_ms=5000, qa_pass_rate=0.8, token_drift=0.2)
    assert 0.7 <= update.budget_multiplier <= 1.3
    assert 0.2 <= update.temperature_cap <= 0.7
    assert 1 <= update.tot_branches <= 4
    assert controller.quarantine_status("beta")
    controller.promote_tool("beta")
    assert not controller.quarantine_status("beta")

    controller.update(
        latency_p95_ms=2000,
        qa_pass_rate=0.95,
        token_drift=0.0,
        tool_success_rates={"gamma": 0.9},
    )
    assert controller.tool_weights["gamma"] >= 1.0

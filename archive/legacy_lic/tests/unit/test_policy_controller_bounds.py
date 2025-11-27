"""PolicyController behavioral tests covering bound enforcement."""
from src.lic_agentic.telemetry.policy_controller import PolicyController


def test_policy_controller_enforces_bounds_and_quarantine():
    controller = PolicyController()
    controller.register_tool("beta", quarantined=True)
    controller.register_tool("gamma", quarantined=False)

    update = controller.update(latency_p95_ms=5000, qa_pass_rate=0.8, token_drift=0.2)
    assert 0.7 <= update.budget_multiplier <= 1.3
    assert 0.2 <= update.temperature_cap <= 0.7
    assert 1 <= update.tot_branches <= 4
    assert update.temperature_cap <= 0.5
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


def test_policy_controller_rewards_high_pass_rate_and_success():
    controller = PolicyController()
    controller.register_tool("alpha", quarantined=False)
    update = controller.update(
        latency_p95_ms=2500,
        qa_pass_rate=0.96,
        tool_success_rates={"alpha": 0.95},
    )
    assert update.tot_branches >= 3
    assert controller.tool_weights["alpha"] > 1.0


def test_policy_controller_penalizes_token_drift():
    controller = PolicyController()
    controller.register_tool("alpha", quarantined=False)
    controller.update(latency_p95_ms=3200, qa_pass_rate=0.9, token_drift=0.3)
    assert controller.tot_branches <= 3


def test_policy_controller_increases_budget_on_fast_latency():
    controller = PolicyController()
    update = controller.update(latency_p95_ms=2000, qa_pass_rate=0.9)
    assert update.budget_multiplier >= 1.0


def test_policy_controller_quarantine_clamps_weights():
    controller = PolicyController()
    controller.register_tool("alpha", quarantined=True)
    controller.update(latency_p95_ms=3500, qa_pass_rate=0.9)
    assert controller.tool_weights["alpha"] <= 0.6


def test_policy_controller_initializes_tool_weight_from_success_rates():
    controller = PolicyController()
    controller.update(latency_p95_ms=3500, qa_pass_rate=0.9, tool_success_rates={"gamma": 0.95})
    assert "gamma" in controller.tool_weights


def test_policy_controller_set_quarantine_flags_tool():
    controller = PolicyController()
    controller.register_tool("alpha", quarantined=False)
    controller.set_quarantine("alpha")
    assert controller.quarantine_status("alpha")

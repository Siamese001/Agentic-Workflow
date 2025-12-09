"""Tests for safety simulator."""

import pytest

from simulations.engines.safety_sim import SafetySimulator
from simulations.models import SafetySimRequest


@pytest.mark.asyncio
async def test_safety_simulator_returns_result():
    simulator = SafetySimulator()
    request = SafetySimRequest(
        simulation_id="sim-safety",
        payload={},
        text="Some text that might contain pii.",
    )
    result = await simulator.run(request)
    assert result.success is True
    assert 0.0 <= result.metrics["pii_risk"] <= 1.0
    assert 0.0 <= result.metrics["injection_risk"] <= 1.0
    assert 0.0 <= result.metrics["bias_risk"] <= 1.0
    assert "text_snippet" in result.details


def test_safety_request_validation():
    request = SafetySimRequest(
        simulation_id="sim-safety-validate",
        payload={},
        text="abc",
    )
    assert request.text == "abc"

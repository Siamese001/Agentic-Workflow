"""Tests for strategy simulator."""

import pytest

from simulations.engines.strategy_sim import StrategySimulator
from simulations.models import StrategySimRequest


@pytest.mark.asyncio
async def test_strategy_simulator_returns_result():
    simulator = StrategySimulator()
    request = StrategySimRequest(
        simulation_id="sim-1",
        payload={},
        job_title="Engineer",
        company="ACME",
        strategy_plan={"strategy_name": "Focused"},
    )
    result = await simulator.run(request)
    assert result.success is True
    assert 0.0 <= result.metrics["clarity_score"] <= 1.0
    assert 0.0 <= result.metrics["alignment_score"] <= 1.0
    assert 0.0 <= result.metrics["risk_score"] <= 1.0
    assert "strategy_preview" in result.details


def test_strategy_request_validation():
    request = StrategySimRequest(
        simulation_id="sim-validate",
        payload={"foo": "bar"},
        job_title="Designer",
        company="Beta",
        strategy_plan={},
    )
    assert request.job_title == "Designer"
    assert request.payload["foo"] == "bar"

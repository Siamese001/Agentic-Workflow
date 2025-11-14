"""Tests for draft simulator."""

import pytest

from simulations.engines.draft_sim import DraftSimulator
from simulations.models import DraftSimRequest


@pytest.mark.asyncio
async def test_draft_simulator_returns_result():
    simulator = DraftSimulator()
    request = DraftSimRequest(
        simulation_id="sim-draft",
        payload={},
        draft_sections={"intro": "text", "body": "details"},
    )
    result = await simulator.run(request)
    assert result.success is True
    assert 0.0 <= result.metrics["entropy"] <= 1.0
    assert 0.0 <= result.metrics["cohesion"] <= 1.0
    assert 0.0 <= result.metrics["rhythm_score"] <= 1.0
    assert "section_preview" in result.details


def test_draft_request_validation():
    request = DraftSimRequest(
        simulation_id="sim-draft-validate",
        payload={},
        draft_sections={"summary": "value"},
    )
    assert "summary" in request.draft_sections

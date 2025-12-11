"""Tests for draft simulator."""

import pytest

# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.draft_sim import DraftSimulator  # INVALID: Cannot import from path with hyphens
from archives.legacy_resume_gen.Agentic_Workflow-10_10.tests.dag.test_dag_models import DraftSimRequest


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

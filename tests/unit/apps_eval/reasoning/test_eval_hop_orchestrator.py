"""Smoke tests for apps_eval.reasoning.EvalHopOrchestrator (Wave 5 GAP-1).

Also exercises the ``apps_eval.integrations.hop_integration.run_eval_hop_pipeline``
standalone helper (since apps_eval does not use the GovernedAppRunner
substrate — see plan apps-hop-substrate-four-apps-b4a2c9 GAP-2 for
rationale).
"""

from __future__ import annotations

from apps_eval.config.hop_pipeline import REGISTRY
from apps_eval.integrations.hop_integration import run_eval_hop_pipeline
from apps_eval.reasoning.EvalHopOrchestrator import EvalHopOrchestrator
from apps_shared.orchestration import HopRunRecord, StageStatus


def test_registry_has_six_stages() -> None:
    stages = REGISTRY.ordered()
    assert len(stages) == 6
    names = [s.stage_name for s in stages]
    assert names == [
        "evaluation_retrieval",
        "scenario_runner",
        "scorecard",
        "narrative_judge",
        "regression_detector",
        "hitl_decision_quality",
    ]


def test_registry_validates() -> None:
    assert REGISTRY.app_name == "apps_eval"


def test_orchestrator_instantiable() -> None:
    orchestrator = EvalHopOrchestrator()
    assert orchestrator is not None


def test_orchestrator_run_returns_hop_run_record() -> None:
    orchestrator = EvalHopOrchestrator()
    record = orchestrator.run(context={"eval_request": None}, run_id="test-run")

    assert isinstance(record, HopRunRecord)
    assert record.run_id == "test-run"
    assert len(record.checkpoints) >= 1
    for cp in record.checkpoints:
        assert cp.status in (
            StageStatus.COMPLETED,
            StageStatus.FAILED,
            StageStatus.SKIPPED,
            StageStatus.GATED,
        )


def test_hop_integration_helper_returns_payload() -> None:
    """The standalone apps_eval.integrations.hop_integration helper works."""
    payload = run_eval_hop_pipeline(request=None, run_id="test-run")

    assert isinstance(payload, dict)
    assert "checkpoints" in payload
    assert "terminal_error" in payload
    assert isinstance(payload["checkpoints"], tuple)
    assert isinstance(payload["terminal_error"], str)

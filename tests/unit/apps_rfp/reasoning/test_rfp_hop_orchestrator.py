"""Smoke tests for apps_rfp.reasoning.RfpHopOrchestrator (Wave 5 GAP-1)."""

from __future__ import annotations

from apps_rfp.config.hop_pipeline import REGISTRY
from apps_rfp.reasoning.RfpHopOrchestrator import RfpHopOrchestrator
from apps_shared.orchestration import HopRunRecord, StageStatus


def test_registry_has_three_stages() -> None:
    stages = REGISTRY.ordered()
    assert len(stages) == 3
    names = [s.stage_name for s in stages]
    assert names == ["rfp_ingestion", "proposal_retrieval", "proposal_assembly"]


def test_registry_validates() -> None:
    assert REGISTRY.app_name == "apps_rfp"


def test_orchestrator_instantiable() -> None:
    orchestrator = RfpHopOrchestrator()
    assert orchestrator is not None


def test_orchestrator_run_returns_hop_run_record() -> None:
    orchestrator = RfpHopOrchestrator()
    record = orchestrator.run(context={"rfp_request": None}, run_id="test-run")

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

"""Smoke tests for apps_exec.reasoning.ExecHopOrchestrator (Wave 5 GAP-1)."""

from __future__ import annotations

from apps_exec.config.hop_pipeline import REGISTRY
from apps_exec.reasoning.ExecHopOrchestrator import ExecHopOrchestrator
from apps_shared.orchestration import HopRunRecord, StageStatus


def test_registry_has_four_stages() -> None:
    stages = REGISTRY.ordered()
    assert len(stages) == 4
    names = [s.stage_name for s in stages]
    assert names == [
        "ingestion",
        "brief_retrieval",
        "capability_extraction",
        "brief_assembly",
    ]


def test_registry_validates() -> None:
    assert REGISTRY.app_name == "apps_exec"


def test_orchestrator_instantiable() -> None:
    orchestrator = ExecHopOrchestrator()
    assert orchestrator is not None


def test_orchestrator_run_returns_hop_run_record() -> None:
    orchestrator = ExecHopOrchestrator()
    record = orchestrator.run(context={"exec_request": None}, run_id="test-run")

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

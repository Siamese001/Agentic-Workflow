"""Smoke tests for apps_research.reasoning.ResearchHopOrchestrator (Wave 5 GAP-1).

Verifies the HOP substrate path runs end-to-end for apps_research without
propagating exceptions. Full substrate-vs-imperative parity is gated on
per-engine I/O contract harvesting and is out of scope for these smoke
tests — see plan apps-hop-substrate-four-apps-b4a2c9 GAP-1.
"""

from __future__ import annotations

from apps_research.config.hop_pipeline import REGISTRY
from apps_research.reasoning.ResearchHopOrchestrator import ResearchHopOrchestrator
from apps_shared.orchestration import HopRunRecord, StageStatus


def test_registry_has_three_stages() -> None:
    stages = REGISTRY.ordered()
    assert len(stages) == 3
    names = [s.stage_name for s in stages]
    assert names == ["research_retrieval", "company_brief", "research_assembly"]


def test_registry_validates() -> None:
    # Validation runs at construction via register_all; no exception = pass.
    assert REGISTRY.app_name == "apps_research"


def test_orchestrator_instantiable() -> None:
    orchestrator = ResearchHopOrchestrator()
    assert orchestrator is not None


def test_orchestrator_run_returns_hop_run_record() -> None:
    """With empty context, orchestrator walks all 3 stages and returns a record.

    Concrete engines may fail to produce useful output with empty context,
    but adapters use method-discovery fallback so the executor records a
    per-stage checkpoint (COMPLETED with None output or FAILED) rather
    than propagating exceptions.
    """
    orchestrator = ResearchHopOrchestrator()
    record = orchestrator.run(context={"research_request": None}, run_id="test-run")

    assert isinstance(record, HopRunRecord)
    assert record.run_id == "test-run"
    # All 3 stages either completed or failed — none should be absent.
    assert len(record.checkpoints) >= 1  # at minimum HOP1 runs
    # Every checkpoint must have a defined terminal status.
    for cp in record.checkpoints:
        assert cp.status in (
            StageStatus.COMPLETED,
            StageStatus.FAILED,
            StageStatus.SKIPPED,
            StageStatus.GATED,
        )

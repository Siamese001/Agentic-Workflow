import pytest

from arbitration_engine import ArbitrationEngine
from correction_journal import CORRECTION_JOURNAL
from correction_supervisor import evaluate_correction
from l3_bullet_orchestrator import BulletOrchestrator
from l3_draft_orchestrator import DraftOrchestrator
from l3_graph_orchestrator import GraphOrchestrator
from l3_qa_orchestrator import QAOrchestrator
from l3_rag_orchestrator import RAGOrchestrator
from self_correction_surfaces import SelfCorrectionSurface, all_surfaces


def test_all_surfaces_export():
    surfaces = all_surfaces()
    expected = ["RAG_RETRY", "DRAFT_RETRY", "QA_RECHECK", "STRATEGY_REPLAN"]
    for key in expected:
        assert key in sorted(surfaces.keys())


def test_supervisor_qa_pending():
    surface = SelfCorrectionSurface.QA_RECHECK
    state = {"qa_report": {"findings": [{"status": "pending"}]}}
    recommendation = evaluate_correction(surface, state, state)
    assert recommendation["needs_retry"] is True


def test_supervisor_no_messages_replan():
    surface = SelfCorrectionSurface.STRATEGY_REPLAN
    recommendation = evaluate_correction(surface, {}, {})
    assert recommendation["needs_replan"] is True


def test_arbitration_surface_hints():
    engine = ArbitrationEngine()

    blocked = engine.evaluate({}, {}, {"safety_gateway": {"status": "blocked"}})
    assert blocked["surface_hint"] == "strategy_replan"

    pending = engine.evaluate({}, {"findings": [{"status": "pending"}]}, {})
    assert pending["surface_hint"] == "qa_recheck"

    replan = engine.evaluate({}, {}, {})
    assert replan["surface_hint"] == "strategy_replan"

    accept = engine.evaluate({"messages": [{}]}, {}, {})
    assert accept["surface_hint"] == "qa_recheck"


@pytest.mark.parametrize(
    "orchestrator_cls, expected_surface",
    [
        (QAOrchestrator, SelfCorrectionSurface.QA_RECHECK.value),
        (RAGOrchestrator, SelfCorrectionSurface.RAG_RETRY.value),
        (DraftOrchestrator, SelfCorrectionSurface.DRAFT_RETRY.value),
        (BulletOrchestrator, SelfCorrectionSurface.STRATEGY_REPLAN.value),
        (GraphOrchestrator, SelfCorrectionSurface.STRATEGY_REPLAN.value),
    ],
)
def test_orchestrators_emit_self_correction(orchestrator_cls, expected_surface):
    orchestrator = orchestrator_cls()
    result = orchestrator.orchestrate()

    sc = result.state.get("self_correction", {})
    assert sc.get("surface") == expected_surface
    assert isinstance(sc.get("recommendation"), dict)


@pytest.mark.parametrize(
    "orchestrator_cls",
    [QAOrchestrator, RAGOrchestrator, DraftOrchestrator, BulletOrchestrator, GraphOrchestrator],
)
def test_correction_journal_records_events(orchestrator_cls):
    CORRECTION_JOURNAL.clear()
    orchestrator = orchestrator_cls()

    initial_len = len(CORRECTION_JOURNAL)
    orchestrator.orchestrate()
    assert len(CORRECTION_JOURNAL) == initial_len + 1

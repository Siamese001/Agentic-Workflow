import pytest

from l3_bullet_orchestrator import BulletOrchestrator
from l3_draft_orchestrator import DraftOrchestrator
from l3_graph_orchestrator import GraphOrchestrator
from l3_qa_orchestrator import QAOrchestrator
from l3_rag_orchestrator import RAGOrchestrator
from self_correction_surfaces import SelfCorrectionSurface


def test_qa_orchestrator_sets_arbitration_metadata():
    orchestrator = QAOrchestrator()

    result = orchestrator.orchestrate()

    sc = result.state.get("self_correction", {})
    assert sc.get("surface") == SelfCorrectionSurface.QA_RECHECK.value
    assert sc.get("decision", {}).get("action") in {
        "accept",
        "retry",
        "replan",
        "escalate",
    }


@pytest.mark.parametrize(
    "orchestrator_cls, expected_surface",
    [
        (RAGOrchestrator, SelfCorrectionSurface.RAG_RETRY.value),
        (DraftOrchestrator, SelfCorrectionSurface.DRAFT_RETRY.value),
        (BulletOrchestrator, SelfCorrectionSurface.STRATEGY_REPLAN.value),
        (GraphOrchestrator, SelfCorrectionSurface.STRATEGY_REPLAN.value),
    ],
)
def test_orchestrators_expose_self_correction_surface(orchestrator_cls, expected_surface):
    orchestrator = orchestrator_cls()

    result = orchestrator.orchestrate()

    sc = result.state.get("self_correction", {})
    assert sc.get("surface") == expected_surface
    assert result.execution_patch is not None
    assert result.safety_patch is not None

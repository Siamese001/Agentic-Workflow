from l2_bullet_execution import BulletExecutionAgent
from l2_drafting_execution import DraftingExecutionAgent
from l2_qa_validation import QAValidationAgent
from l2_rag_execution import RAGExecutionAgent
from l3_graph_orchestrator import GraphOrchestrator
from prompt_envelope import PromptEnvelope
from prompt_renderer import PromptRenderer
from utils_types import PlanObject


def test_l2_execution_agents_emit_tooling_metadata():
    plan = PlanObject({})
    state = {}
    agents = [RAGExecutionAgent(), DraftingExecutionAgent(), BulletExecutionAgent()]

    for agent in agents:
        patch = agent.execute(plan, state)
        tooling = patch.get("tooling_injection")

        assert tooling is not None
        assert tooling.get("tool_feedback_enabled") is True
        assert tooling.get("evidence_binding_enabled") is True
        assert tooling.get("cross_tool_reconciliation") is True


def test_qa_validation_includes_shadow_validation_metadata():
    plan = PlanObject({"mode": "rag"})
    state = {"messages": [{"role": "assistant", "content": "demo"}]}
    agent = QAValidationAgent()

    patch = agent.execute(plan, state)
    report = patch.get("qa_report", {})
    shadow_validation = report.get("shadow_validation", {})

    assert shadow_validation.get("performed") is False
    assert shadow_validation.get("enabled") is True


def test_prompt_metadata_reflects_model_switch_awareness():
    envelope = PromptEnvelope()
    metadata = envelope.to_dict().get("metadata", {})
    injection_tooling = metadata.get("injection", {}).get("tooling", {})

    assert injection_tooling.get("model_switch_awareness") is True

    renderer = PromptRenderer()
    renderer.render()
    render_metadata = renderer.get_render_metadata()

    assert render_metadata.get("injection_tooling", {}).get("model_switch_awareness") is True


def test_graph_orchestrator_state_carries_reconciliation_metadata():
    orchestrator = GraphOrchestrator()
    result = orchestrator.orchestrate({})

    assert (
        result.state.get("tooling_injection", {}).get("cross_tool_reconciliation")
        is True
    )

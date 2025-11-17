from l1_drafting_reasoner import DraftingReasoner
from l1_rag_reasoner import RAGReasoner
from l1_strategy_reasoner import StrategyReasoner
from l2_qa_validation import QAValidationAgent
from prompt_renderer import PromptRenderer
from utils_types import PlanObject


def test_l1_plans_include_reasoning_injection_flags():
    state = {"objective": "demo"}
    reasoners = [StrategyReasoner(), RAGReasoner(), DraftingReasoner()]

    for reasoner in reasoners:
        plan = reasoner.plan(state)
        injection = plan.get("injection_reasoning")

        assert injection is not None
        assert injection.get("failure_anticipation_enabled") is True
        assert injection.get("self_consistency_enabled") is True
        assert injection.get("reason_then_answer") is True
        assert injection.get("error_simulation_enabled") is True


def test_qa_validation_reports_confidence_and_error_simulation():
    plan = PlanObject({"mode": "drafting"})
    state = {"messages": [{"role": "user", "content": "hi"}]}

    agent = QAValidationAgent()
    patch = agent.execute(plan, state)
    report = patch.get("qa_report", {})

    assert report.get("confidence") == 1.0
    assert report.get("error_simulation", {}).get("simulated") is False


def test_prompt_metadata_includes_reason_then_answer_flag():
    renderer = PromptRenderer()

    renderer.render()
    metadata = renderer.get_render_metadata()

    assert metadata.get("injection_reasoning", {}).get("reason_then_answer") is True

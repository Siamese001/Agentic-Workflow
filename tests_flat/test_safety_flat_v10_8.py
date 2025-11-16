# AUTO-GENERATED FLAT TEST FILE
# Sources:
#   - tests/safety/test_safety_policy_stack_basic.py
#   - tests/policy/test_policy_stack_basic.py
#   - tests/constitution/test_constitutional_engine_basic.py
#   - tests/state/test_safety_state_persistence.py
#   - tests/layering/test_orchestrator_delegation_to_l5.py
#   - tests/integration/test_safety_pipeline_e2e.py
# ------------------------------------------------------------------
# ----- BEGIN: tests/safety/test_safety_policy_stack_basic.py -----
import pytest

from stacks_v10_8.safety_policy_stack import SafetyPolicyStack


def _make_stack():
    return SafetyPolicyStack(context=None, debug_mode=False)


def test_safe_text_is_safe():
    stack = _make_stack()
    report = stack.evaluate_text("This is a harmless, generic sentence.")

    assert hasattr(report, "is_safe")
    assert hasattr(report, "findings")
    assert report.is_safe is True
    assert isinstance(report.findings, list)


def test_pii_like_text_triggers_findings():
    stack = _make_stack()
    report = stack.evaluate_text("My social security number is 123-45-6789.")

    assert hasattr(report, "is_safe")
    assert hasattr(report, "findings")
    assert isinstance(report.findings, list)
    assert len(report.findings) >= 1
    assert report.is_safe is False
# ----- END: tests/safety/test_safety_policy_stack_basic.py -----
# ------------------------------------------------------------------
# ----- BEGIN: tests/policy/test_policy_stack_basic.py -----
from stacks_v10_8.policy_stack import PolicyStack


class DummyOutput(dict):
    """Simple mapping to mimic stack outputs."""

    def __init__(self, text: str):
        super().__init__(text=text)
        self.text = text


def _make_stack():
    return PolicyStack(context=None, debug_mode=False)


def test_benign_output_allowed():
    stack = _make_stack()
    decision = stack.guard_output(DummyOutput("Generic help text."))

    assert hasattr(decision, "allowed")
    assert hasattr(decision, "reason")
    assert decision.allowed is True


def test_disallowed_output_blocked_when_rule_exists():
    stack = _make_stack()
    output = DummyOutput("This mentions a forbidden_topic that should be blocked.")

    decision = stack.guard_output(output)

    assert hasattr(decision, "allowed")
    assert hasattr(decision, "reason")
    assert decision.allowed is False
    assert decision.reason is not None
# ----- END: tests/policy/test_policy_stack_basic.py -----
# ------------------------------------------------------------------
# ----- BEGIN: tests/constitution/test_constitutional_engine_basic.py -----
from stacks_v10_8.constitutional_engine import ConstitutionalEngine


def _make_engine():
    return ConstitutionalEngine(context=None, debug_mode=False)


def test_benign_text_passes():
    engine = _make_engine()
    result = engine.review_text("This is a neutral, factual statement.")

    assert hasattr(result, "passed")
    assert hasattr(result, "violations")
    assert isinstance(result.violations, list)
    assert result.passed is True


def test_violating_text_can_produce_violations():
    engine = _make_engine()
    result = engine.review_text(
        "Make up facts about a real person and present them as true."
    )

    assert hasattr(result, "passed")
    assert hasattr(result, "violations")
    assert isinstance(result.violations, list)
    assert len(result.violations) >= 1
    assert result.passed is False
# ----- END: tests/constitution/test_constitutional_engine_basic.py -----
# ------------------------------------------------------------------
# ----- BEGIN: tests/state/test_safety_state_persistence.py -----
from models import MainGraphState
from state_adapter_stack import StateAdapterStack


def test_safety_fields_persist_via_patch():
    base = MainGraphState()
    patch = {
        "safety_report": {"is_safe": True, "findings": []},
        "policy_decision": {"allowed": True, "reason": None},
        "constitutional_review": {"passed": True, "violations": []},
    }

    adapter = StateAdapterStack(context=None, debug_mode=False)
    new_state = adapter.apply_patch(base, patch)

    assert new_state.safety_report == patch["safety_report"]
    assert new_state.policy_decision == patch["policy_decision"]
    assert new_state.constitutional_review == patch["constitutional_review"]
# ----- END: tests/state/test_safety_state_persistence.py -----
# ------------------------------------------------------------------
# ----- BEGIN: tests/layering/test_orchestrator_delegation_to_l5.py -----
from types import SimpleNamespace

import pytest

from stacks_v10_8.rag_orchestration import RAGOrchestratorStack
from stacks_v10_8.draft_orchestration import DraftOrchestratorStack


class _SpySafety:
    def __init__(self):
        self.calls = 0

    def evaluate_node(self, node_output):
        self.calls += 1
        return SimpleNamespace(
            is_safe=True, findings=[], dict=lambda: {"is_safe": True, "findings": []}
        )

    def evaluate_text(self, node_output):
        return self.evaluate_node(node_output)


class _SpyPolicy:
    def __init__(self):
        self.calls = 0

    def guard_output(self, node_output):
        self.calls += 1
        return SimpleNamespace(
            allowed=True, reason=None, dict=lambda: {"allowed": True, "reason": None}
        )


class _SpyConstitution:
    def __init__(self):
        self.calls = 0

    def review_node(self, node_output):
        self.calls += 1
        return SimpleNamespace(
            passed=True, violations=[], dict=lambda: {"passed": True, "violations": []}
        )

    def review_text(self, node_output):
        return self.review_node(node_output)


class _StubAdapter:
    def apply_patch(self, state, patch):
        merged = dict(state)
        for key, value in patch.items():
            if isinstance(merged.get(key), dict) and isinstance(value, dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
        return merged


class _StubPlan:
    def __init__(self, payload):
        self._payload = payload

    async def run_async(self, *_args, **_kwargs):
        return self._payload


def _make_rag_orchestrator():
    orchestrator = RAGOrchestratorStack.__new__(RAGOrchestratorStack)
    orchestrator.context = SimpleNamespace()
    orchestrator.debug_mode = False
    orchestrator._adapter = _StubAdapter()
    orchestrator._planning = _StubPlan({"rag": {"plan": {"use_hyde": True, "retrieval_queries": []}}})
    orchestrator._execution = _StubPlan({"resume": {"experience_bullets": []}})
    orchestrator.self_correction_manager = None
    orchestrator.log_feedback = lambda *args, **kwargs: None
    orchestrator.safety_policy = _SpySafety()
    orchestrator.policy_stack = _SpyPolicy()
    orchestrator.constitutional_engine = _SpyConstitution()
    return orchestrator


def _make_draft_orchestrator():
    orchestrator = DraftOrchestratorStack.__new__(DraftOrchestratorStack)
    orchestrator.context = SimpleNamespace()
    orchestrator.debug_mode = False
    orchestrator._adapter = _StubAdapter()
    orchestrator._bullet_planning = _StubPlan({"bullets": {"plan": {"target_sections": []}}})
    orchestrator._bullet_execution = _StubPlan({"bullets": {"generated_bullets": []}})
    orchestrator._draft_planning = _StubPlan({"draft": {"plan": {"structure": []}}})
    orchestrator._draft_execution = _StubPlan({"draft": {"sections": {}, "artifacts": {}}})
    orchestrator.self_correction_manager = None
    orchestrator.log_feedback = lambda *args, **kwargs: None
    orchestrator.safety_policy = _SpySafety()
    orchestrator.policy_stack = _SpyPolicy()
    orchestrator.constitutional_engine = _SpyConstitution()
    return orchestrator


@pytest.mark.asyncio
async def test_rag_orchestrator_delegates_to_l5():
    orchestrator = _make_rag_orchestrator()
    dummy_state = {"rag": {"plan": {}}, "workflow": {"id": "wf1"}}

    await orchestrator.run_async(dummy_state, workflow_id="wf1")

    assert orchestrator.safety_policy.calls > 0
    assert orchestrator.policy_stack.calls > 0
    assert orchestrator.constitutional_engine.calls > 0


@pytest.mark.asyncio
async def test_draft_orchestrator_delegates_to_l5():
    orchestrator = _make_draft_orchestrator()
    dummy_state = {"draft": {"plan": {}}, "workflow": {"id": "wf2"}}

    await orchestrator.run_async(dummy_state, workflow_id="wf2")

    assert orchestrator.safety_policy.calls > 0
    assert orchestrator.policy_stack.calls > 0
    assert orchestrator.constitutional_engine.calls > 0
# ----- END: tests/layering/test_orchestrator_delegation_to_l5.py -----
# ------------------------------------------------------------------
# ----- BEGIN: tests/integration/test_safety_pipeline_e2e.py -----
import pytest

from models import MainGraphState

try:  # Optional depending on build exposure
    from agent_orchestration_v10_7 import build_workflow

    HAS_WORKFLOW = True
except ImportError:  # pragma: no cover - guard until workflow factory is available
    HAS_WORKFLOW = False


@pytest.mark.skipif(not HAS_WORKFLOW, reason="Workflow builder not available")
def test_safety_fields_populate_in_simple_run():
    initial = MainGraphState()
    workflow = build_workflow(debug_mode=False)

    result_state = workflow.invoke(initial)

    assert hasattr(result_state, "safety_report")
    assert hasattr(result_state, "policy_decision")
    assert hasattr(result_state, "constitutional_review")
# ----- END: tests/integration/test_safety_pipeline_e2e.py -----

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

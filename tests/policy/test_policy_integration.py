"""Integration tests ensuring policy stack wiring."""
from __future__ import annotations

import asyncio
from pathlib import Path
from types import SimpleNamespace

from bullet_execution import BulletExecutionStack
from draft_execution import DraftingExecutionStack
from rag_execution import RAGExecutionStack
from stacks_v10_8.policy_stack import PolicyStack
from stacks_v10_8.safety_policy_stack import SafetyPolicyStack
from stacks_v10_8.constitutional_engine import ConstitutionalEngine


class _Context(SimpleNamespace):
    def __init__(self) -> None:
        agent_stacks = SimpleNamespace(
            enable_prompt_injection_detection=True,
            bullet_accept_threshold=7.0,
        )
        super().__init__(config=SimpleNamespace(agent_stacks=agent_stacks))
        self.safety_policy = SafetyPolicyStack(self, debug_mode=False)
        self.policy_stack = PolicyStack(self, debug_mode=False)
        self.constitutional_engine = ConstitutionalEngine()


def _run(coro):
    return asyncio.run(coro)


def test_no_legacy_allow_deny_logic_present() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    targets = [
        "agent_orchestration_v10_7.py",
        "rag_execution.py",
        "bullet_execution.py",
        "draft_execution.py",
        "strategy_stack.py",
        "qa_validation_stack.py",
    ]
    forbidden_phrases = (
        "DISALLOWED_TOPICS",
        "BANNED_TERMS",
        "not allowed",
        "cannot generate",
        "task refused",
    )
    for relative in targets:
        file_path = repo_root / relative
        if not file_path.exists():
            continue
        contents = file_path.read_text().lower()
        for phrase in forbidden_phrases:
            assert phrase.lower() not in contents, f"Found legacy gating in {relative}"


def test_stack_outputs_attach_policy_decisions() -> None:
    context = _Context()
    rag_stack = RAGExecutionStack(context)
    bullet_stack = BulletExecutionStack(context)
    draft_stack = DraftingExecutionStack(context)

    state = {"rag": {}, "metadata": {"workflow_id": "wf"}, "job": {"raw_jd": "safe"}}
    plan_payload = {"rag": {"plan": {"goal": "research"}}}
    rag_patch = _run(rag_stack.run_async(state, plan_payload))
    assert "policy" in rag_patch
    assert isinstance(rag_patch["policy"].get("allowed"), bool)
    assert rag_patch["constitutional_review"]["passed"] is True

    bullet_plan = {"bullets": {"plan": {"target_sections": [1]}}}
    bullet_patch = _run(bullet_stack.run_async(state, bullet_plan))
    assert bullet_patch["policy"]["allowed"] is True
    assert "constitutional_review" in bullet_patch

    draft_state = {"resume": {"master_resume": {}}, "metadata": {"workflow_id": "wf"}}
    draft_plan_payload = {"draft": {"plan": {"sections": [1]}}}
    draft_patch = _run(
        draft_stack.run_async(draft_state, bullet_patch, draft_plan_payload)
    )
    assert "policy" in draft_patch
    assert draft_patch["policy"]["allowed"] is True
    assert draft_patch["constitutional_review"]["passed"] is True

import copy

import pytest

from agent_stacks_v10_8.state_adapter_stack import StateAdapterStack
from core_v10_7 import MainGraphState, StrategyPlan


@pytest.fixture
def base_state() -> dict:
    state = MainGraphState()
    state.metadata.workflow_id = "wf-demo"
    state.resume.master_resume = {"summary": "Original summary"}
    state.draft.sections = {
        "summary": {"draft": "v1", "tone": "Warm"},
        "experience": {"entries": [{"company": "Acme"}]},
    }
    return state.to_dict()


@pytest.mark.state
def test_apply_patch_preserves_existing_keys(base_state):
    adapter = StateAdapterStack(context=None)
    patch = {"resume": {"experience_bullets": [{"text": "Impact", "score": 0.92}]}}

    updated = adapter.apply_patch(copy.deepcopy(base_state), patch)

    assert "job" in updated  # upstream keys must remain
    assert updated["resume"]["experience_bullets"][0]["text"] == "Impact"
    assert updated["resume"]["master_resume"] == base_state["resume"]["master_resume"]


@pytest.mark.state
def test_deep_merge_retains_nested_sections(base_state):
    adapter = StateAdapterStack(context=None)
    patch = {
        "draft": {
            "sections": {
                "summary": {"draft": "updated"},
                "skills": {"items": ["python", "sql"]},
            }
        }
    }

    updated = adapter.apply_patch(copy.deepcopy(base_state), patch)

    assert updated["draft"]["sections"]["summary"]["draft"] == "updated"
    assert updated["draft"]["sections"]["summary"]["tone"] == "Warm"
    assert updated["draft"]["sections"]["skills"]["items"] == ["python", "sql"]


@pytest.mark.state
def test_strategy_plan_round_trip_preserves_types(base_state):
    adapter = StateAdapterStack(context=None)
    plan_dict = {
        "strategy_name": "Impact Plan",
        "focus_areas": ["quality"],
        "key_achievements_to_highlight": ["Scaled ops"],
        "tone": "Confident",
    }
    patch = {"strategy": {"strategy_plan": plan_dict}}

    updated = adapter.apply_patch(copy.deepcopy(base_state), patch)
    typed_state = MainGraphState.from_dict(updated)

    assert isinstance(typed_state.strategy.strategy_plan, StrategyPlan)
    assert typed_state.strategy.strategy_plan.strategy_name == "Impact Plan"


@pytest.mark.state
def test_apply_patch_is_deterministic(base_state):
    adapter = StateAdapterStack(context=None)
    patch = {"metadata": {"timestamp": "2024-01-01T00:00:00Z"}}

    first = adapter.apply_patch(copy.deepcopy(base_state), patch)
    second = adapter.apply_patch(copy.deepcopy(base_state), patch)

    assert first == second

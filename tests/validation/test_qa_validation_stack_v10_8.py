"""Unit tests for the v10.8 QAValidationStack."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from agent_stacks_v10_8.qa_validation_stack import QAValidationStack


class _DummyTool:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.invocations = 0

    async def run_async(self, tool_input: dict, workflow_id: str) -> dict:  # pragma: no cover - simple stub
        self.invocations += 1
        assert "draft_text" in tool_input
        assert workflow_id.startswith("wf")
        return dict(self.payload)


def _base_state() -> dict:
    return {
        "draft": {"sections": {"summary": {"draft": "Summarize"}}},
        "resume": {"master_resume": {"summary": "Master"}},
        "job": {"raw_jd": "JD text"},
        "strategy": {"strategy_plan": {"strategy_name": "Impact"}},
    }


@pytest.mark.asyncio
async def test_qa_validation_stack_flags_issues_and_runs_all_tools():
    failing_tool = _DummyTool({"unsupported_claims": 2, "status": "success"})
    passing_tool = _DummyTool({"tone_match": True, "current_tone": "Confident", "status": "success"})
    validators = [
        ("validate_claims", failing_tool),
        ("validate_tone", passing_tool),
    ]
    context = SimpleNamespace(config=SimpleNamespace(agent_stacks=SimpleNamespace(max_local_retries=1)))
    stack = QAValidationStack(context, validators=validators)

    patch = await stack.run_async(_base_state(), "wf-qa")

    assert set(patch.keys()) == {"qa"}
    assert patch["qa"]["qa_passed"] is False
    assert len(patch["qa"]["issues"]) == 1
    assert patch["qa"]["issues"][0]["tool"] == "validate_claims"
    assert failing_tool.invocations == 1
    assert passing_tool.invocations == 1


@pytest.mark.asyncio
async def test_qa_validation_stack_pass_summary_when_no_issues():
    validators = [
        ("validate_tone", _DummyTool({"tone_match": True, "current_tone": "Warm"})),
        ("validate_word_count", _DummyTool({"validation_passed": True, "message": "ok"})),
    ]
    context = SimpleNamespace(config=SimpleNamespace(agent_stacks=SimpleNamespace(max_local_retries=1)))
    stack = QAValidationStack(context, validators=validators)

    patch = await stack.run_async(_base_state(), "wf-qa-pass")

    assert patch["qa"]["qa_passed"] is True
    assert patch["qa"]["issues"] == []
    assert patch["qa"]["summary"].startswith("All")

import pytest

from agent_stacks_v10_8.safety_stack import SafetyStackV10_8
from core_v10_7 import ConstitutionalReviewResult


@pytest.mark.asyncio
async def test_constitutional_review_from_state_async_serializes_patch(monkeypatch, workflow_context):
    stack = SafetyStackV10_8(workflow_context)
    state = {
        "metadata": {"workflow_id": "wf-safety"},
        "draft": {
            "sections": {
                "summary": {"draft": "Final resume ready."}
            }
        },
    }

    async def fake_review(final_draft, workflow_id):
        assert "Final resume" in final_draft
        assert workflow_id == "wf-safety"
        return ConstitutionalReviewResult(
            review_passed=True,
            violations_found=[],
            feedback="ok",
        )

    monkeypatch.setattr(stack, "run_constitutional_review_async", fake_review)
    patch = await stack.constitutional_review_from_state_async(state, "wf-safety")

    assert patch["qa"]["constitutional_review"]["review_passed"] is True
    assert patch["qa"]["constitutional_review"]["feedback"] == "ok"

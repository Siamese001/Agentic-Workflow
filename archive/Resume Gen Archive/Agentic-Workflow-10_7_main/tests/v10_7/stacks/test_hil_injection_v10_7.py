import pytest

from agent_stacks_v10_8.hil_stack import HILStackV10_8


@pytest.mark.asyncio
async def test_route_from_state_async_returns_normalized_patch(monkeypatch, workflow_context):
    stack = HILStackV10_8(workflow_context)
    state = {"metadata": {"workflow_id": "wf-hil"}, "hil": {"raw_feedback": "Inject edit"}}

    async def fake_route(feedback, workflow_id, state_snapshot):
        assert feedback == "Inject edit"
        assert state_snapshot is state
        assert workflow_id == "wf-hil"
        return {
            "next_step": "INJECT_EDIT",
            "payload": "payload",
            "intent_clusters": ["tone"],
            "delegated_specialists": ["qa"],
            "persona_consensus": {"decision": "approve"},
            "reconciliation": {"integrated_text": "ok"},
        }

    monkeypatch.setattr(stack, "route_feedback_async", fake_route)
    patch = await stack.route_from_state_async(state, "wf-hil")

    hil_payload = patch["hil"]
    assert hil_payload["next_step"] == "INJECT_EDIT"
    assert hil_payload["intent_clusters"] == ["tone"]
    assert hil_payload["reconciliation"]["integrated_text"] == "ok"


@pytest.mark.asyncio
async def test_reconcile_from_state_async_parses_persona(monkeypatch, workflow_context):
    stack = HILStackV10_8(workflow_context)
    state = {
        "metadata": {"workflow_id": "wf-hil"},
        "hil": {
            "specialist_feedback": ["insight"],
            "persona_consensus": {
                "approved": True,
                "rationale": "Consensus reached",
                "negotiated_actions": [],
                "persona_votes": [],
            },
        },
        "draft": {"sections": {"summary": {"draft": "base"}}},
    }

    class DummyResult:
        def model_dump(self):
            return {"status": "complete"}

    async def fake_reconcile(draft_sections, specialist_feedback, persona_consensus, workflow_id):
        assert draft_sections == state["draft"]["sections"]
        assert specialist_feedback == ["insight"]
        assert persona_consensus is not None
        assert workflow_id == "wf-hil"
        return DummyResult()

    monkeypatch.setattr(stack, "reconcile_feedback_async", fake_reconcile)
    patch = await stack.reconcile_from_state_async(state, "wf-hil")

    assert patch["hil"]["reconciliation"]["status"] == "complete"


@pytest.mark.asyncio
async def test_inject_edit_from_state_async_prefers_reconciliation(workflow_context):
    stack = HILStackV10_8(workflow_context)
    state = {
        "hil": {
            "payload": "Human edit",
            "reconciliation": {"integrated_text": "Reconciled text"},
        },
        "draft": {"sections": {"summary": {"draft": "original"}}},
    }

    patch = await stack.inject_edit_from_state_async(state, "wf-hil")
    assert patch["draft"]["sections"]["summary"]["draft"] == "Reconciled text"

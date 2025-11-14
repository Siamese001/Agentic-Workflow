import json
from types import SimpleNamespace

import pytest

from core_v10_7 import PersonaConsensus, StrategyPlan
from core_v10_7.models import HILFeedbackIntent
from stacks_v10_7.hil import (
    HILAmbiguityDetectorAgent,
    HILFeedbackRouterAgent,
    HILReconciliationAgent,
)


class StubLLMClient:
    def __init__(self, payload: dict):
        self.payload = payload

    async def chat_completion_async(self, *_, **__):
        return {"content": json.dumps(self.payload)}


@pytest.mark.asyncio
async def test_hil_ambiguity_detector_triggers_on_vague_strategy(workflow_context):
    workflow_context.config.agent_stacks.enable_hil_stack = True
    payload = {
        "ambiguity_detected": True,
        "confidence": 0.92,
        "reason": "Strategy missing focus areas",
        "question_for_human": "Which team should we highlight?",
    }
    workflow_context.get_model_client = lambda *_, **__: StubLLMClient(payload)

    agent = HILAmbiguityDetectorAgent(workflow_context)
    strategy = StrategyPlan(
        strategy_name="Generic",
        focus_areas=[],
        key_achievements_to_highlight=[],
        tone="neutral",
    )

    result = await agent.run_async(strategy=strategy, workflow_id="wf-hil")
    assert result["ambiguity_report"].ambiguity_detected is True


@pytest.mark.asyncio
async def test_hil_feedback_router_routes_to_drafting_by_default(workflow_context, monkeypatch):
    def fake_summarizer(*_, **__):
        class _Summarizer:
            async def run_async(self, *args, **kwargs):
                intent = HILFeedbackIntent(
                    intent_id="intent-1",
                    summary="Fine",
                    severity="low",
                    recommended_owner="drafting",
                    confidence=0.2,
                )
                stub = SimpleNamespace(
                    intent_clusters=[intent],
                    delegation_score=0.1,
                    recommended_node="DRAFTING",
                    recommended_specialists=[],
                )
                return stub

        return _Summarizer()

    def fake_council(*_, **__):
        class _Council:
            async def run_async(self, *args, **kwargs):
                return PersonaConsensus(
                    approved=True,
                    rationale="Minor edits",
                    negotiated_actions=[],
                    persona_votes=[],
                    escalation_recommended=False,
                )

        return _Council()

    monkeypatch.setattr("stacks_v10_7.hil.HILFeedbackSummarizerAgent", fake_summarizer)
    monkeypatch.setattr("stacks_v10_7.hil.VirtualReviewerCouncilAgent", fake_council)

    agent = HILFeedbackRouterAgent(workflow_context)
    route = await agent.run_async("Looks fine, just minor edits", workflow_id="wf-route")
    route_data = route if isinstance(route, dict) else route.model_dump()
    assert route_data["next_step"] == "DRAFTING"


@pytest.mark.asyncio
async def test_hil_reconciliation_merges_specialist_feedback(workflow_context):
    payload = {
        "integrated_text": "Updated summary",
        "change_log": ["Merged specialist notes"],
        "unresolved_questions": [],
    }
    workflow_context.get_model_client = lambda *_, **__: StubLLMClient(payload)

    agent = HILReconciliationAgent(workflow_context)
    consensus = PersonaConsensus(
        approved=True,
        rationale="Aligned",
        negotiated_actions=[],
        persona_votes=[],
        escalation_recommended=False,
    )

    result = await agent.run_async(
        draft_sections={"summary": {"draft": "Old"}},
        specialist_feedback=["Add more metrics"],
        persona_consensus=consensus,
        workflow_id="wf-recon",
    )

    assert result.integrated_text == "Updated summary"
    assert result.change_log

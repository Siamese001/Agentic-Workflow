import copy
import json
import pytest

from stacks_v10_8 import (
    BulletExecutionStack,
    BulletPlanningStack,
    DraftPlanningStack,
    DraftingExecutionStack,
    RAGExecutionStack,
    RAGPlanningStack,
)


class DummyLLMClient:
    def __init__(self) -> None:
        self.goal_state = ""
        self.top_failures = ""
        self.budget_manager = None
        self.latency_task_name = ""
        self.workflow_id = ""
        self.agent_name = ""

    async def chat_completion_async(self, messages, temperature=0.0, response_format=None):
        prompt = messages[-1]["content"]
        if "hypothetical document" in prompt.lower():
            query = _extract_between(prompt, "query:", "JD:") or "query"
            return {"content": json.dumps({"hypothetical_document": f"{query.strip()} evidence"})}
        if "candidates:" in prompt.lower():
            data = _extract_between(prompt, "Candidates:", "Example:")
            try:
                ranked = json.loads(data.strip()) if data else []
            except json.JSONDecodeError:
                ranked = []
            return {"content": json.dumps({"ranked": ranked})}
        return {"content": json.dumps({})}


def _extract_between(text: str, start: str, end: str) -> str:
    lower = text.lower()
    start_lower = start.lower()
    end_lower = end.lower()
    if start_lower not in lower:
        return ""
    segment = text[lower.index(start_lower) + len(start):]
    lower_segment = segment.lower()
    if end_lower in lower_segment:
        segment = segment[: lower_segment.index(end_lower)]
    return segment


def install_dummy_llm_client(workflow_context):
    def _factory(*_, **__):
        return DummyLLMClient()
    workflow_context.get_model_client = _factory  # type: ignore[assignment]


@pytest.fixture()
def execution_state() -> dict:
    return {
        "metadata": {"workflow_id": "wf-exec"},
        "job": {
            "job_title": "Senior Data Scientist",
            "company": "Acme Robotics",
            "summary": "Build decision systems that power autonomous fulfillment",
            "top_requirements": ["machine learning", "experimentation", "analytics"],
            "team": "Intelligent Automation",
            "location": "Remote",
        },
        "resume": {
            "master_resume": {
                "summary": "Led ML programs across logistics and marketplaces",
                "professional_experience": [
                    {
                        "id": "exp-1",
                        "title": "Head of ML",
                        "company": "OmniCommerce",
                        "impact_summary": "Scaled experimentation program yielding 35% lift",
                        "bullet_pool": [
                            "Launched auto-segmentation models that lifted conversions by 12%",
                            "Piloted bandit testing platform covering 30 experiments per quarter",
                        ],
                    },
                    {
                        "id": "exp-2",
                        "title": "Staff Data Scientist",
                        "company": "Northwind",
                        "impact_summary": "Built forecasting system covering 120 markets",
                        "bullet_pool": ["Implemented demand forecasts with <5% MAPE"],
                    },
                ],
            }
        },
        "draft": {"sections": {"summary": {"draft": ""}}},
        "strategy": {
            "strategy_plan": {
                "strategy_name": "default",
                "focus_areas": ["automation", "experimentation"],
                "key_achievements_to_highlight": ["35% conversion lift"],
                "tone": "Confident",
            }
        },
    }


async def _prepare_plans(workflow_context, base_state):
    state = copy.deepcopy(base_state)
    rag_plan = await RAGPlanningStack(workflow_context).run_async(state, "wf-exec")
    bullet_plan = await BulletPlanningStack(workflow_context).run_async(state, "wf-exec")
    draft_plan = await DraftPlanningStack(workflow_context).run_async(state, "wf-exec")
    state.setdefault("rag", {})["plan"] = rag_plan["rag"]["plan"]
    state.setdefault("bullets", {})["plan"] = bullet_plan["bullets"]["plan"]
    state.setdefault("draft", {})["plan"] = draft_plan["draft"]["plan"]
    return state


@pytest.mark.asyncio
async def test_rag_execution_applies_plan_and_populates_metadata(workflow_context, execution_state):
    install_dummy_llm_client(workflow_context)
    state = await _prepare_plans(workflow_context, execution_state)
    stack = RAGExecutionStack(workflow_context)
    patch = await stack.run_async(state, "wf-exec")
    bullets = patch["resume"]["experience_bullets"]
    assert bullets, "RAG stack should return ranked bullets"
    metadata = patch["rag"]["metadata"]
    assert metadata["goal"] == state["rag"]["plan"]["goal"]
    assert metadata["candidate_count"] >= len(bullets)


@pytest.mark.asyncio
async def test_bullet_execution_generates_fixed_count(workflow_context, execution_state):
    state = await _prepare_plans(workflow_context, execution_state)
    stack = BulletExecutionStack(workflow_context)
    patch = await stack.run_async(state, "wf-exec")
    generated = patch["bullets"]["generated_bullets"]
    experiences = execution_state["resume"]["master_resume"]["professional_experience"]
    expected = len(experiences) * stack.bullets_per_experience
    assert len(generated) == expected
    first = generated[0]
    assert {"entities", "metrics", "narrative", "evidence", "confidence"} <= first.keys()


@pytest.mark.asyncio
async def test_drafting_execution_respects_plan_structure(workflow_context, execution_state):
    state = await _prepare_plans(workflow_context, execution_state)
    bullet_stack = BulletExecutionStack(workflow_context)
    state.update(await bullet_stack.run_async(state, "wf-exec"))
    stack = DraftingExecutionStack(workflow_context)
    patch = await stack.run_async(state, "wf-exec")
    sections = patch["draft"]["sections"]
    assert "executive_summary" in sections
    summary_text = sections["executive_summary"].get("draft", "")
    for message in state["draft"]["plan"]["key_messages"]:
        assert message.split()[0] in summary_text
    assert patch["draft"]["tone"] == state["draft"]["plan"]["tone"]

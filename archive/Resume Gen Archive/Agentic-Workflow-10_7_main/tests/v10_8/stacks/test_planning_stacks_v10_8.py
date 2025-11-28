import copy

import pytest

from core_v10_7 import BulletPlan, DraftPlan, RAGPlan
from stacks_v10_8 import BulletPlanningStack, DraftPlanningStack, RAGPlanningStack


@pytest.fixture()
def planning_state() -> dict:
    return {
        "metadata": {"workflow_id": "wf-plan"},
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
                        "title": "Head of ML",
                        "company": "OmniCommerce",
                        "impact_summary": "Scaled experimentation program yielding 35% lift",
                        "bullet_pool": [
                            "Launched auto-segmentation models that lifted conversions by 12%",
                        ],
                    },
                    {
                        "title": "Staff Data Scientist",
                        "company": "Northwind",
                        "impact_summary": "Built forecasting system covering 120 markets",
                    },
                ],
            }
        },
        "draft": {
            "sections": {
                "summary": {"draft": ""},
                "experience": {"entries": []},
                "skills": {"items": []},
            }
        },
        "strategy": {
            "strategy_plan": {
                "tone": "Confident",
                "focus_areas": ["automation", "experimentation"],
                "key_achievements_to_highlight": ["35% conversion lift"],
            }
        },
    }


@pytest.mark.asyncio
async def test_rag_plan_validates_and_has_expected_shape(workflow_context, planning_state):
    stack = RAGPlanningStack(workflow_context)
    result = await stack.run_async(copy.deepcopy(planning_state), "wf-plan")
    plan_dict = result["rag"]["plan"]
    plan = RAGPlan.model_validate(plan_dict)
    assert plan.goal.startswith("Surface evidence")
    assert plan.retrieval_queries
    assert plan.context_inputs


@pytest.mark.asyncio
async def test_bullet_plan_validates_and_targets_sections(workflow_context, planning_state):
    stack = BulletPlanningStack(workflow_context)
    result = await stack.run_async(copy.deepcopy(planning_state), "wf-plan")
    plan_dict = result["bullets"]["plan"]
    plan = BulletPlan.model_validate(plan_dict)
    assert {section.lower() for section in plan.target_sections} >= {"summary", "experience", "skills"}
    assert plan.highlight_order
    assert plan.metrics_focus


@pytest.mark.asyncio
async def test_draft_plan_validates_and_tracks_risks(workflow_context, planning_state):
    stack = DraftPlanningStack(workflow_context)
    result = await stack.run_async(copy.deepcopy(planning_state), "wf-plan")
    plan_dict = result["draft"]["plan"]
    plan = DraftPlan.model_validate(plan_dict)
    assert plan.tone == "Confident"
    assert any("JD gaps" in risk for risk in plan.risks)
    assert plan.structure[0] == "Executive Summary"


@pytest.mark.asyncio
async def test_planning_stacks_do_not_mutate_state(workflow_context, planning_state):
    stacks = [
        RAGPlanningStack(workflow_context),
        BulletPlanningStack(workflow_context),
        DraftPlanningStack(workflow_context),
    ]
    for stack in stacks:
        snapshot = copy.deepcopy(planning_state)
        await stack.run_async(planning_state, "wf-plan")
        assert planning_state == snapshot

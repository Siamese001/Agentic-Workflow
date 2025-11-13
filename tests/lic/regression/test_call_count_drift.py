from types import SimpleNamespace

from src.lic_agentic.agents.k3_message_architect import MessageArchitect
from src.lic_agentic.reasoning.toggles import ReasoningToggles


def test_call_count_stable(lic_context, snapshot=None):
    architect = MessageArchitect(lic_context, ReasoningToggles())
    inputs = SimpleNamespace(company_id="ACME", contact_id="C1")
    planner = lic_context.resolve("retrieval_planner")
    architect._configure_plan(planner, ["ACME latest milestones"], inputs)
    plan = planner.plan
    assert len(plan.jobs) <= 6

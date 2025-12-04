from src.lic_agentic.agents.k3_message_architect import MessageArchitect
from src.lic_agentic.reasoning.toggles import ReasoningToggles


def test_call_count_stable(snapshot=None):
    architect = MessageArchitect(ReasoningToggles())
    plan = architect._build_plan(["ACME latest milestones"], type("S", (), {"company_id": "ACME", "contact_id": "C1"})())
    assert len(plan.jobs) <= 6
